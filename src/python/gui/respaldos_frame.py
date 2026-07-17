import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from modules import respaldos as backup_mod


class RespaldosFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()
        self.actualizar_lista()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        ttk.Label(top, text="Respaldos Automáticos",
                  font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        ttk.Button(top, text="🔄 Actualizar", command=self.actualizar_lista).pack(side=tk.RIGHT, padx=2)

        # Left panel - create backup
        left = ttk.LabelFrame(self, text="Nuevo Respaldo")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        f = ttk.Frame(left)
        f.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(f, text="Origen:").pack(side=tk.LEFT)
        self.origen_var = tk.StringVar(value=os.path.expanduser('~'))
        ttk.Entry(f, textvariable=self.origen_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(f, text="📂", command=lambda: self._seleccionar('origen')).pack(side=tk.LEFT)

        f = ttk.Frame(left)
        f.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(f, text="Destino:").pack(side=tk.LEFT)
        self.destino_var = tk.StringVar(value=os.path.join(os.path.dirname(__file__), '..', '..', '..', 'respaldos'))
        ttk.Entry(f, textvariable=self.destino_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(f, text="📂", command=lambda: self._seleccionar('destino')).pack(side=tk.LEFT)

        f = ttk.Frame(left)
        f.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(f, text="Tipo:").pack(side=tk.LEFT)
        self.tipo_var = tk.StringVar(value='completo')
        ttk.Radiobutton(f, text="Completo", variable=self.tipo_var, value='completo').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(f, text="Incremental", variable=self.tipo_var, value='incremental').pack(side=tk.LEFT, padx=5)

        ttk.Button(left, text="💾 Ejecutar Respaldo", command=self.ejecutar_respaldo_thread).pack(pady=10)

        # Right panel - backup list
        right = ttk.LabelFrame(self, text="Historial de Respaldos")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('nombre', 'fecha', 'tamano', 'tipo')
        self.tree = ttk.Treeview(right, columns=columns, show='headings', height=15)
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('tamano', text='Tamaño')
        self.tree.heading('tipo', text='Tipo')
        self.tree.column('nombre', width=200)
        self.tree.column('fecha', width=150)
        self.tree.column('tamano', width=80)
        self.tree.column('tipo', width=80)

        scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="↩ Restaurar", command=self.restaurar).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑 Eliminar", command=self.eliminar_respaldo).pack(side=tk.LEFT, padx=2)

    def _seleccionar(self, tipo):
        if tipo == 'origen':
            ruta = filedialog.askdirectory(initialdir=self.origen_var.get())
            if ruta:
                self.origen_var.set(ruta)
        else:
            ruta = filedialog.askdirectory(initialdir=self.destino_var.get())
            if ruta:
                self.destino_var.set(ruta)

    @property
    def root(self):
        return self.winfo_toplevel()

    def ejecutar_respaldo_thread(self):
        origen = self.origen_var.get().strip()
        destino = self.destino_var.get().strip()
        tipo = self.tipo_var.get()

        if not origen or not os.path.exists(origen):
            messagebox.showerror("Error", "El origen no existe")
            return

        self.app.set_status(f"Ejecutando respaldo de {origen}...")

        def run():
            try:
                info = backup_mod.ejecutar_respaldo(origen, destino, tipo)
                self.root.after(0, lambda: self._respaldo_completado(info))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _respaldo_completado(self, info):
        self._format_size = lambda s: f"{s/1024/1024:.1f} MB" if s > 1024*1024 else f"{s/1024:.1f} KB"
        msg = (f"Respaldo completado:\n{info['nombre']}\n"
               f"Tamaño: {self._format_size(info['tamano'])}")
        messagebox.showinfo("Éxito", msg)
        self.app.set_status(f"Respaldo completado: {info['nombre']}")
        self.actualizar_lista()

    def actualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            respaldos = backup_mod.listar_respaldos()
            for r in respaldos:
                fecha = r.get('fecha', '')[:19]
                tamano = r.get('tamano', 0)
                size_str = f"{tamano/1024/1024:.1f} MB" if tamano > 1024*1024 else f"{tamano/1024:.1f} KB"
                self.tree.insert('', tk.END, values=(
                    r['nombre'], fecha, size_str, r.get('tipo', 'completo')
                ))
        except Exception as e:
            self.app.set_status(f"Error cargando respaldos: {str(e)}")

    def restaurar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un respaldo")
            return
        item = self.tree.item(sel[0])
        nombre = item['values'][0]

        destino = filedialog.askdirectory(title="Seleccionar destino para restaurar")
        if not destino:
            return

        def run():
            try:
                msg = backup_mod.restaurar_respaldo(nombre, destino)
                self.root.after(0, lambda: messagebox.showinfo("Éxito", msg))
                self.root.after(0, lambda: self.app.set_status(msg))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        t = threading.Thread(target=run, daemon=True)
        t.start()

    def eliminar_respaldo(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un respaldo")
            return
        item = self.tree.item(sel[0])
        nombre = item['values'][0]

        if messagebox.askyesno("Confirmar", f"¿Eliminar respaldo '{nombre}'?"):
            try:
                msg = backup_mod.eliminar_respaldo(nombre)
                self.app.set_status(msg)
                self.actualizar_lista()
            except Exception as e:
                messagebox.showerror("Error", str(e))



