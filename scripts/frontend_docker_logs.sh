#!/usr/bin/env bash
set -euo pipefail

# Retrieve logs from the local frontend Docker container.
#
# Container name:
#   possibilista-frontend
#
# Usage:
#   scripts/frontend_docker_logs.sh
#   scripts/frontend_docker_logs.sh --help

CONTAINER_NAME="possibilista-frontend"

usage() {
  cat <<USAGE
Usage: $0 [--help]

Displays logs from the running ${CONTAINER_NAME} Docker container.

The script checks that the container exists before calling docker logs. If the
container exists but is stopped, start it before viewing logs:
  docker start ${CONTAINER_NAME}

If the container does not exist, create it through Docker Compose or docker run first.
USAGE
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker CLI is not installed or is not available on PATH." >&2
    exit 1
  fi
}

container_exists() {
  local output

  if ! output=$(docker ps -a \
    --filter "name=^/${CONTAINER_NAME}$" \
    --format "{{.Names}}" 2>&1); then
    echo "Error: unable to query Docker for containers." >&2
    echo "${output}" >&2
    return 2
  fi

  grep -Fxq "${CONTAINER_NAME}" <<<"${output}"
}

container_is_running() {
  local output

  if ! output=$(docker ps \
    --filter "name=^/${CONTAINER_NAME}$" \
    --filter "status=running" \
    --format "{{.Names}}" 2>&1); then
    echo "Error: unable to query Docker for running containers." >&2
    echo "${output}" >&2
    return 2
  fi

  grep -Fxq "${CONTAINER_NAME}" <<<"${output}"
}

show_frontend_logs() {
  require_docker
  local exists_status
  local running_status

  if container_exists; then
    :
  else
    exists_status=$?
    case "${exists_status}" in
      1)
        echo "Error: frontend container '${CONTAINER_NAME}' was not found." >&2
        echo "Start the frontend container before requesting logs." >&2
        return 1
        ;;
      *)
        return 1
        ;;
    esac
  fi

  if container_is_running; then
    :
  else
    running_status=$?
    case "${running_status}" in
      1)
        echo "Frontend container '${CONTAINER_NAME}' exists but is stopped." >&2
        echo "Start it before viewing logs: docker start ${CONTAINER_NAME}" >&2
        return 1
        ;;
      *)
        return 1
        ;;
    esac
  fi

  docker logs "${CONTAINER_NAME}"
}

main() {
  case "${1:-}" in
    "" )
      show_frontend_logs
      ;;
    --help|-h)
      usage
      ;;
    *)
      echo "Error: unknown command '${1}'." >&2
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
