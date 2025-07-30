import React from 'react';
import PropTypes from 'prop-types';
import './GoNoGoRecommendation.css';

const GoNoGoRecommendation = ({ briefing }) => {
  const reasons = [];
  let isGo = true;

  // Example logic: Check for critical NOTAMs or weather
  if (briefing) {
    if (briefing.notams.departure.some(n => n.text.includes('CLSD'))) {
      isGo = false;
      reasons.push('Departure airport has closed runways.');
    }
    if (briefing.weather.enroute.warnings.length > 0) {
      reasons.push(`Enroute weather warnings: ${briefing.weather.enroute.warnings.join(', ')}`);
    }
    if (parseInt(briefing.weather.destination.metar.split(' ').find(s => s.endsWith('KT')).substring(3, 5)) > 20) {
        isGo = false;
        reasons.push('Destination winds exceed limits.');
    }
  }

  if (reasons.length === 0) {
    reasons.push('All conditions are within acceptable parameters.');
  }

  return (
    <div className={`gono-container ${isGo ? 'go' : 'no-go'}`}>
      <h3 className="gono-title">{isGo ? '✅ GO' : '❌ NO-GO'} Recommendation</h3>
      <ul className="gono-reasons">
        {reasons.map((reason, index) => (
          <li key={index}>{reason}</li>
        ))}
      </ul>
    </div>
  );
};

GoNoGoRecommendation.propTypes = {
  briefing: PropTypes.object,
};

export default GoNoGoRecommendation;
