## Relevant Files

- `backend/main.py` - Main FastAPI application file, defines API endpoints.
- `backend/services/weather_service.py` - Contains logic for fetching weather data from external APIs (AWC).
- `backend/services/notam_service.py` - Contains logic for fetching NOTAMs from external APIs (FAA).
- `backend/services/airport_service.py` - Fetches airport information from the local database.
- `backend/core/config.py` - Manages configuration and environment variables.
- `backend/database.py` - Handles database connection, session management, and table creation.
- `backend/models.py` - Pydantic models for API request/response validation.
- `backend/schemas.py` - Defines the database table structures.
- `backend/crud.py` - Contains functions for Create, Read, Update, Delete database operations.
- `backend/tests/test_main.py` - Unit and integration tests for the FastAPI endpoints.
- `backend/tests/test_services.py` - Unit tests for the external data services.
- `frontend/src/components/BriefingDisplay.jsx` - The frontend component that will be updated to consume data from the new backend API.

### Notes

- A new `backend` directory will be created in the project root.
- Unit tests should be created for all new services and API endpoints.
- Use `pytest` to run backend tests.

## Tasks

- [x] 1.0 Setup Python Backend Project with FastAPI
  - [x] 1.1 Initialize a new Python project in a `backend` directory with a virtual environment (`venv`).
  - [x] 1.2 Install FastAPI, Uvicorn, SQLAlchemy, Pydantic, and `python-dotenv`.
  - [x] 1.3 Create the initial project structure: `main.py`, and directories for `services`, `core`, `tests`, `models`.
  - [x] 1.4 Create a simple `/health` endpoint in `main.py` to confirm the FastAPI application is running correctly.
- [x] 2.0 Implement External Data Acquisition Layer
  - [x] 2.1 In `services/weather_service.py`, create a function to fetch METARs and TAFs from the Aviation Weather Center (AWC) API for a given ICAO code.
  - [x] 2.2 In `services/notam_service.py`, create a function to fetch NOTAMs from the FAA NOTAM System for a given ICAO code.
  - [x] 2.3 In `services/weather_service.py`, add a function to fetch enroute weather warnings from AWC.
  - [x] 2.4 Implement robust error handling in all service functions to manage external API failures gracefully.
  - [x] 2.5 In `tests/test_services.py`, write unit tests for the `weather_service` and `notam_service` functions, mocking external API calls.
- [ ] 3.0 Implement Caching and Data Persistence
  - [x] 3.1 In `database.py`, set up the SQLAlchemy engine and session management for a SQLite database.
  - [x] 3.2 In `schemas.py`, define the table schema for storing FAA airport data (e.g., name, elevation, runways).
  - [x] 3.3 Create a one-off script to download and populate the SQLite database with the FAA Airport Data.
  - [x] 3.4 In `services/airport_service.py`, create a function to retrieve airport details from the database.
  - [x] 3.5 Implement a caching layer (e.g., using `cachetools` or a simple dictionary with timestamps) for external API responses to minimize redundant calls.
  - [x] 3.6 In `tests/test_services.py`, write unit tests for the `airport_service` functions, mocking database interactions.
- [ ] 4.0 Develop Go/No-Go Recommendation Engine
  - [ ] 4.1 In `models.py`, define the Pydantic model for pilot preferences received in the API request.
  - [ ] 4.2 Create a new `services/recommendation_service.py` to house the Go/No-Go logic.
  - [ ] 4.3 Implement the rules-based engine that takes fetched weather/NOTAM data and pilot preferences to produce a "Go" or "No-Go" decision.
  - [ ] 4.4 The engine must generate a list of human-readable reasons for its recommendation.
  - [ ] 4.5 In `tests/test_services.py`, write unit tests for the `recommendation_service` to validate the Go/No-Go logic under various conditions.
- [ ] 5.0 Build and Integrate Frontend with `/api/briefing` Endpoint
  - [ ] 5.1 In `main.py`, define the `GET /api/briefing` endpoint that accepts departure, destination, and preferences as query parameters.
  - [ ] 5.2 In the endpoint logic, orchestrate calls to the weather, NOTAM, airport, and recommendation services.
  - [ ] 5.3 Structure the JSON response to match the format expected by the frontend's `BriefingDisplay` component.
  - [ ] 5.4 In `tests/test_main.py`, write integration tests for the `/api/briefing` endpoint, mocking the service layer to ensure correct API behavior.
  - [ ] 5.5 Modify `frontend/src/components/BriefingDisplay.jsx` to fetch data from the `/api/briefing` endpoint instead of using `MOCK_BRIEFING_DATA`.
  - [ ] 5.6 Update the `GoNoGoRecommendation` and other relevant components to display the live data from the backend.
