"""
Aplicación Web Universitaria y Laboratorio de Concurrencia
Universidad Virtual - Portal de Inscripción Académica
"""

import os
import sys
import json
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from simulator.academic_service import AcademicService
from simulator.runner import SimulationRunner, run_comparative_experiment
from simulator.models import SimulationConfig

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(CURRENT_DIR, "templates"),
        static_folder=os.path.join(CURRENT_DIR, "static")
    )
    app.config["SECRET_KEY"] = "academic-concurrency-secret-key-2026"

    # Inicializar servicio académico
    academic_service = AcademicService()

    # Memoria en sesión para el laboratorio de concurrencia
    simulation_history = []

    @app.route("/")
    def index():
        student = academic_service.get_student_info()
        summary = academic_service.calculate_summary()
        return render_template("index.html", student=student, summary=summary)

    @app.route("/curriculum")
    def curriculum():
        student = academic_service.get_student_info()
        summary = academic_service.calculate_summary()
        semesters = academic_service.get_semesters()
        return render_template(
            "curriculum.html",
            student=student,
            summary=summary,
            semesters=semesters
        )

    @app.route("/schedule")
    def schedule():
        student = academic_service.get_student_info()
        summary = academic_service.calculate_summary()
        enrolled_slots = academic_service.get_enrolled_schedules()
        all_courses = academic_service.get_all_courses()
        return render_template(
            "schedule.html",
            student=student,
            summary=summary,
            enrolled_slots=enrolled_slots,
            courses=all_courses
        )

    @app.route("/simulator")
    def simulator():
        student = academic_service.get_student_info()
        return render_template("simulator.html", student=student)

    @app.route("/results")
    def results():
        student = academic_service.get_student_info()
        return render_template("results.html", student=student, history=simulation_history)

    @app.route("/analysis")
    def analysis():
        student = academic_service.get_student_info()
        return render_template("analysis.html", student=student)

    @app.route("/history")
    def history():
        student = academic_service.get_student_info()
        summary = academic_service.calculate_summary()
        courses = academic_service.get_all_courses()
        enrolled_courses = [c for c in courses.values() if c.get("status") == "inscrita"]
        cursadas_courses = [c for c in courses.values() if c.get("status") == "cursada"]
        return render_template(
            "history.html",
            student=student,
            summary=summary,
            enrolled_courses=enrolled_courses,
            cursadas_courses=cursadas_courses
        )

    # ==========================
    # API ENDPOINTS
    # ==========================

    @app.route("/api/curriculum")
    def api_curriculum():
        return jsonify({
            "student": academic_service.get_student_info(),
            "summary": academic_service.calculate_summary(),
            "semesters": academic_service.get_semesters()
        })

    @app.route("/api/course/<course_code>")
    def api_course_detail(course_code):
        courses = academic_service.get_all_courses()
        course = courses.get(course_code)
        if not course:
            return jsonify({"success": False, "message": "Materia no encontrada"}), 404
        has_prereqs, unmet = academic_service.validate_prerequisites(course_code)
        return jsonify({
            "success": True,
            "course": course,
            "has_prerequisites": has_prereqs,
            "unmet_prerequisites": unmet
        })

    @app.route("/api/enroll", methods=["POST"])
    def api_enroll():
        data = request.get_json() or {}
        course_code = data.get("course_code")
        group_id = data.get("group_id")
        if not course_code or not group_id:
            return jsonify({"success": False, "message": "Datos incompletos"}), 400

        success, message = academic_service.enroll_course(course_code, group_id)
        return jsonify({
            "success": success,
            "message": message,
            "summary": academic_service.calculate_summary()
        }), (200 if success else 400)

    @app.route("/api/cancel", methods=["POST"])
    def api_cancel():
        data = request.get_json() or {}
        course_code = data.get("course_code")
        if not course_code:
            return jsonify({"success": False, "message": "Código de materia requerido"}), 400

        success, message = academic_service.cancel_enrollment(course_code)
        return jsonify({
            "success": success,
            "message": message,
            "summary": academic_service.calculate_summary()
        }), (200 if success else 400)

    @app.route("/api/simulate", methods=["POST"])
    def api_simulate():
        data = request.get_json() or {}
        try:
            total_quota = int(data.get("total_quota", 5))
            num_students = int(data.get("num_students", 10))
            delay = float(data.get("artificial_delay", 0.01))
            mode = str(data.get("mode", "unsafe"))
            course_code = str(data.get("course_code", "IS100"))

            # Validar límites seguros
            if total_quota < 1 or total_quota > 500:
                return jsonify({"success": False, "message": "Cupos fuera de rango (1-500)"}), 400
            if num_students < 1 or num_students > 1000:
                return jsonify({"success": False, "message": "Estudiantes fuera de rango (1-1000)"}), 400
            if delay < 0.0 or delay > 1.0:
                return jsonify({"success": False, "message": "Pausa fuera de rango (0.0 - 1.0s)"}), 400

            config = SimulationConfig(
                total_quota=total_quota,
                num_students=num_students,
                course_code=course_code,
                artificial_delay=delay,
                mode=mode,
                barrier_sync=True
            )
            runner = SimulationRunner(config)
            metrics = runner.run()

            # Convertir dataclass a dict para JSON
            metrics_dict = {
                "simulation_id": metrics.simulation_id,
                "mode": metrics.mode,
                "initial_quota": metrics.initial_quota,
                "num_students": metrics.num_students,
                "successful_enrollments": metrics.successful_enrollments,
                "rejected_enrollments": metrics.rejected_enrollments,
                "final_quota": metrics.final_quota,
                "oversubscriptions": metrics.oversubscriptions,
                "inconsistencies": metrics.inconsistencies,
                "total_time": round(metrics.total_time, 4),
                "avg_wait_time": round(metrics.avg_wait_time, 6),
                "max_wait_time": round(metrics.max_wait_time, 6),
                "status_label": metrics.status_label,
                "events": [
                    {
                        "timestamp": ev.timestamp,
                        "student_id": ev.student_id,
                        "event_type": ev.event_type,
                        "message": ev.message,
                        "remaining_quota": ev.remaining_quota
                    }
                    for ev in metrics.events[:150]  # Limitar eventos enviados al navegador para fluidez
                ],
                "results": [
                    {
                        "student_id": r.student_id,
                        "success": r.success,
                        "wait_time": round(r.wait_time, 6),
                        "observed_quota": r.observed_quota,
                        "message": r.message
                    }
                    for r in metrics.results[:100]
                ]
            }

            simulation_history.insert(0, metrics_dict)
            return jsonify({"success": True, "metrics": metrics_dict})

        except Exception as e:
            return jsonify({"success": False, "message": f"Error al ejecutar simulación: {str(e)}"}), 500

    @app.route("/api/compare", methods=["POST"])
    def api_compare():
        data = request.get_json() or {}
        try:
            total_quota = int(data.get("total_quota", 5))
            num_students = int(data.get("num_students", 10))
            delay = float(data.get("artificial_delay", 0.01))
            course_code = str(data.get("course_code", "IS100"))

            results = run_comparative_experiment(
                total_quota=total_quota,
                num_students=num_students,
                artificial_delay=delay,
                course_code=course_code
            )

            response_data = {}
            for mode, m in results.items():
                m_dict = {
                    "simulation_id": m.simulation_id,
                    "mode": mode,
                    "initial_quota": m.initial_quota,
                    "num_students": m.num_students,
                    "successful_enrollments": m.successful_enrollments,
                    "rejected_enrollments": m.rejected_enrollments,
                    "final_quota": m.final_quota,
                    "oversubscriptions": m.oversubscriptions,
                    "inconsistencies": m.inconsistencies,
                    "total_time": round(m.total_time, 4),
                    "avg_wait_time": round(m.avg_wait_time, 6),
                    "max_wait_time": round(m.max_wait_time, 6),
                    "status_label": m.status_label
                }
                response_data[mode] = m_dict
                simulation_history.insert(0, m_dict)

            return jsonify({"success": True, "comparison": response_data})

        except Exception as e:
            return jsonify({"success": False, "message": f"Error en comparativa: {str(e)}"}), 500

    @app.route("/api/history/clear", methods=["POST"])
    def api_clear_history():
        nonlocal simulation_history
        simulation_history = []
        return jsonify({"success": True, "message": "Historial reiniciado correctamente"})

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
