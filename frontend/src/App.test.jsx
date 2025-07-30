import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';

describe('App Integration Tests', () => {
  it('disables Plan Flight button when ICAO codes are invalid', async () => {
    render(<App />);
    const planFlightButton = screen.getByRole('button', { name: /Plan Flight/i });
    expect(planFlightButton).toBeDisabled();

    const departureInput = screen.getByLabelText(/Departure Airport/i);
    const destinationInput = screen.getByLabelText(/Destination Airport/i);

    fireEvent.change(departureInput, { target: { value: 'INVALID' } });
    fireEvent.blur(departureInput);
    fireEvent.change(destinationInput, { target: { value: 'KLAX' } });
    fireEvent.blur(destinationInput);

    await waitFor(() => {
      expect(planFlightButton).toBeDisabled();
    });
    expect(screen.getAllByText(/Invalid ICAO code/i).length).toBeGreaterThan(0);
  });
});
