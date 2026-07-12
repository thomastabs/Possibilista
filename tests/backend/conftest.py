"""Test-session setup.

backend.main.validate_required_environment_variables() (Story 9402359) runs at import time
and calls SystemExit if DATABASE_URL is unset — which would abort pytest collection entirely
the moment any test imports backend.main (Story 9402360's startup-connection tests do).
Setting a default here, before collection imports any test module, keeps that import safe
without requiring a real Postgres connection (the tests that need one fake out
backend.main.engine directly).
"""

import os
from collections.abc import Callable
import asyncio
import inspect

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista",
)


class ASGISyncClient:
    """Small TestClient replacement for this suite's async FastAPI endpoints.

    The local Starlette TestClient blocks in this environment. The endpoint tests only need
    simple request methods, so this adapter drives the app through httpx's ASGITransport.
    """

    __test__ = False

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.base_url = str(kwargs.get("base_url", "http://testserver"))
        self.raise_app_exceptions = kwargs.get("raise_server_exceptions", True)
        self._normalize_dependency_overrides()

    def _normalize_dependency_overrides(self) -> None:
        normalized = {}

        for dependency, override in self.app.dependency_overrides.items():
            if inspect.iscoroutinefunction(override):
                normalized[dependency] = override
                continue

            async def async_override(_override: Callable = override):
                return _override()

            normalized[dependency] = async_override

        self.app.dependency_overrides.update(normalized)

    async def _request(self, method: str, url: str, **kwargs):
        from httpx import ASGITransport, AsyncClient

        transport = ASGITransport(
            app=self.app,
            raise_app_exceptions=self.raise_app_exceptions,
        )
        async with AsyncClient(transport=transport, base_url=self.base_url) as client:
            return await client.request(method, url, **kwargs)

    def request(self, method: str, url: str, **kwargs):
        return asyncio.run(self._request(method, url, **kwargs))

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def pytest_configure() -> None:
    import fastapi.testclient

    fastapi.testclient.TestClient = ASGISyncClient
