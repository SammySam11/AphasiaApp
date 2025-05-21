
import tkinter as tk
from tkinter import ttk, messagebox

class VentanaSugerencias(tk.Toplevel):
    def __init__(self, parent, sugerencias, texto_original, controller):
        super().__init__(parent)
        self.title("Frases Sugeridas")
        self.geometry("500x300")
        self.controller = controller
        self.texto_original = texto_original

        self.sugerencias = sugerencias
        self.sugerencias_mostradas = sugerencias[:4]  # Máximo 4 a la vez

        self.lista = tk.Listbox(self, height=6, width=60)
        for s in self.sugerencias_mostradas:
            self.lista.insert(tk.END, s)
        self.lista.pack(pady=10)

        marco_botones = tk.Frame(self)
        marco_botones.pack(pady=5)

        ttk.Button(marco_botones, text="Buena sugerencia", command=self.marcar_buena).pack(side="left", padx=10)
        ttk.Button(marco_botones, text="Mala sugerencia", command=self.marcar_mala).pack(side="right", padx=10)

    def marcar_buena(self):
        seleccion = self.lista.curselection()
        if seleccion:
            frase = self.lista.get(seleccion)
            self.controller.datos_compartidos["registro_retroalimentacion"].append({
                "frase": frase,
                "tipo": "buena",
                "contexto": self.texto_original
            })
            messagebox.showinfo("Gracias", "Gracias por tu retroalimentación.")
            self.destroy()
        else:
            messagebox.showwarning("Advertencia", "Selecciona una frase para calificarla.")

    def marcar_mala(self):
        seleccion = self.lista.curselection()
        if seleccion:
            frase_mala = self.lista.get(seleccion)
            self.controller.datos_compartidos["registro_retroalimentacion"].append({
                "frase": frase_mala,
                "tipo": "mala",
                "contexto": self.texto_original
            })
            nuevas = [s for s in self.sugerencias if s not in self.sugerencias_mostradas]
            if nuevas:
                self.lista.delete(0, tk.END)
                nuevas_mostradas = nuevas[:4]
                for nueva in nuevas_mostradas:
                    self.lista.insert(tk.END, nueva)
                self.sugerencias_mostradas = nuevas_mostradas
            else:
                messagebox.showinfo("Sin nuevas sugerencias", "No se encontraron más frases nuevas.")
        else:
            messagebox.showwarning("Advertencia", "Selecciona una frase para marcarla como inadecuada.")
