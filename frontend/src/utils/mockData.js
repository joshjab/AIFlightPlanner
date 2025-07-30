export const MOCK_BRIEFING_DATA = {
  route: {
    departure: 'KSFO',
    destination: 'KLAX',
    distance: 337, // nautical miles
    estimatedTimeEnroute: '1h 15m',
  },
  weather: {
    departure: {
      metar: 'KSFO 290853Z 21006KT 10SM FEW025 SCT045 BKN060 15/12 A2992 RMK AO2 SLP132 T01500122',
      taf: 'KSFO 290526Z 2906/3012 21008KT P6SM FEW025 SCT060 FM291500 25012G20KT P6SM SCT030 BKN050 FM300300 21008KT P6SM FEW025',
    },
    destination: {
      metar: 'KLAX 290853Z 25004KT 10SM CLR 18/10 A2995 RMK AO2 SLP141 T01830100',
      taf: 'KLAX 290526Z 2906/3012 25008KT P6SM FEW030 FM291800 26015G25KT P6SM SCT040',
    },
    enroute: {
      warnings: ['Occasional turbulence below 10,000ft'],
    },
  },
  notams: {
    departure: [
      {
        id: 'N1234/25',
        text: 'RWY 10L/28R CLSD FOR LANDING AND TAKEOFF',
      },
    ],
    destination: [
      {
        id: 'N5678/25',
        text: 'TWY C BTN TWY C1 AND TWY C2 CLSD',
      },
    ],
  },
  airportInfo: {
    departure: {
      name: 'San Francisco International Airport',
      elevation: '13 ft',
      runways: ['01L/19R', '01R/19L', '10L/28R', '10R/28L'],
    },
    destination: {
      name: 'Los Angeles International Airport',
      elevation: '128 ft',
      runways: ['06L/24R', '06R/24L', '07L/25R', '07R/25L'],
    },
  },
};
