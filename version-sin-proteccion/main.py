"""
=============================================================================
SIMULADOR DE INSCRIPCIÓN - VERSIÓN SIN PROTECCIÓN (CONDICIÓN DE CARRERA)
=============================================================================
Esta versión demuestra experimentalmente la CONDICIÓN DE CARRERA (Race Condition)
cuando múltiples estudiantes intentan inscribirse simultáneamente en una materia
con cupos limitados sin ningún mecanismo de sincronización (sin Mutex ni Semáforo).

Flujo de la operación crítica no atómica:
1. Lectura del contador de cupos disponibles.
2. Comprobación de existencia de cupos (> 0).
3. Pausa artificial configurable (amplía la ventana de intercalación temporal).
4. Decremento del contador de cupos.
5. Registro del estudiante en la lista de inscritos.

Autor / Responsable: Integrante 1 (Versión Sin Protección)
"""

import sys
import os
import time
import threading

# Asegurar acceso al paquete simulator desde cualquier directorio de ejecución
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from simulator.enrollment import UnsafeEnrollmentManager
from simulator.metrics import calculate_metrics

def run_standalone(total_quota: int = 5, num_students: int = 10, delay: float = 0.01):
    print("=" * 75)
    print(" UNIVERSIDAD VIRTUAL - SIMULADOR DE INSCRIPCIONES ")
    print(" MÓDULO 1: VERSIÓN SIN PROTECCIÓN (INSEGURA) ")
    print("=" * 75)
    print(f"[*] Parámetros iniciales:")
    print(f"    - Materia de prueba:       IS100 (Sistemas Operativos)")
    print(f"    - Cupos disponibles:       {total_quota}")
    print(f"    - Estudiantes concurrentes: {num_students}")
    print(f"    - Pausa artificial:        {delay:.4f} segundos")
    print("-" * 75)
    print("[*] Iniciando hilos de estudiantes (sincronizados mediante barrera)...")
    print("-" * 75)

    manager = UnsafeEnrollmentManager(initial_quota=total_quota, course_code="IS100", artificial_delay=delay)

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
        elif event.event_type == "read":
            color = "[LECTURA]   "
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
        simulation_id="CLI-UNSAFE",
        mode="unsafe",
        initial_quota=total_quota,
        num_students=num_students,
        final_quota=manager.available_quota,
        results=manager.results,
        events=events_log,
        total_time=total_time
    )

    print("-" * 75)
    print(" RESULTADOS DE LA EJECUCIÓN SIN PROTECCIÓN:")
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

    if metrics.oversubscriptions > 0 or metrics.final_quota < 0:
        print("[!] ADVERTENCIA CRÍTICA: Se manifestó una CONDICIÓN DE CARRERA.")
        print("    Varios hilos leyeron el contador antes de que fuera decrementado,")
        print("    concediendo más cupos de los físicamente disponibles.")
    else:
        print("[i] NOTA: En esta corrida puntual no se observó inconsistencia.")
        print("    Recuerde que la ausencia de fallo no demuestra seguridad.")
    print("=" * 75)

    return metrics

if __name__ == "__main__":
    q = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    d = float(sys.argv[3]) if len(sys.argv) > 3 else 0.01
    run_standalone(total_quota=q, num_students=n, delay=d)
