"""
Paquete simulator para experimentación de concurrencia e inscripción académica.
"""

from simulator.models import (
    Course,
    CourseGroup,
    GroupSchedule,
    SimulationConfig,
    SimulationMetrics,
    SimulationLogEvent,
    StudentAttemptResult,
)
from simulator.enrollment import (
    UnsafeEnrollmentManager,
    MutexEnrollmentManager,
    SemaphoreEnrollmentManager,
)
from simulator.runner import SimulationRunner, run_comparative_experiment
from simulator.metrics import calculate_metrics

__all__ = [
    "Course",
    "CourseGroup",
    "GroupSchedule",
    "SimulationConfig",
    "SimulationMetrics",
    "SimulationLogEvent",
    "StudentAttemptResult",
    "UnsafeEnrollmentManager",
    "MutexEnrollmentManager",
    "SemaphoreEnrollmentManager",
    "SimulationRunner",
    "run_comparative_experiment",
    "calculate_metrics",
]
