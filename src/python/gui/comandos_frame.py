import tkinter as tk
from tkinter import ttk, messagebox
import threading
from modules import comandos as cmd_mod


class ComandosFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.historial = []
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        ttk.Label(top, text="Ejecutar Comandos",
                  font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        ttk.Button(top, text="📋 Historial", command=self.mostrar_historial).pack(side=tk.RIGHT, padx=2)
        ttk.Button(top, text="🧹 Limpiar", command=self.limpiar_salida).pack(side=tk.RIGHT, padx=2)

        cmd_frame = ttk.LabelFrame(self, text="Comando")
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)

        input_frame = ttk.Frame(cmd_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.cmd_var = tk.StringVar()
        self.cmd_entry = ttk.Entry(input_frame, textvariable=self.cmd_var, width=80,
                                   font=('Courier', 10))
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.cmd_entry.bind('<Return>', lambda e: self.ejecutar())
        self.cmd_entry.focus_set()

        ttk.Button(input_frame, text="▶ Ejecutar", command=self.ejecutar).pack(side=tk.LEFT, padx=5)

        opt_frame = ttk.Frame(cmd_frame)
        opt_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(opt_frame, text="Timeout (s):").pack(side=tk.LEFT, padx=5)
        self.timeout_var = tk.IntVar(value=30)
        ttk.Spinbox(opt_frame, from_=1, to=300, textvariable=self.timeout_var, width=8).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.LabelFrame(self, text="Salida")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.output_text = tk.Text(output_frame, font=('Courier', 10), wrap=tk.WORD,
                                   bg='#1e1e1e', fg='#d4d4d4', insertbackground='white')
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scroll = ttk.Scrollbar(self.output_text)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=scroll.set)
        scroll.configure(command=self.output_text.yview)

    def ejecutar(self):
        comando = self.cmd_var.get().strip()
        if not comando:
            return

        timeout = self.timeout_var.get()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"$ {comando}\n", 'prompt')
        self.output_text.tag_config('prompt', foreground='#6a9955')
        self.output_text.tag_config('error', foreground='#f44747')
        self.output_text.tag_config('success', foreground='#6a9955')

        self.app.set_status(f"Ejecutando: {comando}")

        def run():
            result = cmd_mod.ejecutar(comando, timeout)
            self.root.after(0, lambda: self._mostrar_resultado(result))

        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _mostrar_resultado(self, result):
        if result['stderr']:
            self.output_text.insert(tk.END, result['stderr'] + '\n', 'error')
        if result['stdout']:
            self.output_text.insert(tk.END, result['stdout'] + '\n', 'success')
        if result['codigo'] == 0:
            self.output_text.insert(tk.END, f"\n✅ Código de salida: {result['codigo']}\n", 'success')
        else:
            self.output_text.insert(tk.END, f"\n❌ Código de salida: {result['codigo']}\n", 'error')
        self.app.set_status(f"Comando finalizado (código {result['codigo']})")
        self.output_text.see(tk.END)

    def mostrar_historial(self):
        self.historial = cmd_mod.obtener_historial()
        if not self.historial:
            messagebox.showinfo("Historial", "No hay comandos en el historial")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Historial de comandos")
        dialog.geometry("600x350")
        dialog.transient(self.root)

        hist_text = tk.Text(dialog, font=('Courier', 9))
        hist_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for h in reversed(self.historial[-50:]):
            hist_text.insert(tk.END, f"[{h.get('timestamp', '?')[:19]}] {h['comando']} (→ {h['codigo']})\n")

        def usar_comando():
            sel = hist_text.tag_ranges(tk.SEL)
            if sel:
                line = hist_text.get(sel[0], sel[1])
            else:
                try:
                    idx = hist_text.index(tk.INSERT).split('.')[0]
                    line = hist_text.get(f"{idx}.0", f"{idx}.end")
                except Exception:
                    return
            parts = line.split('] ', 1)
            if len(parts) > 1:
                cmd = parts[1].rsplit(' (', 1)[0]
                self.cmd_var.set(cmd)
                dialog.destroy()

        ttk.Button(dialog, text="Usar comando", command=usar_comando).pack(pady=5)

    def limpiar_salida(self):
        self.output_text.delete(1.0, tk.END)

    @property
    def root(self):
        return self.winfo_toplevel()
