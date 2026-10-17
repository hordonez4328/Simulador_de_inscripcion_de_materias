"""
Pruebas para la versión sin protección (insegura).
Verifica que la ejecución se complete, que se registren los intentos,
y que admita la detección de inconsistencias sin obligar determinísticamente al fallo.
"""

import pytest
from simulator.enrollment import UnsafeEnrollmentManager
from simulator.runner import SimulationRunner
from simulator.models import SimulationConfig

def test_unsafe_initialization():
    manager = UnsafeEnrollmentManager(initial_quota=5, course_code="IS100", artificial_delay=0.0)
    assert manager.initial_quota == 5
    assert manager.available_quota == 5
    assert len(manager.enrolled_students) == 0
    assert len(manager.rejected_students) == 0

def test_unsafe_single_thread_execution():
    manager = UnsafeEnrollmentManager(initial_quota=2, course_code="IS100", artificial_delay=0.0)
    r1 = manager.attempt_enrollment("EST-001")
    r2 = manager.attempt_enrollment("EST-002")
    r3 = manager.attempt_enrollment("EST-003")

    assert r1.success is True
    assert r2.success is True
    assert r3.success is False
    assert manager.available_quota == 0
    assert len(manager.enrolled_students) == 2
    assert len(manager.rejected_students) == 1

def test_unsafe_concurrent_execution_completes():
    """
    Verifica que la simulación concurrente con hilos reales se complete,
    registre todos los estudiantes y calcule métricas sin bloquearse.
    """
    config = SimulationConfig(
        total_quota=3,
        num_students=12,
        course_code="IS100",
        artificial_delay=0.005,
        mode="unsafe",
        barrier_sync=True
    )
    runner = SimulationRunner(config)
    metrics = runner.run()

    # Todos los estudiantes deben haber sido procesados
    assert len(metrics.results) == 12
    assert metrics.num_students == 12
    assert metrics.initial_quota == 3
    # En la versión insegura, si ocurre sobreinscripción, oversubscriptions > 0
    # No forzamos que SIEMPRE falle, pero verificamos que las métricas sean coherentes
    assert metrics.successful_enrollments + metrics.rejected_enrollments == 12
