import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import BriefingDisplay from './BriefingDisplay';
import { MOCK_BRIEFING_DATA } from '../utils/mockData';

describe('BriefingDisplay', () => {
  it('renders placeholder text when departure or destination is missing', () => {
    render(<BriefingDisplay />);
    expect(screen.getByText(/select a departure and destination/i)).toBeInTheDocument();
  });

  it('renders the full briefing when departure and destination are provided', async () => {
    render(<BriefingDisplay departure="KSFO" destination="KLAX" briefingAcknowledged={false} />);

    // Click to expand
    fireEvent.click(screen.getByText(/View Detailed Briefing/i));

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

  it('toggles detailed briefing visibility on header click', async () => {
    render(<BriefingDisplay departure="KSFO" destination="KLAX" briefingAcknowledged={false} />);

    // Initially, details should be hidden
    expect(screen.queryByText(/Route Information/i)).not.toBeInTheDocument();

    // Click to expand
    fireEvent.click(screen.getByText(/View Detailed Briefing/i));
    expect(screen.getByText(/Route Information/i)).toBeInTheDocument();

    // Click again to collapse
    fireEvent.click(screen.getByText(/View Detailed Briefing/i));
    expect(screen.queryByText(/Route Information/i)).not.toBeInTheDocument();
  });

  it('enables acknowledge button after delay when briefing is expanded', async () => {
    jest.useFakeTimers();
    render(<BriefingDisplay departure="KSFO" destination="KLAX" briefingAcknowledged={false} />);

    // Click to expand
    fireEvent.click(screen.getByText(/View Detailed Briefing/i));

    const acknowledgeButton = screen.getByRole('button', { name: /Acknowledge Briefing/i });
    expect(acknowledgeButton).toBeDisabled();

    await act(async () => {
      jest.advanceTimersByTime(3000);
    });

    expect(acknowledgeButton).toBeEnabled();

    jest.useRealTimers();
  });
});
