"""Deterministic embedding stand-in shared by every document ingestion pipeline.

See ``DETERMINISTIC_STUBS.md`` — no live embedding API call in this repo slice.
"""

from __future__ import annotations

from backend.models.document import EMBEDDING_DIMENSIONS


def generate_embedding(content: str) -> list[float]:
    """Deterministic stand-in for a real embedding call.

    Derives a fixed-length numeric vector from the content's character codes so identical
    content always yields the same vector, without depending on any external service.
    """

    vector = [0.0] * EMBEDDING_DIMENSIONS
    if not content:
        return vector

    for index, char in enumerate(content):
        vector[index % EMBEDDING_DIMENSIONS] += ord(char)

    magnitude = max(vector) or 1.0
    return [round(value / magnitude, 6) for value in vector]
