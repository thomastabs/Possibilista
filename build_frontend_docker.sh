#!/usr/bin/env bash
set -euo pipefail

# Build the Possibilista frontend Docker image from the repository root.
#
# Usage:
#   ./build_frontend_docker.sh
#   bash build_frontend_docker.sh
#
# Image:
#   possibilista-frontend:latest
#
# Dockerfile:
#   frontend/Dockerfile
#
# Run the built container on the default Next.js port:
#   docker run --rm -p 3000:3000 possibilista-frontend:latest
#
# After a successful start, the frontend is available at:
#   http://localhost:3000
#
# Port conflicts:
#   If host port 3000 is already in use, Docker will fail with a bind/port allocation
#   error. Either stop the process using port 3000 or map the container to another host
#   port, for example:
#     docker run --rm -p 3001:3000 possibilista-frontend:latest
#   Then open:
#     http://localhost:3001
#
# Helpful checks for the process using port 3000:
#   lsof -i :3000
#   netstat -anp | grep 3000

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
