# Documentación Técnica - Linux Admin Tool

## 1. Introducción

Linux Admin Tool es una herramienta de administración para sistemas Linux que integra seis módulos principales: gestión de procesos, gestión de archivos, ejecución de comandos, respaldos automáticos, análisis de scripts Bash y gestor de descargas.

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────┐
│                    GUI (Tkinter)                     │
│  main_window.py + 6 frames (procesos, archivos...)  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│              Módulos Python (capa lógica)            │
│  procesos.py  archivos.py  comandos.py  respaldos.py │
│  bash_analysis.py  descargas.py                      │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
┌──────────┴──────────┐  ┌───────┴───────────────────┐
│  Binarios C (sistema) │  │  Librerías Python stdlib │
│  ps_list  ps_kill     │  │  subprocess  os  shutil  │
│  ps_nice  file_info   │  │  threading  json  tar    │
│  file_ops             │  │  urllib.request          │
└──────────────────────┘  └──────────────────────────┘
```

### 2.1 Capas

- **Capa 1 - Binarios C**: Operaciones de sistema que requieren acceso directo a syscalls de Linux (lectura de `/proc`, signals, syscalls de archivos).
- **Capa 2 - Módulos Python**: Lógica de aplicación que orquesta los binarios C y las librerías estándar.
- **Capa 3 - GUI Tkinter**: Interfaz gráfica con 6 frames independientes.

## 3. Módulo de Procesos

### 3.1 Binario C: `ps_list`

Lee `/proc/[pid]/stat`, `/proc/[pid]/status` y `/proc/stat` para obtener información de procesos.

**Formato de salida**: `PID\tNOMBRE\tCPU_PCT\tMEM_PCT\tESTADO\tUSUARIO`

**Algoritmo de CPU%**:
1. Lee `utime` y `stime` de `/proc/[pid]/stat` (jiffies de usuario y kernel)
2. Lee suma total de jiffies de `/proc/stat`
3. Espera 100ms
4. Repite lecturas
5. CPU% = 100 × (proc_delta) / (total_delta)

### 3.2 Binario C: `ps_kill`

Envía señales a procesos usando `kill()`. Soporta SIGTERM (15) por defecto.

### 3.3 Binario C: `ps_nice`

Cambia prioridad de proceso usando `setpriority()`. Rango -20 a 19.

## 4. Módulo de Archivos

### 4.1 Binario C: `file_info`

Usa `lstat()` para obtener metadatos de archivos. Lee UID/GID y los resuelve a nombres mediante `getpwuid()`/`getgrgid()`.

### 4.2 Binario C: `file_ops`

- **copy**: `open()` + `read()`/`write()` con buffer de 64KB
- **move**: `rename()` con fallback a copiar+borrar si cruza sistemas de archivos (`EXDEV`)
- **delete**: `remove()`

## 5. Módulo de Comandos

Implementado en Python con `subprocess.run()`. Soporta:
- Ejecución síncrona con timeout configurable
- Captura de stdout/stderr por separado
- Historial persistente en JSON (últimos 100 comandos)

## 6. Módulo de Respaldos

Usa `tar` + `gzip` via `subprocess` para crear respaldos comprimidos.
- Respaldo completo: `tar -czf backup.tar.gz origen`
- Restauración: `tar -xzf backup.tar.gz -C destino`
- Historial persistente en `historial_respaldos.json`

## 7. Módulo de Análisis Bash

Análisis estático de scripts Bash:
- Conteo de líneas, funciones (regex: `function name` y `name()`)
- Detección de variables con `$VAR` y `$[VAR}`
- Advertencias: backticks, variables sin comillas, redirecciones
- Integración con `shellcheck` si está disponible

## 8. Módulo de Descargas

Descarga de archivos vía HTTP con `urllib.request`:
- Hilos separados por descarga (daemon)
- Soporte de pausa/reanudación
- Barra de progreso basada en Content-Length
- Historial persistente en JSON

## 9. Estructura del Proyecto

```
PS-proyect/
├── Makefile                    # Automatización de compilación y tareas
├── requirements.txt            # Dependencias Python
├── src/
│   ├── c_bins/                 # Código fuente C
│   │   ├── ps_list.c
│   │   ├── ps_kill.c
│   │   ├── ps_nice.c
│   │   ├── file_info.c
│   │   └── file_ops.c
│   └── python/
│       ├── main.py             # Punto de entrada
│       ├── gui/                # Interfaces gráficas
│       │   ├── main_window.py
│       │   ├── procesos_frame.py
│       │   ├── archivos_frame.py
│       │   ├── comandos_frame.py
│       │   ├── respaldos_frame.py
│       │   ├── bash_frame.py
│       │   └── descargas_frame.py
│       └── modules/            # Lógica de negocio
│           ├── procesos.py
│           ├── archivos.py
│           ├── comandos.py
│           ├── respaldos.py
│           ├── bash_analysis.py
│           └── descargas.py
├── bin/                        # Binarios compilados (generado)
├── docs/
│   ├── documentacion_tecnica.md
│   └── manual_usuario.md
└── presentacion/
    └── presentacion.md
```

## 10. Compilación y Ejecución

```bash
make build      # Compilar binarios C
make install    # Instalar dependencias Python
make run        # Compilar + ejecutar
make clean      # Limpiar archivos compilados
```

## 11. Dependencias

- Python 3.8+
- Tkinter (incluido en Python)
- psutil (opcional, para respaldo)
- requests (opcional)
- gcc (para compilar binarios C)
- make
