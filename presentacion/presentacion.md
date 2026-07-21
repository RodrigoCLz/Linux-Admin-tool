# 🐧 Linux Admin Tool
### Herramienta de Administración para Linux

---

## Integrantes

- _[Nombre del equipo]_

---

## ¿Qué es?

Herramienta gráfica que integra 6 módulos de administración:

| Módulo | Función |
|--------|---------|
| ⚙ Procesos | Monitoreo y control de procesos |
| 📁 Archivos | Gestión del sistema de archivos |
| ⌨ Comandos | Ejecución de comandos del sistema |
| 💾 Respaldos | Backup y restauración automática |
| 📜 Bash | Análisis estático de scripts |
| ⬇ Descargas | Gestor de descargas HTTP |

---

## Arquitectura

```
┌──────────────────┐
│   GUI Tkinter    │  ← 6 frames modulares
├──────────────────┤
│  Módulos Python  │  ← Lógica de negocio
├──────────────────┤
│  Binarios C      │  ← Syscalls Linux
└──────────────────┘
```

**Hybrid approach**: C para operaciones de sistema, Python para lógica e interfaz.

---

## Módulo: Procesos

- Lectura de `/proc/` en C para listar procesos
- Cálculo de CPU% con dos muestras (100ms)
- Matar procesos con señales POSIX
- Cambiar prioridad (nice -20 a 19)

✨ **Tecnología**: Lectura directa de procfs + syscalls `kill()` y `setpriority()`

---

## Módulo: Archivos

- Navegador de directorios con Treeview
- Operaciones: copiar, mover, eliminar
- Búsqueda por patrón recursiva
- Binarios C para operaciones de bajo nivel

✨ **Tecnología**: `stat()`, `open()`, `read()`/`write()` con buffer de 64KB

---

## Módulo: Comandos

- Shell interactivo dentro de la GUI
- Timeout configurable
- Historial persistente (JSON)
- Separación de stdout/stderr

✨ **Tecnología**: `subprocess.run()` con `shell=True`

---

## Módulo: Respaldos

- Compresión tar.gz
- Restauración con un clic
- Historial de respaldos
- Configuración persistente

✨ **Tecnología**: `tar` via subprocess + JSON para metadata

---

## Módulo: Análisis Bash

- Conteo de líneas, funciones y variables
- Detección de malas prácticas (backticks, quoting)
- Integración con ShellCheck
- Vista partida: código + resultados

✨ **Tecnología**: Regex + subprocess (shellcheck)

---

## Módulo: Descargas

- Descargas HTTP con urllib
- Múltiples descargas simultáneas (threading)
- Pausar / Reanudar / Cancelar
- Velocidad y progreso en tiempo real
- Historial persistente

✨ **Tecnología**: `urllib.request` + `threading`

---

## Makefile

```makefile
make build      # Compilar binarios C
make install    # pip install -r requirements.txt
make run        # Compilar + ejecutar
make clean      # Limpiar compilados
```

---

## Demo

1. Compilar: `make build`
2. Ejecutar: `make run`
3. Probar cada módulo

---

## Conclusiones

- ✅ Integración C + Python funcional
- ✅ Interfaz gráfica completa con 6 módulos
- ✅ Makefile para automatización
- ✅ Persistencia de datos (JSON)
- ✅ Código modular y extensible

---

## Preguntas

🙋‍♂️ ¿Preguntas?
