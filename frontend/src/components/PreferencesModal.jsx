import React, { useState } from 'react';
import IcaoSelect from './IcaoSelect';
import './PreferencesModal.css';

export default function PreferencesModal({ open, onClose, onSave, initialPrefs, icaoList }) {
  const [crosswind, setCrosswind] = useState(initialPrefs?.crosswind || '');
  const [homeBase, setHomeBase] = useState(initialPrefs?.homeBase || '');
  const [aircraft, setAircraft] = useState(initialPrefs?.aircraft || '');
  const [speed, setSpeed] = useState(initialPrefs?.speed || '');
  const [range, setRange] = useState(initialPrefs?.range || '');
  const [cruiseAlt, setCruiseAlt] = useState(initialPrefs?.cruiseAlt || '');

  if (!open) return null;

  function handleSave(e) {
    e.preventDefault();
    onSave({ crosswind, homeBase, aircraft, speed, range, cruiseAlt });
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>Pilot Preferences</h3>
        <form onSubmit={handleSave}>
          <label style={{ display: 'block', marginBottom: 4 }}>
            Max Crosswind (kts)
            <input
              type="number"
              min="0"
              value={crosswind}
              onChange={e => setCrosswind(e.target.value)}
              style={{ width: '100%', marginTop: 4 }}
              required
            />
          </label>
          <IcaoSelect
            label="Home Base (ICAO)"
            value={homeBase}
            onChange={setHomeBase}
            icaoList={icaoList}
          />
          <label style={{ display: 'block', marginBottom: 4 }}>
            Aircraft Type
            <input
              type="text"
              value={aircraft}
              onChange={e => setAircraft(e.target.value)}
              style={{ width: '100%', marginTop: 4 }}
              placeholder="e.g. C172"
              required
            />
          </label>
          <label style={{ display: 'block', marginBottom: 4 }}>
            Aircraft Speed (ktas)
            <input
              type="number"
              min="0"
              value={speed}
              onChange={e => setSpeed(e.target.value)}
              style={{ width: '100%', marginTop: 4 }}
              required
            />
          </label>
          <label style={{ display: 'block', marginBottom: 4 }}>
            Aircraft Range (nm)
            <input
              type="number"
              min="0"
              value={range}
              onChange={e => setRange(e.target.value)}
              style={{ width: '100%', marginTop: 4 }}
              required
            />
          </label>
          <label style={{ display: 'block', marginBottom: 4 }}>
            Preferred Cruise Altitude (ft)
            <input
              type="number"
              min="0"
              value={cruiseAlt}
              onChange={e => setCruiseAlt(e.target.value)}
              style={{ width: '100%', marginTop: 4 }}
              required
            />
          </label>
          <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
            <button type="submit" style={{ flex: 1 }}>Save</button>
            <button type="button" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}
