#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="pm-app"
CONTAINER_NAME="pm-app"

cd "$ROOT_DIR"

docker build -t "$IMAGE_NAME" .

if docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "$CONTAINER_NAME"
fi

docker run -d \
  --name "$CONTAINER_NAME" \
  -p 8000:8000 \
  --env-file .env \
  "$IMAGE_NAME"

echo "Running at http://127.0.0.1:8000"
