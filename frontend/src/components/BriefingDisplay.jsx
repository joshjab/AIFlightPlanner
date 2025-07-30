import React from 'react';
import PropTypes from 'prop-types';
import { MOCK_BRIEFING_DATA } from '../utils/mockData';
import './BriefingDisplay.css';

const BriefingDisplay = ({ departure, destination }) => {
  // In a real app, you'd fetch this data based on departure/destination
  const briefing = MOCK_BRIEFING_DATA;

  if (!departure || !destination) {
    return (
      <div className="briefing-container placeholder">
        <p>Please select a departure and destination airport to generate a briefing.</p>
      </div>
    );
  }

  return (
    <div className="briefing-container">
      <h3>Flight Briefing: {briefing.route.departure} to {briefing.route.destination}</h3>

      <div className="map-placeholder">
        <img src="https://piperowner.org/wp-content/uploads/2024/08/VFR-Charts-cross-country-6.jpg" alt="VFR Map" />
      </div>

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
    </div>
  );
};

BriefingDisplay.propTypes = {
  departure: PropTypes.string,
  destination: PropTypes.string,
};

export default BriefingDisplay;