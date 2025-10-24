import React from 'react';
import PropTypes from 'prop-types';
import './GoNoGoRecommendation.css';

/**
 * Displays the Go/No-Go recommendation and reasons from the backend.
 * This component no longer contains any business logic.
 */
const GoNoGoRecommendation = ({ recommendation, reasons }) => {
  const isGo = recommendation.recommendation; // Get boolean from the backend

  // Use the backend reasons, or a default message if none are provided
  const displayReasons = reasons.length > 0 
    ? reasons 
    : ['All conditions are within acceptable parameters.'];

  return (
    <div className={`gono-container ${isGo ? 'go' : 'no-go'}`}>
      <h3 className="gono-title">{isGo ? '✅ GO' : '❌ NO-GO'} Recommendation</h3>
      <ul className="gono-reasons">
        {displayReasons.map((reason, index) => (
          // Add a class to highlight critical/info reasons
          <li 
            key={index} 
            className={reason.includes('Critical') ? 'critical' : 'info'}
          >
            {reason}
          </li>
        ))}
      </ul>
    </div>
  );
};

GoNoGoRecommendation.propTypes = {
  // Expecting the 'recommendation' object from the backend
  recommendation: PropTypes.shape({
    recommendation: PropTypes.bool.isRequired,
  }).isRequired,
  // Expecting the list of 'reasons' from the backend
  reasons: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default GoNoGoRecommendation;