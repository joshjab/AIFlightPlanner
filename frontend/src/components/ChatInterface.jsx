import React from 'react';
import PropTypes from 'prop-types';
import './ChatInterface.css';

const ChatInterface = ({ enabled }) => {
  const message = enabled
    ? "Welcome! How can I help you with your flight briefing?"
    : "Waiting for acknowledgement...";

  return (
    <div className="chat-interface-container">
      <div className={`chat-messages ${enabled ? 'expanded' : 'collapsed'}`}>
        <p>{message}</p>
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          placeholder={enabled ? "Type your message..." : "Acknowledge briefing to chat"}
          disabled={!enabled}
        />
        <button disabled={!enabled}>Send</button>
      </div>
    </div>
  );
};

ChatInterface.propTypes = {
  enabled: PropTypes.bool.isRequired,
};

export default ChatInterface;
