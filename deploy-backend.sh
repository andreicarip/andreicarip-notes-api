#!/bin/bash
set -euo pipefail

echo "[deploy] Starting backend deployment..."

cd /opt/api

echo "[deploy] Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main

echo "[deploy] Building Docker image notes-api:latest..."
sudo docker build -t notes-api:latest .

echo "[deploy] Stopping old container (if it exists)..."
sudo docker stop notes-api || true
sudo docker rm notes-api || true

echo "[deploy] Ensuring data directory exists..."
sudo mkdir -p /opt/api/data

echo "[deploy] Starting new container..."
sudo docker run -d \
  --name notes-api \
  -p 8000:8000 \
  --restart always \
  -v /opt/api/data:/app/data \
  notes-api:latest

echo "[deploy] Deployment finished successfully."
