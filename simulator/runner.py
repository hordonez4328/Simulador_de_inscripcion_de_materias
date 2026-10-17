"""
Ejecutor de simulaciones concurrentes con hilos reales y barrera de sincronización.
"""

import threading
import time
import uuid
from typing import List, Dict, Optional, Callable
from queue import Queue

from simulator.models import SimulationConfig, SimulationMetrics, SimulationLogEvent, StudentAttemptResult
from simulator.enrollment import (
    BaseEnrollmentManager,
    UnsafeEnrollmentManager,
    MutexEnrollmentManager,
    SemaphoreEnrollmentManager
)
from simulator.metrics import calculate_metrics

class SimulationRunner:
    """
    Coordina la creación, sincronización y recolección de resultados de hilos reales
    para una simulación de inscripción.
    """

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.simulation_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
        self.events: List[SimulationLogEvent] = []
        self.event_queue: Optional[Queue] = None

    def _create_manager(self) -> BaseEnrollmentManager:
        mode = self.config.mode.lower()
        if mode in ("sin-proteccion", "unsafe", "insegura"):
            return UnsafeEnrollmentManager(
                initial_quota=self.config.total_quota,
                course_code=self.config.course_code,
                artificial_delay=self.config.artificial_delay
            )
        elif mode in ("mutex", "lock"):
            return MutexEnrollmentManager(
                initial_quota=self.config.total_quota,
                course_code=self.config.course_code,
                artificial_delay=self.config.artificial_delay
            )
        elif mode in ("semaforo", "semaphore"):
            return SemaphoreEnrollmentManager(
                initial_quota=self.config.total_quota,
                course_code=self.config.course_code,
                artificial_delay=self.config.artificial_delay
            )
        else:
            raise ValueError(f"Modo de simulación no soportado: {self.config.mode}")

    def run(self, event_callback: Optional[Callable[[SimulationLogEvent], None]] = None) -> SimulationMetrics:
        manager = self._create_manager()
        manager.event_callback = lambda ev: self._on_event(ev, event_callback)

        num_students = self.config.num_students
        barrier = threading.Barrier(num_students) if (self.config.barrier_sync and num_students > 1) else None

        threads: List[threading.Thread] = []
        worker_exceptions: List[Exception] = []

        self._on_event(
            SimulationLogEvent(
                timestamp=time.time(),
                student_id="SISTEMA",
                event_type="info",
                message=f"Iniciando simulación {self.simulation_id} [{self.config.mode.upper()}]. "
                        f"Cupos: {self.config.total_quota}, Estudiantes: {num_students}",
                remaining_quota=self.config.total_quota
            ),
            event_callback
        )

        def student_worker(student_id: str):
            try:
                # Sincronización mediante barrera para lanzamiento simultáneo
                if barrier is not None:
                    barrier.wait(timeout=10.0)
                manager.attempt_enrollment(student_id)
            except Exception as e:
                worker_exceptions.append(e)
                self._on_event(
                    SimulationLogEvent(
                        timestamp=time.time(),
                        student_id=student_id,
                        event_type="inconsistent",
                        message=f"Error en hilo de estudiante {student_id}: {str(e)}",
                        remaining_quota=manager.available_quota
                    ),
                    event_callback
                )

        t_start_global = time.perf_counter()

        # Creación de hilos con identificadores claros EST-001, EST-002, etc.
        for i in range(1, num_students + 1):
            student_id = f"EST-{i:03d}"
            t = threading.Thread(
                target=student_worker,
                args=(student_id,),
                name=f"Thread-{student_id}"
            )
            threads.append(t)

        # Iniciar todos los hilos
        for t in threads:
            t.start()

        # Esperar la finalización controlada de todos los hilos
        for t in threads:
            t.join(timeout=30.0)

        t_end_global = time.perf_counter()
        total_time = t_end_global - t_start_global

        self._on_event(
            SimulationLogEvent(
                timestamp=time.time(),
                student_id="SISTEMA",
                event_type="info",
                message=f"Simulación finalizada en {total_time:.4f}s. "
                        f"Inscritos registrados: {len(manager.enrolled_students)}, "
                        f"Cupos finales: {manager.available_quota}",
                remaining_quota=manager.available_quota
            ),
            event_callback
        )

        metrics = calculate_metrics(
            simulation_id=self.simulation_id,
            mode=self.config.mode,
            initial_quota=self.config.total_quota,
            num_students=self.config.num_students,
            final_quota=manager.available_quota,
            results=manager.results,
            events=self.events,
            total_time=total_time
        )

        return metrics

    def _on_event(self, event: SimulationLogEvent, callback: Optional[Callable[[SimulationLogEvent], None]]):
        self.events.append(event)
        if self.event_queue is not None:
            self.event_queue.put(event)
        if callback:
            try:
                callback(event)
            except Exception:
                pass


def run_comparative_experiment(
    total_quota: int = 5,
    num_students: int = 10,
    artificial_delay: float = 0.01,
    course_code: str = "IS100"
) -> Dict[str, SimulationMetrics]:
    """
    Ejecuta las tres implementaciones con exactamente los mismos parámetros iniciales,
    reiniciando contadores y listas en cada versión.
    """
    modes = ["unsafe", "mutex", "semaforo"]
    comparative_results: Dict[str, SimulationMetrics] = {}

    for mode in modes:
        config = SimulationConfig(
            total_quota=total_quota,
            num_students=num_students,
            course_code=course_code,
            artificial_delay=artificial_delay,
            mode=mode,
            barrier_sync=True
        )
        runner = SimulationRunner(config)
        metrics = runner.run()
        comparative_results[mode] = metrics

    return comparative_results
