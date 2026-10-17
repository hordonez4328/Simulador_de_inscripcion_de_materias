"""
Prueba unitaria para el CLI de la versión con Semáforo.
"""
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from main import run_standalone

def test_semaforo_cli_execution():
    metrics = run_standalone(total_quota=3, num_students=6, delay=0.001)
    assert metrics.num_students == 6
    assert metrics.successful_enrollments == 3
    assert metrics.final_quota == 0
    assert metrics.oversubscriptions == 0
