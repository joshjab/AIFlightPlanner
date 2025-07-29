// Static list of valid ICAO codes (sample, extend as needed)
export const ICAO_CODES = [
  'KSQL', // San Carlos
  'KTRK', // Truckee
  'KSFO', // San Francisco Intl
  'KOAK', // Oakland Intl
  'KSJC', // San Jose Intl
  'KRHV', // Reid-Hillview
  'KPAO', // Palo Alto
  'KHWD', // Hayward Exec
  'KLVK', // Livermore
  'KAPC', // Napa County
  'KHUA', // Redstone AAF
];

// Returns true if the code is a valid ICAO code in the list
export function isValidIcao(code) {
  return ICAO_CODES.includes(code.toUpperCase());
}

// TODO: Replace with a larger or dynamic list for production use
