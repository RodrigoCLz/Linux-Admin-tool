import tkinter as tk
from tkinter import ttk, messagebox
import threading
from modules import procesos as proc_mod


class ProcesosFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.procesos = []

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        ttk.Label(top, text="Gestión de Procesos",
                  font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        btn_frame = ttk.Frame(top)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="🔄 Actualizar", command=self.cargar_datos_thread).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✖ Matar", command=self.matar_proceso).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🎯 Prioridad", command=self.cambiar_prioridad).pack(side=tk.LEFT, padx=2)

        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', lambda *a: self._filtrar())
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=30).pack(side=tk.LEFT, padx=5)

        columns = ('pid', 'nombre', 'cpu', 'mem', 'estado', 'usuario')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=20)

        headings = {'pid': 'PID', 'nombre': 'Nombre', 'cpu': 'CPU %',
                    'mem': 'Mem %', 'estado': 'Estado', 'usuario': 'Usuario'}
        widths = {'pid': 80, 'nombre': 250, 'cpu': 80, 'mem': 80, 'estado': 80, 'usuario': 100}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor='center' if col != 'nombre' else 'w')

        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.tree.bind('<Double-1>', lambda e: self.mostrar_detalle())

    def cargar_datos_thread(self):
        self.app.set_status("Cargando procesos...")
        t = threading.Thread(target=self.cargar_datos, daemon=True)
        t.start()

    def cargar_datos(self):
        try:
            self.procesos = proc_mod.listar_procesos()
            self.root.after(0, self._mostrar_datos)
        except Exception as e:
            self.root.after(0, lambda: self.app.set_status(f"Error: {str(e)}"))

    @property
    def root(self):
        return self.winfo_toplevel()

    def _mostrar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.procesos:
            self.tree.insert('', tk.END, values=(
                p['pid'], p['nombre'], f"{p['cpu']:.1f}", f"{p['mem']:.1f}",
                p['estado'], p['usuario']
            ))
        self.app.set_status(f"Procesos: {len(self.procesos)} cargados")

    def _filtrar(self):
        filtro = self.filter_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.procesos:
            if filtro in p['nombre'].lower() or filtro in str(p['pid']) or filtro in p['usuario'].lower():
                self.tree.insert('', tk.END, values=(
                    p['pid'], p['nombre'], f"{p['cpu']:.1f}", f"{p['mem']:.1f}",
                    p['estado'], p['usuario']
                ))

    def matar_proceso(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un proceso primero")
            return
        item = self.tree.item(sel[0])
        pid = item['values'][0]
        nombre = item['values'][1]
        if messagebox.askyesno("Confirmar", f"¿Matar proceso {nombre} (PID {pid})?"):
            try:
                msg = proc_mod.matar_proceso(pid)
                self.app.set_status(msg)
                self.cargar_datos_thread()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def cambiar_prioridad(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un proceso primero")
            return
        item = self.tree.item(sel[0])
        pid = item['values'][0]
        nombre = item['values'][1]

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Prioridad - {nombre}")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text=f"PID: {pid} ({nombre})", font=('Helvetica', 10, 'bold')).pack(pady=10)
        ttk.Label(dialog, text="Nuevo valor nice (-20 a 19):").pack()
        var = tk.IntVar(value=0)
        ttk.Entry(dialog, textvariable=var, width=10).pack(pady=5)

        def aplicar():
            try:
                msg = proc_mod.cambiar_prioridad(pid, var.get())
                self.app.set_status(msg)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Aplicar", command=aplicar).pack(pady=10)

    def mostrar_detalle(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        vals = item['values']
        msg = (f"PID: {vals[0]}\nNombre: {vals[1]}\nCPU: {vals[2]}%\n"
               f"Mem: {vals[3]}%\nEstado: {vals[4]}\nUsuario: {vals[5]}")
        messagebox.showinfo("Detalle del Proceso", msg)
