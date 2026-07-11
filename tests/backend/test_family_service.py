import asyncio
from types import SimpleNamespace
from uuid import uuid4

from backend.services.family_service import get_exploration_path_explanation


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def scalar_one_or_none(self):
        return self._records

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, interests=None, motivation=None, strengths=None):
        self.interests = interests or []
        self.motivation = motivation
        self.strengths = strengths

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        name = getattr(entity, "__name__", "")
        if name == "StudentInterest":
            return DummyResult(self.interests)
        if name == "StudentMotivation":
            return DummyResult(self.motivation)
        if name == "StudentStrengthWeakness":
            return DummyResult(self.strengths)
        return DummyResult([])


def test_get_exploration_path_explanation_describes_interests_in_accessible_language():
    db = DummyDB(interests=[SimpleNamespace(interest="Robotics", skipped=False)])

    result = asyncio.run(get_exploration_path_explanation(db, str(uuid4())))

    assert result["no_data"] is False
    assert "Robotics" in result["interests_explanation"]
    assert "The student is interested in" in result["interests_explanation"]


def test_get_exploration_path_explanation_ignores_skipped_interests():
    db = DummyDB(
        interests=[
            SimpleNamespace(interest="Robotics", skipped=False),
            SimpleNamespace(interest=None, skipped=True),
        ]
    )

    result = asyncio.run(get_exploration_path_explanation(db, str(uuid4())))

    assert "Robotics" in result["interests_explanation"]
    assert result["interests_explanation"].count(",") == 0


def test_get_exploration_path_explanation_describes_motivations_in_accessible_language():
    db = DummyDB(motivation=SimpleNamespace(motivations="Wants to help people.", declined=False))

    result = asyncio.run(get_exploration_path_explanation(db, str(uuid4())))

    assert result["no_data"] is False
    assert "Wants to help people." in result["motivations_explanation"]


def test_get_exploration_path_explanation_treats_declined_motivation_as_no_motivation_data():
    db = DummyDB(
        interests=[SimpleNamespace(interest="Robotics", skipped=False)],
        motivation=SimpleNamespace(motivations="Wants to help people.", declined=True),
    )

    result = asyncio.run(get_exploration_path_explanation(db, str(uuid4())))

    assert result["no_data"] is False
    assert "No motivation information" in result["motivations_explanation"]


def test_get_exploration_path_explanation_describes_academic_areas_in_accessible_language():
    db = DummyDB(
        strengths=SimpleNamespace(strengths=["Math", "Science"], weaknesses=["History"], partial=False)
    )

    result = asyncio.run(get_exploration_path_explanation(db, str(uuid4())))

    assert result["no_data"] is False
    assert "strong in Math, Science" in result["academic_areas_explanation"]
    assert "working to improve History" in result["academic_areas_explanation"]


def test_get_exploration_path_explanation_returns_no_data_true_when_nothing_recorded():
    db = DummyDB()

    result = asyncio.run(get_exploration_path_explanation(db, str(uuid4())))

    assert result["no_data"] is True
    assert "not started exploring" in result["interests_explanation"].lower()
    assert "not started exploring" in result["motivations_explanation"].lower()
    assert "not started exploring" in result["academic_areas_explanation"].lower()


def test_get_exploration_path_explanation_full_data_across_all_categories():
    db = DummyDB(
        interests=[SimpleNamespace(interest="Robotics", skipped=False)],
        motivation=SimpleNamespace(motivations="Wants to help people.", declined=False),
        strengths=SimpleNamespace(strengths=["Math"], weaknesses=[], partial=False),
    )

    result = asyncio.run(get_exploration_path_explanation(db, str(uuid4())))

    assert result["no_data"] is False
    assert "Robotics" in result["interests_explanation"]
    assert "Wants to help people." in result["motivations_explanation"]
    assert "Math" in result["academic_areas_explanation"]
