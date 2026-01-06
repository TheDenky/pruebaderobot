"""
UI MEJORADA CON SOPORTE DE IMÁGENES - Interfaz gráfica moderna para niños
Incluye animaciones, gamificación, diseño atractivo y apoyo visual con imágenes
"""
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import math
import time
import os
from PIL import Image, ImageTk


class Config:
    """Configuración de colores e interfaz"""
    # Paleta de colores para niños
    COLOR_FONDO = '#E8F4FF'
    COLOR_FONDO_OSCURO = '#4A90E2'
    COLOR_PRIMARIO = '#FF6B9D'
    COLOR_SECUNDARIO = '#FFA500'
    COLOR_TERCIARIO = '#9B59B6'
    COLOR_TEXTO = '#2C3E50'
    COLOR_TEXTO_CLARO = '#FFFFFF'
    COLOR_EXITO = '#2ECC71'
    COLOR_ERROR = '#E74C3C'
    COLOR_ADVERTENCIA = '#F39C12'
    COLOR_AMARILLO = '#FFD93D'
    COLOR_VERDE_AGUA = '#6BCF7F'
    COLOR_MORADO_CLARO = '#C77DFF'
    COLOR_ROSA_CLARO = '#FFB3D9'
    
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    FUENTE_PRINCIPAL = "Comic Sans MS"
    FUENTE_ALTERNATIVA = "Arial"
    
    # Carpeta de imágenes
    CARPETA_IMAGENES = "imagenes"


class AnimatedLabel(tk.Canvas):
    """Label animado con efectos de pulso y color"""
    
    def __init__(self, parent, text="", font_size=20, color="#000000", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.text = text
        self.font_size = font_size
        self.color = color
        self.scale = 1.0
        self.text_id = None
        self.animating = False
        self.dibujar()
    
    def dibujar(self):
        """Dibujar el texto"""
        self.delete("all")
        if self.text:
            font = (Config.FUENTE_PRINCIPAL, int(self.font_size * self.scale), "bold")
            self.text_id = self.create_text(
                self.winfo_width() // 2 if self.winfo_width() > 1 else 150,
                self.winfo_height() // 2 if self.winfo_height() > 1 else 50,
                text=self.text,
                font=font,
                fill=self.color,
                justify="center"
            )
    
    def actualizar_texto(self, texto, color=None):
        """Actualizar texto y opcionalmente el color"""
        self.text = texto
        if color:
            self.color = color
        self.dibujar()
    
    def animar_pulso(self, veces=2):
        """Animación de pulso"""
        if self.animating:
            return
        self.animating = True
        self._pulso_step(0, veces * 2)
    
    def _pulso_step(self, step, max_steps):
        """Un paso de la animación de pulso"""
        if step >= max_steps:
            self.scale = 1.0
            self.animating = False
            self.dibujar()
            return
        
        # Calcular escala usando función seno
        progress = step / max_steps
        self.scale = 1.0 + 0.1 * math.sin(progress * math.pi * 2)
        self.dibujar()
        
        self.after(50, lambda: self._pulso_step(step + 1, max_steps))


class ProgressBarCustom(tk.Canvas):
    """Barra de progreso personalizada con diseño infantil"""
    
    def __init__(self, parent, width=300, height=40, max_value=100):
        super().__init__(parent, width=width, height=height, 
                        bg=Config.COLOR_FONDO, highlightthickness=0)
        self.width = width
        self.height = height
        self.max_value = max_value
        self.current_value = 0
        self.dibujar()
    
    def dibujar(self):
        """Dibujar la barra de progreso"""
        self.delete("all")
        
        # Fondo de la barra (redondeado)
        self.create_rounded_rectangle(
            5, 5, self.width - 5, self.height - 5,
            radius=20, fill="#D3D3D3", outline=""
        )
        
        # Progreso (redondeado)
        if self.current_value > 0:
            progress_width = (self.current_value / self.max_value) * (self.width - 10)
            if progress_width > 20:  # Mínimo para que se vea el redondeo
                self.create_rounded_rectangle(
                    5, 5, 5 + progress_width, self.height - 5,
                    radius=20, fill=Config.COLOR_EXITO, outline=""
                )
        
        # Texto del porcentaje
        porcentaje = int((self.current_value / self.max_value) * 100)
        self.create_text(
            self.width // 2, self.height // 2,
            text=f"{porcentaje}%",
            font=(Config.FUENTE_PRINCIPAL, 14, "bold"),
            fill=Config.COLOR_TEXTO
        )
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Crear un rectángulo redondeado"""
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def actualizar(self, valor):
        """Actualizar valor de la barra"""
        self.current_value = min(valor, self.max_value)
        self.dibujar()


class EstrellasWidget(tk.Canvas):
    """Widget de estrellas para gamificación"""
    
    def __init__(self, parent, max_estrellas=5):
        super().__init__(parent, width=300, height=60, 
                        bg=Config.COLOR_FONDO, highlightthickness=0)
        self.max_estrellas = max_estrellas
        self.estrellas_actuales = 0
        self.dibujar()
    
    def dibujar(self):
        """Dibujar las estrellas"""
        self.delete("all")
        
        size = 40
        spacing = 60
        start_x = (300 - (self.max_estrellas * spacing)) // 2 + 30
        
        for i in range(self.max_estrellas):
            x = start_x + (i * spacing)
            y = 30
            
            if i < self.estrellas_actuales:
                # Estrella llena (amarilla)
                self._dibujar_estrella(x, y, size, Config.COLOR_AMARILLO, Config.COLOR_SECUNDARIO)
            else:
                # Estrella vacía (gris)
                self._dibujar_estrella(x, y, size, "#E0E0E0", "#CCCCCC")
    
    def _dibujar_estrella(self, cx, cy, size, fill, outline):
        """Dibujar una estrella de 5 puntas"""
        points = []
        for i in range(5):
            # Puntas externas
            angle = math.radians(i * 72 - 90)
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            points.extend([x, y])
            
            # Puntas internas
            angle = math.radians(i * 72 - 90 + 36)
            x = cx + (size * 0.4) * math.cos(angle)
            y = cy + (size * 0.4) * math.sin(angle)
            points.extend([x, y])
        
        self.create_polygon(points, fill=fill, outline=outline, width=2, smooth=False)
    
    def agregar_estrella(self):
        """Agregar una estrella con animación"""
        if self.estrellas_actuales < self.max_estrellas:
            self.estrellas_actuales += 1
            self.dibujar()
            self._animar_nueva_estrella()
    
    def _animar_nueva_estrella(self):
        """Animación simple para nueva estrella"""
        # Aquí podrías agregar una animación más compleja
        pass
    
    def reset(self):
        """Resetear estrellas"""
        self.estrellas_actuales = 0
        self.dibujar()


class RobotAvatar(tk.Canvas):
    """Avatar animado del robot DODO"""
    
    def __init__(self, parent, size=150):
        super().__init__(parent, width=size, height=size, 
                        bg=Config.COLOR_FONDO, highlightthickness=0)
        self.size = size
        self.estado = "neutral"  # neutral, hablando, feliz, triste
        self.dibujar()
    
    def dibujar(self):
        """Dibujar el robot"""
        self.delete("all")
        center = self.size // 2
        
        # Cuerpo del robot (redondeado)
        body_size = self.size * 0.8
        self.create_oval(
            center - body_size // 2, center - body_size // 2,
            center + body_size // 2, center + body_size // 2,
            fill=Config.COLOR_PRIMARIO, outline=Config.COLOR_FONDO_OSCURO, width=3
        )
        
        # Antena
        antenna_y = center - body_size // 2
        self.create_line(
            center, antenna_y, center, antenna_y - 20,
            fill=Config.COLOR_FONDO_OSCURO, width=4
        )
        self.create_oval(
            center - 8, antenna_y - 28, center + 8, antenna_y - 12,
            fill=Config.COLOR_AMARILLO, outline=Config.COLOR_FONDO_OSCURO, width=2
        )
        
        # Ojos según estado
        eye_size = 15
        eye_y = center - 15
        
        if self.estado == "feliz":
            # Ojos cerrados (líneas)
            self.create_arc(
                center - 30 - eye_size, eye_y - eye_size,
                center - 30 + eye_size, eye_y + eye_size,
                start=0, extent=-180, style="arc", width=4,
                outline=Config.COLOR_FONDO_OSCURO
            )
            self.create_arc(
                center + 30 - eye_size, eye_y - eye_size,
                center + 30 + eye_size, eye_y + eye_size,
                start=0, extent=-180, style="arc", width=4,
                outline=Config.COLOR_FONDO_OSCURO
            )
        else:
            # Ojos abiertos
            self.create_oval(
                center - 30 - eye_size, eye_y - eye_size,
                center - 30 + eye_size, eye_y + eye_size,
                fill="white", outline=Config.COLOR_FONDO_OSCURO, width=2
            )
            self.create_oval(
                center + 30 - eye_size, eye_y - eye_size,
                center + 30 + eye_size, eye_y + eye_size,
                fill="white", outline=Config.COLOR_FONDO_OSCURO, width=2
            )
            
            # Pupilas
            pupil_size = 6
            self.create_oval(
                center - 30 - pupil_size, eye_y - pupil_size,
                center - 30 + pupil_size, eye_y + pupil_size,
                fill=Config.COLOR_FONDO_OSCURO
            )
            self.create_oval(
                center + 30 - pupil_size, eye_y - pupil_size,
                center + 30 + pupil_size, eye_y + pupil_size,
                fill=Config.COLOR_FONDO_OSCURO
            )
        
        # Boca según estado
        mouth_y = center + 20
        if self.estado == "feliz":
            # Sonrisa grande
            self.create_arc(
                center - 30, mouth_y - 15,
                center + 30, mouth_y + 15,
                start=0, extent=180, style="arc", width=4,
                outline=Config.COLOR_FONDO_OSCURO
            )
        elif self.estado == "triste":
            # Boca triste
            self.create_arc(
                center - 30, mouth_y - 25,
                center + 30, mouth_y + 5,
                start=0, extent=-180, style="arc", width=4,
                outline=Config.COLOR_FONDO_OSCURO
            )
        else:
            # Boca neutral
            self.create_line(
                center - 25, mouth_y,
                center + 25, mouth_y,
                fill=Config.COLOR_FONDO_OSCURO, width=4
            )
    
    def cambiar_estado(self, estado):
        """Cambiar estado del robot"""
        self.estado = estado
        self.dibujar()


class InterfazEjerciciosMejorada:
    """Interfaz visual mejorada para ejercicios CON IMÁGENES"""
    
    def __init__(self):
        self.ventana = None
        self.frame_principal = None
        self.robot_avatar = None
        self.label_estado = None
        self.label_texto_escuchado = None
        self.label_usuario = None
        self.label_ejercicio = None
        self.label_imagen = None  # Para mostrar imágenes
        self.progress_bar = None
        self.estrellas = None
        self.ejercicios_totales = 0
        self.ejercicios_completados = 0
        self.imagen_actual = None  # Referencia a la imagen PIL
    
    def crear(self):
        """Crear ventana principal mejorada"""
        self.ventana = tk.Tk()
        self.ventana.title("🤖 Robot DODO - ¡Aprende y Diviértete!")
        self.ventana.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.ventana.configure(bg=Config.COLOR_FONDO)
        
        # Crear frame principal con scroll
        self.frame_principal = tk.Frame(self.ventana, bg=Config.COLOR_FONDO)
        self.frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === SECCIÓN SUPERIOR: Header ===
        frame_header = tk.Frame(self.frame_principal, bg=Config.COLOR_PRIMARIO, height=100)
        frame_header.pack(fill="x", pady=(0, 20))
        frame_header.pack_propagate(False)
        
        # Título con sombra de texto
        try:
            fuente_titulo = tkfont.Font(family=Config.FUENTE_PRINCIPAL, size=40, weight="bold")
        except:
            fuente_titulo = tkfont.Font(family="Arial", size=40, weight="bold")
        
        tk.Label(
            frame_header,
            text="🤖 ROBOT DODO 🤖",
            font=fuente_titulo,
            bg=Config.COLOR_PRIMARIO,
            fg="white"
        ).pack(pady=25)
        
        # === SECCIÓN MEDIA: Avatar y Usuario ===
        frame_medio = tk.Frame(self.frame_principal, bg=Config.COLOR_FONDO)
        frame_medio.pack(fill="x", pady=10)
        
        # Avatar del robot
        self.robot_avatar = RobotAvatar(frame_medio, size=150)
        self.robot_avatar.pack(side="left", padx=20)
        
        # Panel de información del usuario
        frame_info = tk.Frame(frame_medio, bg=Config.COLOR_FONDO)
        frame_info.pack(side="left", fill="both", expand=True)
        
        try:
            fuente_usuario = tkfont.Font(family=Config.FUENTE_PRINCIPAL, size=24, weight="bold")
            fuente_estado = tkfont.Font(family=Config.FUENTE_PRINCIPAL, size=18)
        except:
            fuente_usuario = tkfont.Font(family="Arial", size=24, weight="bold")
            fuente_estado = tkfont.Font(family="Arial", size=18)
        
        self.label_usuario = tk.Label(
            frame_info,
            text="",
            font=fuente_usuario,
            bg=Config.COLOR_FONDO,
            fg=Config.COLOR_PRIMARIO
        )
        self.label_usuario.pack(pady=5)
        
        self.label_estado = tk.Label(
            frame_info,
            text="⏳ Preparando...",
            font=fuente_estado,
            bg=Config.COLOR_FONDO,
            fg=Config.COLOR_TEXTO
        )
        self.label_estado.pack(pady=5)
        
        # Estrellas
        self.estrellas = EstrellasWidget(frame_info, max_estrellas=5)
        self.estrellas.pack(pady=10)
        
        # Barra de progreso
        self.progress_bar = ProgressBarCustom(frame_info, width=400, height=40)
        self.progress_bar.pack(pady=10)
        
        # === SECCIÓN DE ESCUCHA ===
        frame_escucha = tk.Frame(self.frame_principal, bg="white", relief="raised", bd=3)
        frame_escucha.pack(fill="x", pady=20)
        
        try:
            fuente_escucha = tkfont.Font(family=Config.FUENTE_PRINCIPAL, size=16)
        except:
            fuente_escucha = tkfont.Font(family="Arial", size=16)
        
        tk.Label(
            frame_escucha,
            text="🎤 ESCUCHANDO:",
            font=fuente_escucha,
            bg="white",
            fg=Config.COLOR_SECUNDARIO
        ).pack(pady=5)
        
        self.label_texto_escuchado = tk.Label(
            frame_escucha,
            text="...",
            font=fuente_escucha,
            bg="white",
            fg=Config.COLOR_TEXTO,
            wraplength=1000,
            height=3
        )
        self.label_texto_escuchado.pack(pady=10, padx=20)
        
        # === SECCIÓN PRINCIPAL: Ejercicio CON IMAGEN ===
        frame_ejercicio = tk.Frame(
            self.frame_principal, 
            bg=Config.COLOR_MORADO_CLARO,
            relief="raised",
            bd=5
        )
        frame_ejercicio.pack(fill="both", expand=True, pady=20)
        
        # Label para la imagen
        self.label_imagen = tk.Label(
            frame_ejercicio,
            bg=Config.COLOR_MORADO_CLARO
        )
        self.label_imagen.pack(pady=20)
        
        # Canvas para ejercicio animado (texto)
        self.label_ejercicio = AnimatedLabel(
            frame_ejercicio,
            text="",
            font_size=72,
            color=Config.COLOR_TEXTO_CLARO,
            bg=Config.COLOR_MORADO_CLARO,
            width=1000,
            height=150
        )
        self.label_ejercicio.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.ventana.update()
    
    def cargar_y_mostrar_imagen(self, ruta_imagen: str):
        """
        Carga y muestra una imagen
        
        Args:
            ruta_imagen: Ruta de la imagen (ej: "imagenes/CASA.png")
        """
        if not ruta_imagen or not os.path.exists(ruta_imagen):
            # Limpiar imagen anterior si no existe
            self.label_imagen.config(image='')
            self.imagen_actual = None
            return
        
        try:
            # Cargar imagen con PIL
            imagen_pil = Image.open(ruta_imagen)
            
            # Redimensionar manteniendo aspecto (máximo 300x300)
            imagen_pil.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage de tkinter
            self.imagen_actual = ImageTk.PhotoImage(imagen_pil)
            
            # Mostrar en el label
            self.label_imagen.config(image=self.imagen_actual)
            
        except Exception as e:
            print(f"⚠️ Error al cargar imagen {ruta_imagen}: {e}")
            self.label_imagen.config(image='')
            self.imagen_actual = None
    
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
    
    def mostrar_ejercicio(self, palabra: str, ruta_imagen: str = None):
        """
        Mostrar palabra del ejercicio con animación E IMAGEN
        
        Args:
            palabra: Palabra a mostrar
            ruta_imagen: Ruta opcional de la imagen de apoyo
        """
        if self.label_ejercicio:
            self.label_ejercicio.actualizar_texto(palabra.upper(), Config.COLOR_TEXTO_CLARO)
            self.label_ejercicio.animar_pulso(veces=2)
            
            # Cambiar robot a estado neutral
            if self.robot_avatar:
                self.robot_avatar.cambiar_estado("neutral")
        
        # Mostrar imagen si está disponible
        if ruta_imagen:
            self.cargar_y_mostrar_imagen(ruta_imagen)
        else:
            # Limpiar imagen anterior
            if self.label_imagen:
                self.label_imagen.config(image='')
                self.imagen_actual = None
    
    def limpiar_ejercicio(self):
        """Limpiar pantalla de ejercicio"""
        if self.label_ejercicio:
            self.label_ejercicio.actualizar_texto("")
            self.ventana.update()
        
        # Limpiar imagen también
        if self.label_imagen:
            self.label_imagen.config(image='')
            self.imagen_actual = None
            self.ventana.update()
    
    def celebrar_exito(self):
        """Animación de celebración por éxito"""
        if self.robot_avatar:
            self.robot_avatar.cambiar_estado("feliz")
        
        if self.estrellas:
            self.estrellas.agregar_estrella()
    
    def mostrar_error(self):
        """Mostrar retroalimentación de error"""
        if self.robot_avatar:
            self.robot_avatar.cambiar_estado("triste")
            # Volver a neutral después de un tiempo
            self.ventana.after(2000, lambda: self.robot_avatar.cambiar_estado("neutral"))
    
    def actualizar_progreso(self, actual, total):
        """Actualizar barra de progreso"""
        self.ejercicios_completados = actual
        self.ejercicios_totales = total
        
        if self.progress_bar and total > 0:
            self.progress_bar.max_value = total
            self.progress_bar.actualizar(actual)
    
    def robot_hablando(self, hablando=True):
        """Indicar cuando el robot está hablando"""
        if self.robot_avatar:
            if hablando:
                self.robot_avatar.cambiar_estado("hablando")
            else:
                self.robot_avatar.cambiar_estado("neutral")
    
    def cerrar(self):
        """Cerrar ventana"""
        if self.ventana:
            try:
                self.ventana.destroy()
            except:
                pass


# Alias para compatibilidad con código existente
InterfazEjercicios = InterfazEjerciciosMejorada