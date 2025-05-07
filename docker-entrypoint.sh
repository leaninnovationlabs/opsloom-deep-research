#!/bin/sh
set -e

# Modify the connection string to use asyncpg
echo $POSTGRES_CONNECTION_STRING
export POSTGRES_CONNECTION_STRING=$(echo "$POSTGRES_CONNECTION_STRING" | sed 's/^postgresql:\/\//postgresql+asyncpg:\/\//')

# Enable static file serving
export STATIC="true"

export multitenant="false"

echo "Running database migrations..."
echo $POSTGRES_CONNECTION_STRING
uv run alembic upgrade head

# Start the application
echo "Starting Opsloom application..."
exec uv run uvicorn server:app --host 0.0.0.0 --port 8080
