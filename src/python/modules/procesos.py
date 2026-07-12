import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bin')

def _bin_path(name):
    return os.path.abspath(os.path.join(BIN_DIR, name))

def listar_procesos():
    result = subprocess.run(
        [_bin_path('ps_list')],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error listando procesos: {result.stderr.strip()}")
    lines = result.stdout.strip().split('\n')
    if not lines:
        return []
    header = lines[0].split('\t')
    procesos = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 6:
            procesos.append({
                'pid': int(parts[0]),
                'nombre': parts[1],
                'cpu': float(parts[2]),
                'mem': float(parts[3]),
                'estado': parts[4],
                'usuario': parts[5],
            })
    return procesos

def matar_proceso(pid, signal=15):
    result = subprocess.run(
        [_bin_path('ps_kill'), str(pid), str(signal)],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

def cambiar_prioridad(pid, nice_val):
    result = subprocess.run(
        [_bin_path('ps_nice'), str(pid), str(nice_val)],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

if __name__ == '__main__':
    procs = listar_procesos()
    for p in procs[:10]:
        print(f"{p['pid']:>7} {p['nombre']:20} CPU:{p['cpu']:6.1f}% MEM:{p['mem']:6.1f}% {p['estado']} {p['usuario']}")
