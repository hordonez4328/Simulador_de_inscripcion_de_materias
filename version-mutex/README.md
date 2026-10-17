# Versión Protegida con Mutex (Lock)

## Responsable
- **Integrante 2**: Implementación y análisis de la versión protegida con exclusión mutua mediante Mutex (`threading.Lock`).

## Objetivo Académico
Demostrar cómo la primitiva de sincronización **Mutex** elimina la condición de carrera al asegurar que la lectura, verificación, decremento y registro se ejecuten como una única **operación indivisible (atómica)**.

## Sección Crítica
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

### Características Clave
- **Atómica e Indivisible:** Solo un hilo ingresa a la sección crítica en un instante determinado.
- **Sin retención indebida:** La pausa artificial no se retiene dentro del bloqueo para evitar degradar el rendimiento innecesariamente.
- **Manejo seguro de excepciones:** El bloque `with` garantiza que el cerrojo siempre sea liberado.
- **Resultado garantizado:** Inscritos <= Cupos iniciales, y cupos finales nunca son negativos.

## Ejecución desde Terminal
```powershell
python version-mutex/main.py
```
