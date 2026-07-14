import subprocess
import os
import re
import json

def analizar_script(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    with open(ruta, 'r') as f:
        contenido = f.read()

    lines = contenido.split('\n')
    resultado = {
        'ruta': os.path.abspath(ruta),
        'tamano': os.path.getsize(ruta),
        'lineas_totales': len(lines),
        'lineas_vacias': sum(1 for l in lines if not l.strip()),
        'lineas_comentarios': sum(1 for l in lines if l.strip().startswith('#')),
        'funciones': [],
        'variables': [],
        'warnings': [],
        'shellcheck': None,
        'errores_sintaxis': [],
    }

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        m = re.match(r'^\s*function\s+(\w+)', stripped)
        if m:
            resultado['funciones'].append({'nombre': m.group(1), 'linea': i})
        m = re.match(r'^\s*(\w+)\s*\(\)\s*\{', stripped)
        if m:
            resultado['funciones'].append({'nombre': m.group(1), 'linea': i})

    var_set = set()
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\$\{?(\w+)\}?', line):
            if m.group(1) not in ('?', '0', '1', '2', '#', '*', '@', '-', '$', '!'):
                var_set.add(m.group(1))

    for i, line in enumerate(lines, 1):
        m = re.match(r'^\s*(\w+)=', line)
        if m and not line.strip().startswith('#'):
            resultado['variables'].append({'nombre': m.group(1), 'linea': i})

    # Check for common issues
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if '[[' in line or ']]' in line:
            pass  # modern bash is fine
        if re.search(r'`[^`]+`', line):
            resultado['warnings'].append({
                'linea': i,
                'tipo': 'backticks',
                'mensaje': 'Usar $(comando) en vez de backticks',
                'contenido': stripped[:80],
            })
        if re.search(r'\becho\s+\$', line) and not re.search(r'\becho\s+"', line):
            resultado['warnings'].append({
                'linea': i,
                'tipo': 'quoting',
                'mensaje': 'Variables sin comillas en echo (posible word splitting)',
                'contenido': stripped[:80],
            })
        if re.search(r'>\s*/dev/stderr', line):
            resultado['warnings'].append({
                'linea': i,
                'tipo': 'redirection',
                'mensaje': 'Usar >&2 en vez de > /dev/stderr',
                'contenido': stripped[:80],
            })

    # Try shellcheck if available
    try:
        result = subprocess.run(
            ['shellcheck', '--format=json', ruta],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode in (0, 1):
            try:
                resultado['shellcheck'] = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return resultado

def formatear_resultado(resultado):
    lines = []
    lines.append(f"=== Análisis de: {resultado['ruta']} ===")
    lines.append(f"Tamaño: {resultado['tamano']} bytes")
    lines.append(f"Líneas totales: {resultado['lineas_totales']}")
    lines.append(f"Líneas vacías: {resultado['lineas_vacias']}")
    lines.append(f"Líneas de comentarios: {resultado['lineas_comentarios']}")
    lines.append(f"Funciones encontradas: {len(resultado['funciones'])}")
    lines.append(f"Variables encontradas: {len(resultado['variables'])}")
    lines.append(f"Advertencias: {len(resultado['warnings'])}")

    if resultado['funciones']:
        lines.append("\n--- Funciones ---")
        for f in resultado['funciones']:
            lines.append(f"  Línea {f['linea']}: {f['nombre']}()")

    if resultado['warnings']:
        lines.append("\n--- Advertencias ---")
        for w in resultado['warnings']:
            lines.append(f"  Línea {w['linea']}: [{w['tipo']}] {w['mensaje']}")

    if resultado['shellcheck']:
        lines.append(f"\n--- ShellCheck ({len(resultado['shellcheck'])} problemas) ---")
        for s in resultado['shellcheck'][:20]:
            lines.append(f"  Línea {s.get('line', '?')}: [{s.get('level', '?')}] {s.get('message', '?')}")

    return '\n'.join(lines)
