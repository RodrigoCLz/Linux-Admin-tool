# Linux Admin Tool

Herramienta de administración para Linux con interfaz gráfica (Tkinter) y binarios en C.

## Módulos

- **Procesos** — listar, buscar, matar y cambiar prioridad
- **Archivos** — navegador, copiar, mover, eliminar, buscar
- **Comandos** — ejecutar comandos con timeout e historial
- **Respaldos** — backup tar.gz, restaurar, historial
- **Bash** — análisis estático de scripts (funciones, variables, shellcheck)
- **Descargas** — descargas HTTP con pausa/reanudar y progreso

## Requisitos

- Python 3.8+
- GCC, Make
- Tkinter (`apt install python3-tk`)

## Instalación y uso

```bash
make build       # Compilar binarios C
make run         # Compilar + ejecutar GUI
```

## Estructura

```
src/c_bins/    → 5 binarios C (procfs, syscalls)
src/python/    → GUI tkinter + módulos lógicos
docs/          → documentación técnica y manual
```

## Entregables

- Código fuente completo
- Makefile funcional
- Documentación técnica
- Manual de usuario
- Repositorio Git
- Presentación final
