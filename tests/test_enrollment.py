"""
Pruebas para el servicio de validación académica:
- Validación de prerrequisitos en el servidor.
- Validación y detección de cruces de horario.
- Validación de cupos por grupo.
- Resumen y conteo de créditos.
"""

import pytest
import tempfile
import json
import os
from simulator.academic_service import AcademicService

@pytest.fixture
def temp_curriculum_service():
    """Crea una instancia de AcademicService con datos temporales aislados."""
    sample_data = {
        "student": {
            "id": "TEST-01",
            "name": "Estudiante Prueba",
            "program": "Ingeniería de Sistemas",
            "period": "2026-2"
        },
        "semesters": [
            {
                "number": 1,
                "name": "Semestre 1",
                "courses": [
                    {
                        "code": "TEST101",
                        "name": "Programación I",
                        "short_name": "Prog I",
                        "credits": 4,
                        "status": "cursada",
                        "prerequisites": [],
                        "groups": []
                    }
                ]
            },
            {
                "number": 2,
                "name": "Semestre 2",
                "courses": [
                    {
                        "code": "TEST201",
                        "name": "Programación II",
                        "short_name": "Prog II",
                        "credits": 4,
                        "status": "disponible",
                        "prerequisites": ["TEST101"],
                        "groups": [
                            {
                                "group_id": "G1",
                                "teacher": "Profesor A",
                                "room": "Lab 1",
                                "total_quota": 2,
                                "available_quota": 2,
                                "schedules": [
                                    {"day": "Lunes", "start_time": "08:00", "end_time": "10:00", "room": "Lab 1"}
                                ]
                            }
                        ]
                    },
                    {
                        "code": "TEST202",
                        "name": "Bases de Datos",
                        "short_name": "BD",
                        "credits": 3,
                        "status": "disponible",
                        "prerequisites": ["UNMET_PREREQ"],
                        "groups": [
                            {
                                "group_id": "G1",
                                "teacher": "Profesor B",
                                "room": "Lab 2",
                                "total_quota": 2,
                                "available_quota": 2,
                                "schedules": [
                                    {"day": "Lunes", "start_time": "09:00", "end_time": "11:00", "room": "Lab 2"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json", encoding="utf-8") as f:
        json.dump(sample_data, f)
        temp_file = f.name

    service = AcademicService(data_file=temp_file)
    yield service

    if os.path.exists(temp_file):
        os.remove(temp_file)

def test_prerequisites_met(temp_curriculum_service):
    met, unmet = temp_curriculum_service.validate_prerequisites("TEST201")
    assert met is True
    assert len(unmet) == 0

def test_prerequisites_unmet(temp_curriculum_service):
    met, unmet = temp_curriculum_service.validate_prerequisites("TEST202")
    assert met is False
    assert len(unmet) == 1
    assert "UNMET_PREREQ" in unmet[0]

def test_enrollment_success_and_quota_decrement(temp_curriculum_service):
    success, msg = temp_curriculum_service.enroll_course("TEST201", "G1")
    assert success is True
    course = temp_curriculum_service.get_all_courses()["TEST201"]
    assert course["status"] == "inscrita"
    assert course["enrolled_group"] == "G1"
    assert course["groups"][0]["available_quota"] == 1

def test_enrollment_rejected_if_already_enrolled(temp_curriculum_service):
    temp_curriculum_service.enroll_course("TEST201", "G1")
    # Intentar reinscribir
    success, msg = temp_curriculum_service.enroll_course("TEST201", "G1")
    assert success is False
    assert "ya se encuentra inscrita" in msg

def test_enrollment_schedule_conflict(temp_curriculum_service):
    # Inscribir TEST201 los Lunes de 08:00 a 10:00
    temp_curriculum_service.enroll_course("TEST201", "G1")

    # Modificar TEST202 para que cumpla prerrequisitos pero tenga conflicto el Lunes 09:00-11:00
    temp_curriculum_service.data["semesters"][1]["courses"][1]["prerequisites"] = []
    conflict, conflict_msg = temp_curriculum_service.check_schedule_conflicts("TEST202", "G1")
    assert conflict is True
    assert "Conflicto de horario" in conflict_msg

def test_cancellation(temp_curriculum_service):
    temp_curriculum_service.enroll_course("TEST201", "G1")
    success, msg = temp_curriculum_service.cancel_enrollment("TEST201")
    assert success is True
    course = temp_curriculum_service.get_all_courses()["TEST201"]
    assert course["status"] == "disponible"
    assert course["groups"][0]["available_quota"] == 2
