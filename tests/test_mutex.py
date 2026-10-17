"""
Pruebas para la versión protegida con Mutex (threading.Lock).
Verifica la exclusión mutua estricta, la ausencia de sobreinscripciones,
el contador no negativo y la liberación del cerrojo.
"""

import pytest
import threading
from simulator.enrollment import MutexEnrollmentManager
from simulator.runner import SimulationRunner
from simulator.models import SimulationConfig

def test_mutex_initialization():
    manager = MutexEnrollmentManager(initial_quota=10, course_code="IS100")
    assert manager.initial_quota == 10
    assert manager.available_quota == 10
    assert isinstance(manager.lock, type(threading.Lock()))

def test_mutex_strict_mutual_exclusion():
    """
    Prueba de estrés con 30 estudiantes y 5 cupos.
    El Mutex DEBE garantizar que nunca se inscriban más de 5 estudiantes,
    que los cupos restantes sean 0 y que no haya inconsistencias.
    """
    config = SimulationConfig(
        total_quota=5,
        num_students=30,
        course_code="IS100",
        artificial_delay=0.001,
        mode="mutex",
        barrier_sync=True
    )
    runner = SimulationRunner(config)
    metrics = runner.run()

    assert metrics.successful_enrollments == 5
    assert metrics.rejected_enrollments == 25
    assert metrics.final_quota == 0
    assert metrics.oversubscriptions == 0
    assert metrics.inconsistencies == 0
    assert metrics.status_label == "Ejecución correcta sin anomalías detectadas"

def test_mutex_lock_releases_on_exception():
    """Verifica que el patrón 'with self.lock' libere el cerrojo si ocurre un fallo."""
    manager = MutexEnrollmentManager(initial_quota=5)

    class CustomError(Exception):
        pass

    try:
        with manager.lock:
            raise CustomError("Fallo simulado dentro de la sección crítica")
    except CustomError:
        pass

    # El cerrojo debe estar libre para ser adquirido por otro hilo
    acquired = manager.lock.acquire(blocking=False)
    assert acquired is True
    manager.lock.release()
