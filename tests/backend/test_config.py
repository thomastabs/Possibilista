import pytest

from backend.config import validate_required_environment_variables


def test_validate_required_environment_variables_passes_when_database_url_is_set(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://possibilista:possibilista@postgres:5432/possibilista",
    )

    validate_required_environment_variables()


def test_validate_required_environment_variables_exits_when_database_url_is_missing(
    monkeypatch, caplog
):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        validate_required_environment_variables()

    assert exc_info.value.code == 1
    assert any("DATABASE_URL" in record.message for record in caplog.records)


def test_validate_required_environment_variables_exits_when_database_url_is_empty(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")

    with pytest.raises(SystemExit):
        validate_required_environment_variables()
