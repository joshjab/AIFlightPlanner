import React from 'react';
import { render, screen } from '@testing-library/react';
import GoNoGoRecommendation from './GoNoGoRecommendation';
import { MOCK_BRIEFING_DATA } from '../utils/mockData';

describe('GoNoGoRecommendation', () => {
  it('renders a GO recommendation when conditions are good', () => {
        const goodBriefing = {
        ...MOCK_BRIEFING_DATA,
        notams: { departure: [], destination: [] },
        weather: {
            ...MOCK_BRIEFING_DATA.weather,
            destination: { metar: 'KLAX 290853Z 25004KT 10SM CLR 18/10 A2995' },
            enroute: { warnings: [] }
        }
    };
    render(<GoNoGoRecommendation briefing={goodBriefing} />);
    expect(screen.getByText(/✅ GO/i)).toBeInTheDocument();
    expect(screen.getByText(/All conditions are within acceptable parameters/i)).toBeInTheDocument();
  });

  it('renders a NO-GO recommendation for closed runways', () => {
    render(<GoNoGoRecommendation briefing={MOCK_BRIEFING_DATA} />);
    expect(screen.getByText(/❌ NO-GO/i)).toBeInTheDocument();
    expect(screen.getByText(/Departure airport has closed runways/i)).toBeInTheDocument();
  });

  it('renders a NO-GO recommendation for high winds', () => {
    const windyBriefing = { ...MOCK_BRIEFING_DATA, weather: { ...MOCK_BRIEFING_DATA.weather, destination: { metar: 'KLAX 290853Z 25025KT 10SM CLR 18/10 A2995' } } };
    render(<GoNoGoRecommendation briefing={windyBriefing} />);
    expect(screen.getByText(/❌ NO-GO/i)).toBeInTheDocument();
    expect(screen.getByText(/Destination winds exceed limits/i)).toBeInTheDocument();
  });
});
