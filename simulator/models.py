"""
Modelos de datos para el simulador de inscripciones y gestión académica.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time

@dataclass
class GroupSchedule:
    day: str  # Lunes, Martes, Miércoles, Jueves, Viernes, Sábado
    start_time: str  # e.g. "08:00"
    end_time: str    # e.g. "10:00"
    room: str        # e.g. "Lab 301"

    def overlaps_with(self, other: "GroupSchedule") -> bool:
        if self.day.lower() != other.day.lower():
            return False
        # Formato HH:MM
        s1 = int(self.start_time.replace(":", ""))
        e1 = int(self.end_time.replace(":", ""))
        s2 = int(other.start_time.replace(":", ""))
        e2 = int(other.end_time.replace(":", ""))
        return max(s1, s2) < min(e1, e2)

@dataclass
class CourseGroup:
    group_id: str
    teacher: str
    room: str
    total_quota: int
    available_quota: int
    schedules: List[GroupSchedule]

@dataclass
class Course:
    code: str
    name: str
    short_name: str
    credits: int
    semester: int
    description: str
    prerequisites: List[str] = field(default_factory=list)
    groups: List[CourseGroup] = field(default_factory=list)
    status: str = "no_habilitada"  # cursada, inscrita, disponible, no_habilitada
    grade: Optional[float] = None
    enrolled_group: Optional[str] = None

@dataclass
class SimulationConfig:
    total_quota: int = 5
    num_students: int = 10
    course_code: str = "IS100"
    artificial_delay: float = 0.01  # Segundos de pausa para exponer condición de carrera
    mode: str = "unsafe"            # unsafe, mutex, semaforo
    barrier_sync: bool = True       # Si se usa barrera para inicio simultáneo

@dataclass
class StudentAttemptResult:
    student_id: str
    success: bool
    start_time: float
    end_time: float
    wait_time: float
    observed_quota: int
    message: str
    thread_name: str

@dataclass
class SimulationLogEvent:
    timestamp: float
    student_id: str
    event_type: str  # attempt, read, critical_enter, success, reject, inconsistent, info
    message: str
    remaining_quota: Optional[int] = None

@dataclass
class SimulationMetrics:
    simulation_id: str
    mode: str
    initial_quota: int
    num_students: int
    successful_enrollments: int
    rejected_enrollments: int
    final_quota: int
    oversubscriptions: int
    inconsistencies: int
    total_time: float
    avg_wait_time: float
    max_wait_time: float
    status_label: str  # Sobreinscripción confirmada, Contador inconsistente, Ejecución correcta, etc.
    results: List[StudentAttemptResult] = field(default_factory=list)
    events: List[SimulationLogEvent] = field(default_factory=list)
