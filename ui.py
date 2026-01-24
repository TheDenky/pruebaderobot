"""
INTERFAZ UNIFICADA - Una sola ventana para todo el flujo
Maneja diferentes estados visuales de forma continua
"""
import tkinter as tk
from PIL import Image, ImageTk
import os
import time


class InterfazUnificada:
    """
    Interfaz única que se mantiene abierta durante toda la ejecución.
    Cambia su contenido según el estado actual del robot.
    """
    
    # Estados posibles
    ESTADO_EYES = "eyes"           # Muestra eyes.gif (default y cuando habla)
    ESTADO_NOMBRE = "nombre"       # Muestra nombre del usuario
    ESTADO_EJERCICIO = "ejercicio" # Muestra imagen + palabra de ejercicio
    
    def __init__(self):
        self.ventana = None
        self.estado_actual = None
        
        # Container principal donde se muestra todo
        self.contenedor_principal = None
        
        # Widgets para eyes.gif
        self.label_gif = None
        self.frames_gif = []
        self.frame_actual_gif = 0
        self.animando_gif = False
        self.imagen_gif_actual = None
        # Widgets para eyes_sleeping.gif
        self.frames_sleeping = []
        self.frame_actual_sleeping = 0
        self.animando_sleeping = False
        self.modo_sleeping = False
        
        # Widgets para celebration.gif
        self.frames_celebration = []
        self.frame_actual_celebration = 0
        self.animando_celebration = False
        
        # Widgets para mostrar nombre
        self.label_nombre = None
        
        # Widgets para ejercicio
        self.label_imagen_ejercicio = None
        self.label_palabra_ejercicio = None
        self.imagen_ejercicio_actual = None
        
        # Colores
        self.color_fondo_negro = 'black'
        self.color_texto_blanco = 'white'
        self.color_exito = '#2ECC71'
        self.color_error = '#E74C3C'
    
    def crear(self):
        """Crear la ventana principal a pantalla completa"""
        self.ventana = tk.Tk()
        self.ventana.title("Robot DODO")
        
        # Pantalla completa
        self.ventana.attributes('-fullscreen', True)
        self.ventana.configure(bg=self.color_fondo_negro)
        
        # Permitir salir con ESC
        self.ventana.bind('<Escape>', lambda e: self.toggle_fullscreen())
        
        # Contenedor principal (centrado)
        self.contenedor_principal = tk.Frame(
            self.ventana, 
            bg=self.color_fondo_negro
        )
        self.contenedor_principal.place(relx=0.5, rely=0.5, anchor='center')
        
        # Crear widgets (pero ocultos inicialmente)
        self._crear_widgets_eyes()
        self._crear_widgets_nombre()
        self._crear_widgets_ejercicio()
        
        # Iniciar mostrando eyes.gif
        self.mostrar_eyes()
        
        self.ventana.update()
    
    def _crear_widgets_eyes(self):
        """Crear widgets para mostrar eyes.gif"""
        self.label_gif = tk.Label(
            self.contenedor_principal,
            bg=self.color_fondo_negro
        )
        # No hacer pack() todavía
    
    def _crear_widgets_nombre(self):
        """Crear widgets para mostrar nombre"""
        try:
            fuente = ('Comic Sans MS', 72, 'bold')
        except:
            fuente = ('Arial', 72, 'bold')
        
        self.label_nombre = tk.Label(
            self.contenedor_principal,
            text="",
            font=fuente,
            bg=self.color_fondo_negro,
            fg=self.color_texto_blanco
        )
        # No hacer pack() todavía
    
    def _crear_widgets_ejercicio(self):
        """Crear widgets para mostrar ejercicio (imagen + palabra)"""
        # Frame contenedor para ejercicio
        frame_ejercicio = tk.Frame(
            self.contenedor_principal,
            bg=self.color_fondo_negro
        )
        
        # Imagen
        self.label_imagen_ejercicio = tk.Label(
            frame_ejercicio,
            bg=self.color_fondo_negro
        )
        self.label_imagen_ejercicio.pack(pady=30)
        
        # Palabra
        try:
            fuente = ('Comic Sans MS', 96, 'bold')
        except:
            fuente = ('Arial', 96, 'bold')
        
        self.label_palabra_ejercicio = tk.Label(
            frame_ejercicio,
            text="",
            font=fuente,
            bg=self.color_fondo_negro,
            fg=self.color_texto_blanco
        )
        self.label_palabra_ejercicio.pack(pady=30)
        
        # Guardar referencia al frame
        self.frame_ejercicio = frame_ejercicio
        # No hacer pack() todavía
    
    def _limpiar_contenedor(self):
        """Ocultar todos los widgets del contenedor"""
        for widget in self.contenedor_principal.winfo_children():
            widget.pack_forget()
    
    # ========== ESTADO: EYES.GIF ==========
    
    def mostrar_eyes(self):
        """Mostrar eyes.gif (estado default)"""
        # Desactivar modo sleeping si estaba activo
        self.modo_sleeping = False
        self.animando_sleeping = False
        
#         if self.estado_actual == self.ESTADO_EYES and not self.modo_sleeping:
#             return
        
        self.estado_actual = self.ESTADO_EYES
        self._limpiar_contenedor()
        self.label_gif.pack(expand=True)
        
        if not self.frames_gif:
            self._cargar_gif('eyes.gif')
        
        if self.frames_gif and not self.animando_gif:
            self.animando_gif = True
            self._animar_gif()
        
        self.ventana.update_idletasks()
        self.ventana.update()
        
    def mostrar_eyes_sleeping(self):
        """Mostrar eyes_sleeping.gif cuando hay inactividad"""
        if self.modo_sleeping:
            return
        
        print("💤 Modo sleeping activado")
        self.modo_sleeping = True
        self.estado_actual = self.ESTADO_EYES
        self.animando_gif = False
        
        self._limpiar_contenedor()
        self.label_gif.pack(expand=True)
        
        if not self.frames_sleeping:
            self._cargar_gif('eyes_sleeping.gif', sleeping=True)
        
        if self.frames_sleeping and not self.animando_sleeping:
            self.animando_sleeping = True
            self.frame_actual_sleeping = 0
            self._animar_gif_sleeping()
        
        self.ventana.update()
    
    def mostrar_celebracion(self, duracion_segundos=2):
        """
        Mostrar GIF de celebración durante un tiempo específico
        
        Args:
            duracion_segundos: Cuánto tiempo mostrar la celebración (default: 2 segundos)
        """
        print("🎉 ¡CELEBRACIÓN!")
        
        # Detener otras animaciones
        self.animando_gif = False
        self.animando_sleeping = False
        self.modo_sleeping = False
        
        # Limpiar contenedor
        self._limpiar_contenedor()
        
        # Mostrar label del GIF
        self.label_gif.pack(expand=True)
        
        # Cargar GIF de celebración si no está cargado
        if not self.frames_celebration:
            if not self._cargar_celebration_gif():
                # Si no se puede cargar el GIF, mostrar texto de celebración
                self.label_gif.config(
                    text="🎉 ¡EXCELENTE! 🎉\n⭐ ¡LO HICISTE! ⭐",
                    font=('Comic Sans MS', 72, 'bold'),
                    fg='#FFD700',  # Dorado
                    bg='black'
                )
                self.ventana.update()
                
                # Volver a eyes.gif después del tiempo especificado
                self.ventana.after(int(duracion_segundos * 1000), self.mostrar_eyes)
                return
        
        # Iniciar animación de celebración
        self.animando_celebration = True
        self.frame_actual_celebration = 0
        self._animar_celebration_gif()
        
        # Programar retorno a eyes.gif después del tiempo especificado
        self.ventana.after(int(duracion_segundos * 1000), self._fin_celebracion)
        
        self.ventana.update()

    def _fin_celebracion(self):
        """Terminar celebración y volver a eyes.gif"""
        self.animando_celebration = False
        self.mostrar_eyes()
    
    def _cargar_gif(self, ruta_gif, sleeping=False):
        """Cargar frames del GIF"""
        if not os.path.exists(ruta_gif):
            print(f"⚠️ No se encontró {ruta_gif}, usando texto")
            # Mostrar texto alternativo
            self.label_gif.config(
                text="🤖 ROBOT DODO",
                font=('Arial', 48, 'bold'),
                fg='white',
                bg='black'
            )
            return False
        
        try:
            gif = Image.open(ruta_gif)
            
            # Obtener tamaño de pantalla
            screen_width = self.ventana.winfo_screenwidth()
            screen_height = self.ventana.winfo_screenheight()
            
            max_width = int(screen_width * 0.8)
            max_height = int(screen_height * 0.8)
            
            # Extraer frames
            if sleeping:
                self.frames_sleeping = []
            else:
                self.frames_gif = []
            try:
                while True:
                    frame = gif.copy()
                    frame.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(frame)
                    if sleeping:
                        self.frames_sleeping.append(photo)
                    else:
                        self.frames_gif.append(photo)
                    gif.seek(len(self.frames_gif))
            except EOFError:
                pass
            
            frames = self.frames_sleeping if sleeping else self.frames_gif

            if len(frames) == 0:
                print("⚠️ No se pudieron extraer frames del GIF")
                return False

            print(f"✅ GIF {'sleeping' if sleeping else 'normal'} cargado: {len(frames)} frames")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar GIF: {e}")
            return False
    
    def _cargar_celebration_gif(self, ruta_gif='celebration.gif'):
        """Cargar frames del GIF de celebración"""
        if not os.path.exists(ruta_gif):
            print(f"⚠️ No se encontró {ruta_gif}")
            return False
        
        try:
            gif = Image.open(ruta_gif)
            
            # Obtener tamaño de pantalla
            screen_width = self.ventana.winfo_screenwidth()
            screen_height = self.ventana.winfo_screenheight()
            
            # Usar 60% de la pantalla para el GIF
            max_width = int(screen_width * 0.6)
            max_height = int(screen_height * 0.6)
            
            # Extraer frames
            self.frames_celebration = []
            try:
                while True:
                    frame = gif.copy()
                    frame.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(frame)
                    self.frames_celebration.append(photo)
                    gif.seek(len(self.frames_celebration))
            except EOFError:
                pass
            
            if len(self.frames_celebration) == 0:
                print("⚠️ No se pudieron extraer frames del GIF de celebración")
                return False
            
            print(f"✅ GIF de celebración cargado: {len(self.frames_celebration)} frames")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar GIF de celebración: {e}")
            return False
    
    def _animar_celebration_gif(self):
        """Animar el GIF de celebración"""
        if not self.animando_celebration or not self.frames_celebration:
            return
        
        try:
            # Mostrar frame actual
            self.label_gif.config(image=self.frames_celebration[self.frame_actual_celebration])
            
            # Avanzar al siguiente frame
            self.frame_actual_celebration = (self.frame_actual_celebration + 1) % len(self.frames_celebration)
            
            # Programar siguiente frame (60ms para animación fluida)
            self.ventana.after(60, self._animar_celebration_gif)
            
        except Exception as e:
            print(f"⚠️ Error en animación de celebración: {e}")
            self.animando_celebration = False
        
    def _animar_gif(self):
        """Animar el GIF continuamente"""
        if not self.animando_gif or not self.frames_gif:
            return
        
        if self.estado_actual != self.ESTADO_EYES:
            return  # Detener si cambió de estado
        
        try:
            # Mostrar frame actual
            self.label_gif.config(image=self.frames_gif[self.frame_actual_gif])
            
            # Avanzar al siguiente frame
            self.frame_actual_gif = (self.frame_actual_gif + 1) % len(self.frames_gif)
            
            # Programar siguiente frame
            self.ventana.after(60, self._animar_gif)
            
        except Exception as e:
            print(f"⚠️ Error en animación: {e}")
            self.animando_gif = False
    
    # ========== ESTADO: NOMBRE ==========
    
    def _animar_gif_sleeping(self):
        """Animar el GIF sleeping continuamente"""
        if not self.animando_sleeping or not self.frames_sleeping:
            return
        
        if not self.modo_sleeping:
            return
        
        try:
            self.label_gif.config(image=self.frames_sleeping[self.frame_actual_sleeping])
            self.frame_actual_sleeping = (self.frame_actual_sleeping + 1) % len(self.frames_sleeping)
            self.ventana.after(5, self._animar_gif_sleeping)
        except Exception as e:
            print(f"⚠️ Error en animación sleeping: {e}")
            self.animando_sleeping = False
        
    def mostrar_nombre(self, nombre: str):
        """Mostrar el nombre del usuario en grande"""
        if self.estado_actual == self.ESTADO_NOMBRE and self.label_nombre['text'] == nombre:
            return  # Ya está mostrando este nombre
        
        self.estado_actual = self.ESTADO_NOMBRE
        
        # Limpiar contenedor
        self._limpiar_contenedor()
        
        # Actualizar y mostrar nombre
        self.label_nombre.config(text=nombre)
        self.label_nombre.pack(expand=True)
        
        self.ventana.update()
    
    # ========== ESTADO: EJERCICIO ==========
    
    def mostrar_ejercicio(self, palabra: str, ruta_imagen: str = None):
        """Mostrar ejercicio (imagen + palabra)"""
        self.estado_actual = self.ESTADO_EJERCICIO
        
        # Limpiar contenedor
        self._limpiar_contenedor()
        
        # Actualizar palabra
        self.label_palabra_ejercicio.config(
            text=palabra.upper(),
            fg=self.color_texto_blanco
        )
        
        # Cargar y mostrar imagen
        if ruta_imagen and os.path.exists(ruta_imagen):
            self._cargar_imagen_ejercicio(ruta_imagen)
        else:
            # Limpiar imagen si no hay
            self.label_imagen_ejercicio.config(image='')
            self.imagen_ejercicio_actual = None
        
        # Mostrar frame de ejercicio
        self.frame_ejercicio.pack(expand=True)
        
        self.ventana.update()
    
    def _cargar_imagen_ejercicio(self, ruta_imagen: str):
        """Cargar imagen del ejercicio"""
        if not ruta_imagen or not os.path.exists(ruta_imagen):
            return
        
        try:
            imagen_pil = Image.open(ruta_imagen)
            
            # Obtener tamaño de pantalla
            screen_width = self.ventana.winfo_screenwidth()
            screen_height = self.ventana.winfo_screenheight()
            
            # Usar 50% de la pantalla
            max_width = int(screen_width * 0.5)
            max_height = int(screen_height * 0.5)
            
            # Redimensionar
            imagen_pil.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            self.imagen_ejercicio_actual = ImageTk.PhotoImage(imagen_pil)
            
            # Mostrar
            self.label_imagen_ejercicio.config(image=self.imagen_ejercicio_actual)
            
        except Exception as e:
            print(f"⚠️ Error al cargar imagen: {e}")
            self.label_imagen_ejercicio.config(image='')
            self.imagen_ejercicio_actual = None
    
    def mostrar_feedback_ejercicio(self, correcto: bool):
        """Mostrar feedback visual en el ejercicio actual"""
        if self.estado_actual != self.ESTADO_EJERCICIO:
            return
        
        # Cambiar color del texto
        color = self.color_exito if correcto else self.color_error
        self.label_palabra_ejercicio.config(fg=color)
        self.ventana.update()
        
        # Volver a blanco después de 1 segundo
        self.ventana.after(1000, lambda: self.label_palabra_ejercicio.config(fg=self.color_texto_blanco))
    
    # ========== UTILIDADES ==========
    
    def toggle_fullscreen(self):
        """Alternar pantalla completa (con ESC)"""
        current = self.ventana.attributes('-fullscreen')
        self.ventana.attributes('-fullscreen', not current)
    
    def actualizar(self):
        """Forzar actualización de la ventana"""
        if self.ventana:
            self.ventana.update()
    
    def cerrar(self):
        """Cerrar la ventana"""
        self.animando_gif = False
        if self.ventana:
            try:
                self.ventana.destroy()
            except:
                pass
    
    def mainloop(self):
        """Iniciar el loop principal de tkinter"""
        if self.ventana:
            self.ventana.mainloop()