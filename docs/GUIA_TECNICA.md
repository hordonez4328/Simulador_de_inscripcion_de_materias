# GUÍA TÉCNICA Y DE ARQUITECTURA

## 1. Arquitectura del Sistema

El proyecto sigue una arquitectura modular desacoplada en tres capas:
1. **Capa de Dominio y Concurrencia (`simulator/`):**
   - Hilos reales (`threading.Thread`).
   - Sincronización de inicio mediante barrera (`threading.Barrier`).
   - Primitivas de exclusión mutua: `threading.Lock` y `threading.Semaphore(1)`.
   - Cálculo de métricas e inconsistencias (`metrics.py`).
2. **Capa de Servicios Académicos (`simulator/academic_service.py`):**
   - Validación estricta en servidor de prerrequisitos mediante grafos de dependencia.
   - Algoritmo de detección de solapamiento de intervalos horarios $[t_{inicio}, t_{fin})$ en días de semana.
   - Control transaccional de cupos en grupos.
3. **Capa de Presentación e Interfaz Web (`interfaz-web/`):**
   - Servidor Flask 3.1 con plantillas Jinja2 y Bootstrap 5.
   - Renderizado dinámico de curvas Bézier en SVG para prerrequisitos.
   - Consola asíncrona de eventos y visualización con Chart.js.

---

## 2. Modelos de Concurrencia

### 2.1. Barrera de Sincronización
Para forzar una condición de carrera altamente reproducible y simular la apertura de inscripciones donde todos los estudiantes hacen clic en el mismo instante, los hilos se detienen en un punto de encuentro:
```python
barrier = threading.Barrier(num_students)

def student_worker(student_id):
    barrier.wait()  # Todos los hilos esperan hasta que el último esté listo
    manager.attempt_enrollment(student_id)
```

### 2.2. Implementación Insegura (Condición de Carrera)
```python
observed_quota = self.available_quota  # Lectura desprotegida
if observed_quota > 0:
    time.sleep(self.delay)             # Ampliación de intercalación
    self.available_quota -= 1          # Modificación no atómica
    self.enrolled_students.append(student_id)
```

### 2.3. Implementación Protegida con Mutex
```python
with self.lock:
    if self.available_quota > 0:
        self.available_quota -= 1
        self.enrolled_students.append(student_id)
```

### 2.4. Implementación Protegida con Semáforo Binario
```python
with self.semaphore:
    if self.available_quota > 0:
        self.available_quota -= 1
        self.enrolled_students.append(student_id)
```

---

## 3. Endpoints de la API REST

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/curriculum` | Retorna el árbol curricular completo en formato JSON. |
| `GET` | `/api/course/<codigo>` | Obtiene el detalle, prerrequisitos y grupos de una asignatura. |
| `POST` | `/api/enroll` | Inscribe una asignatura validando prerrequisitos y cruces de horario. |
| `POST` | `/api/cancel` | Cancela la inscripción de una materia liberando el cupo del grupo. |
| `POST` | `/api/simulate` | Ejecuta una simulación con hilos reales según los parámetros provistos. |
| `POST` | `/api/compare` | Ejecuta secuencialmente las 3 versiones con parámetros idénticos. |
| `POST` | `/api/history/clear` | Limpia el historial en memoria de las simulaciones realizadas. |

---

## 4. Ejecución de Pruebas Automatizadas

La suite de pruebas contiene 28 casos automatizados que validan concurrencia, métricas, reglas de negocio y endpoints web:
```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```
