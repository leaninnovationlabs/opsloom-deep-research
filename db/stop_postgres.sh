#!/bin/bash

# Variables
CONTAINER_NAME="rag-postgres"
NETWORK_NAME="opsloom-network"

# Stop and remove the container if it exists
if sudo docker ps -a --format '{{.Names}}' | grep -wq "$CONTAINER_NAME"; then
  echo "Stopping container: $CONTAINER_NAME"
  sudo docker stop "$CONTAINER_NAME"
  echo "Removing container: $CONTAINER_NAME"
  sudo docker rm "$CONTAINER_NAME"
else
  echo "Container $CONTAINER_NAME does not exist."
fi

# Remove the Docker network if it exists
if sudo docker network ls --format '{{.Name}}' | grep -wq "$NETWORK_NAME"; then
  echo "Removing Docker network: $NETWORK_NAME"
  sudo docker network rm "$NETWORK_NAME"
else
  echo "Docker network $NETWORK_NAME does not exist."
fi
