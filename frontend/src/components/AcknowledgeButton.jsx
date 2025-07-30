import React from 'react';
import PropTypes from 'prop-types';
import './AcknowledgeButton.css';

const AcknowledgeButton = ({ onClick, disabled }) => {
  return (
    <button className="acknowledge-button" onClick={onClick} disabled={disabled}>
      Acknowledge Briefing
    </button>
  );
};

AcknowledgeButton.propTypes = {
  onClick: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

export default AcknowledgeButton;
