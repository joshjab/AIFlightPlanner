import { useState } from 'react';
import './styles/theme.css';
import IcaoSelect from './components/IcaoSelect';
import { ICAO_CODES } from './utils/icaoList';
import SurpriseMeButton from './components/SurpriseMeButton';

function App() {
  const [departure, setDeparture] = useState('');
  const [destination, setDestination] = useState('');

  return (
    <div className="app-container">
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
    </div>
  );
}

export default App;
