# Simulador de Inscripción de Materias Universitarias
### Programación Concurrente con Hilos, Mutex, Semáforos e Interfaz Web

## Escenario
Seguro lo han vivido: llega el día de inscripciones, hay pocos cupos en una materia, y todo el mundo le da clic al mismo tiempo. Eso es justo lo que van a simular. En equipos de 3, van a programar una materia con cupos limitados y varios hilos —cada uno representando a un estudiante— que intentan inscribirse al mismo tiempo.

---

## 1. Descripción General del Proyecto

Este proyecto académico implementa un simulador completo de matrícula universitaria con **hilos reales del sistema operativo**, diseñado para estudiar y demostrar experimentalmente qué ocurre cuando múltiples procesos concurrentes compiten por un recurso crítico limitado.

El sistema incluye:
1. **Versión Sin Protección:** Permite observar de manera reproducible la **Condición de Carrera (*Race Condition*)**, contadores de cupos negativos y sobreinscripciones de estudiantes.
2. **Versión Protegida con Mutex:** Garantiza exclusión mutua estricta mediante `threading.Lock`.
3. **Versión Protegida con Semáforo:** Emplea un semáforo binario `threading.Semaphore(1)` para la sincronización de la sección crítica.
4. **Portal Web Universitario:** Interfaz moderna e interactiva desarrollada con Flask y Bootstrap 5, inspirada en plataformas universitarias reales.
5. **Malla Curricular de 10 Semestres:** Asignaturas codificadas mediante **4 colores normativos** (Cursada, Inscrita, Disponible, No Habilitada) con trazado dinámico de curvas SVG para prerrequisitos.
6. **Módulo de Horarios Semanales:** Calendario de Lunes a Sábado con validación de conflictos y solapamientos de horario en el servidor.
7. **Laboratorio de Concurrencia en Vivo:** Consola de eventos en tiempo real y gráficos comparativos automáticos con Chart.js.
8. **Suite de Pruebas Automatizadas:** 28 pruebas unitarias y de integración con `pytest`.

---

## 2. Tecnologías Utilizadas

- **Lenguaje:** Python 3.12 / 3.13
- **Concurrencia:** `threading.Thread`, `threading.Lock`, `threading.Semaphore`, `threading.Barrier`, `queue.Queue`
- **Backend Web:** Flask 3.1, Jinja2, Werkzeug
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js
- **Formato de Datos:** JSON (`data/curriculum.json`)
- **Pruebas Automatizadas:** `pytest` 9.1
- **Control de Versiones:** Git y GitHub

---

## 3. Estructura del Repositorio

```text
simulador-inscripcion-materias/
│
├── README.md                          # Documentación general del repositorio
├── requirements.txt                    # Dependencias del proyecto (Flask, pytest)
├── .gitignore                          # Exclusiones de Git (venv, cachés, logs)
├── app.py                              # Lanzador principal del Portal Web
│
├── version-sin-proteccion/             # Versión 1: Insegura (Condición de Carrera)
│   ├── README.md                       # Explicación técnica y comandos
│   └── main.py                         # Script ejecutable de consola
│
├── version-mutex/                      # Versión 2: Protegida con Mutex
│   ├── README.md                       # Explicación de exclusión mutua y Lock
│   └── main.py                         # Script ejecutable de consola
│
├── version-semaforo/                   # Versión 3: Protegida con Semáforo
│   ├── README.md                       # Explicación de semáforo binario vs contador
│   └── main.py                         # Script ejecutable de consola
│
├── interfaz-web/                       # Aplicación Web Flask
│   ├── README.md                       # Guía de la aplicación web
│   ├── app.py                          # Rutas y API REST de simulación
│   ├── templates/                      # Vistas Jinja2
│   │   ├── base.html                   # Cabecera institucional y navegación
│   │   ├── index.html                  # Panel de inicio y resumen de créditos
│   │   ├── curriculum.html             # Malla curricular de 10 semestres y SVG
│   │   ├── schedule.html               # Calendario de horarios semanales
│   │   ├── simulator.html              # Laboratorio experimental en tiempo real
│   │   ├── results.html                # Tabla histórica y gráficos
│   │   ├── analysis.html               # Informe de las cuatro preguntas académicas
│   │   └── history.html                # Historial de asignaturas e inscripciones
│   └── static/                         # Estilos y scripts clientes
│       ├── css/styles.css              # Colores obligatorios y cuadrícula 10 sem.
│       └── js/
│           ├── curriculum.js           # Trazado de curvas Bézier SVG y modal
│           └── simulator.js            # Consola en vivo y gráficos Chart.js
│
├── simulator/                          # Motor de concurrencia y lógica de negocio
│   ├── __init__.py                     # Exportación de clases principales
│   ├── models.py                       # Modelos de datos (Cursos, Horarios, Métricas)
│   ├── enrollment.py                   # Manejadores Unsafe, Mutex y Semaphore
│   ├── runner.py                       # Orquestador de hilos reales y barrera
│   ├── metrics.py                      # Detección y cálculo de inconsistencias
│   └── academic_service.py             # Validaciones de prerrequisitos y horarios
│
├── data/
│   └── curriculum.json                 # Plan de estudios de Ingeniería (50 asignaturas)
│
├── tests/                              # Suite de pruebas automatizadas (28 tests)
│   ├── test_unsafe.py                  # Pruebas de la versión sin protección
│   ├── test_mutex.py                   # Pruebas de exclusión mutua estricta
│   ├── test_semaphore.py               # Pruebas de semáforo binario
│   ├── test_enrollment.py              # Pruebas de reglas académicas y horarios
│   ├── test_metrics.py                 # Pruebas de cálculo de anomalías
│   └── test_web.py                     # Pruebas de endpoints web y API REST
│
└── docs/                               # Documentación académica y técnica
    ├── INFORME_COMPARATIVO.md          # Respuestas completas a las 4 preguntas
    ├── GUIA_DE_USUARIO.md              # Manual de navegación del portal
    ├── GUIA_TECNICA.md                 # Arquitectura de software y APIs
    └── GUIA_DE_EXPOSICION.md           # Guión paso a paso para la sustentación
```

---

## 4. Instalación y Ejecución en Windows y Visual Studio Code

### 4.1. Requisitos Previos
Tener instalado Python 3.10 o superior (disponible mediante `python` o el lanzador `py`).

### 4.2. Paso a Paso en PowerShell

1. **Abrir la terminal en la raíz del repositorio:**
   ```powershell
   cd c:\Users\User\.copilot\repos\Simulador_de_inscripcion_de_materias
   ```

2. **Crear el entorno virtual:**
   ```powershell
   py -m venv .venv
   ```

3. **Activar el entorno virtual:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(Si PowerShell bloquea la ejecución de scripts, habilítela temporalmente con: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*.

4. **Instalar dependencias:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

5. **Ejecutar la suite de pruebas automatizadas:**
   ```powershell
   python -m pytest -v
   ```

6. **Iniciar el Portal Web Universitario:**
   ```powershell
   python app.py
   ```

7. **Abrir en el navegador:**
   Acceda a: [http://127.0.0.1:5000](http://127.0.0.1:5000)

8. **Detener el servidor:**
   Presione `Ctrl + C` en la terminal.

---

## 5. Ejecución Independiente por Consola (CLI)

Cada una de las tres versiones de concurrencia puede ejecutarse de manera autónoma desde la terminal:

```powershell
# 1. Versión Sin Protección (Expone condición de carrera y contadores negativos)
python version-sin-proteccion/main.py 5 15 0.01

# 2. Versión con Mutex (Exclusión mutua estricta con threading.Lock)
python version-mutex/main.py 5 15 0.01

# 3. Versión con Semáforo Binario (threading.Semaphore(1))
python version-semaforo/main.py 5 15 0.01
```

*Parámetros opcionales: `<cupos_disponibles> <estudiantes> <pausa_artificial_segundos>`*.

---

## 6. Tabla Comparativa de Mecanismos de Sincronización

| Mecanismo | Primitiva en Python | Atómica | Exclusión Mutua | Prevención de Sobreinscripción | Espera Acotada Garantizada | Rendimiento (1000 Hilos) | Diagnóstico |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Sin Protección** | Ninguna (código desprotegido) | ❌ No | ❌ No | ❌ No (hasta +181 sobrecupos) | N/A | 0.1150 s | Condición de carrera severa |
| **Mutex** | `threading.Lock` |  Sí |  Sí (1 hilo) |  Sí (exactamente 5 inscritos) | ⚠️ No estricta (depende del OS) | 0.1055 s | Exclusión mutua garantizada |
| **Semáforo Binario** | `threading.Semaphore(1)` |  Sí |  Sí (1 hilo) |  Sí (exactamente 5 inscritos) | ⚠️ No estricta (depende del OS) | 0.1095 s | Exclusión mutua garantizada |

---

## 7. Distribución del Equipo de Desarrollo

- **Integrante 1:** Responsable de la **Versión Sin Protección**, caracterización experimental de la condición de carrera y análisis de contadores negativos.
- **Integrante 2:** Responsable de la **Versión con Mutex**, implementación de `threading.Lock` y cálculo de tiempos de espera en la sección crítica.
- **Integrante 3:** Responsable de la **Versión con Semáforo Binario**, implementación de `threading.Semaphore(1)` y diferenciación teórica frente a semáforos contadores.

---

## 8. Enlaces a la Documentación Completa

- [Informe Académico Comparativo (Respuestas a las 4 preguntas)](file:///c:/Users/User/.copilot/repos/Simulador_de_inscripcion_de_materias/docs/INFORME_COMPARATIVO.md)
- [Guía de Usuario del Portal Web](file:///c:/Users/User/.copilot/repos/Simulador_de_inscripcion_de_materias/docs/GUIA_DE_USUARIO.md)
- [Guía Técnica y Arquitectura de Software](file:///c:/Users/User/.copilot/repos/Simulador_de_inscripcion_de_materias/docs/GUIA_TECNICA.md)
- [Guía de Exposición y Sustentación en Clase](file:///c:/Users/User/.copilot/repos/Simulador_de_inscripcion_de_materias/docs/GUIA_DE_EXPOSICION.md)
