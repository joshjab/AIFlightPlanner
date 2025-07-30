import React, { useState, useId, useEffect } from 'react';
import { isValidIcao } from '../utils/icaoList';
import './IcaoSelect.css';

export default function IcaoSelect({ label, value, onChange, icaoList, onValidationChange }) {
  const [input, setInput] = useState(value || '');
  const [touched, setTouched] = useState(false);
  const inputId = useId();

  // Sync input state with value prop
  useEffect(() => {
    setInput(value || '');
  }, [value]);

  // Filter ICAO list based on input
  const filteredList = icaoList.filter(code =>
    code.toLowerCase().includes(input.toLowerCase())
  );

  const isValid = isValidIcao(input);
  const showError = touched && input && !isValid;

  useEffect(() => {
    if (onValidationChange) {
      onValidationChange(isValid);
    }
  }, [isValid, onValidationChange]);

  return (
    <div className="icao-select-container">
      <label htmlFor={inputId} style={{ display: 'block', marginBottom: 4 }}>
        {label}
      </label>
      <input
        id={inputId}
        type="text"
        list="icao-options"
        value={input}
        onChange={e => {
          setInput(e.target.value.toUpperCase());
          onChange(e.target.value.toUpperCase());
        }}
        onBlur={() => setTouched(true)}
        placeholder="Enter or select ICAO code"
        autoComplete="off"
        className={showError ? 'icao-input error' : 'icao-input'}
      />
      <datalist id="icao-options">
        {filteredList.map(code => (
          <option value={code} key={code} />
        ))}
      </datalist>
      {showError && (
        <div style={{ color: 'var(--color-error)', fontSize: '0.95em', marginTop: 2 }}>
          Invalid ICAO code
        </div>
      )}
    </div>
  );
}
