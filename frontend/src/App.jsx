import { useState } from 'react';
import './styles/theme.css';
import './App.css';
import IcaoSelect from './components/IcaoSelect';
import { ICAO_CODES } from './utils/icaoList';
import SurpriseMeButton from './components/SurpriseMeButton';
import PreferencesModal from './components/PreferencesModal';
import BriefingDisplay from './components/BriefingDisplay';
import GoNoGoRecommendation from './components/GoNoGoRecommendation';
import { MOCK_BRIEFING_DATA } from './utils/mockData';

function App() {
  const [departure, setDeparture] = useState('');
  const [destination, setDestination] = useState('');
  const [preferences, setPreferences] = useState(() => {
    const savedPrefs = localStorage.getItem('flightPlannerPrefs');
    return savedPrefs ? JSON.parse(savedPrefs) : {};
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showBriefing, setShowBriefing] = useState(false);

  function handleSavePreferences(newPrefs) {
    setPreferences(newPrefs);
    localStorage.setItem('flightPlannerPrefs', JSON.stringify(newPrefs));
    setIsModalOpen(false);
  }

  function handlePlanFlight() {
    if (departure && destination) {
      setShowBriefing(true);
    }
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
          icaoList={ICAO_CODES}
        />
        <IcaoSelect
          label="Destination Airport (ICAO)"
          value={destination}
          onChange={setDestination}
          icaoList={ICAO_CODES}
        />
        <div className="button-container">
          <button onClick={handlePlanFlight} disabled={!departure || !destination}>
            Plan Flight
          </button>
          <SurpriseMeButton
            icaoList={ICAO_CODES}
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
          <GoNoGoRecommendation briefing={MOCK_BRIEFING_DATA} />
          <BriefingDisplay departure={departure} destination={destination} />
        </>
      )}

      <PreferencesModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSavePreferences}
        initialPrefs={preferences}
        icaoList={ICAO_CODES}
      />
    </div>
  );
}

export default App;
