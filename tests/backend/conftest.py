"""Test-session setup.

backend.main.validate_required_environment_variables() (Story 9402359) runs at import time
and calls SystemExit if DATABASE_URL is unset — which would abort pytest collection entirely
the moment any test imports backend.main (Story 9402360's startup-connection tests do).
Setting a default here, before collection imports any test module, keeps that import safe
without requiring a real Postgres connection (the tests that need one fake out
backend.main.engine directly).
"""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista",
)
