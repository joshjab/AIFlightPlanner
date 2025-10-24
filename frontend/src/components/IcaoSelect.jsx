import React, { useState, useId, useEffect } from 'react';
import { getFilteredAirports } from '../services/apiService'; 
import './IcaoSelect.css';


export default function IcaoSelect({ label, value, onChange, onValidationChange }) {
  const [input, setInput] = useState(value || '');
  const [touched, setTouched] = useState(false);
  const [options, setOptions] = useState([]); // State for filtered options
  const inputId = useId();
// --- Debounce Effect for Fetching ---
  useEffect(() => {
    // Don't fetch if input is too short
    if (input.length < 1) {
       setOptions([]);
       return;
    }

    // Set up a timer
    const debounceTimer = setTimeout(async () => {
      const filtered = await getFilteredAirports(input);
      setOptions(filtered);
    }, 300); // Wait 300ms after user stops typing

    // Cleanup function to cancel the timer if user types again
    return () => clearTimeout(debounceTimer);

  }, [input]); // Re-run effect when input changes


  // --- Validation Logic ---
  // An input is valid if it's exactly 4 chars and exists in the *current* options
  // (This implies the backend search returned it as an exact match)
  const isValid = input.length === 4 && options.includes(input);
  const showError = touched && input && !isValid && input.length >= 4; // Only show error for 4 chars

  // Notify parent about validation status
  useEffect(() => {
    if (onValidationChange) {
      onValidationChange(isValid);
    }
  }, [isValid, onValidationChange]);

  // Sync input state if parent value changes externally
  useEffect(() => {
    setInput(value || '');
  }, [value]);


  return (
    <div className="icao-select-container">
      <label htmlFor={inputId} style={{ display: 'block', marginBottom: 4 }}>
        {label}
      </label>
      <input
        id={inputId}
        type="text"
        list={`icao-options-${inputId}`} // Use unique ID for datalist
        value={input}
        onChange={e => {
          const upperVal = e.target.value.toUpperCase();
          setInput(upperVal);
          onChange(upperVal); // Notify parent immediately
        }}
        onBlur={() => setTouched(true)}
        placeholder="Enter ICAO code (e.g., KMDQ)"
        autoComplete="off"
        maxLength={4} // Limit input length
        className={showError ? 'icao-input error' : 'icao-input'}
      />
      {/* Datalist now uses the fetched options */}
      <datalist id={`icao-options-${inputId}`}>
        {options.map(code => (
          <option value={code} key={code} />
        ))}
      </datalist>
      {showError && (
        <div className="error-text">
          Invalid or unknown ICAO code
        </div>
      )}
    </div>
  );
};