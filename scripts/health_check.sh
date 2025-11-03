#!/usr/bin/env bash
set -e
API_PORT=${MOCK_API_PORT:-6000}
echo "Checking mock_api..."
curl -sf "http://localhost:${API_PORT}/health" || { echo "mock_api down"; exit 1; }
echo "mock_api OK"
echo "Checking mysql via docker-compose exec..."
docker-compose exec -T mysql mysqladmin ping -h localhost -p${DB_PASSWORD}
