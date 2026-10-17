"""
Cálculo de estadísticas y métricas para las ejecuciones del simulador.
"""

from typing import List
from simulator.models import SimulationMetrics, StudentAttemptResult, SimulationLogEvent

def calculate_metrics(
    simulation_id: str,
    mode: str,
    initial_quota: int,
    num_students: int,
    final_quota: int,
    results: List[StudentAttemptResult],
    events: List[SimulationLogEvent],
    total_time: float
) -> SimulationMetrics:
    """Calcula las métricas reales a partir de los resultados de los hilos."""
    successful = [r for r in results if r.success]
    rejected = [r for r in results if not r.success]

    successful_count = len(successful)
    rejected_count = len(rejected)

    # Sobreinscripción: cuántos cupos por encima del cupo inicial se concedieron
    oversubscriptions = max(0, successful_count - initial_quota)

    # Inconsistencia lógica del contador:
    # 1. Si cupos finales < 0
    # 2. Si cupos finales != max(0, initial_quota - successful_count)
    # 3. Si hubo sobreinscripción
    inconsistencies = 0
    expected_final_quota = max(0, initial_quota - successful_count)
    if final_quota < 0:
        inconsistencies += abs(final_quota)
    if final_quota != expected_final_quota:
        inconsistencies += 1
    if oversubscriptions > 0:
        inconsistencies += oversubscriptions

    # Tiempos de espera observados
    wait_times = [r.wait_time for r in results]
    avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0.0
    max_wait_time = max(wait_times) if wait_times else 0.0

    # Categorización del estado
    if oversubscriptions > 0:
        status_label = "Sobreinscripción confirmada"
    elif inconsistencies > 0 or final_quota < 0:
        status_label = "Contador inconsistente"
    else:
        status_label = "Ejecución correcta sin anomalías detectadas"

    return SimulationMetrics(
        simulation_id=simulation_id,
        mode=mode,
        initial_quota=initial_quota,
        num_students=num_students,
        successful_enrollments=successful_count,
        rejected_enrollments=rejected_count,
        final_quota=final_quota,
        oversubscriptions=oversubscriptions,
        inconsistencies=inconsistencies,
        total_time=total_time,
        avg_wait_time=avg_wait_time,
        max_wait_time=max_wait_time,
        status_label=status_label,
        results=results,
        events=events
    )
