import React from 'react';

export default function BriefingDisplay({ briefing }) {
  if (!briefing) {
    return <div>Select a route to generate a briefing.</div>;
  }

  return (
    <div>
      <h3>Flight Briefing</h3>
      <p><strong>Route:</strong> {briefing.route}</p>
      <p><strong>Weather:</strong> {briefing.weather}</p>
      <p><strong>NOTAMs:</strong> {briefing.notams}</p>
    </div>
  );
}
