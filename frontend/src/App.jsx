import { useState } from 'react';
import './styles/theme.css';
import './App.css';
import IcaoSelect from './components/IcaoSelect';
import { ICAO_CODES } from './utils/icaoList';
import SurpriseMeButton from './components/SurpriseMeButton';
import PreferencesModal from './components/PreferencesModal';

function App() {
  const [departure, setDeparture] = useState('');
  const [destination, setDestination] = useState('');
  const [preferences, setPreferences] = useState(() => {
    const savedPrefs = localStorage.getItem('flightPlannerPrefs');
    return savedPrefs ? JSON.parse(savedPrefs) : {};
  });
  const [isModalOpen, setIsModalOpen] = useState(false);

  function handleSavePreferences(newPrefs) {
    setPreferences(newPrefs);
    localStorage.setItem('flightPlannerPrefs', JSON.stringify(newPrefs));
    setIsModalOpen(false);
  }

  return (
    <div className="app-container">
      <div style={{ position: 'absolute', top: 16, right: 16 }}>
        <button onClick={() => setIsModalOpen(true)} className="hamburger-button">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5em' }}>✈️ Flight Planner</h2>
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
      <SurpriseMeButton
        icaoList={ICAO_CODES}
        departure={departure}
        onSurprise={setDestination}
      />
      <div style={{ marginTop: '2em', color: 'var(--color-muted)' }}>
        <div>Selected Departure: <b>{departure}</b></div>
        <div>Selected Destination: <b>{destination}</b></div>
      </div>
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
