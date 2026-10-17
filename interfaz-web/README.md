# Interfaz Web Universitaria y Laboratorio de Concurrencia

Este módulo contiene la aplicación web desarrollada con Flask, HTML5, CSS3, JavaScript y Bootstrap 5, diseñada para la visualización académica de la malla curricular universitaria y la experimentación interactiva de programación concurrente con hilos reales del sistema operativo.

## Estructura de la Interfaz Web
- `app.py`: Servidor y API REST de simulación y validación académica.
- `templates/`: Plantillas Jinja2
  - `base.html`: Diseño base institucional con encabezado de la Universidad Virtual y navegación.
  - `index.html`: Portal de inicio con tarjetas de resumen académico.
  - `curriculum.html`: Malla curricular de 10 semestres con código de 4 colores y trazado SVG de prerrequisitos.
  - `schedule.html`: Vista semanal de horarios de Lunes a Sábado con validación de conflictos.
  - `simulator.html`: Laboratorio experimental de concurrencia en vivo.
  - `results.html`: Comparación tabular y gráfica de mediciones históricas.
  - `analysis.html`: Informe académico detallado con resolución de las cuatro preguntas.
  - `history.html`: Historial académico del estudiante.
- `static/`: Recursos estáticos
  - `css/styles.css`: Estilos de malla curricular, colores normativos y consola de simulación.
  - `js/curriculum.js`: Lógica de curvas Bézier SVG y modal de inscripción.
  - `js/simulator.js`: Conexión asíncrona con el motor de concurrencia y gráficos en Chart.js.

## Ejecución
Desde la raíz del proyecto:
```powershell
python app.py
```
O directamente desde este directorio:
```powershell
python interfaz-web/app.py
```
Abrir en el navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)
