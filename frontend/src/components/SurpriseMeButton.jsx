import React, { useState } from 'react';

const ROUTE_TIMES = [
  { value: 'random', label: '?' },
  { value: '1hr', label: '1 hr' },
  { value: '1-2hr', label: '1-2 hr' },
  { value: '3hr', label: '3+ hr' },
  { value: 'multi', label: 'Multi-stop' },
];

// Stub: In the future, filter the list based on route time
function filterDestinationsByTime(icaoList, routeTime) {
  // TODO: Implement logic based on routeTime
  return icaoList;
}

export default function SurpriseMeButton({ icaoList, departure, onSurprise }) {
  const [routeTime, setRouteTime] = useState('1hr');

  function handleClick() {
    let filtered = icaoList.filter(code => code !== departure);
    filtered = filterDestinationsByTime(filtered, routeTime);
    if (filtered.length === 0) return;
    const randomIcao = filtered[Math.floor(Math.random() * filtered.length)];
    onSurprise(randomIcao);
  }

  return (
    <div style={{ marginBottom: '1em', width: '100%', display: 'flex', gap: 8, alignItems: 'center' }}>
      <button type="button" onClick={handleClick} style={{ flex: 1, minWidth: 0 }}>
        🎲 Surprise Me
      </button>
      <select
        value={routeTime}
        onChange={e => setRouteTime(e.target.value)}
        style={{
          width: 'auto',
          minWidth: 0,
          padding: '0.5em 1.5em 0.5em 0.75em',
          borderRadius: 'var(--border-radius)',
          background: 'var(--color-bg)',
          color: 'var(--color-text)',
          border: '1px solid var(--color-surface)',
          fontSize: '1em',
          appearance: 'none',
          backgroundImage: 'linear-gradient(45deg, var(--color-muted) 50%, transparent 50%), linear-gradient(135deg, transparent 50%, var(--color-muted) 50%)',
          backgroundPosition: 'right 0.7em top 50%, right 1.2em top 50%',
          backgroundSize: '0.5em 0.5em, 0.5em 0.5em',
          backgroundRepeat: 'no-repeat',
        }}
        aria-label="Route Time"
      >
        {ROUTE_TIMES.map(opt => (
          <option value={opt.value} key={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}
