"""
Pruebas automatizadas para la interfaz web Flask y sus endpoints de API.
"""

import pytest
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
WEB_DIR = os.path.join(PROJECT_ROOT, "interfaz-web")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Universidad Virtual" in response.data
    assert b"Carlos Andr" in response.data

def test_curriculum_page(client):
    response = client.get("/curriculum")
    assert response.status_code == 200
    assert b"Malla Curricular" in response.data or b"Plan de Estudios" in response.data
    assert b"Semestre 1" in response.data
    assert b"Semestre 10" in response.data

def test_schedule_page(client):
    response = client.get("/schedule")
    assert response.status_code == 200
    assert b"Horario Semanal" in response.data

def test_simulator_page(client):
    response = client.get("/simulator")
    assert response.status_code == 200
    assert b"Laboratorio" in response.data

def test_results_page(client):
    response = client.get("/results")
    assert response.status_code == 200

def test_analysis_page(client):
    response = client.get("/analysis")
    assert response.status_code == 200
    assert b"Pregunta 1" in response.data

def test_api_curriculum(client):
    response = client.get("/api/curriculum")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "student" in data
    assert "semesters" in data
    assert len(data["semesters"]) == 10

def test_api_simulate_unsafe(client):
    payload = {
        "total_quota": 3,
        "num_students": 6,
        "artificial_delay": 0.005,
        "mode": "unsafe",
        "course_code": "IS100"
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["metrics"]["num_students"] == 6
    assert data["metrics"]["initial_quota"] == 3

def test_api_simulate_mutex(client):
    payload = {
        "total_quota": 4,
        "num_students": 10,
        "artificial_delay": 0.001,
        "mode": "mutex",
        "course_code": "IS100"
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["metrics"]["successful_enrollments"] == 4
    assert data["metrics"]["oversubscriptions"] == 0

def test_api_simulate_invalid_params(client):
    # Cuotas negativas o estudiantes excesivos
    payload = {"total_quota": -5, "num_students": 2000}
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False

def test_api_compare_experiment(client):
    payload = {
        "total_quota": 5,
        "num_students": 12,
        "artificial_delay": 0.005,
        "course_code": "IS100"
    }
    response = client.post("/api/compare", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "unsafe" in data["comparison"]
    assert "mutex" in data["comparison"]
    assert "semaforo" in data["comparison"]
