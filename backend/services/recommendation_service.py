"""
This module contains the logic for generating Go/No-Go recommendations based on
pilot preferences, weather conditions, and airport information.
"""
from typing import Dict, List, Optional, Tuple, Set, Any
import re, math

from backend.models.pilot_preferences import PilotPreferences, PilotRatings, FlightRules
from backend.services.airport_service import get_airport_by_icao, get_runway_idents
from backend.models.weather_models import determine_flight_category, can_fly_vfr, FlightCategory
from backend.services import weather_service, airport_service, notam_service
from backend.utils.reason_formatter import (
    format_weather_reason,
    format_wind_reason,
    format_crosswind_reason,
    format_rating_reason,
    format_notam_reason,
    format_enroute_reason
)

def get_recommendation(
    departure_icao: str,
    arrival_icao: str,
    pilot_preferences: PilotPreferences
) -> Tuple[bool, List[str]]:
        """
        Generate a Go/No-Go recommendation based on pilot preferences and current conditions.

        Args:
            departure_icao: The ICAO code for the departure airport
            arrival_icao: The ICAO code for the arrival airport
            pilot_preferences: The pilot's preferences and minimums

        Returns:
            A tuple containing:
            - bool: True for "Go", False for "No-Go"
            - List[str]: List of reasons supporting the recommendation
        """
        print(f"\n{'='*50}")
        print(f"--- GENERATING NEW RECOMMENDATION: {departure_icao} -> {arrival_icao} ---")
        print(f"{'='*50}")
        reasons: List[str] = []
        
        # Get weather and airport conditions
        dep_weather = weather_service.get_weather_data(departure_icao)
        arr_weather = weather_service.get_weather_data(arrival_icao)
        enroute_warnings = weather_service.get_enroute_weather_warnings()

        # Get NOTAMs
        dep_notams = notam_service.get_notams(departure_icao)
        arr_notams = notam_service.get_notams(arrival_icao)

        # Process weather data into conditions
        dep_conditions = _process_weather_data(dep_weather, departure_icao)
        arr_conditions = _process_weather_data(arr_weather, arrival_icao)

        # Check basic weather minimums
        dep_go = _check_airport_conditions(
            dep_conditions,
            pilot_preferences,
            "Departure",
            reasons
        )
        arr_go = _check_airport_conditions(
            arr_conditions,
            pilot_preferences,
            "Arrival",
            reasons
        )

        # Check NOTAMs for critical issues
        # We only run NOTAM checks if the weather checks passed.
        # This can be changed if NOTAMs should be checked regardless.
        if dep_go:
            dep_notam_go = _check_notams(dep_notams, departure_icao, "Departure", reasons)
            dep_go = dep_go and dep_notam_go # Combine results
        else:
            print(f"\n--- SKIPPING NOTAM CHECK FOR {departure_icao} (Weather No-Go) ---")
            
        if arr_go:
            arr_notam_go = _check_notams(arr_notams, arrival_icao, "Arrival", reasons)
            arr_go = arr_go and arr_notam_go # Combine results
        else:
            print(f"\n--- SKIPPING NOTAM CHECK FOR {arrival_icao} (Weather No-Go) ---")


        # Check enroute conditions
        enroute_go = _check_enroute_conditions(
            enroute_warnings,
            departure_icao,
            arrival_icao,
            pilot_preferences,
            reasons
        )

        # Overall recommendation is "Go" only if all checks pass
        final_go = (dep_go and arr_go and enroute_go)
        print(f"\n--- FINAL RECOMMENDATION ---")
        print(f"DEBUG: dep_go={dep_go}, arr_go={arr_go}, enroute_go={enroute_go}")
        print(f"DEBUG: Final decision: {'GO' if final_go else 'NO-GO'}")
        
        return final_go, reasons

def _check_airport_conditions(
    conditions: Dict,
    preferences: PilotPreferences,
    airport_type: str,
    reasons: List[str]
) -> bool:
    """
    Check if the conditions at an airport meet the pilot's minimums.
    Gathers all reasons for a "no-go" decision.
    (DEBUGGING VERSION)
    """
    print(f"\n--- RUNNING AIRPORT CHECK FOR {airport_type} ({conditions.get('icao', 'N/A')}) ---")
    print(f"DEBUG: Initial conditions: {conditions}")
    print(f"DEBUG: Pilot prefs: VFR/IFR={preferences.flight_rules}, DayMins={preferences.day_minimums}, NightMins={preferences.night_minimums}")
    
    go = True

    # Handle night operations first
    if conditions["is_night"]:
        print("DEBUG: Condition is NIGHT.")
        if preferences.night_minimums is None:
            print("  -> NO-GO: Night ops but no night minimums set.")
            go = False
            reasons.append(
                f"{airport_type} operations will be at night, "
                "but pilot has not specified night minimums"
            )
            # This is a fatal error, as we cannot determine 'minimums'.
            # We must return early.
            print(f"--- Returning go={go} (Early exit: No night minimums) ---")
            return go
        minimums = preferences.night_minimums
    else:
        print("DEBUG: Condition is DAY.")
        minimums = preferences.day_minimums
    
    print(f"DEBUG: Using minimums: {minimums}")

    # For VFR flight plans, check if VFR flight is possible
    if preferences.flight_rules == FlightRules.VFR:
        print("DEBUG: Checking VFR rules.")
        if not can_fly_vfr(conditions):
            print("  -> VFR check: can_fly_vfr() is FALSE.")
            print("  -> SETTING go=False (VFR not possible). Will continue checking.")
            go = False  # Set to No-Go, but continue checking
            if conditions["is_night"]:
                print("  -> VFR check: Is NIGHT.")
                if conditions["visibility"] < 3:
                    print(f"  -> VFR check: Night visibility {conditions['visibility']}SM < 3 SM.")
                    reasons.append(
                        format_weather_reason(
                            "night VFR visibility",
                            conditions["visibility"],
                            3,
                            "SM",
                            airport_type
                        )
                    )
                if conditions["ceiling"] < 1000:
                    print(f"  -> VFR check: Night ceiling {conditions['ceiling']}ft < 1000 ft.")
                    reasons.append(
                        format_weather_reason(
                            "night VFR ceiling",
                            conditions["ceiling"],
                            1000,
                            "ft",
                            airport_type
                        )
                    )
            # Check for Special VFR possibility during day
            elif conditions["visibility"] >= 1 and conditions["ceiling"] >= 500:
                print("  -> VFR check: Day conditions allow Special VFR.")
                pass
            else:
                print("  -> VFR check: Day conditions below VFR and SVFR.")
                reasons.append(
                    f"{airport_type} conditions require IFR. Visibility {conditions['visibility']}SM and "
                    f"ceiling {conditions['ceiling']}ft are below VFR minimums and Special VFR is not possible."
                )

    # Check basic rating requirements and ratings vs conditions
    if preferences.flight_rules == FlightRules.IFR:
        print("DEBUG: Checking IFR rules.")
        if PilotRatings.INSTRUMENT not in preferences.ratings:
            print("  -> NO-GO: IFR flight but no IFR rating.")
            go = False
            reasons.append(
                format_rating_reason(
                    "IFR",
                    "an instrument rating",
                    airport_type
                )
            )
            # This is a legal "no-go". Stop checking.
            print(f"--- Returning go={go} (Early exit: No IFR rating) ---")
            return go
            
        # For IFR flights, check if the conditions are below standard approach minimums
        if conditions["ceiling"] < 200 or conditions["visibility"] < 0.5:
            print(f"  -> IFR check: Conditions {conditions['ceiling']}ft / {conditions['visibility']}SM are below standard IFR minimums.")
            print("  -> SETTING go=False (Below IFR mins). Will continue checking.")
            go = False
            reasons.append(
                f"{airport_type} conditions are below standard IFR approach minimums "
                f"(ceiling {conditions['ceiling']}ft, visibility {conditions['visibility']}SM)"
            )

    # --- FINAL CHECKS ---
    print("DEBUG: Running final weather minimum checks...")

    # Check ceiling against pilot minimums
    if conditions["ceiling"] < minimums.ceiling_ft:
        print(f"  -> NO-GO: Ceiling {conditions['ceiling']}ft is < pilot min {minimums.ceiling_ft}ft.")
        go = False
        reasons.append(
            format_weather_reason(
                "ceiling",
                conditions["ceiling"],
                minimums.ceiling_ft,
                "ft",
                airport_type
            )
        )

    # Check visibility against pilot minimums
    if conditions["visibility"] < minimums.visibility_sm:
        print(f"  -> NO-GO: Visibility {conditions['visibility']}SM is < pilot min {minimums.visibility_sm}SM.")
        go = False
        reasons.append(
            format_weather_reason(
                "visibility",
                conditions["visibility"],
                minimums.visibility_sm,
                "SM",
                airport_type
            )
        )

    # Check wind conditions
    max_wind = minimums.wind_speed_kts
    if conditions["wind_speed"] > max_wind:
        print(f"  -> NO-GO: Wind speed {conditions['wind_speed']}kts is > pilot max {max_wind}kts.")
        go = False
        reasons.append(
            format_wind_reason(
                conditions["wind_speed"],
                conditions["wind_direction"],
                conditions.get("gust_speed"),
                max_wind,
                airport_type
            )
        )

    # Check crosswind component if specified
    if minimums.crosswind_component_kts:
        if "runway_heading" not in conditions:
             print("  -> DEBUG: Skipping crosswind check, 'runway_heading' not in conditions.")
        else:
            crosswind = _calculate_crosswind(
                conditions["wind_direction"],
                conditions["wind_speed"],
                conditions["runway_heading"]
            )
            if crosswind > minimums.crosswind_component_kts:
                print(f"  -> NO-GO: Crosswind {crosswind:.1f}kts is > pilot max {minimums.crosswind_component_kts}kts.")
                go = False
                reasons.append(
                    format_crosswind_reason(
                        crosswind,
                        minimums.crosswind_component_kts,
                        airport_type,
                        conditions.get("runway", "in use")
                    )
                )

    print(f"--- Returning go={go} (Final decision for {airport_type}) ---")
    return go

def _check_notams(notams: List[dict], icao: str, airport_type: str, reasons: List[str]) -> bool:
    """
    Check NOTAMs for critical issues that would prevent flight.
    (DEBUGGING VERSION)
    """
    print(f"\n--- RUNNING NOTAM CHECK FOR {icao} ({airport_type}) ---")
    go = True  # Start with a "Go" status

    # --- 1. Get Airport Runway Data ---
    airport_data = get_airport_by_icao(icao)
    available_runways = set()
    if airport_data and airport_data.get('runways'):
        # Ensure we call the imported get_runway_idents
        available_runways = get_runway_idents(airport_data['runways']) 
    
    has_runway_data = bool(available_runways)
    closed_runways = set()
    print(f"DEBUG: Has runway data: {has_runway_data}. Runways: {available_runways}")

    # --- 2. Define Keyword Lists ---
    hard_nogo_keywords = [
        "AERODROME CLSD", "AD CLSD", "AIRPORT CLSD",
        "NO LANDING", "ALL RWY CLSD", "ALL RUNWAYS CLSD",
    ]
    critical_check_keywords = ["CLSD", "UNUSABLE", "UNSAFE"]
    info_closure_keywords = [
        "TWY", "TAXIWAY", "APRON", "RAMP", "PAD",
        "STAND", "SPOT", "GRASS", "WIP", "PORTION",
    ]
    info_unusable_keywords = [
        "PROCEDURE", "APPROACH", "APCH", "SID", "STAR",
        "RNAV", "GPS", "VFP", "VISUAL", "ILS", "VOR",
        "LOC", "R-",
    ]

    # --- 3. Process All NOTAMs ---
    for i, notam in enumerate(notams):
        message = (notam.get('traditional_message', '') + " " + 
                   notam.get('icao_message', '')).upper()
        
        print(f"\nProcessing NOTAM {i+1} / {len(notams)}:")
        #print(f"  {message.strip()[:150]}...") # Print first 150 chars
        
        if not message.strip():
            print("  -> Skipping empty message.")
            continue

        reason_added_for_this_notam = False

        # --- 3a. Check for Hard No-Go (True Airport Closure) ---
        for keyword in hard_nogo_keywords:
            # Use regex with word boundary \b to find "AD CLSD" and not "PAD CLSD"
            if re.search(r'\b' + re.escape(keyword) + r'\b', message):
                print(f"  HARD NO-GO: Found whole word '{keyword}'. Setting go=False.")
                go = False
                reasons.append(format_notam_reason(notam, airport_type, "Critical"))
                reason_added_for_this_notam = True
                break
        if reason_added_for_this_notam:
            print("  -> Handled as Hard No-Go. Moving to next NOTAM.")
            continue

        # --- 3b. Check for Contextual Keywords (CLSD, UNUSABLE) ---
        for keyword in critical_check_keywords:
            is_info = False 
            
            if keyword in message:
                #print(f"  Found keyword: '{keyword}'. Analyzing context...")
                
                if keyword == "CLSD":
                    is_info_item = False
                    for info_word in info_closure_keywords:
                        if info_word in message:
                            #print(f"    -> Context MATCH: Found info word '{info_word}'.")
                            is_info_item = True
                            break # Found an info word, stop searching
                    
                    if is_info_item:
                        #print("    -> CLASSIFICATION: Info (Closure)")
                        reasons.append(format_notam_reason(notam, airport_type, "Info"))
                        is_info = True
                    else:
                        #print("    -> CLASSIFICATION: Critical (Closure)")
                        reasons.append(format_notam_reason(notam, airport_type, "Critical"))
                        reason_added_for_this_notam = True
                        
                        if has_runway_data:
                            for rwy_ident in available_runways:
                                if f"RWY {rwy_ident}" in message or f"RUNWAY {rwy_ident}" in message:
                                    print(f"    -> Matched closed runway: {rwy_ident}")
                                    closed_runways.add(rwy_ident)
                        else:
                            print("    -> No runway data, treating as Critical.")

                elif keyword in ["UNUSABLE", "UNSAFE"]:
                    is_procedure = False
                    for info_word in info_unusable_keywords:
                        if info_word in message:
                            #print(f"    -> Context MATCH: Found info word '{info_word}'.")
                            is_procedure = True
                            break
                    
                    if is_procedure:
                        #print(f"    -> CLASSIFICATION: Info (Unusable Procedure/System)")
                        reasons.append(format_notam_reason(notam, airport_type, "Info"))
                        is_info = True
                    else:
                        #print(f"    -> CLASSIFICATION: Critical (Unusable/Unsafe)")
                        reasons.append(format_notam_reason(notam, airport_type, "Critical"))
                        reason_added_for_this_notam = True
            
            if reason_added_for_this_notam or is_info:
                #print("  -> Handled. Moving to next NOTAM.")
                break # Keyword was found and handled, move to the next NOTAM
            
        if not reason_added_for_this_notam and not is_info:
             print("  -> No critical keywords found. Ignoring.")

    # --- 4. Final Runway Check ---
    #print("\n--- Final Check (NOTAMs) ---")
    if has_runway_data and len(available_runways) > 0 and available_runways.issubset(closed_runways):
        print(f"  All runways reported closed: {closed_runways}. Setting go=False.")
        go = False
        all_runways_closed_reason = f"{airport_type} airport: All available runways are reported closed by NOTAMs."
        if all_runways_closed_reason not in reasons:
            reasons.append(all_runways_closed_reason)
    else:
        print(f"  Runway status OK. Closed: {closed_runways} / Available: {available_runways}")

    print(f"--- Returning go={go} (Final decision for NOTAMs) ---")
    return go

def _check_enroute_conditions(
    warnings: List[str],
    departure_icao: str,
    arrival_icao: str,
    preferences: PilotPreferences,
    reasons: List[str]
) -> bool:
    """
    Check enroute conditions for potential hazards.
    """
    print(f"\n--- RUNNING ENROUTE CHECK ---")
    go = True

    if not warnings:
        print("DEBUG: No enroute warnings found.")
        return go

    for warning in warnings:
        warning_upper = warning.upper()
        print(f"DEBUG: Checking warning: {warning_upper[:100]}...")
        
        warning_type = "SIGMET" if "SIGMET" in warning_upper else "AIRMET"
        
        # Check for thunderstorms if pilot prefers to avoid them
        if not preferences.allow_thunderstorms_nearby and "THUNDERSTORM" in warning_upper:
            print("  -> NO-GO: Thunderstorms found and pilot avoids them.")
            go = False
            reasons.append(format_enroute_reason("thunderstorms", warning_type, warning))
            
        # Check precipitation type against preferences
        if not preferences.allow_rain and "RAIN" in warning_upper:
            print("  -> NO-GO: Rain found and pilot avoids it.")
            go = False
            reasons.append(format_enroute_reason("rain", warning_type, warning))
            
        if not preferences.allow_snow and "SNOW" in warning_upper:
            print("  -> NO-GO: Snow found and pilot avoids it.")
            go = False
            reasons.append(format_enroute_reason("snow", warning_type, warning))
            
        # Always warn about severe conditions
        if any(hazard in warning_upper for hazard in ["TORNADO", "HURRICANE", "SEVERE TURBULENCE"]):
            print("  -> NO-GO: Severe weather found.")
            go = False
            reasons.append(format_enroute_reason("severe weather", warning_type, warning))

    print(f"--- Returning go={go} (Final decision for Enroute) ---")
    return go

def _process_weather_data(weather_data: Dict, icao_code: str) -> Dict:
    """
    Process raw weather data into a conditions dictionary.

    Args:
        weather_data: Raw weather data from weather service
        icao_code: Airport ICAO code for error messages

    Returns:
        Dict containing processed conditions
    """
    print(f"DEBUG: Processing weather data for {icao_code}")
    metar_str = weather_data.get("metar", "")
    print(f"DEBUG: Raw METAR: {metar_str}")

    # Set sane defaults for a "perfect" VFR day
    conditions = {
        "icao": icao_code,
        "ceiling": 99999,
        "visibility": 10.0,
        "wind_speed": 0,
        "wind_direction": 0,
        "gust_speed": None,
        "runway_heading": 0,
        "is_night": False, # Default to day
        "flight_category": FlightCategory.VFR.value
    }

    # --- 1. Get Runway Heading ---
    # Attempt to get the *first* available runway heading for crosswind calc
    try:
        airport_data = get_airport_by_icao(icao_code)
        if airport_data and airport_data.get('runways'):
            runway_str = airport_data.get('runways') # "04L/22R, 04R/22L"
            first_rwy_pair = runway_str.split(',')[0] # "04L/22R"
            first_rwy_ident = first_rwy_pair.split('/')[0].strip() # "04L"
            # Remove L/R/C to get the number
            heading_str = first_rwy_ident.rstrip('LRC')
            if heading_str.isdigit():
                conditions['runway_heading'] = int(heading_str) * 10 # "04" -> 40
    except Exception as e:
        print(f"DEBUG: Could not parse runway data for {icao_code}: {e}")
        # 'runway_heading' will keep its default of 0

    # --- 2. Calculate is_night ---
    # TODO: Implement night calculation using airport lat/lon and observation time
    # This requires a library like 'astral' to calculate sunrise/sunset
    # For now, we default to False.
    conditions['is_night'] = False

    # --- 3. Parse METAR String ---
    if not metar_str:
        print(f"DEBUG: No METAR string for {icao_code}, using defaults.")
        return conditions
    
    # Wind: 27007KT or 25014G25KT or VRB03KT
    wind_match = re.search(r'(\d{3}|VRB)(\d{2,3})(G(\d{2,3}))?KT', metar_str)
    if wind_match:
        dir_str = wind_match.group(1)
        conditions['wind_direction'] = 0 if dir_str == 'VRB' else int(dir_str)
        conditions['wind_speed'] = int(wind_match.group(2))
        if wind_match.group(4):
            conditions['gust_speed'] = int(wind_match.group(4))

    # Visibility: 10SM or 1 1/2SM or 1/2SM or M1/4SM or P6SM
    vis_sm = 10.0 # Default
    if 'CAVOK' in metar_str:
        vis_sm = 10.0
    else:
        vis_match_complex = re.search(r' ((\d+)\s(\d/\d))SM', metar_str) # 1 1/2SM
        vis_match_frac = re.search(r' (M?(\d/\d))SM', metar_str)        # 1/2SM or M1/4SM
        vis_match_whole = re.search(r' ([P]?(\d+))SM', metar_str)       # 10SM or P6SM

        if vis_match_complex:
            whole = int(vis_match_complex.group(2))
            frac_parts = vis_match_complex.group(3).split('/')
            vis_sm = whole + (int(frac_parts[0]) / int(frac_parts[1]))
        elif vis_match_frac:
            vis_str = vis_match_frac.group(1)
            if vis_str.startswith('M'):
                vis_sm = 0.0 # M1/4 is below minimums
            else:
                frac_parts = vis_str.split('/')
                vis_sm = int(frac_parts[0]) / int(frac_parts[1])
        elif vis_match_whole:
            vis_str_p = vis_match_whole.group(1)
            vis_str_num = vis_match_whole.group(2)
            if vis_str_p.startswith('P'):
                vis_sm = 7.0 # P6SM means "greater than 6"
            else:
                vis_sm = float(vis_str_num)
    conditions['visibility'] = vis_sm

    # Ceiling: Lowest BKN or OVC layer
    # BKN100 SCT029 BKN011
    layer_matches = re.findall(r'(BKN|OVC)(\d{3})', metar_str)
    if layer_matches:
        lowest_ceiling = 99999
        for layer in layer_matches:
            altitude = int(layer[1]) * 100
            if altitude < lowest_ceiling:
                lowest_ceiling = altitude
        conditions['ceiling'] = lowest_ceiling
    elif 'CAVOK' in metar_str or 'CLR' in metar_str or 'SKC' in metar_str:
        conditions['ceiling'] = 99999
    # If no BKN/OVC, 'ceiling' remains the default 99999

    # --- 4. Final Calculation ---
    category = determine_flight_category(conditions['ceiling'], conditions['visibility'])
    conditions["flight_category"] = category.value
    
    print(f"DEBUG: Processed conditions for {icao_code}: {conditions}")
    return conditions

def _calculate_crosswind(
    wind_direction: int,
    wind_speed: float,
    runway_heading: int
) -> float:
    """
    Calculate the crosswind component for a given wind and runway.
    """
    angle = abs(wind_direction - runway_heading)
    if angle > 180:
        angle = 360 - angle
    return abs(wind_speed * math.sin(math.radians(angle)))


if __name__ == "__main__":
    from backend.models.pilot_preferences import (
        PilotPreferences,
        PilotRatings,
        WeatherMinimums,
        FlightRules
    )

    def test_recommendation_service():
        # Create sample pilot preferences
        preferences = PilotPreferences(
            ratings=[PilotRatings.PRIVATE],  # VFR only pilot
            flight_rules=FlightRules.VFR,
            day_minimums=WeatherMinimums(
                visibility_sm=5,
                ceiling_ft=3000,
                wind_speed_kts=15,
                crosswind_component_kts=8
            ),
            # Optional fields with defaults
            night_minimums=None,  # No night operations
            allow_rain=True,
            allow_snow=False,
            allow_thunderstorms_nearby=False
        )

        # Store original get_weather_data function
        original_get_weather = weather_service.get_weather_data

        # Create mock weather data function
        # Store original service functions
        original_get_weather = weather_service.get_weather_data
        original_get_warnings = weather_service.get_enroute_weather_warnings
        original_get_notams = notam_service.get_notams

        # Create mock weather function
        def mock_get_weather(icao: str):
            # Return good VFR conditions for KXXX and marginal VFR for KYYY
            if icao == "KXXX":
                return {
                    "metar": "KXXX 201253Z 18010KT 7SM FEW040 22/14 A3001",
                    "taf": "KXXX 201200Z 2012/2112 18012KT P6SM FEW040"
                }
            else:
                return {
                    "metar": "KYYY 201253Z 09012KT 4SM BR BKN025 18/16 A2992",
                    "taf": "KYYY 201200Z 2012/2112 09010KT 4SM BR BKN025"
                }

        # Create mock enroute warnings function
        def mock_get_warnings():
            return [
                "AIRMET TANGO VALID UNTIL 210300 FOR TURB... MOD TURB BLW FL180",
                "SIGMET A1 VALID 201300/201700 THUNDERSTORMS OBSD MOVING EAST 25KT"
            ]

        # Create mock NOTAMs function
        def mock_get_notams(icao: str):
            if icao == "KXXX":
                return [
                    {"traditional_message": "!KXXX 10/001 KXXX RWY 18/36 EDGE LIGHTING OTS"},
                    {"traditional_message": "!KXXX 10/002 KXXX TWY A CLSD"}
                ]
            else:
                return [
                    {"traditional_message": "!KYYY 10/001 KYYY FUEL UNAVBL"},
                    {"traditional_message": "!KYYY 10/002 KYYY BIRDS VICINITY OF RWY"}
                ]
        
        # MOCK MOCKS FOR IMPORTS THAT AREN'T HERE
        global get_runway_idents
        def mock_get_runway_idents(runway_data: str):
            idents = set()
            if isinstance(runway_data, str):
                runway_pairs = runway_data.split(',')
                for pair in runway_pairs:
                    parts = pair.split('/')
                    for part in parts:
                        part = part.strip()
                        if part:
                            idents.add(part)
            return idents
        
        global get_airport_by_icao
        def mock_get_airport(icao: str):
            if icao == "KXXX":
                return {'runways': '18/36'}
            return {'runways': '09/27'}

        get_runway_idents = mock_get_runway_idents
        get_airport_by_icao = mock_get_airport


        # Replace the real functions with our mocks
        weather_service.get_weather_data = mock_get_weather
        weather_service.get_enroute_weather_warnings = mock_get_warnings
        notam_service.get_notams = mock_get_notams

        try:
            # Test the service with our mock data
            go, reasons = get_recommendation("KXXX", "KYYY", preferences)

            print(f"\nRecommendation: {'GO' if go else 'NO-GO'}")
            print("\nReasons:")
            for reason in reasons:
                print(f"- {reason}")
        
        finally:
            # Restore original functions
            weather_service.get_weather_data = original_get_weather
            weather_service.get_enroute_weather_warnings = original_get_warnings
            notam_service.get_notams = original_get_notams

    # Run the test
    # test_recommendation_service() # Commented out to prevent execution error

def calculate_route_info(departure_icao: str, destination_icao: str) -> Tuple[float, str]:
    """
    Calculate the distance and estimated time between two airports.
    
    Args:
        departure_icao: The ICAO code for the departure airport
        destination_icao: The ICAO code for the destination airport
        
    Returns:
        Tuple containing:
        - float: Distance in nautical miles
        - str: Estimated time enroute in "HH:MM" format
        
    Raises:
        ValueError: If airport not found or missing required coordinates
    """
    dep_airport = get_airport_by_icao(departure_icao)
    dest_airport = get_airport_by_icao(destination_icao)
    
    if not dep_airport or not dest_airport:
        raise ValueError("Airport not found")
        
    # Validate coordinates
    if not dep_airport["latitude"] or not dep_airport["longitude"]:
        raise ValueError(f"Missing coordinates for departure airport {departure_icao}")
    if not dest_airport["latitude"] or not dest_airport["longitude"]:
        raise ValueError(f"Missing coordinates for destination airport {destination_icao}")
        
    # Convert latitude/longitude to radians
    lat1 = math.radians(dep_airport["latitude"])
    lon1 = math.radians(dep_airport["longitude"])
    lat2 = math.radians(dest_airport["latitude"])
    lon2 = math.radians(dest_airport["longitude"])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in nautical miles
    r = 3440.065  # Earth radius in nautical miles
    
    # Calculate distance
    distance = round(c * r)
    
    # Estimate time (assuming 120 knots ground speed)
    hours = distance / 120
    total_minutes = int(hours * 60)
    hrs = total_minutes // 60
    mins = total_minutes % 60
    estimated_time = f"{hrs:02d}:{mins:02d}"
    
    return distance, estimated_time