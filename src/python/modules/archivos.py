import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bin')

def _bin_path(name):
    return os.path.abspath(os.path.join(BIN_DIR, name))

def listar_directorio(path='.'):
    path = os.path.abspath(path)
    try:
        entries = []
        with os.scandir(path) as it:
            for entry in it:
                try:
                    st = entry.stat()
                    entries.append({
                        'nombre': entry.name,
                        'ruta': entry.path,
                        'tipo': 'directorio' if entry.is_dir() else 'archivo',
                        'tamano': st.st_size,
                        'permisos': oct(st.st_mode)[-3:],
                        'modificado': st.st_mtime,
                    })
                except (PermissionError, OSError):
                    entries.append({
                        'nombre': entry.name,
                        'ruta': entry.path,
                        'tipo': '?',
                        'tamano': 0,
                        'permisos': '???',
                        'modificado': 0,
                    })
        entries.sort(key=lambda e: (e['tipo'] != 'directorio', e['nombre'].lower()))
        return entries
    except PermissionError:
        raise PermissionError(f"Permiso denegado: {path}")

def obtener_info(path):
    result = subprocess.run(
        [_bin_path('file_info'), path],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    lines = result.stdout.strip().split('\n')
    if len(lines) < 2:
        return None
    parts = lines[1].split('\t')
    if len(parts) >= 7:
        return {
            'ruta': parts[0],
            'tipo': parts[1],
            'tamano': int(parts[2]),
            'permisos': parts[3],
            'propietario': parts[4],
            'grupo': parts[5],
            'modificacion': parts[6],
        }
    return None

def copiar(origen, destino):
    result = subprocess.run(
        [_bin_path('file_ops'), 'copy', origen, destino],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

def mover(origen, destino):
    result = subprocess.run(
        [_bin_path('file_ops'), 'move', origen, destino],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

def eliminar(ruta):
    result = subprocess.run(
        [_bin_path('file_ops'), 'delete', ruta],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

def buscar(patron, directorio='.'):
    """Busca archivos que contengan el patrón en el nombre."""
    resultados = []
    directorio = os.path.abspath(directorio)
    for root, dirs, files in os.walk(directorio):
        for name in files + dirs:
            if patron.lower() in name.lower():
                try:
                    st = os.stat(os.path.join(root, name))
                    resultados.append({
                        'ruta': os.path.join(root, name),
                        'nombre': name,
                        'tamano': st.st_size,
                        'modificado': st.st_mtime,
                    })
                except (PermissionError, OSError):
                    pass
    return resultados

def estadisticas(directorio='.'):
    directorio = os.path.abspath(directorio)
    total_archivos = 0
    total_dirs = 0
    total_size = 0
    tamano_por_tipo = {}
    archivos_grandes = []
    errores = 0

    for root, dirs, files in os.walk(directorio):
        for d in dirs:
            total_dirs += 1
        for f in files:
            total_archivos += 1
            try:
                st = os.stat(os.path.join(root, f))
                total_size += st.st_size
                ext = os.path.splitext(f)[1].lower() or '(sin ext)'
                tamano_por_tipo[ext] = tamano_por_tipo.get(ext, 0) + st.st_size
                archivos_grandes.append((os.path.join(root, f), st.st_size))
            except (PermissionError, OSError):
                errores += 1

    archivos_grandes.sort(key=lambda x: -x[1])

    return {
        'directorio': directorio,
        'total_archivos': total_archivos,
        'total_dirs': total_dirs,
        'total_size': total_size,
        'tamano_por_tipo': dict(sorted(tamano_por_tipo.items(), key=lambda x: -x[1])),
        'archivos_grandes': archivos_grandes[:10],
        'errores': errores,
    }
