import { isValidIcao, ICAO_CODES } from './icaoList';

describe('isValidIcao', () => {
  it('returns true for valid ICAO codes', () => {
    ICAO_CODES.forEach(code => {
      expect(isValidIcao(code)).toBe(true);
      expect(isValidIcao(code.toLowerCase())).toBe(true);
    });
  });

  it('returns false for invalid ICAO codes', () => {
    expect(isValidIcao('XXXX')).toBe(false);
    expect(isValidIcao('')).toBe(false);
    expect(isValidIcao('K123')).toBe(false);
  });
}); 