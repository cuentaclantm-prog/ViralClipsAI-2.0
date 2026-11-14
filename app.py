import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path
from viralclips.pipeline import create_clips
from viralclips.config import OUTPUT

class App:
    def __init__(self, root):
        self.root = root
        root.title("ViralClipsAI 2.0")
        root.geometry("700x510")
        root.minsize(620, 450)
        ttk.Label(root, text="ViralClipsAI 2.0", font=("Segoe UI", 22, "bold")).pack(pady=(18, 4))
        ttk.Label(root, text="Crea clips verticales con subtítulos automáticos").pack(pady=(0, 18))
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="x")
        ttk.Label(frame, text="Enlace del video (YouTube, Twitch o Kick):").pack(anchor="w")
        self.url = tk.StringVar()
        ttk.Entry(frame, textvariable=self.url, width=80).pack(fill="x", pady=7)
        ttk.Label(frame, text="Cantidad de clips:").pack(anchor="w", pady=(8, 0))
        self.count = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=1, to=20, textvariable=self.count, width=8).pack(anchor="w", pady=5)
        self.progress = ttk.Progressbar(root, maximum=100, mode="determinate")
        self.progress.pack(fill="x", padx=18, pady=(10, 4))
        self.status = tk.StringVar(value="Listo para comenzar")
        ttk.Label(root, textvariable=self.status).pack()
        self.log = tk.Text(root, height=11, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True, padx=18, pady=12)
        self.start_btn = ttk.Button(root, text="GENERAR CLIPS", command=self.start)
        self.start_btn.pack(pady=(0, 16))
        ttk.Label(root, text=f"Los resultados se guardan en: {OUTPUT}", wraplength=650).pack(pady=(0, 8))

    def write_log(self, msg):
        def update():
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.root.after(0, update)

    def update_progress(self, pct, msg):
        def update():
            self.progress["value"] = max(0, min(100, pct))
            self.status.set(msg)
        self.root.after(0, update)

    def start(self):
        url = self.url.get().strip()
        if not url.startswith(("https://", "http://")):
            messagebox.showerror("Enlace inválido", "Pega un enlace público válido.")
            return
        self.start_btn.configure(state="disabled")
        self.progress["value"] = 0
        def worker():
            try:
                create_clips(url, int(self.count.get()), self.update_progress, self.write_log)
                self.root.after(0, lambda: messagebox.showinfo("Terminado", f"Proceso finalizado. Revisa:\n{OUTPUT}"))
            except Exception as e:
                self.write_log("ERROR: " + str(e))
                self.root.after(0, lambda: messagebox.showerror("No se pudo completar", str(e)))
            finally:
                self.root.after(0, lambda: self.start_btn.configure(state="normal"))
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    App(tk.Tk()).root.mainloop()
