"""
Manejadores de inscripción concurrente:
1. UnsafeEnrollmentManager (Sin protección / condición de carrera expuesta)
2. MutexEnrollmentManager (Protegido con threading.Lock)
3. SemaphoreEnrollmentManager (Protegido con threading.Semaphore binario)
"""

import threading
import time
from typing import List, Dict, Optional, Callable
from simulator.models import StudentAttemptResult, SimulationLogEvent

class BaseEnrollmentManager:
    """Clase base para los manejadores de inscripción."""

    def __init__(self, initial_quota: int, course_code: str = "IS100", artificial_delay: float = 0.01):
        self.initial_quota = initial_quota
        self.available_quota = initial_quota
        self.course_code = course_code
        self.artificial_delay = artificial_delay
        self.enrolled_students: List[str] = []
        self.rejected_students: List[str] = []
        self.results: List[StudentAttemptResult] = []
        # Eventos para registro en tiempo real (separado para no alterar la sección crítica)
        self.event_callback: Optional[Callable[[SimulationLogEvent], None]] = None

    def emit_event(self, student_id: str, event_type: str, message: str, remaining_quota: Optional[int] = None):
        if self.event_callback:
            event = SimulationLogEvent(
                timestamp=time.time(),
                student_id=student_id,
                event_type=event_type,
                message=message,
                remaining_quota=remaining_quota
            )
            self.event_callback(event)

    def attempt_enrollment(self, student_id: str) -> StudentAttemptResult:
        raise NotImplementedError("Debe ser implementado por subclases.")


class UnsafeEnrollmentManager(BaseEnrollmentManager):
    """
    Versión sin protección.
    Permite que la lectura del contador, la verificación y la escritura ocurran
    sin ningún mecanismo de sincronización (sin Lock ni Semaphore).
    La pausa artificial amplía la ventana de tiempo para evidenciar la condición de carrera
    (Race Condition) donde múltiples hilos observan cupos disponibles simultáneamente.
    """

    def __init__(self, initial_quota: int, course_code: str = "IS100", artificial_delay: float = 0.01):
        super().__init__(initial_quota, course_code, artificial_delay)
        # Lista separada solo para auditar intentos
        self._audit_attempts: List[str] = []

    def attempt_enrollment(self, student_id: str) -> StudentAttemptResult:
        t_start = time.perf_counter()
        thread_name = threading.current_thread().name

        self.emit_event(student_id, "attempt", f"{student_id} inicia su intento de inscripción en {self.course_code}")

        # 1. Lectura del contador de cupos (sin protección)
        observed_quota = self.available_quota
        self.emit_event(student_id, "read", f"{student_id} lee los cupos disponibles: {observed_quota}", observed_quota)

        # 2. Comprobación de que quedan cupos (sin protección)
        if observed_quota > 0:
            # 3. Pausa artificial configurable (amplía la ventana crítica de intercalación)
            if self.artificial_delay > 0:
                time.sleep(self.artificial_delay)

            # 4. Decremento del contador (operación crítica no atómica sin sincronización)
            # Lectura del valor actual, resta y reasignación: puede sobrescribirse entre hilos
            current_val = self.available_quota
            self.available_quota = current_val - 1

            # 5. Registro del resultado del intento
            self.enrolled_students.append(student_id)
            t_end = time.perf_counter()
            wait_time = t_end - t_start

            msg = f"{student_id} obtiene un cupo (cupos restantes calculados: {self.available_quota})"
            self.emit_event(student_id, "success", msg, self.available_quota)

            result = StudentAttemptResult(
                student_id=student_id,
                success=True,
                start_time=t_start,
                end_time=t_end,
                wait_time=wait_time,
                observed_quota=observed_quota,
                message=msg,
                thread_name=thread_name
            )
        else:
            # Sin cupos observados
            self.rejected_students.append(student_id)
            t_end = time.perf_counter()
            wait_time = t_end - t_start

            msg = f"{student_id} no encuentra cupos disponibles"
            self.emit_event(student_id, "reject", msg, self.available_quota)

            result = StudentAttemptResult(
                student_id=student_id,
                success=False,
                start_time=t_start,
                end_time=t_end,
                wait_time=wait_time,
                observed_quota=observed_quota,
                message=msg,
                thread_name=thread_name
            )

        self.results.append(result)
        return result


class MutexEnrollmentManager(BaseEnrollmentManager):
    """
    Versión protegida con Mutex (threading.Lock).
    Garantiza exclusión mutua estricta sobre la sección crítica:
    - Comprobación de disponibilidad.
    - Decremento del contador.
    - Registro de la inscripción.
    El uso de 'with self.lock' garantiza la liberación del cerrojo incluso ante excepciones.
    """

    def __init__(self, initial_quota: int, course_code: str = "IS100", artificial_delay: float = 0.01):
        super().__init__(initial_quota, course_code, artificial_delay)
        self.lock = threading.Lock()

    def attempt_enrollment(self, student_id: str) -> StudentAttemptResult:
        t_start = time.perf_counter()
        thread_name = threading.current_thread().name

        self.emit_event(student_id, "attempt", f"{student_id} inicia su intento de inscripción en {self.course_code}")
        self.emit_event(student_id, "critical_enter", f"{student_id} intenta adquirir el mutex (Lock)")

        success = False
        observed_quota = 0
        remaining_quota = 0
        message = ""

        # SECCIÓN CRÍTICA PROTEGIDA POR MUTEX
        with self.lock:
            observed_quota = self.available_quota
            if self.available_quota > 0:
                # 1. Comprobar que existe un cupo
                # 2. Decrementar el contador
                self.available_quota -= 1
                remaining_quota = self.available_quota
                # 3. Registrar la inscripción aceptada
                self.enrolled_students.append(student_id)
                success = True
                message = f"{student_id} obtiene un cupo de forma segura (cupos restantes: {remaining_quota})"
            else:
                remaining_quota = self.available_quota
                self.rejected_students.append(student_id)
                success = False
                message = f"{student_id} no encuentra cupos disponibles (rechazado)"

        # Fuera de la sección crítica: emisión de eventos y cálculo de tiempos
        t_end = time.perf_counter()
        wait_time = t_end - t_start

        if success:
            self.emit_event(student_id, "success", message, remaining_quota)
        else:
            self.emit_event(student_id, "reject", message, remaining_quota)

        result = StudentAttemptResult(
            student_id=student_id,
            success=success,
            start_time=t_start,
            end_time=t_end,
            wait_time=wait_time,
            observed_quota=observed_quota,
            message=message,
            thread_name=thread_name
        )
        self.results.append(result)
        return result


class SemaphoreEnrollmentManager(BaseEnrollmentManager):
    """
    Versión protegida con Semáforo Binario (threading.Semaphore(1)).
    En este escenario se inicializa con 1 permiso para actuar como cerrojo binario
    de exclusión mutua sobre la sección crítica de decremento y registro.
    Se utiliza 'with self.semaphore' para garantizar la adquisición y liberación segura del permiso.
    """

    def __init__(self, initial_quota: int, course_code: str = "IS100", artificial_delay: float = 0.01):
        super().__init__(initial_quota, course_code, artificial_delay)
        self.semaphore = threading.Semaphore(1)

    def attempt_enrollment(self, student_id: str) -> StudentAttemptResult:
        t_start = time.perf_counter()
        thread_name = threading.current_thread().name

        self.emit_event(student_id, "attempt", f"{student_id} inicia su intento de inscripción en {self.course_code}")
        self.emit_event(student_id, "critical_enter", f"{student_id} solicita permiso al semáforo binario")

        success = False
        observed_quota = 0
        remaining_quota = 0
        message = ""

        # SECCIÓN CRÍTICA PROTEGIDA POR SEMÁFORO BINARIO
        with self.semaphore:
            observed_quota = self.available_quota
            if self.available_quota > 0:
                # 1. Comprobar que existe un cupo
                # 2. Decrementar el contador
                self.available_quota -= 1
                remaining_quota = self.available_quota
                # 3. Registrar la inscripción aceptada
                self.enrolled_students.append(student_id)
                success = True
                message = f"{student_id} obtiene un cupo protegido por semáforo (cupos restantes: {remaining_quota})"
            else:
                remaining_quota = self.available_quota
                self.rejected_students.append(student_id)
                success = False
                message = f"{student_id} no encuentra cupos disponibles (rechazado)"

        # Fuera de la sección crítica
        t_end = time.perf_counter()
        wait_time = t_end - t_start

        if success:
            self.emit_event(student_id, "success", message, remaining_quota)
        else:
            self.emit_event(student_id, "reject", message, remaining_quota)

        result = StudentAttemptResult(
            student_id=student_id,
            success=success,
            start_time=t_start,
            end_time=t_end,
            wait_time=wait_time,
            observed_quota=observed_quota,
            message=message,
            thread_name=thread_name
        )
        self.results.append(result)
        return result
