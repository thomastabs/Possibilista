"""Student session validation logic."""

from __future__ import annotations

MIN_SCHOOL_YEAR = 9
MAX_SCHOOL_YEAR = 12

SCHOOL_YEAR_INVALID_MESSAGE = (
    f"Please provide a valid school year between {MIN_SCHOOL_YEAR} and {MAX_SCHOOL_YEAR}."
)


def validate_school_year(school_year: int) -> tuple[bool, str]:
    """Check whether school_year falls within the allowed 9.º-12.º range."""
    if MIN_SCHOOL_YEAR <= school_year <= MAX_SCHOOL_YEAR:
        return True, ""
    return False, SCHOOL_YEAR_INVALID_MESSAGE
