import { useState, useEffect } from 'react';
import './styles/theme.css';
import './App.css';
import IcaoSelect from './components/IcaoSelect';
import { ICAO_CODES } from './utils/icaoList';
import SurpriseMeButton from './components/SurpriseMeButton';
import PreferencesModal from './components/PreferencesModal';
import BriefingDisplay from './components/BriefingDisplay';
import GoNoGoRecommendation from './components/GoNoGoRecommendation';
import AcknowledgeButton from './components/AcknowledgeButton';
import { MOCK_BRIEFING_DATA } from './utils/mockData';

const defaultPreferences = {
  ratings: ['PRIVATE'],
  flight_rules: 'VFR',
  day_minimums: {
    visibility_sm: 5.0,
    ceiling_ft: 3000,
    wind_speed_kts: 20,
    crosswind_component_kts: 10,
  },
  night_minimums: {
    visibility_sm: 7.0,
    ceiling_ft: 5000,
    wind_speed_kts: 15,
    crosswind_component_kts: 8,
  },
};

function App() {
  const [departure, setDeparture] = useState('');
  const [destination, setDestination] = useState('');
  const [isDepartureValid, setIsDepartureValid] = useState(false);
  const [isDestinationValid, setIsDestinationValid] = useState(false);

  const [preferences, setPreferences] = useState(() => {
    const savedPrefs = localStorage.getItem('flightPlannerPrefs');
    if (savedPrefs) {
      try {
        const parsed = JSON.parse(savedPrefs);
        // Deep merge with defaults to handle missing keys
        return {
          ratings: parsed.ratings || defaultPreferences.ratings,
          flight_rules: parsed.flight_rules || defaultPreferences.flight_rules,
          day_minimums: { ...defaultPreferences.day_minimums, ...(parsed.day_minimums || {}) },
          night_minimums: { ...defaultPreferences.night_minimums, ...(parsed.night_minimums || {}) },
        };
      } catch (e) {
        console.error("Failed to parse saved preferences, using defaults:", e);
      }
    }
    return defaultPreferences;
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showBriefing, setShowBriefing] = useState(false);
  const [briefingAcknowledged, setBriefingAcknowledged] = useState(false);


  function handleSavePreferences(newPrefs) {
    setPreferences(newPrefs);
    localStorage.setItem('flightPlannerPrefs', JSON.stringify(newPrefs));
    setIsModalOpen(false);
  }

  function handlePlanFlight() {
    if (departure && destination && isDepartureValid && isDestinationValid) {
      setBriefingAcknowledged(false); // Reset acknowledgment for new briefing
      setShowBriefing(true);
    }
  }

  function handleAcknowledge() {
    setBriefingAcknowledged(true);
  }

  return (
    <div className={`app-container ${showBriefing ? 'briefing-view' : ''}`}>
      {showBriefing ? (
        <div className="briefing-header">
          <button onClick={() => setShowBriefing(false)} className="close-button">X</button>
          <div className="flight-info">
            <span>{departure}</span> ✈️ <span>{destination}</span>
          </div>
          <button onClick={() => setIsModalOpen(true)} className="hamburger-button">
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      ) : (
        <div style={{ position: 'absolute', top: 16, right: 16 }}>
          <button onClick={() => setIsModalOpen(true)} className="hamburger-button">
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      )}
      {!showBriefing && <h2 style={{ textAlign: 'center', marginBottom: '1.5em' }}>✈️ Flight Planner</h2>}
      <div style={{ display: showBriefing ? 'none' : 'block' }}>
        <IcaoSelect
          label="Departure Airport (ICAO)"
          value={departure}
          onChange={setDeparture}
          onValidationChange={setIsDepartureValid}
        />
        <IcaoSelect
          label="Destination Airport (ICAO)"
          value={destination}
          onChange={setDestination}
          onValidationChange={setIsDestinationValid}
        />
        <div className="button-container">
          <button onClick={handlePlanFlight} disabled={!departure || !destination || !isDepartureValid || !isDestinationValid}>
            Plan Flight
          </button>
          <SurpriseMeButton
            //icaoList={icaoList} // Pass the fetched list
            departure={departure}
            onSurprise={setDestination}
          />
        </div>
        <div style={{ marginTop: '2em', color: 'var(--color-muted)' }}>
          <div>Selected Departure: <b>{departure}</b></div>
          <div>Selected Destination: <b>{destination}</b></div>
        </div>
      </div>

      {showBriefing && (
        <>
          {/* GoNoGoRecommendation is no longer here. 
              BriefingDisplay now renders it internally.
           */}
          <BriefingDisplay
            departure={departure}
            destination={destination}
            pilotPreferences={preferences} // Pass the preferences object
            onAcknowledge={handleAcknowledge}
            briefingAcknowledged={briefingAcknowledged}
          />
        </>
      )}

      <PreferencesModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSavePreferences}
        initialPrefs={preferences}
        //icaoList={icaoList} // Pass the fetched list
      />
    </div>
  );
}

export default App;
