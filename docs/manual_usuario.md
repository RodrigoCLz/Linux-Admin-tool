# Manual de Usuario - Linux Admin Tool

## 1. Requisitos del Sistema

- Sistema operativo Linux
- Python 3.8 o superior
- GCC (para compilar los binarios C)
- Make

## 2. Instalación

```bash
# 1. Clonar o copiar el proyecto
cd PS-proyect

# 2. Compilar los binarios C
make build

# 3. Instalar dependencias Python (opcional)
make install

# 4. Ejecutar la herramienta
make run

# O directamente:
python3 src/python/main.py
```

## 3. Interfaz Principal

Al iniciar, se abre una ventana con:

1. **Barra superior**: Botones para cada módulo (Procesos, Archivos, Comandos, Respaldos, Bash, Descargas)
2. **Área central**: Contenido del módulo seleccionado
3. **Barra de estado**: Mensajes informativos en la parte inferior

## 4. Módulo de Procesos

### Funcionalidades

- **Listar procesos**: Muestra PID, nombre, CPU%, memoria%, estado y usuario
- **Buscar**: Filtra procesos por nombre, PID o usuario
- **Matar proceso**: Seleccione un proceso y haga clic en "Matar"
- **Cambiar prioridad**: Seleccione un proceso y haga clic en "Prioridad"
- **Ver detalle**: Haga doble clic en un proceso para ver información detallada

### Uso

1. Seleccione el módulo "Procesos" en la barra superior
2. Espere a que se cargue la lista de procesos
3. Use el campo de búsqueda para filtrar
4. Seleccione un proceso y use los botones de acción

## 5. Módulo de Archivos

### Funcionalidades

- **Navegar**: Explore el sistema de archivos con doble clic en directorios
- **Subir**: Vuelva al directorio padre
- **Abrir**: Seleccione un directorio manualmente
- **Copiar**: Copie archivos seleccionados
- **Mover**: Mueva archivos a otra ubicación
- **Eliminar**: Borre archivos (con confirmación)
- **Buscar**: Encuentre archivos por nombre (patrón)

### Uso

1. Haga clic en "Archivos" en la barra superior
2. Navegue haciendo doble clic en los directorios
3. Seleccione un archivo y use los botones para copiar/mover/eliminar
4. Use "Buscar" para encontrar archivos por patrón

## 6. Módulo de Comandos

### Funcionalidades

- **Ejecutar comandos**: Ingrese cualquier comando del sistema
- **Timeout**: Configure un límite de tiempo (por defecto 30s)
- **Historial**: Vea y reutilice comandos anteriores
- **Salida**: Muestra stdout y stderr con código de retorno

### Uso

1. Vaya al módulo "Comandos"
2. Escriba un comando en el campo de texto
3. Ajuste el timeout si es necesario
4. Haga clic en "Ejecutar" o presione Enter
5. Vea la salida en el panel inferior

## 7. Módulo de Respaldos

### Funcionalidades

- **Nuevo respaldo**: Seleccione origen, destino y tipo (completo/incremental)
- **Historial**: Lista de respaldos realizados con fecha y tamaño
- **Restaurar**: Seleccione un respaldo y un destino para restaurarlo
- **Eliminar**: Borre respaldos del historial

### Uso

1. Vaya al módulo "Respaldos"
2. Configure origen y destino del respaldo
3. Seleccione tipo (Completo recomendado)
4. Haga clic en "Ejecutar Respaldo"
5. Espere la confirmación
6. Para restaurar, seleccione un respaldo de la lista y haga clic en "Restaurar"

## 8. Módulo de Análisis Bash

### Funcionalidades

- **Abrir script**: Cargue un archivo `.sh` para analizar
- **Analizar**: Procesa el script y muestra:
  - Estadísticas: líneas, funciones, variables
  - Advertencias de estilo y seguridad
  - Resultados de ShellCheck (si está instalado)

### Uso

1. Vaya al módulo "Bash"
2. Haga clic en "Abrir Script" y seleccione un archivo `.sh`
3. Haga clic en "Analizar"
4. Vea los resultados en el panel derecho

## 9. Módulo de Descargas

### Funcionalidades

- **Nueva descarga**: Ingrese una URL para descargar
- **Configurar destino**: Seleccione dónde guardar el archivo
- **Nombre personalizado**: Opcional, nombre para el archivo
- **Pausar/Reanudar**: Controle descargas en curso
- **Cancelar**: Detenga descargas activas
- **Historial**: Vea descargas anteriores

### Uso

1. Vaya al módulo "Descargas"
2. Ingrese la URL del archivo
3. Opcional: cambie destino o nombre
4. Haga clic en "Descargar"
5. Use los botones Pausar/Reanudar/Cancelar para controlar

## 10. Atajos y Consejos

- **Enter** en el campo de comandos ejecuta inmediatamente
- **Doble clic** en un directorio del explorador de archivos navega a él
- **Actualizar** recarga los datos del módulo actual
- Los respaldos se guardan como archivos `.tar.gz`

## 11. Solución de Problemas

| Problema | Solución |
|----------|----------|
| "Permiso denegado" en procesos | Ejecutar con `sudo` |
| ShellCheck no disponible | Instalar con `apt install shellcheck` |
| No se ven los binarios C | Ejecutar `make build` primero |
| Error de import tkinter | Instalar: `apt install python3-tk` |
