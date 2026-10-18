# Versión Sin Protección (Condición de Carrera)

## Responsable
- **Integrante 1**: Implementación y análisis de la versión insegura sin sincronización.

## Objetivo Académico
Evidenciar experimentalmente la **Condición de Carrera** (*Race Condition*) en el proceso de inscripción concurrente de una materia con cupos limitados.

## Descripción del Flujo
Cada hilo representa un estudiante que ejecuta la siguiente secuencia sin cerrojos:
1. **Lectura del contador** de cupos disponibles (`observed_quota = self.available_quota`).
2. **Comprobación de existencia de cupos** (`if observed_quota > 0:`).
3. **Pausa artificial configurable** (`time.sleep(delay)`), simulando latencia de red o procesamiento en base de datos.
4. **Decremento no atómico** (`self.available_quota = current_val - 1`).
5. **Registro de inscripción** en la lista compartida.

Al no existir exclusión mutua, múltiples hilos leen el mismo valor de cupos antes de que el primer hilo alcance a decrementar el contador. Como resultado:
- Se generan **sobreinscripciones** (más estudiantes inscritos que los cupos iniciales disponibles).
- El contador de cupos puede terminar en **valores negativos**.

## Ejecución desde Terminal
```powershell
# Ejecución estándar (5 cupos, 10 estudiantes, 0.01s pausa)
python version-sin-proteccion/main.py

# Parámetros personalizados: python version-sin-proteccion/main.py <cupos> <estudiantes> <pausa>
python version-sin-proteccion/main.py 5 20 0.02
```
## Sección crítica

Son los pasos 1 a 5 del flujo: leer `available_quota`, comprobar `> 0`, la pausa
artificial, el decremento y el registro del estudiante en la lista compartida.

Es la sección crítica porque son los únicos pasos que leen y modifican estado
compartido (`available_quota` y la lista de inscritos), y la decisión de inscribir
depende de que el contador no cambie entre la lectura y la escritura. Crear los
hilos, esperar en la barrera e imprimir resultados no tocan datos compartidos,
por eso quedan fuera. Sin exclusión mutua, estos pasos se intercalan entre hilos y
varios estudiantes obtienen cupo con la misma lectura.
