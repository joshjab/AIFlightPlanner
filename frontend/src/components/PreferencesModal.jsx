import React, { useState, useEffect } from 'react';
import './PreferencesModal.css';

// This is the data structure your BACKEND expects
const defaultPrefs = {
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

export default function PreferencesModal({ open, onClose, onSave, initialPrefs }) {
  // Use the initialPrefs or the default
  const [prefs, setPrefs] = useState(initialPrefs || defaultPrefs);

  useEffect(() => {
    if (open) {
      setPrefs(initialPrefs || defaultPrefs);
    }
  }, [open, initialPrefs]);

  if (!open) return null;

  // Helper to update nested state (e.g., day_minimums.visibility_sm)
  const handleChange = (e, section) => {
    const { name, value, type } = e.target;
    const val = type === 'number' ? parseFloat(value) : value;

    if (section) {
      // Handle nested objects like 'day_minimums'
      setPrefs(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [name]: val,
        },
      }));
    } else {
      // Handle top-level keys like 'flight_rules'
      setPrefs(prev => ({
        ...prev,
        [name]: val,
      }));
    }
  };
  
  function handleSave(e) {
    e.preventDefault();
    onSave(prefs);
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>Pilot Preferences</h3>
        <form onSubmit={handleSave}>
          <label>
            Flight Rules
            <select 
              name="flight_rules" 
              value={prefs.flight_rules} 
              onChange={handleChange}
            >
              <option value="VFR">VFR</option>
              <option value="IFR">IFR</option>
            </select>
          </label>
          {/* TODO: You could add a multi-select for 'ratings' here */}
          
          <h4>Day Minimums</h4>
          <label>Visibility (SM):
            <input
              type="number"
              name="visibility_sm"
              value={prefs.day_minimums.visibility_sm}
              onChange={e => handleChange(e, 'day_minimums')}
            />
          </label>
          <label>Ceiling (ft):
            <input
              type="number"
              name="ceiling_ft"
              value={prefs.day_minimums.ceiling_ft}
              onChange={e => handleChange(e, 'day_minimums')}
            />
          </label>
          <label>Max Wind (kts):
            <input
              type="number"
              name="wind_speed_kts"
              value={prefs.day_minimums.wind_speed_kts}
              onChange={e => handleChange(e, 'day_minimums')}
            />
          </label>
          <label>Max Crosswind (kts):
            <input
              type="number"
              name="crosswind_component_kts"
              value={prefs.day_minimums.crosswind_component_kts}
              onChange={e => handleChange(e, 'day_minimums')}
            />
          </label>

          <h4>Night Minimums</h4>
          {/* Repeat inputs for 'night_minimums' */}
          <label>Visibility (SM):
            <input
              type="number"
              name="visibility_sm"
              value={prefs.night_minimums.visibility_sm}
              onChange={e => handleChange(e, 'night_minimums')}
            />
          </label>
          {/* ... other night minimums fields ... */}

          <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
            <button type="submit" style={{ flex: 1 }}>Save</button>
            <button type="button" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}