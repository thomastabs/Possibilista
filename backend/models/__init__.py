"""ORM models for Possibilista."""

from .base import Base
from .chat_message import ChatMessage
from .student_interest import StudentInterest
from .student_session import StudentSession
from .student_motivation import StudentMotivation
from .student_strength_weakness import StudentStrengthWeakness
from .secondary_track import (
    SecondaryTrack,
    SecondaryTrackDiscipline,
    SecondaryTrackDisciplineCombination,
    SecondaryTrackExamRequirement,
    SecondaryTrackHigherEdImpact,
)
from .higher_ed_course import HigherEdCourse
from .higher_ed_course_compatibility import HigherEdCourseCompatibility
