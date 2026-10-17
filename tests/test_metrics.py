"""
Pruebas para el módulo de cálculo de métricas e inconsistencias.
"""

from simulator.metrics import calculate_metrics
from simulator.models import StudentAttemptResult

def test_metrics_clean_run():
    results = [
        StudentAttemptResult("EST-001", True, 0.0, 0.01, 0.01, 2, "OK", "t1"),
        StudentAttemptResult("EST-002", True, 0.0, 0.02, 0.02, 1, "OK", "t2"),
        StudentAttemptResult("EST-003", False, 0.0, 0.03, 0.03, 0, "No cupo", "t3"),
    ]
    metrics = calculate_metrics(
        simulation_id="TEST-1",
        mode="mutex",
        initial_quota=2,
        num_students=3,
        final_quota=0,
        results=results,
        events=[],
        total_time=0.05
    )

    assert metrics.successful_enrollments == 2
    assert metrics.rejected_enrollments == 1
    assert metrics.oversubscriptions == 0
    assert metrics.inconsistencies == 0
    assert metrics.status_label == "Ejecución correcta sin anomalías detectadas"
    assert round(metrics.avg_wait_time, 4) == 0.02
    assert round(metrics.max_wait_time, 4) == 0.03

def test_metrics_oversubscription_detection():
    results = [
        StudentAttemptResult("EST-001", True, 0.0, 0.01, 0.01, 2, "OK", "t1"),
        StudentAttemptResult("EST-002", True, 0.0, 0.01, 0.01, 2, "OK", "t2"),
        StudentAttemptResult("EST-003", True, 0.0, 0.01, 0.01, 2, "OK", "t3"),
    ]
    # Cupos iniciales: 2, pero se inscribieron 3 (sobreinscripción de 1) y contador final -1
    metrics = calculate_metrics(
        simulation_id="TEST-2",
        mode="unsafe",
        initial_quota=2,
        num_students=3,
        final_quota=-1,
        results=results,
        events=[],
        total_time=0.03
    )

    assert metrics.oversubscriptions == 1
    assert metrics.inconsistencies > 0
    assert metrics.status_label == "Sobreinscripción confirmada"
