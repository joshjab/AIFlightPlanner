import React from 'react';
import { render, screen } from '@testing-library/react';
import BriefingDisplay from './BriefingDisplay';
import { MOCK_BRIEFING_DATA } from '../utils/mockData';

describe('BriefingDisplay', () => {
  it('renders placeholder text when departure or destination is missing', () => {
    render(<BriefingDisplay />);
    expect(screen.getByText(/select a departure and destination/i)).toBeInTheDocument();
  });

  it('renders the full briefing when departure and destination are provided', () => {
    render(<BriefingDisplay departure="KSFO" destination="KLAX" />);

    // Check for key sections
    expect(screen.getByText(/Flight Briefing: KSFO to KLAX/i)).toBeInTheDocument();
    expect(screen.getByText(/Route Information/i)).toBeInTheDocument();
    expect(screen.getByText(/Weather/i)).toBeInTheDocument();
    expect(screen.getByText(/NOTAMs/i)).toBeInTheDocument();
    expect(screen.getByText(/Airport Information/i)).toBeInTheDocument();

    // Check for a specific piece of data
    expect(screen.getByText(/Distance:/i).parentElement).toHaveTextContent('Distance: 337 NM');
    expect(screen.getByText(/RWY 10L\/28R CLSD/i)).toBeInTheDocument();
  });
});
