"""
=============================================================================
SIMULADOR DE INSCRIPCIÓN - VERSIÓN PROTEGIDA CON MUTEX (LOCK)
=============================================================================
Esta versión resuelve la condición de carrera empleando un cerrojo de exclusión
mutua (threading.Lock).

Sección Crítica Atómica:
- Comprobación de disponibilidad (available_quota > 0).
- Decremento del contador de cupos (available_quota -= 1).
- Registro del estudiante en la lista de inscritos.

El patrón `with self.lock` garantiza que la sección crítica se ejecute de manera
indivisible para un único hilo a la vez y libera el bloqueo ante cualquier excepción.

Autor / Responsable: Integrante 2 (Versión Mutex)
"""

import sys
import os
import time
import threading

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from simulator.enrollment import MutexEnrollmentManager
from simulator.metrics import calculate_metrics

def run_standalone(total_quota: int = 5, num_students: int = 10, delay: float = 0.01):
    print("=" * 75)
    print(" UNIVERSIDAD VIRTUAL - SIMULADOR DE INSCRIPCIONES ")
    print(" MÓDULO 2: VERSIÓN PROTEGIDA CON MUTEX (LOCK) ")
    print("=" * 75)
    print(f"[*] Parámetros iniciales:")
    print(f"    - Materia de prueba:       IS100 (Sistemas Operativos)")
    print(f"    - Cupos disponibles:       {total_quota}")
    print(f"    - Estudiantes concurrentes: {num_students}")
    print(f"    - Mecanismo:               threading.Lock (Exclusión Mutua)")
    print("-" * 75)
    print("[*] Iniciando hilos de estudiantes (sincronizados mediante barrera)...")
    print("-" * 75)

    manager = MutexEnrollmentManager(initial_quota=total_quota, course_code="IS100", artificial_delay=delay)

    barrier = threading.Barrier(num_students)
    threads = []
    events_log = []

    def on_event(event):
        events_log.append(event)
        color = ""
        if event.event_type == "success":
            color = "[OK] "
        elif event.event_type == "reject":
            color = "[RECHAZADO] "
        elif event.event_type == "critical_enter":
            color = "[LOCK]      "
        else:
            color = "[INFO]      "
        print(f"  {color:<12} {event.message}")

    manager.event_callback = on_event

    def worker(student_id: str):
        barrier.wait()
        manager.attempt_enrollment(student_id)

    t0 = time.perf_counter()
    for i in range(1, num_students + 1):
        sid = f"EST-{i:03d}"
        t = threading.Thread(target=worker, args=(sid,), name=f"Thread-{sid}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_time = time.perf_counter() - t0

    metrics = calculate_metrics(
        simulation_id="CLI-MUTEX",
        mode="mutex",
        initial_quota=total_quota,
        num_students=num_students,
        final_quota=manager.available_quota,
        results=manager.results,
        events=events_log,
        total_time=total_time
    )

    print("-" * 75)
    print(" RESULTADOS DE LA EJECUCIÓN CON MUTEX:")
    print("-" * 75)
    print(f"  - Cupos iniciales:               {metrics.initial_quota}")
    print(f"  - Estudiantes que compitieron:   {metrics.num_students}")
    print(f"  - Inscripciones exitosas:        {metrics.successful_enrollments}")
    print(f"  - Inscripciones rechazadas:      {metrics.rejected_enrollments}")
    print(f"  - Cupos finales en contador:     {metrics.final_quota}")
    print(f"  - Sobreinscripciones detectadas: {metrics.oversubscriptions}")
    print(f"  - Inconsistencias lógicas:       {metrics.inconsistencies}")
    print(f"  - Diagnóstico:                   {metrics.status_label}")
    print(f"  - Tiempo total de ejecución:     {metrics.total_time:.4f} s")
    print(f"  - Tiempo medio de espera:        {metrics.avg_wait_time:.4f} s")
    print(f"  - Tiempo máximo de espera:       {metrics.max_wait_time:.4f} s")
    print("=" * 75)

    if metrics.oversubscriptions == 0 and metrics.final_quota >= 0:
        print("[+] ÉXITO: El Mutex garantizó la exclusión mutua estricta.")
        print("    Nunca se otorgaron más cupos que los disponibles inicialmente.")
    else:
        print("[!] ERROR INESPERADO: Fallo en la exclusión mutua.")
    print("=" * 75)

    return metrics

if __name__ == "__main__":
    q = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    d = float(sys.argv[3]) if len(sys.argv) > 3 else 0.01
    run_standalone(total_quota=q, num_students=n, delay=d)
