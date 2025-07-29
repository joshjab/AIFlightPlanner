# ✈️ AI Flight Planner

This project is a web-based "Flight Planner" tool designed to assist pilots with pre-flight planning. It leverages an AI agent to gather essential data, provide a preliminary go/no-go analysis, and allow for interactive exploration of flight routes.

This README documents the current state of the **frontend** application.

---

## Directory Structure

-   `/doc`: Contains architecture and design documents.
-   `/frontend`: Contains the React-based frontend application.
-   `/rules`: Contains rules and guidelines for the development process.
-   `/tasks`: Contains product requirements and task lists.

---

## Current Features (Frontend)

The frontend is a minimal, mobile-friendly single-page application with the following implemented features:

* **Departure & Destination Input:** Pilots can enter ICAO codes for their departure and destination airports. The input fields provide a searchable dropdown of available airports and validate the codes.
* **"Surprise Me" Destination Suggestion:**
    * A "Surprise Me" button allows the application to randomly select a valid destination airport.
    * An inline dropdown next to the button allows specifying a desired trip length (`?` for random, `1 hr`, `1-2 hr`, etc.) to influence the suggestion (Note: the filtering logic for trip length is currently a stub).
* **Pilot Preferences Modal:** A settings modal allows pilots to input and save their preferences, including:
    * Personal Minimums (Max Crosswind)
    * Aircraft Details (Type, Speed, Range)
    * Home Base
    * Preferred Cruise Altitude
    (Note: This modal is built but not yet integrated to be opened from the main UI, nor is its data saved or used yet).

---

## Getting Started

Follow these instructions to run the frontend application on your local machine for development and testing purposes.

### Prerequisites

You will need **Node.js version 20.19.0 or newer**. You can manage Node.js versions easily using [nvm](https://github.com/nvm-sh/nvm).

1.  **Install or Switch to Node.js v20:**
    ```sh
    # Install nvm (if you don't have it)
    curl -o- [https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh](https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh) | bash

    # Install and use Node.js v20
    nvm install 20
    nvm use 20
    ```

### Installation & Running the App

1.  **Navigate to the frontend directory:**
    ```sh
    cd frontend
    ```

2.  **Install dependencies:**
    If you haven't already, install the necessary npm packages.
    ```sh
    npm install
    ```

3.  **Start the development server:**
    This command runs the app in development mode.
    ```sh
    npm run dev
    ```

4.  **Open the application:**
    Open your web browser and navigate to the URL provided in the terminal (usually `http://localhost:5173`). The page will automatically reload if you make changes to the code.

### Running Tests

To run the automated tests for the components:

1.  Navigate to the `frontend` directory.
2.  Run the following command:
    ```sh
    npm test
    ```

---

## How to Use the Application

Once the application is running in your browser:

1.  **Select Departure Airport:**
    * Click on the "Departure Airport (ICAO)" input box.
    * Start typing an ICAO code (e.g., `KSQL`). The list will filter as you type.
    * Select a valid airport from the dropdown list.

2.  **Select Destination Airport:**
    * You can manually enter a destination in the "Destination Airport (ICAO)" input box, just like the departure airport.
    * **Alternatively, use the "Surprise Me" feature:**
        * Optionally, select a desired trip duration from the small dropdown next to the "Surprise Me" button.
        * Click the **🎲 Surprise Me** button.
        * A random valid destination will be selected and will automatically populate the "Destination Airport (ICAO)" text box.
