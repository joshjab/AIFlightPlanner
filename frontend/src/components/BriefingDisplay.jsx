import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { MOCK_BRIEFING_DATA } from '../utils/mockData';
import AcknowledgeButton from './AcknowledgeButton';
import ChatInterface from './ChatInterface';
import './BriefingDisplay.css';

const BriefingDisplay = ({ departure, destination, onAcknowledge, briefingAcknowledged }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [canAcknowledge, setCanAcknowledge] = useState(false);
  const [briefingError, setBriefingError] = useState(null);

  // Simulate API call for briefing data
  const briefing = MOCK_BRIEFING_DATA;

  useEffect(() => {
    // Simulate API error for specific ICAO codes
    if (departure === 'KDEN' || destination === 'KDEN') {
      setBriefingError('Error fetching briefing data for KDEN. Please try another airport.');
    } else {
      setBriefingError(null);
    }
  }, [departure, destination]);

  useEffect(() => {
    if (isExpanded) {
      const timer = setTimeout(() => setCanAcknowledge(true), 3000); // 3 seconds to review
      return () => clearTimeout(timer);
    }
  }, [isExpanded]);

  if (!departure || !destination) {
    return (
      <div className="briefing-container placeholder">
        <p>Please select a departure and destination airport to generate a briefing.</p>
      </div>
    );
  }

  if (briefingError) {
    return (
      <div className="briefing-container error">
        <p>{briefingError}</p>
      </div>
    );
  }

  return (
    <div className="briefing-container">
      <h3>Flight Briefing: {departure} to {destination}</h3>

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
          <div className="briefing-section">
            <h4>Route Information</h4>
            <p><strong>Distance:</strong> {briefing.route.distance} NM</p>
            <p><strong>Estimated Time Enroute:</strong> {briefing.route.estimatedTimeEnroute}</p>
          </div>

          <div className="briefing-section">
            <h4>Weather</h4>
            <h5>Departure ({briefing.route.departure})</h5>
            <p><strong>METAR:</strong> {briefing.weather.departure.metar}</p>
            <p><strong>TAF:</strong> {briefing.weather.departure.taf}</p>
            <h5>Destination ({briefing.route.destination})</h5>
            <p><strong>METAR:</strong> {briefing.weather.destination.metar}</p>
            <p><strong>TAF:</strong> {briefing.weather.destination.taf}</p>
            <h5>Enroute</h5>
            <p>{briefing.weather.enroute.warnings.join(', ')}</p>
          </div>

          <div className="briefing-section">
            <h4>NOTAMs</h4>
            <h5>Departure ({briefing.route.departure})</h5>
            <ul>
              {briefing.notams.departure.map((notam) => (
                <li key={notam.id}><strong>{notam.id}:</strong> {notam.text}</li>
              ))}
            </ul>
            <h5>Destination ({briefing.route.destination})</h5>
            <ul>
              {briefing.notams.destination.map((notam) => (
                <li key={notam.id}><strong>{notam.id}:</strong> {notam.text}</li>
              ))}
            </ul>
          </div>

          <div className="briefing-section">
            <h4>Airport Information</h4>
            <h5>Departure ({briefing.route.departure})</h5>
            <p><strong>Name:</strong> {briefing.airportInfo.departure.name}</p>
            <p><strong>Elevation:</strong> {briefing.airportInfo.departure.elevation}</p>
            <p><strong>Runways:</strong> {briefing.airportInfo.departure.runways.join(', ')}</p>
            <h5>Destination ({briefing.route.destination})</h5>
            <p><strong>Name:</strong> {briefing.airportInfo.destination.name}</p>
            <p><strong>Elevation:</strong> {briefing.airportInfo.destination.elevation}</p>
            <p><strong>Runways:</strong> {briefing.airportInfo.destination.runways.join(', ')}</p>
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
  onAcknowledge: PropTypes.func.isRequired,
  briefingAcknowledged: PropTypes.bool.isRequired,
};

export default BriefingDisplay;
