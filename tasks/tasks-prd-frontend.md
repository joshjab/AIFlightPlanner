## Tasks

- [ ] 1.0 Set up project structure and development environment
  - [x] 1.1 Choose frontend stack (React with Vite, Jest, CSS for dark theme)
  - [x] 1.2 Initialize project with chosen stack (Vite React app scaffolded in 'frontend', dependencies installed)
  - [x] 1.3 Set up directory structure for components, utils, and styles (created directories and placeholder files)
  - [x] 1.4 Add basic routing if needed (Not required for this SPA at this stage)
  - [x] 1.5 Configure testing framework (Jest, React Testing Library, Babel config complete)
  - [x] 1.6 Add dark theme base styles and ensure mobile responsiveness (theme.css implemented and imported in App.jsx)

- [x] 2.0 Implement ICAO code selection and validation (departure, destination, "Surprise Me")
  - [x] 2.1 Create static/mock ICAO code list in `utils/icaoList.js` (ICAO_CODES array and isValidIcao function implemented)
  - [x] 2.2 Build `IcaoSelect` component with dropdown/searchable select and strict validation (IcaoSelect.jsx implemented with search/filter, strict validation, and error display)
  - [x] 2.3 Integrate `IcaoSelect` for both departure and destination fields in main UI (Both selects are now in App.jsx, with state and display)
  - [x] 2.4 Implement `SurpriseMeButton` to suggest a valid destination based on preferences (SurpriseMeButton is implemented and integrated in App.jsx, sets destination randomly)
  - [x] 2.5 Write unit tests for ICAO selection and validation (All tests pass for IcaoSelect and isValidIcao)

- [x] 3.0 Build pilot preferences modal (crosswind, home base, aircraft type, localStorage)
  - [x] 3.1 Design and implement `PreferencesModal` component
  - [x] 3.2 Add form fields for crosswind, home base, and aircraft type
  - [x] 3.3 Store/retrieve preferences in browser localStorage
  - [x] 3.4 Integrate modal into main UI (settings button, etc.)
  - [x] 3.5 Write unit tests for preferences modal and localStorage logic

- [x] 4.0 Implement Briefing View UI Transformation
  - [x] 4.1 On "Plan Flight" click, transition the main container to a full-screen or expanded view.
  - [x] 4.2 Create a header bar within the briefing view that includes key flight info (departure/destination), a settings (hamburger) icon, and a prominent "X" or "Close" button.
  - [x] 4.3 Ensure the header is mobile-friendly, possibly by reducing text size or using icons.
  - [x] 4.4 Implement the "Close" button functionality to reset the view back to the initial flight planning state.
  - [x] 4.5 Add a placeholder for a map image in the briefing display, which will be implemented later.

- [X] 5.0 Create briefing display and go/no-go recommendation UI
  - [x] 5.1 Create `BriefingDisplay` component to show route, weather, NOTAMs, and airport info (mocked data)
  - [x] 5.2 Build `GoNoGoRecommendation` component to display decision and reasons
  - [x] 5.3 Integrate both components into main UI, updating on route selection
  - [x] 5.4 Write unit tests for briefing and go/no-go components

- [x] 6.1 Create a dropdown component to hide/show the detailed briefing information (weather, NOTAMs, etc.).
  - [x] 6.2 Place the `AcknowledgeButton` within the collapsible section, making it visible only when the briefing is expanded.
  - [x] 6.3 The `AcknowledgeButton` should become enabled after a delay, only when the briefing is expanded and visible.
  - [x] 6.4 Implement the `ChatInterface` component below the map but before the collapsible briefing section.
  - [x] 6.5 The `ChatInterface` should only be enabled after the briefing has been acknowledged.
  - [x] 6.6 Write unit tests for the new collapsible functionality and the chat interface integration.

- [ ] 7.0 Apply dark theme, mobile responsiveness, and error handling
  - [x] 7.1 Finalize dark theme and ensure all components use consistent styles
  - [x] 7.2 Test and refine mobile responsiveness for all UI elements
  - [x] 7.3 Implement error handling for API failures and invalid ICAO codes.
  - [x] 7.4 Display clear error messages and fallback UI as needed
  - [ ] 7.5 Write integration tests for error handling and responsiveness 