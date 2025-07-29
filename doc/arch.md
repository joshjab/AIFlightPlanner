### **Flight Planner Tool: System Architecture**

This document details the proposed architecture for a "Flight Planner" agent. The goal is to create a tool that assists pilots in pre-flight planning by gathering essential data, providing a preliminary go/no-go analysis, and allowing for interactive "chair flying" of the route.

#### **1. Core Concept & User Flow**

The user, a pilot, will interact with a single-page web application. The core of the application is an AI agent they can converse with.

**The typical user workflow will be:**

1.  **Destination Discovery (Optional):** The pilot can use a "Surprise Me" feature. They provide their home base, aircraft type, and desired trip length, and the agent suggests a suitable destination.
2.  **Route Input:** The pilot enters a departure and destination airport (using ICAO codes, e.g., `KSQL`, `KTRK`).
3.  **Automated Briefing:** The agent automatically fetches and presents a comprehensive briefing package, including a proposed route, Weather (METARs, TAFs), NOTAMs, and relevant airport information.
4.  **Go/No-Go Recommendation:** Based on the gathered data and pre-set pilot preferences (e.g., crosswind limits), the agent provides an initial "Go" or "No-Go" suggestion with clear reasons.
5.  **Pilot Acknowledgement:** The pilot *must* interact with the UI to acknowledge that they have read and understood all the presented data. This is a critical safety step.
6.  **Conversational Q&A:** After acknowledgement, the pilot can ask follow-up questions in natural language (e.g., "What are the operating hours for the FBO at the destination?").
7.  **Chair Flying Simulation:** The pilot can request to "chair fly" the route. The agent can provide the simulation as a full script or as an interactive, step-by-step experience.

#### **2. System Architecture Diagram**
+-----------------+      +------------------------+      +--------------------------+
|                 |      |                        |      |                          |
|  Web Frontend   |<---->|  OpenAI Agent (Backend)|<---->|   External Data APIs     |
| (HTML/CSS/JS)   |      |   (Agents SDK)         |      | (FAA, NOAA/AWC, etc.)    |
|                 |      |                        |      |                          |
+-----------------+      +-----------+------------+      +--------------------------+
^                      |
|                      |
|                      v
|      +------------------------------+
|      |       Agent Tools/Functions  |
|      |------------------------------|
|      | - suggest_destination()      |
|      | - get_route_details()        |
|      | - get_weather_briefing()     |
|      | - get_notams()               |
|      | - get_airport_info()         |
|      | - analyze_go_no_go()         |
|      | - simulate_flight_comms()    |
+----->| - get_pilot_preferences()    |
+------------------------------+

#### **3. Component Breakdown**

##### **a. Web Frontend**

* **Technology:** A simple, lightweight single-page application built with HTML, CSS, and JavaScript.
* **UI Elements:**
    * **Main Input Section:**
        * Two text inputs for "Departure" and "Destination" ICAO codes and a "Plan Flight" button.
        * A "Surprise Me" button that opens a small form for destination discovery.
    * **Pilot Preferences:** A settings modal where a pilot can input:
        * Personal minimums (max crosswind, min ceiling, etc.).
        * Home Base ICAO.
        * Primary Aircraft Type (e.g., C172, PA-28).
        * This data will be saved in the browser's `localStorage`.
    * **Briefing Display:** A well-organized, tabbed interface for the Summary, Route, Weather, NOTAMs, and Airports.
    * **Acknowledgement Gate:** A prominent button, disabled by default, labeled "Acknowledge Briefing."
    * **Chat Interface:** A standard chat window for conversational interaction.

##### **b. Backend (OpenAI Agent)**

* **Core Agent:** Instructed to act as a helpful, safety-conscious flight planning assistant. It must enforce the "acknowledgement" workflow and clearly state that its outputs are advisory only.
* **Agent Tools (Functions):**

| **Tool/Function Name** | **Parameters** | **Description** |
| -------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------- |
| `suggest_destination`            | `home_base`, `aircraft_type`, `trip_length` | Suggests a suitable destination based on aircraft range and desired flight duration.   |
| `get_route_details`              | `dep`, `dest`                               | Fetches a standard VFR or IFR route between two airports.                              |
| `get_weather_briefing`           | `route`                                     | Retrieves METARs and TAFs for airports along the route.                                |
| `get_notams`                     | `route`                                     | Pulls all relevant NOTAMs (aerodrome, center, FDC) for the flight.                     |
| `get_airport_info`               | `icao_code`                                 | Gets detailed airport data (frequencies, runways, etc.).                               |
| `analyze_go_no_go`               | `weather`, `notams`, `prefs`                | Compares fetched data against pilot preferences to generate a recommendation.          |
| `simulate_flight_communications` | `route`, `airport_data`, `mode`             | Generates a script of likely ATC communications. `mode` can be 'sequential' or 'interactive'. |

##### **c. Data Sources (Free Government APIs)**

* **Aviation Weather Center (AWC):** `https://www.aviationweather.gov/dataserver`
* **FAA NOTAM System:** `https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/`
* **FAA Airport Data:** From the 28-day NASR subscription, parsed into a queryable database.

#### **4. Key Feature Implementation Strategy**

* **Destination Suggestion ('Surprise Me'):** The `suggest_destination` function will:
    1.  Use the `aircraft_type` to look up an estimated cruise speed and endurance from an internal table.
    2.  Calculate a search radius based on the `trip_length` category (e.g., "1-2 hours" -> speed \* 1.5 hours).
    3.  Query the airport database for all public-use airports with paved runways within that radius.
    4.  Randomly select one or a few candidates and return them to the user. A future enhancement could be to perform a quick check for severely adverse weather at the suggested locations.
* **Go/No-Go Decision:** The `analyze_go_no_go` function will be a rules engine comparing flight data against pilot preferences to produce a structured output: `{decision: "Go", reasons: ["..."]}`.
* **Pilot Acknowledgement:** A workflow where the frontend enables an "Acknowledge" button that, when clicked, sends a specific `/acknowledge` message to the agent to unlock further interaction.
* **Chair Flying Simulation:** The `simulate_flight_communications` tool will support two modes:
    * **Sequential:** The agent provides the entire communication script at once, from clearance to shutdown.
    * **Interactive:** The agent provides one communication segment (e.g., the pilot's call to clearance) and then waits for the user to click a "Continue" button in the UI. The frontend then sends a `/next_comm` message to the agent, prompting it to deliver the next expected transmission. This creates a turn-by-turn simulation.