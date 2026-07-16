import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from modules import archivos as file_mod


class ArchivosFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_path = os.path.expanduser('~')
        self.entries = []

        self._build_ui()
        self.cargar_directorio()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        ttk.Label(top, text="Gestión de Archivos",
                  font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        nav = ttk.Frame(top)
        nav.pack(side=tk.RIGHT)

        ttk.Button(nav, text="📂 Abrir", command=self.abrir_dialogo).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="⬆ Subir", command=self.subir).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="🔄 Actualizar", command=self.cargar_directorio_thread).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="✂ Copiar", command=self.copiar_archivo).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="✄ Mover", command=self.mover_archivo).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="🗑 Eliminar", command=self.eliminar_archivo).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="🔍 Buscar", command=self.buscar_archivos).pack(side=tk.LEFT, padx=2)

        path_frame = ttk.Frame(self)
        path_frame.pack(fill=tk.X, pady=2)
        ttk.Label(path_frame, text="Ruta:").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=80)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        path_entry.bind('<Return>', lambda e: self.ir_a_ruta())

        columns = ('nombre', 'tamano', 'tipo', 'permisos', 'modificado')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=20)

        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('tamano', text='Tamaño')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('permisos', text='Permisos')
        self.tree.heading('modificado', text='Modificado')

        self.tree.column('nombre', width=350)
        self.tree.column('tamano', width=100, anchor='e')
        self.tree.column('tipo', width=100, anchor='center')
        self.tree.column('permisos', width=100, anchor='center')
        self.tree.column('modificado', width=150, anchor='center')

        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.tree.bind('<Double-1>', self._on_double_click)

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def root(self):
        return self.winfo_toplevel()

    def cargar_directorio_thread(self):
        self.app.set_status(f"Cargando: {self.current_path}")
        t = threading.Thread(target=self.cargar_directorio, daemon=True)
        t.start()

    def cargar_directorio(self, path=None):
        if path:
            self.current_path = path
        try:
            entries = file_mod.listar_directorio(self.current_path)
            self.entries = entries
            self.root.after(0, self._mostrar_entradas)
        except PermissionError as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        except Exception as e:
            self.root.after(0, lambda: self.app.set_status(f"Error: {str(e)}"))

    def _mostrar_entradas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.path_var.set(self.current_path)
        for e in self.entries:
            size_str = self._format_size(e['tamano']) if e['tipo'] == 'archivo' else ''
            modified = e.get('modificado', 0)
            try:
                import datetime
                mod_str = datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M') if modified else ''
            except Exception:
                mod_str = ''
            self.tree.insert('', tk.END, values=(
                e['nombre'], size_str, e['tipo'], e['permisos'], mod_str
            ))
        self.app.set_status(f"{self.current_path} — {len(self.entries)} elementos")

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        nombre = item['values'][0]
        ruta = os.path.join(self.current_path, nombre)
        if os.path.isdir(ruta):
            self.cargar_directorio_thread()
            self.current_path = ruta
            t = threading.Thread(target=lambda: self.cargar_directorio(ruta), daemon=True)
            t.start()

    def subir(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.cargar_directorio(parent)

    def ir_a_ruta(self):
        ruta = self.path_var.get().strip()
        if os.path.exists(ruta):
            self.current_path = ruta
            self.cargar_directorio_thread()
        else:
            messagebox.showerror("Error", f"Ruta no existe: {ruta}")

    def abrir_dialogo(self):
        ruta = filedialog.askdirectory(initialdir=self.current_path)
        if ruta:
            self.current_path = ruta
            self.cargar_directorio_thread()

    def copiar_archivo(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un archivo")
            return
        item = self.tree.item(sel[0])
        nombre = item['values'][0]
        origen = os.path.join(self.current_path, nombre)
        destino = filedialog.asksaveasfilename(initialdir=self.current_path, initialfile=nombre)
        if destino:
            try:
                msg = file_mod.copiar(origen, destino)
                self.app.set_status(msg)
                self.cargar_directorio_thread()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def mover_archivo(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un archivo")
            return
        item = self.tree.item(sel[0])
        nombre = item['values'][0]
        origen = os.path.join(self.current_path, nombre)
        destino = filedialog.asksaveasfilename(initialdir=self.current_path, initialfile=nombre)
        if destino:
            try:
                msg = file_mod.mover(origen, destino)
                self.app.set_status(msg)
                self.cargar_directorio_thread()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def eliminar_archivo(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un archivo")
            return
        item = self.tree.item(sel[0])
        nombre = item['values'][0]
        ruta = os.path.join(self.current_path, nombre)
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
            try:
                msg = file_mod.eliminar(ruta)
                self.app.set_status(msg)
                self.cargar_directorio_thread()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def buscar_archivos(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Buscar archivos")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Patrón de búsqueda:").pack(pady=10)
        pattern_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=pattern_var, width=40).pack(pady=5)

        result_text = tk.Text(dialog, height=6, width=50)
        result_text.pack(pady=10)

        def buscar():
            patron = pattern_var.get()
            if not patron:
                return
            result_text.delete(1.0, tk.END)
            try:
                resultados = file_mod.buscar(patron, self.current_path)
                if not resultados:
                    result_text.insert(tk.END, "Sin resultados")
                else:
                    for r in resultados[:50]:
                        result_text.insert(tk.END, f"{r['ruta']}\n")
                    if len(resultados) > 50:
                        result_text.insert(tk.END, f"... y {len(resultados)-50} más")
            except Exception as e:
                result_text.insert(tk.END, f"Error: {str(e)}")

        ttk.Button(dialog, text="Buscar", command=buscar).pack()
