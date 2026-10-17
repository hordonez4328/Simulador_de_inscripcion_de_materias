"""
Servicio de validación y gestión académica para el Portal Universitario:
- Validación de prerrequisitos en el servidor.
- Detección de solapamiento de horarios entre grupos.
- Control de cupos y estado académico del estudiante.
- Cálculo de indicadores y resumen curricular.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "curriculum.json")

class AcademicService:
    def __init__(self, data_file: str = DATA_PATH):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_student_info(self) -> Dict[str, Any]:
        return self.data.get("student", {})

    def get_all_courses(self) -> Dict[str, Dict[str, Any]]:
        """Retorna un diccionario indexado por código de materia."""
        courses = {}
        for sem in self.data.get("semesters", []):
            for c in sem.get("courses", []):
                courses[c["code"]] = c
        return courses

    def get_semesters(self) -> List[Dict[str, Any]]:
        return self.data.get("semesters", [])

    def calculate_summary(self) -> Dict[str, Any]:
        courses = self.get_all_courses()
        approved_credits = 0
        enrolled_credits = 0
        cursadas_count = 0
        inscritas_count = 0
        disponibles_count = 0
        no_habilitadas_count = 0

        for c in courses.values():
            status = c.get("status")
            creds = c.get("credits", 0)
            if status == "cursada":
                cursadas_count += 1
                approved_credits += creds
            elif status == "inscrita":
                inscritas_count += 1
                enrolled_credits += creds
            elif status == "disponible":
                disponibles_count += 1
            else:
                no_habilitadas_count += 1

        return {
            "approved_credits": approved_credits,
            "enrolled_credits": enrolled_credits,
            "cursadas_count": cursadas_count,
            "inscritas_count": inscritas_count,
            "disponibles_count": disponibles_count,
            "no_habilitadas_count": no_habilitadas_count,
            "total_courses": len(courses)
        }

    def validate_prerequisites(self, course_code: str) -> Tuple[bool, List[str]]:
        """Verifica si todos los prerrequisitos están aprobados (cursados)."""
        courses = self.get_all_courses()
        course = courses.get(course_code)
        if not course:
            return False, ["Materia no encontrada."]

        unmet = []
        for prereq_code in course.get("prerequisites", []):
            prereq = courses.get(prereq_code)
            if not prereq or prereq.get("status") != "cursada":
                prereq_name = prereq.get("name") if prereq else prereq_code
                unmet.append(f"{prereq_code} - {prereq_name}")

        return len(unmet) == 0, unmet

    def get_enrolled_schedules(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de todas las franjas horarias actualmente inscritas."""
        courses = self.get_all_courses()
        enrolled_slots = []
        for c in courses.values():
            if c.get("status") == "inscrita" and c.get("enrolled_group"):
                grp_id = c.get("enrolled_group")
                group = next((g for g in c.get("groups", []) if g["group_id"] == grp_id), None)
                if group:
                    for s in group.get("schedules", []):
                        enrolled_slots.append({
                            "course_code": c["code"],
                            "course_name": c["name"],
                            "group_id": grp_id,
                            "day": s["day"],
                            "start_time": s["start_time"],
                            "end_time": s["end_time"],
                            "room": s.get("room", group.get("room", "N/A"))
                        })
        return enrolled_slots

    def check_schedule_conflicts(self, course_code: str, group_id: str) -> Tuple[bool, Optional[str]]:
        """Verifica si el grupo a inscribir genera conflicto de horario con materias ya inscritas."""
        courses = self.get_all_courses()
        course = courses.get(course_code)
        if not course:
            return True, "Materia no encontrada."

        group = next((g for g in course.get("groups", []) if g["group_id"] == group_id), None)
        if not group:
            return True, f"Grupo {group_id} no encontrado en {course_code}."

        enrolled_slots = self.get_enrolled_schedules()

        for slot in group.get("schedules", []):
            s_day = slot["day"].lower()
            s_start = int(slot["start_time"].replace(":", ""))
            s_end = int(slot["end_time"].replace(":", ""))

            for enr in enrolled_slots:
                # Si es la misma materia no comparar consigo misma
                if enr["course_code"] == course_code:
                    continue
                if enr["day"].lower() == s_day:
                    e_start = int(enr["start_time"].replace(":", ""))
                    e_end = int(enr["end_time"].replace(":", ""))
                    # Chequeo de solapamiento de intervalos [start, end)
                    if max(s_start, e_start) < min(s_end, e_end):
                        conflict_desc = (
                            f"Conflicto de horario con {enr['course_code']} ({enr['course_name']}) "
                            f"el día {slot['day']} de {slot['start_time']} a {slot['end_time']}."
                        )
                        return True, conflict_desc

        return False, None

    def enroll_course(self, course_code: str, group_id: str) -> Tuple[bool, str]:
        """Procesa una inscripción académica con todas las validaciones de servidor."""
        courses = self.get_all_courses()
        course = courses.get(course_code)
        if not course:
            return False, f"La asignatura {course_code} no existe."

        if course.get("status") == "cursada":
            return False, f"La asignatura {course_code} ya fue aprobada y cursada."

        if course.get("status") == "inscrita":
            return False, f"La asignatura {course_code} ya se encuentra inscrita en este periodo."

        # 1. Validar prerrequisitos
        has_prereqs, unmet = self.validate_prerequisites(course_code)
        if not has_prereqs:
            return False, f"No cumple con los prerrequisitos obligatorios: {', '.join(unmet)}"

        # 2. Validar grupo y cupo
        group = next((g for g in course.get("groups", []) if g["group_id"] == group_id), None)
        if not group:
            return False, f"El grupo {group_id} no está habilitado."

        if group.get("available_quota", 0) <= 0:
            return False, f"No hay cupos disponibles en el grupo {group_id}."

        # 3. Validar conflictos de horario
        conflict, conflict_msg = self.check_schedule_conflicts(course_code, group_id)
        if conflict:
            return False, f"Cruce de horario detectado: {conflict_msg}"

        # Aplicar inscripción
        course["status"] = "inscrita"
        course["enrolled_group"] = group_id
        group["available_quota"] -= 1

        self._save_data()
        return True, f"Inscripción exitosa en {course['name']} ({course_code}) - Grupo {group_id}."

    def cancel_enrollment(self, course_code: str) -> Tuple[bool, str]:
        """Cancela la inscripción de una materia previamente inscrita."""
        courses = self.get_all_courses()
        course = courses.get(course_code)
        if not course or course.get("status") != "inscrita":
            return False, f"La asignatura {course_code} no está actualmente inscrita."

        group_id = course.get("enrolled_group")
        if group_id:
            group = next((g for g in course.get("groups", []) if g["group_id"] == group_id), None)
            if group:
                group["available_quota"] += 1

        course["status"] = "disponible"
        course["enrolled_group"] = None

        self._save_data()
        return True, f"Cancelación exitosa de {course['name']} ({course_code})."

    def reset_to_initial_state(self):
        """Restaura el estado académico inicial de demostración."""
        # Se recarga el archivo base desde el disco si es necesario
        pass
