# Product Requirements Document: Flight Planner Backend (Data & Go/No-Go)

## 1. Introduction/Overview

This document outlines the requirements for the initial backend component of the Flight Planner application. The primary goal of this phase is to establish a robust backend service capable of fetching real-time aviation data from external sources, caching it, and performing rules-based Go/No-Go flight recommendations. This backend will serve as the data provider for the existing frontend, replacing its mock data with live information and laying the groundwork for future integration with LLM-based functionalities.

## 2. Goals

*   To provide real-time aviation weather (METARs, TAFs), NOTAMs, and airport information to the frontend.
*   To implement a rules-based Go/No-Go flight recommendation system based on fetched data and pilot preferences.
*   To establish a persistent data store for caching external API responses and managing airport data.
*   To build the backend using Python/FastAPI to facilitate future integration with the OpenAI Agents SDK.
*   To define a clear and consistent REST API interface for communication with the frontend.

## 3. User Stories

*   As a pilot, I want the system to fetch current weather (METARs, TAFs) for my departure and destination airports so I have up-to-date information for my flight.
*   As a pilot, I want the system to retrieve relevant NOTAMs for my departure and destination airports so I am aware of any operational changes or hazards.
*   As a pilot, I want the system to provide detailed airport information (e.g., name, elevation, runways) for my selected airports so I can quickly reference key details.
*   As a pilot, I want the system to calculate a Go/No-Go recommendation based on my personal preferences and the fetched aviation data so I can quickly assess flight feasibility.
*   As a pilot, I want the system to handle external data retrieval gracefully, even if an external API is temporarily unavailable, so my planning process is not completely interrupted.

## 4. Functional Requirements

1.  **Data Acquisition:**
    *   The backend must scrape METARs and TAFs from the Aviation Weather Center (AWC) website for specified ICAO codes.
    *   The backend must scrape NOTAMs from the FAA NOTAM System website for specified ICAO codes.
    *   The backend must retrieve detailed airport information (name, elevation, runways) from a local database populated with FAA Airport Data.
    *   The backend must be able to scrape enroute weather warnings (e.g., turbulence, thunderstorms) from the AWC website.
2.  **Data Caching and Persistence:**
    *   The backend must implement a mechanism to cache data obtained from external web scraping to reduce redundant requests and improve response times.
    *   The backend must maintain a persistent database for FAA Airport Data, which can be updated periodically.
    *   The caching mechanism should handle data freshness, potentially with configurable expiry times.
3.  **Go/No-Go Recommendation Logic:**
    *   The backend must implement a rules-based engine to determine a "Go" or "No-Go" recommendation.
    *   This engine must consider pilot preferences (e.g., max crosswind, min ceiling) and the fetched weather and NOTAM data.
    *   The recommendation must include clear reasons for the decision.
4.  **API Endpoints:**
    *   The backend must expose a REST API endpoint to provide comprehensive flight briefing data to the frontend.
    *   **Endpoint:** `GET /api/briefing`
    *   **Parameters:**
        *   `dep`: String, ICAO code for the departure airport (e.g., `KDEN`).
        *   `dest`: String, ICAO code for the destination airport (e.g., `KLAX`).
        *   `preferences`: JSON string, containing pilot preferences (e.g., `{"crosswind": 15, "homeBase": "KSQL", "aircraft": "C172", "speed": 120, "range": 500, "cruiseAlt": 8500}`).
5.  **Frontend Integration:**
    *   The frontend must be updated to send the departure ICAO, destination ICAO, and pilot preferences to the backend's `/api/briefing` endpoint.
    *   The frontend must be updated to consume the data returned by the backend's `/api/briefing` endpoint and display it in the `BriefingDisplay` component, replacing the mock data.
    *   **Response Structure (JSON):** The response should mirror the structure of `MOCK_BRIEFING_DATA` to seamlessly integrate with the existing frontend components.
        ```json
        {
          "route": {
            "distance": "number",
            "estimatedTimeEnroute": "string",
            "departure": "string",
            "destination": "string"
          },
          "weather": {
            "departure": {
              "metar": "string",
              "taf": "string"
            },
            "destination": {
              "metar": "string",
              "taf": "string"
            },
            "enroute": {
              "warnings": ["string"]
            }
          },
          "notams": {
            "departure": [
              {"id": "string", "text": "string"}
            ],
            "destination": [
              {"id": "string", "text": "string"}
            ]
          },
          "airportInfo": {
            "departure": {
              "name": "string",
              "elevation": "string",
              "runways": ["string"]
            },
            "destination": {
              "name": "string",
              "elevation": "string",
              "runways": ["string"]
            }
          },
          "goNoGo": {
            "decision": "string", // "Go" or "No-Go"
            "reasons": ["string"]
          }
        }
        ```
5.  **Error Handling:**
    *   The backend must gracefully handle errors during web scraping (e.g., network issues, website structure changes, CAPTCHAs).
    *   In case of web scraping failures, the backend should return appropriate error messages or status codes to the frontend, indicating which data could not be retrieved.
    *   The data caching/database population process should be resilient to errors from external sources.

## 5. Non-Goals (Out of Scope)

*   Implementation of the `simulate_flight_communications` functionality (this is reserved for a future LLM-driven phase).
*   User authentication or account management.
*   Advanced route planning or optimization (e.g., IFR routing, wind optimization).
*   Real-time flight tracking.

## 6. Design Considerations

*   **Data Model:** A clear and extensible data model for storing airport information, weather data, and NOTAMs in the chosen database.
*   **Modularity:** The backend should be designed with modularity in mind, allowing for easy integration of new data sources or LLM functionalities in the future.
*   **API Design:** The API should be RESTful, intuitive, and well-documented.

## 7. Technical Considerations

*   **Technology Stack:** Python with FastAPI for the web framework.
*   **Database:** A suitable database (e.g., PostgreSQL, SQLite for simplicity initially) for caching and storing FAA Airport Data.
*   **External API Clients:** Use appropriate Python libraries for making HTTP requests to external aviation APIs.
*   **Deployment:** Consider containerization (e.g., Docker) for ease of deployment.

## 8. Success Metrics

*   The backend successfully provides all required briefing data to the frontend, replacing `MOCK_BRIEFING_DATA`.
*   API response times for `/api/briefing` are consistently below 500ms (excluding initial external API fetch on cache miss).
*   The Go/No-Go recommendation logic accurately reflects the defined rules based on pilot preferences and current data.
*   The backend gracefully handles and reports errors from external data sources without crashing.

## 9. Open Questions

*   What specific database technology should be used for caching and airport data (e.g., SQLite for development, PostgreSQL for production)?
*   What are the exact rules and thresholds for the Go/No-Go decision logic (e.g., specific crosswind limits, ceiling minimums, NOTAM criticality)?
*   How frequently should cached external data be refreshed? Should this be configurable?
*   Are there any specific security considerations for the backend API (e.g., API key management for external services)?