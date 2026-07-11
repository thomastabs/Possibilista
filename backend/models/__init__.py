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
from .higher_ed_course_entrance_exam import HigherEdCourseEntranceExam
from .higher_ed_course_admission_average import HigherEdCourseAdmissionAverage
from .eligibility_simulation_result import EligibilitySimulationResult
from .session_secondary_track_memory import SessionSecondaryTrackMemory
from .explanation import Explanation
