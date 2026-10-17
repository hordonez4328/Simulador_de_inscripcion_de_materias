# GUÍA DE EXPOSICIÓN Y DEMOSTRACIÓN EN CLASE

Esta guía está diseñada para estructurar la sustentación oral del proyecto ante el docente y compañeros de clase.

---

## 1. Estructura y Distribución del Tiempo (10 a 12 minutos)

| Tiempo | Sección | Responsable | Contenido Clave |
| :---: | :--- | :--- | :--- |
| **00:00 - 02:00** | Introducción y Planteamiento | Todo el equipo | Presentación del escenario de apertura de matrículas y objetivos. |
| **02:00 - 04:30** | Demostración de Condición de Carrera | Integrante 1 | Ejecución de la versión sin protección en vivo (CLI y Web). |
| **04:30 - 07:00** | Demostración de Mutex y Semáforo | Integrantes 2 y 3 | Ejecución protegida, sección crítica atómica y comparativa en vivo. |
| **07:00 - 09:00** | Malla Curricular y Reglas Académicas | Todo el equipo | Visualización de 10 semestres, 4 colores, líneas SVG y cruces de horario. |
| **09:00 - 11:00** | Prueba de Estrés (1000 Estudiantes) | Todo el equipo | Escalabilidad, tiempos de respuesta y análisis de preguntas teóricas. |
| **11:00 - 12:00** | Conclusiones y Preguntas | Todo el equipo | Ronda de preguntas del docente. |

---

## 2. Guión Paso a Paso para la Demostración en Vivo

### Paso 1: Introducción (2 min)
- *"Buenos días profesor y compañeros. Hoy presentamos nuestro Simulador de Inscripción de Materias Universitarias con Hilos Reales, Mutex, Semáforos e Interfaz Web."*
- *"Todos hemos vivido el día de inscripciones cuando se habilitan los cupos de una materia popular y cientos de estudiantes dan clic simultáneamente. Eso es exactamente lo que recreamos experimentalmente."*

### Paso 2: Exposición de la Condición de Carrera (2.5 min - Integrante 1)
1. **Abrir la terminal o la web:**
   - Ejecutar en consola: `python version-sin-proteccion/main.py 5 15 0.01`
   - O en la interfaz web (`/simulator`): Cupos=5, Estudiantes=15, Pausa=0.01s.
2. **Explicar lo que ocurre:**
   - *"Observen la consola: Todos los hilos leyeron 5 cupos disponibles al inicio porque no había cerrojo. Cada uno pensó que había cupo disponible. Al decrementar, se inscribieron los 15 estudiantes y el contador final quedó en -10. Tenemos 10 sobreinscripciones confirmadas."*

### Paso 3: Demostración de Soluciones Protegidas (2.5 min - Integrantes 2 y 3)
1. **Demostración de Mutex:**
   - Ejecutar: `python version-mutex/main.py 5 15 0.01`
   - *"Con `threading.Lock`, la sección crítica de verificación, decremento y registro es atómica. Exactamente 5 estudiantes obtienen cupo y 10 son rechazados de forma consistente. Cupos finales: 0."*
2. **Demostración de Semáforo Binario:**
   - Ejecutar: `python version-semaforo/main.py 5 15 0.01`
   - *"Con `threading.Semaphore(1)`, el semáforo binario proporciona exclusión mutua análoga al mutex en este escenario. Nótese que si usáramos un semáforo contador de 5 permisos, no protegería la variable compartida contra colisiones."*

### Paso 4: Portal Web y Malla Curricular (2 min)
1. Ir a `/curriculum`:
   - Mostrar los **10 semestres** organizados en columnas.
   - Mostrar la leyenda y los **4 colores normativos**:
     - Verde: Cursada.
     - Amarillo: Inscrita en 2026-2.
     - Naranja: Disponible para inscribir.
     - Rojo: Bloqueada por falta de prerrequisitos.
   - Activar y desactivar el interruptor de **Líneas SVG de prerrequisitos**.
2. Abrir el modal de una materia disponible (naranja) e intentar inscribirla:
   - Mostrar cómo se decrementa el cupo del grupo y se actualiza el resumen de créditos.
3. Ir a `/schedule`:
   - Mostrar la vista semanal de Lunes a Sábado con las franjas horarias ocupadas.

### Paso 5: Prueba de Estrés con 1000 Hilos (2 min)
1. En `/simulator`, seleccionar **1000 estudiantes** y presionar *"Comparar las 3 Versiones"*:
   - Mostrar los gráficos generados en vivo con Chart.js.
   - Resaltar que las versiones con Mutex y Semáforo tardan apenas ~0.10s en coordinar 1000 hilos reales, manteniendo 0 inconsistencias y 0 sobrecupos.

---

## 3. Respuestas Preparadas ante Preguntas del Profesor

- **¿Por qué usaron barrera (`threading.Barrier`)?**
  *Para asegurar que todos los hilos inicien exactamente al mismo tiempo y simular el pico de avalancha de solicitudes concurrentes.*
- **¿Es lo mismo un semáforo contador que un semáforo binario?**
  *No. El semáforo binario (1 permiso) restringe la sección crítica a un solo hilo. Un semáforo contador de 5 permisos permitiría 5 hilos simultáneos, lo que corrompería el contador compartido.*
- **¿Garantizan Lock o Semaphore atención justa (FIFO)?**
  *No en estricto rigor matemático. Dependen de la planificación del kernel del sistema operativo y del GIL de Python, por lo que no garantizan espera acotada pura, aunque empíricamente la contención fue casi instantánea.*
- **¿Cómo se evitan los bloqueos mutuos (*Deadlocks*)?**
  *Se utiliza el context manager `with lock:` / `with semaphore:`, que asegura la liberación incondicional del recurso incluso si se produce un error o excepción.*
