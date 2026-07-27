import tkinter as tk
from tkinter import ttk, messagebox
import threading
from modules import procesos as proc_mod


class ProcesosFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.procesos = []
        self.vista_arbol = False

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
        ttk.Button(btn_frame, text="⏸ Suspender", command=self.suspender_proceso).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="▶ Reanudar", command=self.reanudar_proceso).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🎯 Prioridad", command=self.cambiar_prioridad).pack(side=tk.LEFT, padx=2)
        self.arbol_btn = ttk.Button(btn_frame, text="🌳 Árbol", command=self.toggle_vista)
        self.arbol_btn.pack(side=tk.LEFT, padx=2)

        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', lambda *a: self._filtrar())
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=30).pack(side=tk.LEFT, padx=5)

        columns = ('pid', 'nombre', 'cpu', 'mem', 'estado', 'usuario')
        self.tree = ttk.Treeview(self, columns=columns, show='tree headings', height=20)

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
        if self.vista_arbol:
            self._mostrar_arbol()
        else:
            self._mostrar_lista()
        self.app.set_status(f"Procesos: {len(self.procesos)} cargados")

    def _mostrar_lista(self):
        for p in self.procesos:
            self.tree.insert('', tk.END, values=(
                p['pid'], p['nombre'], f"{p['cpu']:.1f}", f"{p['mem']:.1f}",
                p['estado'], p['usuario']
            ))

    def _mostrar_arbol(self):
        hijos = {}
        for p in self.procesos:
            ppid = p['ppid']
            if ppid not in hijos:
                hijos[ppid] = []
            hijos[ppid].append(p)

        def insertar_hijos(parent_id, ppid):
            for p in hijos.get(ppid, []):
                pid = p['pid']
                node_id = self.tree.insert(parent_id, tk.END, values=(
                    pid, p['nombre'], f"{p['cpu']:.1f}", f"{p['mem']:.1f}",
                    p['estado'], p['usuario']
                ))
                insertar_hijos(node_id, pid)

        insertar_hijos('', 0)

    def _filtrar(self):
        filtro = self.filter_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.vista_arbol:
            self._mostrar_arbol_filtrado(filtro)
        else:
            for p in self.procesos:
                if filtro in p['nombre'].lower() or filtro in str(p['pid']) or filtro in p['usuario'].lower():
                    self.tree.insert('', tk.END, values=(
                        p['pid'], p['nombre'], f"{p['cpu']:.1f}", f"{p['mem']:.1f}",
                        p['estado'], p['usuario']
                    ))

    def _mostrar_arbol_filtrado(self, filtro):
        hijos = {}
        for p in self.procesos:
            ppid = p['ppid']
            if ppid not in hijos:
                hijos[ppid] = []
            hijos[ppid].append(p)

        def insertar_hijos(parent_id, ppid):
            for p in hijos.get(ppid, []):
                coincide = (filtro in p['nombre'].lower() or
                            filtro in str(p['pid']) or
                            filtro in p['usuario'].lower())
                pid = p['pid']
                node_id = self.tree.insert(parent_id, tk.END, values=(
                    pid, p['nombre'], f"{p['cpu']:.1f}", f"{p['mem']:.1f}",
                    p['estado'], p['usuario']
                ))
                if not coincide:
                    self.tree.detach(node_id)
                insertar_hijos(node_id, pid)

        insertar_hijos('', 0)

    def toggle_vista(self):
        self.vista_arbol = not self.vista_arbol
        self.arbol_btn.config(text="📋 Lista" if self.vista_arbol else "🌳 Árbol")
        self._mostrar_datos()

    def _get_selected_pid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un proceso primero")
            return None
        item = self.tree.item(sel[0])
        return item['values'][0], item['values'][1]

    def matar_proceso(self):
        r = self._get_selected_pid()
        if not r:
            return
        pid, nombre = r
        if messagebox.askyesno("Confirmar", f"¿Matar proceso {nombre} (PID {pid})?"):
            try:
                msg = proc_mod.matar_proceso(pid)
                self.app.set_status(msg)
                self.cargar_datos_thread()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def suspender_proceso(self):
        r = self._get_selected_pid()
        if not r:
            return
        pid, nombre = r
        try:
            msg = proc_mod.matar_proceso(pid, 19)
            self.app.set_status(f"Suspendido: {nombre} (PID {pid})")
            self.cargar_datos_thread()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reanudar_proceso(self):
        r = self._get_selected_pid()
        if not r:
            return
        pid, nombre = r
        try:
            msg = proc_mod.matar_proceso(pid, 18)
            self.app.set_status(f"Reanudado: {nombre} (PID {pid})")
            self.cargar_datos_thread()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cambiar_prioridad(self):
        r = self._get_selected_pid()
        if not r:
            return
        pid, nombre = r

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
        r = self._get_selected_pid()
        if not r:
            return
        pid, nombre = r
        for p in self.procesos:
            if p['pid'] == pid:
                msg = (f"PID: {pid}\nNombre: {nombre}\nCPU: {p['cpu']}%\n"
                       f"Mem: {p['mem']}%\nEstado: {p['estado']}\n"
                       f"Usuario: {p['usuario']}\nPPID: {p['ppid']}")
                messagebox.showinfo("Detalle del Proceso", msg)
                break
