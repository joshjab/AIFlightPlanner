## Relevant Files

- `frontend/src/App.jsx` - Main application entry point and layout.
- `frontend/src/components/IcaoSelect.jsx` - Dropdown/searchable select for ICAO code entry and validation.
- `frontend/src/components/SurpriseMeButton.jsx` - Button and logic for "Surprise Me" destination suggestion.
- `frontend/src/components/PreferencesModal.jsx` - Modal for pilot preferences (crosswind, home base, aircraft type).
- `frontend/src/components/BriefingDisplay.jsx` - Displays route, weather, NOTAMs, and airport info.
- `frontend/src/components/GoNoGoRecommendation.jsx` - Shows go/no-go decision and reasons.
- `frontend/src/components/AcknowledgeButton.jsx` - Button for acknowledging the briefing.
- `frontend/src/components/ChatInterface.jsx` - Chat window for LLM interaction.
- `frontend/src/utils/icaoList.js` - Static/mock ICAO code list and validation helpers.
- `frontend/src/utils/mockData.js` - Mocked data for route, weather, NOTAMs, etc.
- `frontend/src/styles/theme.css` - Dark theme and responsive styles.
- `frontend/src/App.test.jsx` - Main integration tests for the app.
- `frontend/src/components/IcaoSelect.test.jsx` - Unit tests for ICAO select and validation.
- `frontend/src/components/PreferencesModal.test.jsx` - Unit tests for preferences modal.
- `frontend/src/components/BriefingDisplay.test.jsx` - Unit tests for briefing display.
- `frontend/src/components/ChatInterface.test.jsx` - Unit tests for chat interface.

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `MyComponent.jsx` and `MyComponent.test.jsx` in the same directory).
- Use `npx jest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the Jest configuration.

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

- [ ] 4.0 Create briefing display and go/no-go recommendation UI
  - [x] 4.1 Create `BriefingDisplay` component to show route, weather, NOTAMs, and airport info (mocked data)
  - [x] 4.2 Build `GoNoGoRecommendation` component to display decision and reasons
  - [x] 4.3 Integrate both components into main UI, updating on route selection
  - [ ] 4.4 Write unit tests for briefing and go/no-go components

- [ ] 5.0 Implement acknowledgement workflow and chat interface
  - [ ] 5.1 Add `AcknowledgeButton` component, disabled until briefing is reviewed
  - [ ] 5.2 Enable chat interface only after acknowledgement
  - [ ] 5.3 Build `ChatInterface` component for LLM Q&A (mocked responses)
  - [ ] 5.4 Write unit tests for acknowledgement and chat workflow

- [ ] 6.0 Apply dark theme, mobile responsiveness, and error handling
  - [ ] 6.1 Finalize dark theme and ensure all components use consistent styles
  - [ ] 6.2 Test and refine mobile responsiveness for all UI elements
  - [ ] 6.3 Implement error handling for API failures and invalid ICAO codes
  - [ ] 6.4 Display clear error messages and fallback UI as needed
  - [ ] 6.5 Write integration tests for error handling and responsiveness 