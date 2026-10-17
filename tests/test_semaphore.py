"""
Pruebas para la versión protegida con Semáforo Binario (threading.Semaphore(1)).
Verifica exclusión mutua, límite exacto de cupos y liberación de permisos.
"""

import pytest
import threading
from simulator.enrollment import SemaphoreEnrollmentManager
from simulator.runner import SimulationRunner
from simulator.models import SimulationConfig

def test_semaphore_initialization():
    manager = SemaphoreEnrollmentManager(initial_quota=7, course_code="IS100")
    assert manager.initial_quota == 7
    assert manager.available_quota == 7
    assert isinstance(manager.semaphore, threading.Semaphore)

def test_semaphore_strict_mutual_exclusion():
    """
    Prueba con 40 estudiantes y 6 cupos.
    El semáforo binario DEBE asegurar que solo 6 inscripciones sean exitosas.
    """
    config = SimulationConfig(
        total_quota=6,
        num_students=40,
        course_code="IS100",
        artificial_delay=0.001,
        mode="semaforo",
        barrier_sync=True
    )
    runner = SimulationRunner(config)
    metrics = runner.run()

    assert metrics.successful_enrollments == 6
    assert metrics.rejected_enrollments == 34
    assert metrics.final_quota == 0
    assert metrics.oversubscriptions == 0
    assert metrics.inconsistencies == 0
    assert metrics.status_label == "Ejecución correcta sin anomalías detectadas"

def test_semaphore_releases_on_exception():
    """Verifica que el bloque 'with self.semaphore' libere el permiso en caso de excepción."""
    manager = SemaphoreEnrollmentManager(initial_quota=5)

    class CustomError(Exception):
        pass

    try:
        with manager.semaphore:
            raise CustomError("Fallo simulado en la sección crítica")
    except CustomError:
        pass

    # El semáforo debe poder adquirirse inmediatamente
    acquired = manager.semaphore.acquire(blocking=False)
    assert acquired is True
    manager.semaphore.release()
