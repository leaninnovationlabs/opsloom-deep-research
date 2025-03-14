# Build stage
FROM node:18-alpine AS builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci

# Copy the code and run the build
COPY frontend/ .
RUN npm run build
RUN ls -la dist
