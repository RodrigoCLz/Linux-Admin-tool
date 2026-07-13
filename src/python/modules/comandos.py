import subprocess
import shlex
import os
import json
import datetime

HISTORIAL_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'historial_comandos.json')

def _cargar_historial():
    try:
        if os.path.exists(HISTORIAL_FILE):
            with open(HISTORIAL_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []

def _guardar_historial(historial):
    try:
        with open(HISTORIAL_FILE, 'w') as f:
            json.dump(historial[-100:], f, indent=2)
    except IOError:
        pass

def ejecutar(comando, timeout=30):
    if not comando or not comando.strip():
        raise ValueError("Comando vacío")

    try:
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        salida = {
            'codigo': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'comando': comando,
            'timestamp': datetime.datetime.now().isoformat(),
        }

        hist = _cargar_historial()
        hist.append({'comando': comando, 'codigo': result.returncode, 'timestamp': salida['timestamp']})
        _guardar_historial(hist)

        return salida
    except subprocess.TimeoutExpired:
        return {
            'codigo': -1,
            'stdout': '',
            'stderr': f"ERROR: Timeout de {timeout}s excedido",
            'comando': comando,
            'timestamp': datetime.datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            'codigo': -1,
            'stdout': '',
            'stderr': f"ERROR: {str(e)}",
            'comando': comando,
            'timestamp': datetime.datetime.now().isoformat(),
        }

def obtener_historial():
    return _cargar_historial()

def limpiar_historial():
    _guardar_historial([])
    return "Historial limpiado"
