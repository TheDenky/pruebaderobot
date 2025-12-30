"""
UI - Interfaz gráfica de usuario
Todo lo relacionado con Tkinter en un solo archivo
"""
import tkinter as tk
from tkinter import font as tkfont
from config import Config


class InterfazEjercicios:
    """Interfaz visual para ejercicios"""
    
    def __init__(self):
        self.ventana = None
        self.label_estado = None
        self.label_texto_escuchado = None
        self.label_usuario = None
        self.label_ejercicio = None
    
    def crear(self):
        """Crear ventana principal"""
        self.ventana = tk.Tk()
        self.ventana.title("🤖 Robot DODO - Ejercicios")
        self.ventana.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.ventana.configure(bg=Config.COLOR_FONDO)
        
        # Fuentes
        fuente_titulo = tkfont.Font(family="Arial", size=24, weight="bold")
        fuente_estado = tkfont.Font(family="Arial", size=16)
        fuente_texto = tkfont.Font(family="Arial", size=14)
        fuente_ejercicio = tkfont.Font(family="Arial", size=72, weight="bold")
        
        # Título
        tk.Label(
            self.ventana,
            text="🤖 ROBOT DODO",
            font=fuente_titulo,
            bg=Config.COLOR_FONDO,
            fg=Config.COLOR_PRIMARIO
        ).pack(pady=20)
        
        # Usuario
        self.label_usuario = tk.Label(
            self.ventana,
            text="",
            font=fuente_estado,
            bg=Config.COLOR_FONDO,
            fg=Config.COLOR_TEXTO
        )
        self.label_usuario.pack(pady=5)
        
        # Estado
        self.label_estado = tk.Label(
            self.ventana,
            text="⏳ Iniciando...",
            font=fuente_estado,
            bg=Config.COLOR_FONDO,
            fg=Config.COLOR_ADVERTENCIA
        )
        self.label_estado.pack(pady=10)
        
        # Texto escuchado
        tk.Label(
            self.ventana,
            text="🎤 Escuchando:",
            font=fuente_texto,
            bg=Config.COLOR_FONDO,
            fg='#888888'
        ).pack(pady=5)
        
        self.label_texto_escuchado = tk.Label(
            self.ventana,
            text="...",
            font=fuente_texto,
            bg='#2a2a3e',
            fg=Config.COLOR_EXITO,
            wraplength=800,
            height=3
        )
        self.label_texto_escuchado.pack(pady=10, padx=20, fill='x')
        
        # Ejercicio (palabra grande)
        self.label_ejercicio = tk.Label(
            self.ventana,
            text="",
            font=fuente_ejercicio,
            bg=Config.COLOR_FONDO,
            fg=Config.COLOR_SECUNDARIO,
            height=4
        )
        self.label_ejercicio.pack(pady=30)
        
        self.ventana.update()
    
    def actualizar_usuario(self, texto: str):
        """Actualizar información del usuario"""
        if self.label_usuario:
            self.label_usuario.config(text=f"👤 {texto}")
            self.ventana.update()
    
    def actualizar_estado(self, texto: str):
        """Actualizar estado actual"""
        if self.label_estado:
            self.label_estado.config(text=texto)
            self.ventana.update()
    
    def actualizar_texto_escuchado(self, texto: str):
        """Actualizar texto escuchado"""
        if self.label_texto_escuchado:
            self.label_texto_escuchado.config(text=texto if texto else "...")
            self.ventana.update()
    
    def mostrar_ejercicio(self, palabra: str):
        """Mostrar palabra del ejercicio"""
        if self.label_ejercicio:
            self.label_ejercicio.config(text=palabra.upper())
            self.ventana.update()
    
    def limpiar_ejercicio(self):
        """Limpiar pantalla de ejercicio"""
        if self.label_ejercicio:
            self.label_ejercicio.config(text="")
            self.ventana.update()
    
    def cerrar(self):
        """Cerrar ventana"""
        if self.ventana:
            try:
                self.ventana.destroy()
            except:
                pass