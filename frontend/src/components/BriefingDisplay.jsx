import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
// import { MOCK_BRIEFING_DATA } from '../utils/mockData'; // Removed - no longer using mock data

import { getBriefing, getFilteredAirports } from '../services/apiService'; 
import GoNoGoRecommendation from './GoNoGoRecommendation';
import AcknowledgeButton from './AcknowledgeButton';
import ChatInterface from './ChatInterface';
import './BriefingDisplay.css';

const BriefingDisplay = ({ departure, destination, pilotPreferences, onAcknowledge, briefingAcknowledged }) => {
  const [briefingData, setBriefingData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [canAcknowledge, setCanAcknowledge] = useState(false);
  // const [briefingError, setBriefingError] = useState(null); // Removed redundant error state, using 'error'

  useEffect(() => {
    // Don't fetch if props are missing
    if (!departure || !destination || !pilotPreferences) {
      setBriefingData(null);
      return;
    }

    const fetchBriefingData = async () => {
      setIsLoading(true);
      setError(null);
      setBriefingData(null);
      setIsExpanded(false); // Collapse on new search
      setCanAcknowledge(false); // Reset acknowledge
      
      try {
        // 1. Pass all required data to the API call
        const data = await getBriefing(departure, destination, pilotPreferences);
        setBriefingData(data);
        
        // Automatically expand if it's a "No-Go"
        if (data && !data.recommendation.recommendation) {
          setIsExpanded(true);
        }
      } catch (err) {
        setError(err.message || 'Failed to fetch briefing.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBriefingData();
  }, [departure, destination, pilotPreferences]); // Re-run when prefs change too

  useEffect(() => {
    if (isExpanded) {
      const timer = setTimeout(() => setCanAcknowledge(true), 3000); // 3 seconds to review
      return () => clearTimeout(timer);
    }
  }, [isExpanded]);

  // --- Render Logic ---

  if (!departure || !destination) {
    return (
      <div className="briefing-container placeholder">
        <p>Please select a departure and destination airport to generate a briefing.</p>
      </div>
    );
  }
  
  if (isLoading) {
    return (
      <div className="briefing-container loading">
        <p>Generating Briefing for {departure} to {destination}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="briefing-container error">
        <p>Error fetching briefing: {error}</p>
      </div>
    );
  }
  
  // Don't render anything if we have no data (and not loading/error)
  if (!briefingData) {
    return null;
  }

  // --- Data has been loaded ---
  // Destructure the data from the backend response
  const { recommendation, route, weather, notams, airport_info } = briefingData;

  const reasons = recommendation ? recommendation.reasons : [];

  return (
    <div className="briefing-container">
      {/* This component now displays the Go/No-Go status
        and reasons from the backend.
      */}
      <GoNoGoRecommendation
        recommendation={recommendation}
        reasons={reasons}
      />

      <div className="map-placeholder">
        <img src="https://piperowner.org/wp-content/uploads/2024/08/VFR-Charts-cross-country-6.jpg" alt="VFR Map" />
      </div>

      <ChatInterface enabled={briefingAcknowledged} />

      <div className="collapsible-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h4>View Detailed Briefing</h4>
        <div className="header-controls">
          {!isExpanded && <AcknowledgeButton onClick={() => {}} disabled={true} />}
          <span className={`arrow ${isExpanded ? 'down' : 'right'}`}></span>
        </div>
      </div>

      {isExpanded && (
        <div className="briefing-details">
          {/* The following sections are now populated from the 'briefingData' state
            using the correct property names from your backend API.
          */}
          
          <div className="briefing-section">
            <h4>Route Information</h4>
            <p><strong>Distance:</strong> {route.distance} NM</p>
            <p><strong>Estimated Time Enroute:</strong> {route.estimated_time_enroute}</p>
          </div>

          <div className="briefing-section">
            {/* Check if weather exists before accessing properties */}
            <h4>Weather</h4>
            {weather ? (
              <>
              <h5>Departure ({departure})</h5>
              <p><strong>METAR:</strong> {weather.departure.metar}</p>
              <p><strong>TAF:</strong> {weather.departure.taf}</p>
              <h5>Destination ({destination})</h5>
              <p><strong>METAR:</strong> {weather.destination.metar}</p>
              <p><strong>TAF:</strong> {weather.destination.taf}</p>
              <h5>Enroute</h5>
            {/* enroute_warnings is an array of strings */}
            <p>Enroute weather warnings are included in the Go/No-Go reasons.</p>
              </>
              ) : <p>Weather information unavailable.</p>}
          </div>

          <div className="briefing-section">
            <h4>NOTAMs</h4>
            {/* Check if notams exists before accessing properties */}
            {notams ? (
              <>
                <h5>Departure ({departure})</h5>
                <ul>
                  {/* FIX: Access a specific property (e.g., traditional_message) 
                      from the 'notam' object instead of rendering the whole object. 
                  */}
                  {notams.departure?.length > 0 ? (
                    notams.departure.map((notam, index) => (
                      <li key={notam.number || index}>{notam.traditional_message || "NOTAM text unavailable"}</li>
                    ))
                  ) : (
                    <li>No NOTAMs reported.</li>
                  )}
                </ul>
                <h5>Destination ({destination})</h5>
                <ul>
                  {/* FIX: Also applied here for destination NOTAMs. */}
                  {notams.destination?.length > 0 ? (
                    notams.destination.map((notam, index) => (
                       <li key={notam.number || index}>{notam.traditional_message || "NOTAM text unavailable"}</li>
                    ))
                  ) : (
                    <li>No NOTAMs reported.</li>
                  )}
                </ul>
              </>
            ) : <p>NOTAM information unavailable.</p>}
          </div>
          
          <div className="briefing-section">
            <h4>Airport Information</h4>
            {/* Check if airport_info and its nested objects exist */}
            {airport_info ? (
              <>
                <h5>Departure ({departure})</h5>
                {/* Add optional chaining (?.) and nullish coalescing (??) for safety */}
                <p><strong>Name:</strong> {airport_info.departure?.name ?? "N/A"}</p>
                <p><strong>Elevation:</strong> {airport_info.departure?.elevation ?? "N/A"} ft</p>
                <p><strong>Runways:</strong> {airport_info.departure?.runways ?? "N/A"}</p>

                <h5>Destination ({destination})</h5>
                {/* Add optional chaining (?.) and nullish coalescing (??) for safety */}
                <p><strong>Name:</strong> {airport_info.destination?.name ?? "N/A"}</p>
                <p><strong>Elevation:</strong> {airport_info.destination?.elevation ?? "N/A"} ft</p>
                <p><strong>Runways:</strong> {airport_info.destination?.runways ?? "N/A"}</p>
              </>
            ) : (
              <p>Airport information not available in response.</p>
            )}
          </div>
          <AcknowledgeButton onClick={onAcknowledge} disabled={!canAcknowledge} />
        </div>
      )}
    </div>
  );
};

BriefingDisplay.propTypes = {
  departure: PropTypes.string,
  destination: PropTypes.string,
  pilotPreferences: PropTypes.object, // Added this prop
  onAcknowledge: PropTypes.func.isRequired,
  briefingAcknowledged: PropTypes.bool.isRequired,
};

export default BriefingDisplay;