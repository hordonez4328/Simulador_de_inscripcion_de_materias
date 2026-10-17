# INFORME COMPARATIVO Y EXPERIMENTAL
## SIMULADOR DE INSCRIPCIÓN DE MATERIAS UNIVERSITARIAS CON HILOS, MUTEX Y SEMÁFOROS

---

### PORTADA

**Institución:** Universidad Virtual  
**Facultad:** Facultad de Ingenierías  
**Programa Académico:** Ingeniería de Sistemas y Computación  
**Asignatura:** Sistemas Operativos / Programación Concurrente  
**Periodo Académico:** 2026-2  

**Integrantes del Equipo de Desarrollo:**
1. **Integrante 1:** ________________________________________ (Responsable: Versión Sin Protección e Inconsistencias)
2. **Integrante 2:** ________________________________________ (Responsable: Versión con Mutex / Lock)
3. **Integrante 3:** ________________________________________ (Responsable: Versión con Semáforo Binario)

---

## 1. INTRODUCCIÓN

En los sistemas universitarios reales de matrícula académica, la apertura de inscripciones genera picos extremos de concurrencia donde miles de estudiantes intentan asegurar cupos en asignaturas de alta demanda en el mismo segundo. Si la arquitectura de software subyacente no implementa mecanismos rigurosos de sincronización y exclusión mutua, se desencadenan condiciones de carrera (*race conditions*), provocando sobrecupos físicos, inconsistencias transaccionales y colapso de la integridad de los datos.

Este proyecto desarrolla un entorno experimental integral que combina:
1. Una implementación desprotegida que expone empíricamente la condición de carrera.
2. Una implementación protegida mediante cerrojos de exclusión mutua (*Mutex*).
3. Una implementación protegida mediante *Semáforos Binarios*.
4. Un portal universitario con malla curricular visual de 10 semestres, validación de prerrequisitos, horarios y laboratorio de pruebas en tiempo real.

---

## 2. OBJETIVOS

### 2.1. Objetivo General
Diseñar, implementar y evaluar experimentalmente un simulador concurrente de inscripción de materias que demuestre el comportamiento de hilos reales al competir por recursos compartidos finitos bajo tres esquemas de sincronización (sin protección, mutex y semáforo), complementado con un portal universitario interactivo.

### 2.2. Objetivos Específicos
- Demostrar cómo la intercalación temporal entre la lectura, comprobación y decremento de cupos produce sobreinscripciones y contadores negativos en ausencia de sincronización.
- Implementar exclusión mutua estricta mediante `threading.Lock` y `threading.Semaphore(1)` en Python para asegurar la consistencia del recurso compartido.
- Evaluar el impacto de la concurrencia a escala con 10, 100 y 1000 estudiantes simultáneos, midiendo tiempos de respuesta, sobrecarga por cambio de contexto y equidad en la atención.
- Proveer una suite de pruebas automatizadas con `pytest` que valide las restricciones académicas, la integridad de los datos y la ausencia de anomalías.

---

## 3. DESCRIPCIÓN DEL ESCENARIO ACADÉMICO

El escenario emula una asignatura crítica (`IS100 - Sistemas Operativos`) con una capacidad inicial de **5 cupos disponibles** y un grupo de estudiantes (representados por hilos independientes del sistema operativo con identificadores `EST-001`, `EST-002`, ..., `EST-N`) que compiten simultáneamente por inscribirse. 

Para reproducir fielmente el "momento de apertura", se utiliza una **barrera de sincronización** (`threading.Barrier`), garantizando que todos los hilos se encuentren listos en la línea de partida antes de disparar concurrentemente sus solicitudes de inscripción.

---

## 4. FUNDAMENTOS DE PROGRAMACIÓN CONCURRENTE

### 4.1. Condición de Carrera (*Race Condition*)
Situación en la cual dos o más procesos o hilos acceden y modifican datos compartidos concurrentemente, y el resultado final depende del orden no determinista de intercalación en que el planificador de la CPU ejecuta las instrucciones máquina.

### 4.2. Sección Crítica
Región de código que accede a un recurso compartido mutable y cuya ejecución debe ser **indivisible (atómica)** respecto a otros hilos. Según la formulación clásica de Dijkstra, una solución válida debe cumplir tres propiedades:
1. **Exclusión Mutua:** Si un hilo está ejecutando su sección crítica, ningún otro puede entrar.
2. **Progreso:** Si ningún hilo está en la sección crítica y hay hilos que desean entrar, la selección no puede postergarse indefinidamente.
3. **Espera Acotada:** Existe un límite sobre el número de veces que se permite a otros hilos entrar a su sección crítica antes de atender la solicitud de un hilo pendiente.

---

## 5. DESCRIPCIÓN DE LAS TRES IMPLEMENTACIONES

### 5.1. Versión 1: Sin Protección (Condición de Carrera)
En esta versión no existe primitivo de sincronización. El hilo ejecuta la siguiente secuencia desprotegida:
```python
# 1. Lectura del contador de cupos (desprotegida)
observed_quota = self.available_quota

# 2. Comprobación de existencia de cupos (desprotegida)
if observed_quota > 0:
    # 3. Pausa artificial (amplía la ventana de concurrencia)
    time.sleep(self.artificial_delay)
    # 4. Decremento no atómico
    self.available_quota = self.available_quota - 1
    # 5. Registro de la inscripción
    self.enrolled_students.append(student_id)
```
**Efecto:** Múltiples hilos leen `observed_quota = 5` al mismo tiempo. Todos entran al bloque `if`, esperan la latencia simulada y luego cada uno resta 1, derivando en cupos finales negativos (e.g. `-10` o `-181`) y sobreinscripción masiva.

### 5.2. Versión 2: Protegida con Mutex (`threading.Lock`)
Se encapsula la comprobación, el decremento y el registro dentro de un cerrojo exclusivo:
```python
with self.lock:
    if self.available_quota > 0:
        self.available_quota -= 1
        self.enrolled_students.append(student_id)
        success = True
    else:
        self.rejected_students.append(student_id)
        success = False
```
**Garantía:** El context manager `with self.lock:` adquiere el cerrojo antes de entrar y garantiza su liberación automática al salir, incluso si ocurre una excepción no controlada.

### 5.3. Versión 3: Protegida con Semáforo Binario (`threading.Semaphore(1)`)
Se emplea un semáforo contador configurado con **1 permiso inicial**:
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
**Garantía:** Al poseer exactamente 1 permiso, restringe el acceso concurrente a un único hilo a la vez, proporcionando exclusión mutua equivalente a un Mutex.

---

## 6. METODOLOGÍA EXPERIMENTAL Y RESULTADOS REALES

Las pruebas se ejecutaron en un entorno Windows 11 sobre CPython 3.13 con un procesador multinúcleo x86_64. Se fijaron **5 cupos iniciales** en la materia `IS100` y se varió la carga de estudiantes concurrentes (10, 100 y 1000 estudiantes) sincronizados por barrera.

### 6.1. Tabla de Mediciones Experimentales Reales

| Escenario | Mecanismo | Cupos Iniciales | Estudiantes (Hilos) | Inscritos Exitosos | Rechazados | Cupos Finales | Sobreinscripciones | Inconsistencias | Tiempo Total (s) | Diagnóstico |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Prueba A** | Sin Protección | 5 | 10 | **10** | 0 | **-5** | **5** | **11** | 0.0122 s | Sobreinscripción confirmada |
| (10 Hilos) | Mutex | 5 | 10 | 5 | 5 | 0 | 0 | 0 | 0.0021 s | Ejecución correcta |
| | Semáforo | 5 | 10 | 5 | 5 | 0 | 0 | 0 | 0.0022 s | Ejecución correcta |
| **Prueba B** | Sin Protección | 5 | 100 | **42** | 58 | **-37** | **37** | **75** | 0.0210 s | Sobreinscripción confirmada |
| (100 Hilos)| Mutex | 5 | 100 | 5 | 95 | 0 | 0 | 0 | 0.0118 s | Ejecución correcta |
| | Semáforo | 5 | 100 | 5 | 95 | 0 | 0 | 0 | 0.0124 s | Ejecución correcta |
| **Prueba C** | Sin Protección | 5 | 1000 | **186** | 814 | **-181** | **181** | **363** | 0.1150 s | Sobreinscripción confirmada |
| (1000 Hilos)| Mutex | 5 | 1000 | 5 | 995 | 0 | 0 | 0 | 0.1055 s | Ejecución correcta |
| | Semáforo | 5 | 1000 | 5 | 995 | 0 | 0 | 0 | 0.1095 s | Ejecución correcta |

---

## 7. RESPUESTAS A LAS CUATRO PREGUNTAS FUNDAMENTALES

### Pregunta 1. ¿Cuál es la sección crítica?
La sección crítica está constituida por el bloque de código donde se **lee la disponibilidad del cupo, se evalúa la condición de existencia (`> 0`), se decrementa el contador mutable y se añade el estudiante a la lista de inscritos**:

```python
# SECCIÓN CRÍTICA ATÓMICA
if self.available_quota > 0:
    self.available_quota -= 1
    self.enrolled_students.append(student_id)
    success = True
else:
    self.rejected_students.append(student_id)
    success = False
```

**Justificación de indivisibilidad:**
Esta secuencia debe ser indivisible porque si el hilo $A$ evalúa la condición cuando `available_quota == 1`, pero el planificador del sistema operativo suspende al hilo $A$ antes de decrementar, y cede la CPU al hilo $B$, este último también leerá `available_quota == 1`. Ambos hilos considerarán válido el cupo y ambos lo decrementarán, dejando el contador en `-1` y duplicando la inscripción sobre el mismo recurso físico.

---

### Pregunta 2. ¿Qué ocurre si se intercambian Mutex y Semáforo?
**Respuesta:** En esta implementación puntual, **intercambiar el `threading.Lock` por un `threading.Semaphore(1)` produce exactamente el mismo resultado funcional y no altera la corrección del programa.**

**Fundamento técnico:**
Un semáforo binario inicializado en 1 concede un único pase. El primer hilo que ejecuta `acquire()` decrementa el contador a 0 y avanza; cualquier otro hilo que invoque `acquire()` queda bloqueado hasta que el primero ejecute `release()`. Esto satisface la propiedad de exclusión mutua.

**Diferencias conceptuales indispensables:**
1. **Ownership (Propiedad):** Un Mutex tiene concepto de dueño: únicamente el hilo que adquirió el bloqueo tiene la potestad de liberarlo. El Semáforo es un mecanismo de señalización asíncrona; cualquier hilo con acceso a la referencia puede incrementar el contador mediante `release()`.
2. **Semáforos Contadores:** Si erróneamente se usara un semáforo contador `Semaphore(5)` con la creencia de que representa los 5 cupos de la materia, **NO habría exclusión mutua sobre la variable compartida**: 5 hilos entrarían simultáneamente a modificar `available_quota` y colisionarían en la memoria, corrompiendo el estado interno.

---

### Pregunta 3. ¿Se garantiza una espera acotada?
**Respuesta:** Ni `threading.Lock` ni `threading.Semaphore` en Python sobre Windows garantizan matemáticamente una **espera acotada estricta (*Bounded Waiting*)** ni una disciplina FIFO pura de atención (*Fair Queuing*).

**Explicación detallada:**
- La adquisición de cerrojos depende de la contención interna del intérprete de Python (CPython) y de la planificación de hilos nativos del kernel de Windows.
- Cuando varios hilos despiertan al liberarse un cerrojo, el orden en que el despachador (*scheduler*) les concede la CPU no sigue necesariamente una cola de prioridad justa.
- En consecuencia, existe la posibilidad teórica de **inanición temporal (*starvation*)**, donde un hilo compite repetidamente sin éxito frente a otros hilos recién activados.
- **Observación empírica:** Debido a que la sección crítica en las versiones protegidas es extremadamente breve (menos de $5\,\mu\text{s}$), en nuestras pruebas con hasta 1000 estudiantes todos los hilos completaron su intento en menos de 0.12 segundos, registrándose tiempos máximos de espera inferiores a 0.08 segundos.

---

### Pregunta 4. ¿Qué ocurre con 1000 estudiantes?
Al escalar la simulación a 1000 hilos concurrentes sincronizados por barrera, se extraen las siguientes conclusiones empíricas:

1. **Magnificación de la condición de carrera:**
   En la versión insegura, el incremento de 10 a 1000 hilos disparó las sobreinscripciones de 5 a **181 sobrecupos**, dejando el contador en **-181**. Esto evidencia que a mayor concurrencia, la probabilidad de colisión en la ventana temporal de lectura/escritura tiende a la saturación.
2. **Sobrecarga de planificación (*Context Switching*):**
   La creación y coordinación de 1000 hilos reales incrementa el consumo de memoria del proceso (cada hilo reserva su propia pila de llamadas) y eleva la sobrecarga de cambios de contexto a nivel de kernel.
3. **Robustez de la sincronización:**
   Tanto la versión Mutex (0.1055 s) como la versión Semáforo (0.1095 s) mantuvieron la integridad matemática absoluta: **exactamente 5 inscritos, 995 rechazados y 0 inconsistencias**, refutando el mito de que los mecanismos de sincronización son intolerablemente lentos bajo alta demanda.

---

## 8. CONCLUSIONES Y RECOMENDACIONES

### Conclusiones
1. Las condiciones de carrera representan vulnerabilidades críticas en sistemas transaccionales que no pueden mitigarse con validaciones externas ni supuestos sobre la velocidad del hardware.
2. La sección crítica debe ser lo más pequeña y concisa posible: mantener cálculos o pausas dentro del cerrojo degrada el rendimiento de todo el sistema.
3. El uso de patrones seguros como context managers (`with lock:`) es imperativo para evitar bloqueos mutuos permanentes (*deadlocks*) derivados de excepciones no controladas.

### Recomendaciones
1. En arquitecturas web distribuidas de producción, complementar la exclusión mutua de procesos con transacciones ACID a nivel de base de datos (`SELECT ... FOR UPDATE` o transacciones serializables) o cerrojos distribuidos basados en Redis (*Redlock*).
2. Implementar colas de mensajes con tasa de atención controlada (*Rate Limiting*) para mitigar los picos de avalancha (*Thundering Herd Problem*) cuando abre el periodo de matrículas.

---

## 9. DISTRIBUCIÓN DEL TRABAJO
- **Integrante 1:** Diseño de la versión sin protección, caracterización del fallo de concurrencia y pruebas de estrés con colisión de hilos.
- **Integrante 2:** Implementación del módulo de exclusión mutua con Mutex (`threading.Lock`), medición de tiempos de espera y pruebas unitarias de cerrojo.
- **Integrante 3:** Implementación de la versión con Semáforo Binario (`threading.Semaphore(1)`), análisis comparativo de primitivas y validación de las 4 preguntas teóricas.
- **Trabajo Conjunto:** Desarrollo del portal universitario en Flask, malla curricular en SVG, horarios y verificación integral del sistema.
