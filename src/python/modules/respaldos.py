import subprocess
import os
import json
import datetime
import shutil

RESPALDOS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'respaldos')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config_respaldos.json')
HISTORIAL_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'historial_respaldos.json')

os.makedirs(RESPALDOS_DIR, exist_ok=True)

def _cargar_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default

def _guardar_json(path, data):
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass

def _generar_nombre_backup(origen):
    base = os.path.basename(os.path.normpath(origen)) or 'backup'
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base}_{ts}.tar.gz"

def ejecutar_respaldo(origen, destino=None, tipo='completo'):
    origen = os.path.abspath(origen)
    if not os.path.exists(origen):
        raise FileNotFoundError(f"Origen no existe: {origen}")

    if destino is None:
        destino = RESPALDOS_DIR

    os.makedirs(destino, exist_ok=True)

    nombre = _generar_nombre_backup(origen)
    ruta_destino = os.path.join(destino, nombre)

    if tipo == 'completo':
        result = subprocess.run(
            ['tar', '-czf', ruta_destino, '-C', os.path.dirname(origen), os.path.basename(origen)],
            capture_output=True, text=True, timeout=300
        )
    else:
        result = subprocess.run(
            ['tar', '-czf', ruta_destino, '-C', os.path.dirname(origen), os.path.basename(origen)],
            capture_output=True, text=True, timeout=300
        )

    if result.returncode != 0:
        raise RuntimeError(f"Error en respaldo: {result.stderr.strip()}")

    st = os.stat(ruta_destino)
    info = {
        'nombre': nombre,
        'origen': origen,
        'destino': ruta_destino,
        'tamano': st.st_size,
        'tipo': tipo,
        'fecha': datetime.datetime.now().isoformat(),
        'estado': 'completado',
    }

    hist = _cargar_json(HISTORIAL_FILE, [])
    hist.append(info)
    _guardar_json(HISTORIAL_FILE, hist)

    return info

def listar_respaldos():
    return _cargar_json(HISTORIAL_FILE, [])

def restaurar_respaldo(nombre_respaldo, destino_extract=None):
    respaldos = listar_respaldos()
    info = None
    for r in respaldos:
        if r['nombre'] == nombre_respaldo:
            info = r
            break
    if not info:
        raise FileNotFoundError(f"Respaldo no encontrado: {nombre_respaldo}")

    ruta = info['destino']
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo de respaldo no existe: {ruta}")

    if destino_extract is None:
        destino_extract = os.path.dirname(ruta)

    os.makedirs(destino_extract, exist_ok=True)

    result = subprocess.run(
        ['tar', '-xzf', ruta, '-C', destino_extract],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error en restauración: {result.stderr.strip()}")

    return f"Restaurado {nombre_respaldo} en {destino_extract}"

def eliminar_respaldo(nombre_respaldo):
    respaldos = listar_respaldos()
    nuevos = []
    eliminado = False
    for r in respaldos:
        if r['nombre'] == nombre_respaldo:
            if os.path.exists(r['destino']):
                os.remove(r['destino'])
            eliminado = True
        else:
            nuevos.append(r)

    if not eliminado:
        raise FileNotFoundError(f"Respaldo no encontrado: {nombre_respaldo}")

    _guardar_json(HISTORIAL_FILE, nuevos)
    return f"Respaldo eliminado: {nombre_respaldo}"

def guardar_configuracion(config):
    _guardar_json(CONFIG_FILE, config)

def cargar_configuracion():
    return _cargar_json(CONFIG_FILE, {'origen': '', 'destino': RESPALDOS_DIR, 'tipo': 'completo'})
