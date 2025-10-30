# Use an official Python runtime
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the backend subdir
# (The build context will be the project root)
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into a 'backend' subdir in /app
# This creates the /app/backend package
COPY ./backend /app/backend

# Set PYTHONPATH to include /app so 'from backend.main' works
ENV PYTHONPATH="${PYTHONPATH}:/app"

