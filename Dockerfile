# Build stage for frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Build stage for backend
FROM ghcr.io/astral-sh/uv:bookworm-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    unzip \
    python3-pip \
    less \
    groff \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Copy Python project files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync

# Copy application code
COPY backend backend
COPY server.py server.py
COPY alembic.ini alembic.ini
COPY db db

# Create public directory for static files
RUN mkdir -p public/opsloom

# Copy frontend build from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist/ /app/public/opsloom/

# Expose the port the app runs on
EXPOSE 8080

# Use an entrypoint script to handle DB migrations and app startup
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]