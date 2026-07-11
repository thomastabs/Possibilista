#!/usr/bin/env bash
# Starts the PostgreSQL container via Docker Compose, refusing to proceed if the target
# host port is already occupied (Story US#9402358).
#
# Usage:
#   ./start_postgres.sh                          # uses the default port (5432)
#   POSTGRES_HOST_PORT=5433 ./start_postgres.sh   # uses an alternative port
#
# Any extra arguments are passed through to the underlying compose command, e.g.:
#   ./start_postgres.sh --detach

set -euo pipefail

PORT="${POSTGRES_HOST_PORT:-5432}"

port_in_use() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1
    return $?
  fi

  if command -v nc >/dev/null 2>&1; then
    nc -z localhost "${PORT}" >/dev/null 2>&1
    return $?
  fi

  # Portable fallback with no external dependency: attempt a raw TCP connection via bash's
  # /dev/tcp pseudo-device. A successful connection means something is already listening.
  (exec 3<>"/dev/tcp/127.0.0.1/${PORT}") 2>/dev/null
}

if port_in_use; then
  echo "Error: port ${PORT} is already in use." >&2
  echo "Another process on this machine is already listening on port ${PORT}, so the" >&2
  echo "PostgreSQL container cannot bind to it." >&2
  echo >&2
  echo "To resolve this, either stop whatever is using port ${PORT}, or start this" >&2
  echo "container on a different host port, e.g.:" >&2
  echo "  POSTGRES_HOST_PORT=5433 ./start_postgres.sh" >&2
  echo >&2
  echo "See the \"PostgreSQL Port Conflict Resolution\" section in README.md for details." >&2
  exit 1
fi

echo "Port ${PORT} is free. Starting the PostgreSQL container..."

if docker compose version >/dev/null 2>&1; then
  exec docker compose up "$@"
elif command -v docker-compose >/dev/null 2>&1; then
  exec docker-compose up "$@"
else
  echo "Error: neither 'docker compose' nor 'docker-compose' is available." >&2
  echo "Install Docker Compose to start the PostgreSQL container." >&2
  exit 1
fi
