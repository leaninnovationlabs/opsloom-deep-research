#!/bin/sh
set -e

# Load environment variables from AWS SSM
if [ "$LOAD_FROM_SSM" = "true" ]; then
  echo "Loading environment variables from AWS SSM Parameter Store..."
  
  # Get DB connection string and other parameters
  export POSTGRES_CONNECTION_STRING="$(aws ssm get-parameter --name "/opsloom/rds/connection_string" --with-decryption --query "Parameter.Value" --output text)"
  
  export ENV="dev"
  # Get other parameters as needed
  for PARAM in $(aws ssm get-parameters-by-path --path "/opsloom/env/" --recursive --with-decryption --query "Parameters[].Name" --output text); do
    PARAM_NAME=$(echo $PARAM | awk -F '/' '{print $NF}')
    PARAM_VALUE=$(aws ssm get-parameter --name "$PARAM" --with-decryption --query "Parameter.Value" --output text)
    export $PARAM_NAME="$PARAM_VALUE"
    echo "Loaded $PARAM_NAME from SSM"
  done
fi
export VITE_API_URL="https://api.opsloom.fish/"

# Modify the connection string to use asyncpg
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