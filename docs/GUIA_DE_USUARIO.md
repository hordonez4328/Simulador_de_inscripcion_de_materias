# GUÍA DE USUARIO - PORTAL DE INSCRIPCIÓN Y SIMULADOR

Esta guía explica paso a paso cómo utilizar el **Portal Académico Universitario** y el **Laboratorio de Concurrencia**.

---

## 1. Acceso a la Aplicación
1. Inicie el servidor ejecutando en PowerShell:
   ```powershell
   python app.py
   ```
2. Abra su navegador web en la dirección:
   ```text
   http://127.0.0.1:5000
   ```

---

## 2. Secciones Principales del Sistema

### 2.1. Inicio
- Muestra el perfil del estudiante de demostración (**Carlos Andrés Mendoza**).
- Resumen en tiempo real de:
  - Créditos aprobados e inscritos.
  - Cantidad de asignaturas cursadas, inscritas, disponibles y bloqueadas.

### 2.2. Plan de Estudios (Malla Curricular)
- **Organización:** 10 semestres completos organizados en columnas horizontales con scroll interactivo.
- **Leyenda de 4 Colores Obligatorios:**
  - 🟩 **VERDE (Cursada):** Materia ya aprobada en semestres previos. No requiere inscripción.
  - 🟨 **AMARILLO (Inscrita):** Materia actualmente inscrita en el periodo 2026-2.
  - 🟧 **NARANJA (Disponible):** Cumple con todos los prerrequisitos y tiene cupos disponibles. Lista para inscribir.
  - 🟥 **ROJO (No habilitada):** Bloqueada porque el estudiante aún no ha aprobado las asignaturas prerrequisito.
- **Líneas de Prerrequisitos:** Curvas SVG dinámicas que conectan las asignaturas dependientes. Se pueden activar o desactivar con el interruptor superior.
- **Detalle de Asignatura:** Haga clic sobre cualquier tarjeta de materia para abrir el modal con descripción, prerrequisitos, docentes, horarios y botón de inscripción directa.

### 2.3. Horarios Semanales
- Vista semanal de **Lunes a Sábado** (07:00 a 21:00).
- Visualización de bloques de clases inscritas con salón, grupo y docente.
- Botón *"Consultar Horarios Ofertados"* para revisar grupos disponibles sin inscribirlos.

### 2.4. Laboratorio de Concurrencia
Permite experimentar qué sucede cuando múltiples estudiantes intentan inscribirse simultáneamente:
1. **Configurar parámetros:**
   - Cupos disponibles iniciales (por defecto 5).
   - Cantidad de estudiantes / hilos reales (presets: 10, 100, 500, 1000).
   - Pausa artificial (slider de latencia).
   - Mecanismo: Sin Protección, Mutex o Semáforo.
2. **Ejecutar prueba:** Presione *"Ejecutar Prueba"* para ver el registro en vivo en la consola de la derecha.
3. **Comparar las 3 versiones:** Presione *"Comparar las 3 Versiones"* para ejecutar secuencialmente los tres métodos bajo idénticas condiciones y generar los gráficos comparativos.

### 2.5. Comparación de Resultados
- Tabla histórica de todas las ejecuciones realizadas en la sesión.
- Diagnóstico automático:
  - *Sobreinscripción confirmada*
  - *Contador inconsistente*
  - *Ejecución correcta sin anomalías*

### 2.6. Historial de Asignaturas
- Lista oficial de materias inscritas con opción de cancelación individual.
- Registro histórico de asignaturas aprobadas con sus respectivas notas.
