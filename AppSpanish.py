import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import shutil
import os
import pyttsx3  # Para funcionalidad de texto a voz
import csv
from datetime import datetime
import speech_recognition as sr
from transformers import pipeline
from ventana_sugerencias import VentanaSugerencias

class AplicacionAfasia(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicación de Comunicación para Afasia")
        self.state('zoomed')  # Maximiza la ventana con los botones visibles
        # self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.resizable(False, False)

        self.datos_compartidos = {
            "frase": tk.StringVar(),
            "categoria": tk.StringVar(),
            "palabras_seleccionadas": [],
            "registro_retroalimentacion": []
        }

        print("Cargando modelos de Aprendizaje Profundo...")
        self.cargar_modelos_aprendizaje()

        print("Cargando datos desde archivos JSON...")
        self.cargar_datos()

        print("Cargando plantillas de frases...")
        self.cargar_plantillas()

        contenedor = tk.Frame(self)
        contenedor.pack(side="top", fill="both", expand=True)

        self.frames = {}
        for F in (PaginaInicio, PaginaCategoria, PaginaPalabras):
            frame = F(parent=contenedor, controller=self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.mostrar_pantalla(PaginaInicio)

    def descargar_reporte(self):
        try:
            archivo = filedialog.asksaveasfilename(defaultextension=".csv",
                                                   filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                                                   title="Guardar Reporte de Retroalimentación")
            if archivo:
                if os.path.exists("feedback_report.csv"):
                    shutil.copy("feedback_report.csv", archivo)
                    messagebox.showinfo("Éxito", f"Reporte guardado en {archivo}")
                else:
                    messagebox.showerror("Error", "No existe un reporte para guardar.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el reporte: {e}")

    def cargar_modelos_aprendizaje(self):
        self.modelo_emocion = pipeline("sentiment-analysis")
        self.reconocedor = sr.Recognizer()

    def cargar_datos(self):
        try:
            with open('data_es_final.json', 'r', encoding='utf-8') as f:
                self.diccionario_palabras = json.load(f)
        except FileNotFoundError:
            self.diccionario_palabras = {}
            with open('data_es_final.json', 'w', encoding='utf-8') as f:
                json.dump(self.diccionario_palabras, f, ensure_ascii=False, indent=4)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "El archivo data_es_final.json está corrupto o mal formado.")
            self.diccionario_palabras = {}

    def cargar_plantillas(self):
        try:
            with open('frases_es_final.json', 'r', encoding='utf-8') as f:
                self.plantillas_frases = json.load(f)
        except FileNotFoundError:
            self.plantillas_frases = {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "El archivo frases_es_final.json está corrupto o mal formado.")
            self.plantillas_frases = {}

    def guardar_datos(self):
        try:
            with open('data_es_final.json', 'w', encoding='utf-8') as f:
                json.dump(self.diccionario_palabras, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar data_es_final.json: {e}")

    def mostrar_pantalla(self, pagina):
        frame = self.frames[pagina]
        frame.tkraise()
        frame.event_generate("<<MostrarPantalla>>")

    def detectar_emocion(self, texto):
        resultado = self.modelo_emocion(texto)[0]
        emocion = resultado['label']
        return emocion

    def voz_a_texto(self):
        with sr.Microphone() as source:
            try:
                audio = self.reconocedor.listen(source)
                texto = self.reconocedor.recognize_google(audio)
                return texto
            except sr.UnknownValueError:
                messagebox.showerror("Error", "No se reconoció el habla.")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Error del servicio de reconocimiento: {e}")

    def sugerir_frases(self, top_n=4):
        texto = self.frames[PaginaPalabras].cuadro_frase.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Advertencia", "Por favor escriba una frase.")
            return []

        palabras_clave = texto.split()
        if len(palabras_clave) < 3:
            messagebox.showwarning("Advertencia", "Ingrese al menos 3 palabras clave.")
            return []

        emocion = self.detectar_emocion(' '.join(palabras_clave))
        coincidencias = self.encontrar_plantillas(palabras_clave)
        return coincidencias[:top_n] if coincidencias else []

    def encontrar_plantillas(self, palabras):
        coincidencias = []
        for categoria, frases in self.plantillas_frases.items():
            for frase in frases:
                if any(p.lower() in frase.lower() for p in palabras):
                    coincidencias.append(frase)
        return coincidencias


class PaginaInicio(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Estilo para botones grandes
        style = ttk.Style()
        style.configure("BotonGrande.TButton", font=("Helvetica", 16), padding=10)

        # Marco centrado
        marco_central = tk.Frame(self)
        marco_central.place(relx=0.5, rely=0.5, anchor="center")

        etiqueta = ttk.Label(marco_central, text="Bienvenido", font=("Helvetica", 32))
        etiqueta.pack(pady=40)

        boton_inicio = ttk.Button(marco_central, text="Iniciar",
                                  style="BotonGrande.TButton",
                                  command=lambda: controller.mostrar_pantalla(PaginaCategoria))
        boton_inicio.pack(pady=10)

        boton_reporte = ttk.Button(marco_central, text="Descargar Reporte de Retroalimentación",
                                   style="BotonGrande.TButton",
                                   command=controller.descargar_reporte)
        boton_reporte.pack(pady=10)


class PaginaCategoria(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Estilo para botones grandes
        style = ttk.Style()
        style.configure("Categoria.TButton", font=("Helvetica", 14), padding=10)

        etiqueta = ttk.Label(self, text="Seleccione una Categoría", font=("Helvetica", 24))
        etiqueta.pack(pady=30)

        self.marco_botones = tk.Frame(self)
        self.marco_botones.pack()

        self.bind("<<MostrarPantalla>>", self.al_mostrar)

        boton_atras = ttk.Button(self, text="Atrás",
                                 style="Categoria.TButton",
                                 command=lambda: controller.mostrar_pantalla(PaginaInicio))
        boton_atras.pack(side="bottom", pady=20)

        self.imagenes_categoria = {}  # Guardar referencias

    def al_mostrar(self, event):
        for widget in self.marco_botones.winfo_children():
            widget.destroy()

        self.categorias = list(self.controller.diccionario_palabras.keys())

        columnas = 3
        for idx, categoria in enumerate(self.categorias):
            ruta_imagen = None
            lista_palabras = self.controller.diccionario_palabras.get(categoria)
            if lista_palabras and "image" in lista_palabras[0]:
                ruta_imagen = lista_palabras[0]["image"]

            try:
                imagen = Image.open(ruta_imagen).resize((80, 80), Image.LANCZOS)
                foto = ImageTk.PhotoImage(imagen)
            except:
                foto = None

            boton = ttk.Button(self.marco_botones,
                               text=categoria.replace("_", " "),
                               image=foto,
                               compound="top",
                               style="Categoria.TButton",
                               command=lambda c=categoria: self.seleccionar_categoria(c))
            boton.image = foto  # Referencia para evitar recolección de basura
            fila = idx // columnas
            col = idx % columnas
            boton.grid(row=fila, column=col, padx=25, pady=25)

    def seleccionar_categoria(self, categoria):
        self.controller.datos_compartidos["categoria"].set(categoria)
        self.controller.mostrar_pantalla(PaginaPalabras)


class PaginaPalabras(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Estilo para botones con imágenes
        style = ttk.Style()
        style.configure("BotonImagen.TButton", font=("Helvetica", 14), padding=10)

        # Estilo para botones de control
        style.configure("BotonControl.TButton", font=("Helvetica", 12), padding=8)

        marco_principal = tk.Frame(self)
        marco_principal.pack(fill="both", expand=True)

        self.etiqueta = ttk.Label(marco_principal, text="", font=("Helvetica", 22))
        self.etiqueta.pack(pady=20)

        self.marco_botones = tk.Frame(marco_principal)
        self.marco_botones.pack(pady=10)

        # Cuadro de texto para frase
        self.cuadro_frase = tk.Text(marco_principal, height=3, width=60, font=("Helvetica", 16))
        self.cuadro_frase.pack(side="bottom", pady=10)

        # Botones inferiores
        marco_controles = tk.Frame(marco_principal)
        marco_controles.pack(side="bottom", pady=10)

        ttk.Button(marco_controles, text="Hablar", style="BotonControl.TButton",
                   command=self.hablar_frase).grid(row=0, column=0, padx=10)
        ttk.Button(marco_controles, text="Borrar", style="BotonControl.TButton",
                   command=self.borrar_frase).grid(row=0, column=1, padx=10)
        ttk.Button(marco_controles, text="Atrás", style="BotonControl.TButton",
                   command=lambda: controller.mostrar_pantalla(PaginaCategoria)).grid(row=0, column=2, padx=10)
        ttk.Button(marco_controles, text="Sugerencias", style="BotonControl.TButton",
                   command=self.mostrar_sugerencias).grid(row=0, column=3, padx=10)
        ttk.Button(marco_controles, text="Voz a Texto", style="BotonControl.TButton",
                   command=self.convertir_voz_a_texto).grid(row=0, column=4, padx=10)

        self.bind("<<MostrarPantalla>>", self.al_mostrar)

    def al_mostrar(self, event):
        self.controller.cargar_datos()

        categoria = self.controller.datos_compartidos["categoria"].get()
        self.etiqueta.config(text=f"Categoría: {categoria.replace('_', ' ')}")

        for widget in self.marco_botones.winfo_children():
            widget.destroy()

        datos = self.controller.diccionario_palabras.get(categoria, [])

        for index, entrada in enumerate(datos):
            palabra = entrada["palabra"]
            ruta_imagen = entrada["image"]

            try:
                imagen = Image.open(ruta_imagen).resize((150, 150), Image.LANCZOS)
                foto = ImageTk.PhotoImage(imagen)
            except Exception as e:
                print(f"Error al cargar la imagen {ruta_imagen}: {e}")
                foto = None

            boton = ttk.Button(self.marco_botones, text=palabra, image=foto, compound="top",
                               command=lambda w=palabra: self.agregar_palabra(w),
                               style="BotonImagen.TButton")
            boton.image = foto
            boton.grid(row=index // 5, column=index % 5, padx=20, pady=20)

    def agregar_palabra(self, palabra):
        texto_actual = self.cuadro_frase.get("1.0", tk.END).strip()
        nuevo_texto = f"{texto_actual} {palabra}".strip()
        self.cuadro_frase.delete("1.0", tk.END)
        self.cuadro_frase.insert(tk.END, nuevo_texto)

    def mostrar_sugerencias(self):
        texto = self.cuadro_frase.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Advertencia", "Por favor escriba una frase.")
            return

        sugerencias = self.controller.sugerir_frases(top_n=10)
        if sugerencias:
            VentanaSugerencias(self, sugerencias, texto, self.controller)
        else:
            messagebox.showinfo("Sin sugerencias", "No se encontraron frases sugeridas.")

    def hablar_frase(self):
        texto = self.cuadro_frase.get("1.0", tk.END).strip()
        if texto:
            motor = pyttsx3.init()
            motor.setProperty('rate', 150)
            motor.setProperty('volume', 1.0)
            motor.say(texto)
            motor.runAndWait()

    def borrar_frase(self):
        self.cuadro_frase.delete("1.0", tk.END)

    def convertir_voz_a_texto(self):
        texto_voz = self.controller.voz_a_texto()
        if texto_voz:
            self.cuadro_frase.delete("1.0", tk.END)
            self.cuadro_frase.insert(tk.END, texto_voz)
            messagebox.showinfo("Voz a Texto", f"Texto reconocido: {texto_voz}")


if __name__ == "__main__":
    app = AplicacionAfasia()
    app.mainloop()