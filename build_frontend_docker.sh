#!/usr/bin/env bash
set -euo pipefail

# Build the Possibilista frontend Docker image from the repository root.
# Usage:
#   ./build_frontend_docker.sh
#   bash build_frontend_docker.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"
DOCKERFILE_PATH="${FRONTEND_DIR}/Dockerfile"
IMAGE_TAG="possibilista-frontend:latest"

if [[ ! -f "${DOCKERFILE_PATH}" ]]; then
  echo "Error: frontend Dockerfile is missing or misnamed; build aborted." >&2
  echo "Expected file: ${DOCKERFILE_PATH}" >&2
  echo "Ensure the file is named Dockerfile and placed directly inside the frontend directory." >&2
  exit 1
fi

cd "${SCRIPT_DIR}"
docker build -t "${IMAGE_TAG}" ./frontend
