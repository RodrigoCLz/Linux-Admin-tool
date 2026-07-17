import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from modules import bash_analysis as bash_mod


class BashFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_file = None
        self.resultado = None
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        ttk.Label(top, text="Análisis de Scripts Bash",
                  font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        self.file_label = ttk.Label(top, text="Ningún archivo seleccionado",
                                    font=('Helvetica', 9))
        self.file_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(top, text="📂 Abrir Script", command=self.abrir_archivo).pack(side=tk.RIGHT, padx=2)
        ttk.Button(top, text="▶ Analizar", command=self.analizar_thread).pack(side=tk.RIGHT, padx=2)

        panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left = ttk.LabelFrame(panes, text="Contenido del Script")
        panes.add(left, weight=1)

        self.code_text = tk.Text(left, font=('Courier', 10), wrap=tk.NONE,
                                 bg='#1e1e1e', fg='#d4d4d4')
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        h_scroll = ttk.Scrollbar(left, orient=tk.HORIZONTAL, command=self.code_text.xview)
        h_scroll.pack(fill=tk.X)
        v_scroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.code_text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_text.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        right = ttk.LabelFrame(panes, text="Resultados")
        panes.add(right, weight=1)

        self.result_text = tk.Text(right, font=('Courier', 10), bg='#f0f0f0')
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        r_scroll = ttk.Scrollbar(self.result_text, orient=tk.VERTICAL,
                                 command=self.result_text.yview)
        r_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=r_scroll.set)

    @property
    def root(self):
        return self.winfo_toplevel()

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar script Bash",
            filetypes=[("Scripts Bash", "*.sh"), ("Todos", "*")]
        )
        if ruta:
            self.current_file = ruta
            self.file_label.config(text=os.path.basename(ruta))
            try:
                with open(ruta, 'r') as f:
                    contenido = f.read()
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(tk.END, contenido)
                self.app.set_status(f"Archivo cargado: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def analizar_thread(self):
        if not self.current_file:
            messagebox.showwarning("Abrir archivo", "Seleccione un script Bash primero")
            return

        self.app.set_status("Analizando script...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Analizando...\n")

        def run():
            try:
                resultado = bash_mod.analizar_script(self.current_file)
                self.resultado = resultado
                self.root.after(0, self._mostrar_resultados)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _mostrar_resultados(self):
        self.result_text.delete(1.0, tk.END)
        r = self.resultado

        self.result_text.insert(tk.END, f"Archivo: {r['ruta']}\n", 'header')
        self.result_text.insert(tk.END, f"Tamaño: {r['tamano']} bytes\n")
        self.result_text.insert(tk.END, f"Líneas totales: {r['lineas_totales']}\n")
        self.result_text.insert(tk.END, f"Líneas vacías: {r['lineas_vacias']}\n")
        self.result_text.insert(tk.END, f"Líneas comentarios: {r['lineas_comentarios']}\n")
        self.result_text.insert(tk.END, f"Funciones: {len(r['funciones'])}\n")
        self.result_text.insert(tk.END, f"Variables: {len(r['variables'])}\n")
        self.result_text.insert(tk.END, f"Advertencias: {len(r['warnings'])}\n\n")

        if r['funciones']:
            self.result_text.insert(tk.END, "=== Funciones ===\n", 'section')
            for f in r['funciones']:
                self.result_text.insert(tk.END, f"  L{f['linea']}: {f['nombre']}()\n")
            self.result_text.insert(tk.END, "\n")

        if r['warnings']:
            self.result_text.insert(tk.END, "=== Advertencias ===\n", 'section')
            for w in r['warnings']:
                self.result_text.insert(tk.END, f"  L{w['linea']}: [{w['tipo']}] {w['mensaje']}\n")
            self.result_text.insert(tk.END, "\n")

        if r['shellcheck']:
            self.result_text.insert(tk.END, "=== ShellCheck ===\n", 'section')
            for s in r['shellcheck'][:30]:
                self.result_text.insert(tk.END,
                    f"  L{s.get('line', '?')}: [{s.get('level', '?')}] {s.get('message', '?')}\n")

        self.result_text.tag_config('header', font=('Courier', 10, 'bold'))
        self.result_text.tag_config('section', font=('Courier', 10, 'bold'), foreground='#2c3e50')
        self.app.set_status("Análisis completado")
