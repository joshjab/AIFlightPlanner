import { render, screen, fireEvent } from '@testing-library/react';
import IcaoSelect from './IcaoSelect';

const ICAO_CODES = ['KSQL', 'KTRK', 'KSFO'];

describe('IcaoSelect', () => {
  it('renders the input and label', () => {
    render(
      <IcaoSelect label="Test" value="" onChange={() => {}} icaoList={ICAO_CODES} />
    );
    expect(screen.getByLabelText('Test')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('updates input value as user types', () => {
    render(
      <IcaoSelect label="Test" value="" onChange={() => {}} icaoList={ICAO_CODES} />
    );
    const input = screen.getByRole('combobox');
    fireEvent.change(input, { target: { value: 'KS' } });
    expect(input.value).toBe('KS');
    fireEvent.change(input, { target: { value: 'KSQL' } });
    expect(input.value).toBe('KSQL');
  });

  it('shows error for invalid ICAO code', () => {
    render(
      <IcaoSelect label="Test" value="" onChange={() => {}} icaoList={ICAO_CODES} />
    );
    const input = screen.getByRole('combobox');
    fireEvent.change(input, { target: { value: 'XXXX' } });
    fireEvent.blur(input);
    expect(screen.getByText(/invalid icao code/i)).toBeInTheDocument();
  });

  it('calls onChange with uppercase ICAO code', () => {
    const handleChange = jest.fn();
    render(
      <IcaoSelect label="Test" value="" onChange={handleChange} icaoList={ICAO_CODES} />
    );
    const input = screen.getByRole('combobox');
    fireEvent.change(input, { target: { value: 'ksfo' } });
    expect(handleChange).toHaveBeenCalledWith('KSFO');
  });
}); 