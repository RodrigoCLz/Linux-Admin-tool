#!/usr/bin/env python3
"""
Linux Admin Tool v1.0
Herramienta de administración para Linux que integra monitoreo de procesos,
gestión de archivos, respaldo automático, ejecución de comandos y
análisis de scripts Bash.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    app = MainWindow()
    app.run()


if __name__ == '__main__':
    main()
