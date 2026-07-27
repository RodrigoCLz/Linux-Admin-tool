import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import subprocess
from modules import descargas as dl_mod


class DescargasFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.descargas = []
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        ttk.Label(top, text="Descargas",
                  font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        ttk.Button(top, text="📋 Historial", command=self.mostrar_historial).pack(side=tk.RIGHT, padx=2)
        ttk.Button(top, text="🧹 Limpiar completadas", command=self.limpiar_completadas).pack(side=tk.RIGHT, padx=2)

        # URL input
        url_frame = ttk.LabelFrame(self, text="Nueva descarga")
        url_frame.pack(fill=tk.X, padx=10, pady=5)

        f = ttk.Frame(url_frame)
        f.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(f, text="URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.url_var, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(f, text="⬇ Descargar", command=self.iniciar_descarga).pack(side=tk.LEFT, padx=5)

        f2 = ttk.Frame(url_frame)
        f2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(f2, text="Destino:").pack(side=tk.LEFT)
        self.destino_var = tk.StringVar(value=os.path.join(os.path.dirname(__file__), '..', '..', '..', 'descargas'))
        ttk.Entry(f2, textvariable=self.destino_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(f2, text="📂", command=lambda: self._seleccionar_destino()).pack(side=tk.LEFT)

        ttk.Label(f2, text="Nombre:").pack(side=tk.LEFT, padx=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(f2, textvariable=self.nombre_var, width=20).pack(side=tk.LEFT, padx=5)

        # Active downloads list
        list_frame = ttk.LabelFrame(self, text="Descargas activas")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('nombre', 'progreso', 'velocidad', 'estado', 'tamano')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('progreso', text='Progreso')
        self.tree.heading('velocidad', text='Velocidad')
        self.tree.heading('estado', text='Estado')
        self.tree.heading('tamano', text='Tamaño')
        self.tree.column('nombre', width=250)
        self.tree.column('progreso', width=100, anchor='center')
        self.tree.column('velocidad', width=100, anchor='center')
        self.tree.column('estado', width=120, anchor='center')
        self.tree.column('tamano', width=120, anchor='center')

        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="⏸ Pausar", command=self.pausar_descarga).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="▶ Reanudar", command=self.reanudar_descarga).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✖ Cancelar", command=self.cancelar_descarga).pack(side=tk.LEFT, padx=2)

        self._update_loop()

    def _seleccionar_destino(self):
        ruta = filedialog.askdirectory(initialdir=self.destino_var.get())
        if ruta:
            self.destino_var.set(ruta)

    @property
    def root(self):
        return self.winfo_toplevel()

    def iniciar_descarga(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL", "Ingrese una URL")
            return

        destino = self.destino_var.get().strip() or None
        nombre = self.nombre_var.get().strip() or None

        def on_update(dl):
            self.root.after(0, self._refrescar_tabla)
            if dl.estado == 'completado':
                self.root.after(0, lambda: self._notificar_descarga(dl))

        dl = dl_mod.nueva_descarga(url, destino, nombre, callback=on_update)
        self.app.set_status(f"Descargando: {dl.nombre}")
        self.url_var.set('')
        self.nombre_var.set('')

    def _notificar_descarga(self, dl):
        try:
            subprocess.run(['notify-send', 'Linux Admin Tool',
                            f'Descarga completada: {dl.nombre}',
                            '--icon=dialog-information'], timeout=5)
        except FileNotFoundError:
            pass
        self.app.set_status(f"Descarga completada: {dl.nombre}")

    def _refrescar_tabla(self):
        self.descargas = dl_mod.listar_descargas_activas()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for d in self.descargas:
            size_str = self._format_size(d.tamano_total) if d.tamano_total > 0 else "?"
            speed_str = f"{self._format_size(int(d.velocidad))}/s" if d.velocidad > 0 else ""
            self.tree.insert('', tk.END, values=(
                d.nombre, f"{d.progreso:.1f}%", speed_str,
                d.estado.capitalize(), size_str
            ))

    def _update_loop(self):
        self._refrescar_tabla()
        self.after(1000, self._update_loop)

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def pausar_descarga(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if idx < len(self.descargas):
            self.descargas[idx].pausar()
            self.app.set_status(f"Pausado: {self.descargas[idx].nombre}")

    def reanudar_descarga(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if idx < len(self.descargas):
            self.descargas[idx].reanudar()
            self.app.set_status(f"Reanudado: {self.descargas[idx].nombre}")

    def cancelar_descarga(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if idx < len(self.descargas):
            self.descargas[idx].cancelar()
            self.app.set_status(f"Cancelado: {self.descargas[idx].nombre}")

    def mostrar_historial(self):
        hist = dl_mod.listar_historial()
        if not hist:
            messagebox.showinfo("Historial", "No hay descargas en el historial")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Historial de descargas")
        dialog.geometry("700x400")
        dialog.transient(self.root)

        columns = ('nombre', 'estado', 'tamano', 'fecha')
        tree = ttk.Treeview(dialog, columns=columns, show='headings', height=20)
        tree.heading('nombre', text='Nombre')
        tree.heading('estado', text='Estado')
        tree.heading('tamano', text='Tamaño')
        tree.heading('fecha', text='Fecha')
        tree.column('nombre', width=250)
        tree.column('estado', width=100)
        tree.column('tamano', width=100)
        tree.column('fecha', width=200)

        for h in reversed(hist[-100:]):
            ts = h.get('fin') or h.get('inicio') or ''
            ts = ts[:19] if ts else ''
            size = h.get('tamano_total', 0)
            size_str = self._format_size(size) if size else '?'
            tree.insert('', tk.END, values=(h['nombre'], h['estado'], size_str, ts))

        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def limpiar_completadas(self):
        self.descargas = [d for d in self.descargas if d.estado in ('descargando', 'pausado')]
        self._refrescar_tabla()
        self.app.set_status("Descargas completadas eliminadas de la lista")
