# --- Stage 1: Build the React App ---
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the source code and build the app
COPY . .
RUN npm run build
# This creates the /app/dist folder

# --- Stage 2: Serve with Nginx ---
FROM nginx:alpine

# Copy the static build files from the 'builder' stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our custom Nginx configuration
# This file (nginx.conf) must be in the same 'frontend' directory
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]