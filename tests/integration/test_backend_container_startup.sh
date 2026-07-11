#!/usr/bin/env bash
# Integration test: backend container startup with and without required environment
# variables (Story US#9402359, both Gherkin scenarios). See tests/integration/README.md
# for prerequisites and how to run this.
#
# backend/config.py's validate_required_environment_variables() only checks that
# DATABASE_URL is *set* — SQLAlchemy's async engine connects lazily (per request), not at
# import/startup time — so this test doesn't need a running Postgres container. It only
# exercises the environment-variable validation path described in the Gherkin scenarios.

set -uo pipefail # not -e: failing docker commands are inspected explicitly below

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE_TAG="possibilista-backend-integration-test"
CONTAINER_NAME="possibilista-backend-integration-test"
HOST_PORT="${BACKEND_TEST_HOST_PORT:-18000}"

cleanup() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

failures=0

fail() {
  echo "FAIL: $1" >&2
  failures=$((failures + 1))
}

pass() {
  echo "PASS: $1"
}

echo "Building backend image from backend/Dockerfile..."
if ! docker build -f "${REPO_ROOT}/backend/Dockerfile" -t "${IMAGE_TAG}" "${REPO_ROOT}" \
  >/tmp/possibilista-backend-build.log 2>&1; then
  fail "image build failed — see /tmp/possibilista-backend-build.log"
  exit 1
fi
echo "Image built."

echo
echo "--- Scenario 1: all required environment variables set ---"
cleanup
docker run -d --name "${CONTAINER_NAME}" \
  -e DATABASE_URL="postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista" \
  -p "${HOST_PORT}:8000" \
  "${IMAGE_TAG}" >/dev/null
sleep 3

if [ "$(docker inspect -f '{{.State.Running}}' "${CONTAINER_NAME}" 2>/dev/null)" = "true" ]; then
  pass "container is running with DATABASE_URL set."
else
  fail "container exited unexpectedly with DATABASE_URL set. Logs:"
  docker logs "${CONTAINER_NAME}" >&2
fi

if docker logs "${CONTAINER_NAME}" 2>&1 | grep -qi "Missing required environment variable"; then
  fail "unexpected missing-env-var error logged even though DATABASE_URL was set."
else
  pass "no missing-env-var error logged."
fi

cleanup

echo
echo "--- Scenario 2: DATABASE_URL missing ---"
docker run --name "${CONTAINER_NAME}" "${IMAGE_TAG}" \
  >/tmp/possibilista-backend-missing-env.log 2>&1
exit_code=$?

if [ "${exit_code}" -ne 0 ]; then
  pass "container exited non-zero (${exit_code}) when DATABASE_URL was missing."
else
  fail "container did not exit with a non-zero status when DATABASE_URL was missing."
fi

if grep -qi "Missing required environment variable(s): DATABASE_URL" \
  /tmp/possibilista-backend-missing-env.log; then
  pass "log clearly identifies DATABASE_URL as the missing variable."
else
  fail "expected error message not found in container logs:"
  cat /tmp/possibilista-backend-missing-env.log >&2
fi

if [ "$(docker inspect -f '{{.State.Running}}' "${CONTAINER_NAME}" 2>/dev/null)" != "true" ]; then
  pass "container is not running after the failed start attempt."
else
  fail "container is still running despite the missing environment variable."
fi

cleanup

echo
if [ "${failures}" -eq 0 ]; then
  echo "All backend container startup scenarios passed."
  exit 0
else
  echo "${failures} scenario(s) failed." >&2
  exit 1
fi
