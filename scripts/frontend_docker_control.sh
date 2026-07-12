#!/usr/bin/env bash
set -euo pipefail

# Manage the local frontend Docker container used by Possibilista.
#
# Container name:
#   possibilista-frontend
#
# Usage:
#   scripts/frontend_docker_control.sh --check-running
#   scripts/frontend_docker_control.sh --stop
#   scripts/frontend_docker_control.sh --remove
#   scripts/frontend_docker_control.sh --stop-remove
#
# Test aliases used by the Apex developer packs:
#   scripts/frontend_docker_control.sh --test-stop
#   scripts/frontend_docker_control.sh --test-remove
#   scripts/frontend_docker_control.sh --test-stop-nonrunning

CONTAINER_NAME="possibilista-frontend"

usage() {
  cat <<USAGE
Usage: $0 COMMAND

Commands:
  --check-running        Check whether ${CONTAINER_NAME} is currently running.
  --stop                 Stop ${CONTAINER_NAME} if it is running.
  --remove               Remove ${CONTAINER_NAME} if it exists.
  --stop-remove          Stop the container if needed, then remove it.
  --test-stop            Alias for --stop.
  --test-remove          Alias for --remove.
  --test-stop-nonrunning Alias for --stop.
  --help                 Show this help.
USAGE
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker CLI is not installed or is not available on PATH." >&2
    exit 1
  fi
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

check_frontend_container_running() {
  require_docker

  if container_is_running; then
    echo "Frontend container '${CONTAINER_NAME}' is running."
    return 0
  fi

  echo "Frontend container '${CONTAINER_NAME}' is not running."
  return 1
}

stop_frontend_container() {
  require_docker
  local running_status

  if container_is_running; then
    if docker stop "${CONTAINER_NAME}" >/dev/null; then
      echo "Frontend container '${CONTAINER_NAME}' stopped successfully."
      return 0
    fi

    echo "Error: failed to stop frontend container '${CONTAINER_NAME}'." >&2
    return 1
  else
    running_status=$?
  fi

  case "${running_status}" in
    1)
      echo "No running frontend container found to stop."
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

remove_frontend_container() {
  require_docker
  local exists_status

  if container_exists; then
    if docker rm "${CONTAINER_NAME}" >/dev/null; then
      echo "Frontend container '${CONTAINER_NAME}' removed successfully."
      return 0
    fi

    echo "Error: failed to remove frontend container '${CONTAINER_NAME}'." >&2
    echo "If it is still running, stop it first with: $0 --stop" >&2
    return 1
  else
    exists_status=$?
  fi

  case "${exists_status}" in
    1)
      echo "No frontend container named '${CONTAINER_NAME}' exists to remove."
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

stop_and_remove_frontend_container() {
  stop_frontend_container
  remove_frontend_container
}

main() {
  case "${1:---help}" in
    --check-running)
      check_frontend_container_running
      ;;
    --stop|--test-stop|--test-stop-nonrunning)
      stop_frontend_container
      ;;
    --remove|--test-remove)
      remove_frontend_container
      ;;
    --stop-remove)
      stop_and_remove_frontend_container
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
