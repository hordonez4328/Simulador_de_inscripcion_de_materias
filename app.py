"""
Punto de entrada principal para el Simulador de Inscripción y Portal Universitario.
Permite iniciar la aplicación Flask directamente desde la raíz del repositorio:
    python app.py
"""

import sys
import os
import importlib.util

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Cargar dinámicamente el módulo app.py de interfaz-web para evitar conflicto de nombres
WEB_APP_PATH = os.path.join(CURRENT_DIR, "interfaz-web", "app.py")
spec = importlib.util.spec_from_file_location("interfaz_web_app", WEB_APP_PATH)
interfaz_web_app = importlib.util.module_from_spec(spec)
sys.modules["interfaz_web_app"] = interfaz_web_app
spec.loader.exec_module(interfaz_web_app)

create_app = interfaz_web_app.create_app
app = create_app()

if __name__ == "__main__":
    print("=" * 70)
    print(" UNIVERSIDAD VIRTUAL - SIMULADOR DE INSCRIPCIÓN DE MATERIAS ")
    print("=" * 70)
    print(" Servidor web disponible en: http://127.0.0.1:5000")
    print(" Presione CTRL+C para detener el servidor.")
    print("=" * 70)
    app.run(host="127.0.0.1", port=5000, debug=True)
