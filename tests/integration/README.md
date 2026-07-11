# Integration tests

These are shell-script integration tests that exercise real Docker behavior — they need a
running Docker daemon and are not part of `pytest tests/backend`.

## Prerequisites

- Docker installed, with the daemon running and reachable (`docker ps` should succeed).
- Run from anywhere; the script resolves the repo root relative to its own path.

## `test_backend_container_startup.sh`

Covers both Gherkin scenarios for Story US#9402359 (Backend Docker Container):

1. **All required environment variables set** — builds `backend/Dockerfile`, runs it with
   `DATABASE_URL` set, and asserts the container stays running (doesn't exit from
   `backend/config.py`'s `validate_required_environment_variables()`).
2. **`DATABASE_URL` missing** — runs the same image with no `DATABASE_URL` set, and asserts
   the container exits with a non-zero status, logs a message identifying `DATABASE_URL` as
   the missing variable, and is not left running.

Note: this only exercises the environment-variable validation path, not a live database
connection — the backend's async SQLAlchemy engine connects lazily per request, not at
startup, so scenario 1 doesn't require a running Postgres container.

Run it:

```bash
bash tests/integration/test_backend_container_startup.sh
```

The script builds its own tagged image (`possibilista-backend-integration-test`) and cleans
up any container it starts on exit (including on failure), so it's safe to re-run. Override
the host port it binds to for scenario 1 with `BACKEND_TEST_HOST_PORT` if `18000` is taken:

```bash
BACKEND_TEST_HOST_PORT=18001 bash tests/integration/test_backend_container_startup.sh
```

Exits `0` if both scenarios pass, `1` otherwise, printing a `PASS`/`FAIL` line per assertion.
