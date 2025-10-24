/**
 * Fetches the flight briefing from the backend.
 * This now requires pilotPreferences to be passed.
 */

export const getFilteredAirports = async (query) => {
  if (!query || query.length < 1) {
    return []; // Don't search for empty strings
  }
  // Use absolute URL
  const url = `http://127.0.0.1:8003/api/airports?q=${query.toUpperCase()}`;
  const response = await fetch(url);
  if (!response.ok) {
    console.error("Failed to fetch filtered airports");
    return [];
  }
  return await response.json();
};

export const getBriefing = async (departure, destination, pilotPreferences) => {
  // 1. Serialize the preferences object into a JSON string
  const prefsJson = JSON.stringify(pilotPreferences);
  
  // 2. Encode the JSON string so it's safe for a URL
  const encodedPrefs = encodeURIComponent(prefsJson);

  // 3. Use the correct endpoint and query parameters from your example
  const url = `http://127.0.0.1:8003/api/briefing?departure=${departure}&destination=${destination}&pilot_preferences=${encodedPrefs}`;

  const response = await fetch(url);
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
};