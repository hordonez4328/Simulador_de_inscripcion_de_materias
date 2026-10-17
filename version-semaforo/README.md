# Versión Protegida con Semáforo Binario

## Responsable
- **Integrante 3**: Implementación y análisis de la versión protegida mediante semáforo (`threading.Semaphore(1)`).

## Objetivo Académico
Comprender el funcionamiento de un **Semáforo Binario** como mecanismo de sincronización que proporciona exclusión mutua, contrastándolo conceptualmente con un semáforo contador.

## Sección Crítica
```python
with self.semaphore:
    if self.available_quota > 0:
        self.available_quota -= 1
        self.enrolled_students.append(student_id)
        success = True
    else:
        self.rejected_students.append(student_id)
        success = False
```

### Diferenciación Conceptual: Semáforo Binario vs. Contador
- **Semáforo Binario (`Semaphore(1)`):** Tiene un único permiso disponible. Solo permite el acceso a un hilo a la vez, garantizando que el decremento del contador sea atómico.
- **Semáforo Contador (e.g. `Semaphore(5)`):** Permitiría que hasta 5 hilos ejecuten simultáneamente el bloque. Si se usa para proteger la variable `available_quota`, los 5 hilos entrarían al mismo tiempo y colisionarían en la lectura/escritura del contador, reproduciendo la condición de carrera sobre la variable compartida.

## Ejecución desde Terminal
```powershell
python version-semaforo/main.py
```
