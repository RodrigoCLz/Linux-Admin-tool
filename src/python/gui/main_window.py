import tkinter as tk
from tkinter import ttk, messagebox
import os
from gui.procesos_frame import ProcesosFrame
from gui.archivos_frame import ArchivosFrame
from gui.comandos_frame import ComandosFrame
from gui.respaldos_frame import RespaldosFrame
from gui.bash_frame import BashFrame
from gui.descargas_frame import DescargasFrame


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Linux Admin Tool")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        try:
            self.root.iconbitmap(default='')
        except Exception:
            pass

        self._configure_styles()

        self.current_frame = None
        self.frames = {}
        self.status_bar = None

        self._build_header()
        self._build_content()
        self._build_status_bar()

        self.mostrar_modulo('procesos')

        self.root.protocol("WM_DELETE_WINDOW", self._salir)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Header.TFrame', background='#2c3e50')
        style.configure('Header.TLabel', background='#2c3e50', foreground='white',
                        font=('Helvetica', 16, 'bold'))
        style.configure('Module.TButton', font=('Helvetica', 10), padding=8)
        style.configure('Status.TLabel', background='#34495e', foreground='white',
                        font=('Helvetica', 9))
        style.configure('Content.TFrame', background='#ecf0f1')

    def _build_header(self):
        header = ttk.Frame(self.root, style='Header.TFrame')
        header.pack(fill=tk.X, side=tk.TOP)

        logo_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logo_unsa.png')
        try:
            logo_img = tk.PhotoImage(file=logo_path)
            logo_label = ttk.Label(header, image=logo_img, style='Header.TLabel')
            logo_label.image = logo_img
            logo_label.pack(side=tk.LEFT, padx=(10, 2), pady=5)
        except Exception:
            pass

        ttk.Label(header, text=" Linux Admin Tool", style='Header.TLabel').pack(
            side=tk.LEFT, padx=(2, 15), pady=10)

        modulos = [
            ('procesos', '⚙ Procesos'),
            ('archivos', '📁 Archivos'),
            ('comandos', '⌨ Comandos'),
            ('respaldos', '💾 Respaldos'),
            ('bash', '📜 Bash'),
            ('descargas', '⬇ Descargas'),
        ]

        btn_frame = ttk.Frame(header, style='Header.TFrame')
        btn_frame.pack(side=tk.RIGHT, padx=10)

        for key, label in modulos:
            btn = ttk.Button(btn_frame, text=label, style='Module.TButton',
                             command=lambda k=key: self.mostrar_modulo(k))
            btn.pack(side=tk.LEFT, padx=3, pady=5)

    def _build_content(self):
        self.content = ttk.Frame(self.root, style='Content.TFrame')
        self.content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _build_status_bar(self):
        self.status_bar = ttk.Frame(self.root, style='Status.TLabel')
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = ttk.Label(self.status_bar, text="Listo",
                                      style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=3)

    def set_status(self, msg):
        self.status_label.config(text=msg[:120])

    def mostrar_modulo(self, modulo):
        if self.current_frame:
            self.current_frame.pack_forget()

        if modulo not in self.frames:
            frame_class = {
                'procesos': ProcesosFrame,
                'archivos': ArchivosFrame,
                'comandos': ComandosFrame,
                'respaldos': RespaldosFrame,
                'bash': BashFrame,
                'descargas': DescargasFrame,
            }
            self.frames[modulo] = frame_class[modulo](self.content, self)

        self.current_frame = self.frames[modulo]
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.set_status(f"Módulo: {modulo.capitalize()}")

    def _salir(self):
        if messagebox.askokcancel("Salir", "¿Desea salir de Linux Admin Tool?"):
            self.root.destroy()

    def run(self):
        self.root.mainloop()
