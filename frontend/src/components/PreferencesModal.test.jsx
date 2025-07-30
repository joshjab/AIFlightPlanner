import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PreferencesModal from './PreferencesModal';
import { ICAO_CODES } from '../utils/icaoList';

describe('PreferencesModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();

  const initialPrefs = {
    crosswind: '15',
    homeBase: 'KSFO',
    aircraft: 'C172',
    speed: '120',
    range: '500',
    cruiseAlt: '10000',
  };

  it('renders correctly when open', () => {
    render(
      <PreferencesModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        initialPrefs={initialPrefs}
        icaoList={ICAO_CODES}
      />
    );

    expect(screen.getByText('Pilot Preferences')).toBeInTheDocument();
    expect(screen.getByLabelText('Max Crosswind (kts)')).toHaveValue(15);
    expect(screen.getByLabelText('Home Base (ICAO)')).toHaveValue('KSFO');
    expect(screen.getByLabelText('Aircraft Type')).toHaveValue('C172');
    expect(screen.getByLabelText('Aircraft Speed (ktas)')).toHaveValue(120);
    expect(screen.getByLabelText('Aircraft Range (nm)')).toHaveValue(500);
    expect(screen.getByLabelText('Preferred Cruise Altitude (ft)')).toHaveValue(10000);
  });

  it('calls onSave with the updated preferences', () => {
    render(
      <PreferencesModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        initialPrefs={initialPrefs}
        icaoList={ICAO_CODES}
      />
    );

    fireEvent.change(screen.getByLabelText('Max Crosswind (kts)'), { target: { value: '20' } });
    fireEvent.change(screen.getByLabelText('Aircraft Type'), { target: { value: 'PA-28' } });

    fireEvent.click(screen.getByText('Save'));

    expect(mockOnSave).toHaveBeenCalledWith({
      crosswind: '20',
      homeBase: 'KSFO',
      aircraft: 'PA-28',
      speed: '120',
      range: '500',
      cruiseAlt: '10000',
    });
  });

  it('calls onClose when the cancel button is clicked', () => {
    render(
      <PreferencesModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        initialPrefs={initialPrefs}
        icaoList={ICAO_CODES}
      />
    );

    fireEvent.click(screen.getByText('Cancel'));

    expect(mockOnClose).toHaveBeenCalled();
  });
});
