"""
PANTALLA INICIAL - Muestra eyes.gif al iniciar el robot
"""
import tkinter as tk
from PIL import Image, ImageTk
import os


class PantallaInicial:
    """Pantalla inicial con animación eyes.gif"""
    
    def __init__(self):
        self.ventana = None
        self.label_gif = None
        self.frames = []
        self.frame_actual = 0
        self.animando = False
        self.callback_completado = None
        
    def crear(self, duracion_segundos=3, callback=None):
        """
        Crear y mostrar la pantalla inicial
        
        Args:
            duracion_segundos: Cuánto tiempo mostrar la pantalla (0 = indefinido)
            callback: Función a llamar cuando termine la animación
        """
        self.callback_completado = callback
        
        self.ventana = tk.Tk()
        self.ventana.title("Robot DODO")
        self.ventana.attributes('-fullscreen', True)
        self.ventana.configure(bg='black')
        
        # Permitir salir con ESC
        self.ventana.bind('<Escape>', lambda e: self.cerrar())
        
        # Frame principal
        frame_principal = tk.Frame(self.ventana, bg='black')
        frame_principal.pack(fill="both", expand=True)
        
        # Label para el GIF
        self.label_gif = tk.Label(frame_principal, bg='black')
        self.label_gif.pack(expand=True)
        
        # Cargar y mostrar el GIF
        if not self.cargar_gif('eyes.gif'):
            # Si no se encuentra el gif, mostrar texto
            self.label_gif.config(
                text="🤖 ROBOT DODO\nCargando...",
                font=('Arial', 48, 'bold'),
                fg='white',
                bg='black'
            )
            
            # Cerrar después del tiempo especificado
            if duracion_segundos > 0:
                self.ventana.after(int(duracion_segundos * 1000), self.cerrar)
        else:
            # Iniciar animación
            self.animando = True
            self.animar_gif()
            
            # Cerrar después del tiempo especificado
            if duracion_segundos > 0:
                self.ventana.after(int(duracion_segundos * 1000), self.cerrar)
        
        # Mantener ventana abierta
        self.ventana.mainloop()
    
    def cargar_gif(self, ruta_gif):
        """
        Cargar frames del GIF
        
        Returns:
            True si se cargó correctamente, False si no
        """
        if not os.path.exists(ruta_gif):
            print(f"⚠️ No se encontró {ruta_gif}")
            return False
        
        try:
            # Abrir GIF
            gif = Image.open(ruta_gif)
            
            # Extraer todos los frames
            self.frames = []
            try:
                while True:
                    # Copiar frame actual
                    frame = gif.copy()
                    
                    # Redimensionar si es necesario (mantener aspecto)
                    # Obtener tamaño de la pantalla
                    screen_width = self.ventana.winfo_screenwidth()
                    screen_height = self.ventana.winfo_screenheight()
                    
                    # Calcular tamaño para que ocupe 60% de la pantalla
                    max_width = int(screen_width * 0.6)
                    max_height = int(screen_height * 0.6)
                    
                    # Redimensionar manteniendo aspecto
                    frame.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    
                    # Convertir a PhotoImage
                    photo = ImageTk.PhotoImage(frame)
                    self.frames.append(photo)
                    
                    # Ir al siguiente frame
                    gif.seek(len(self.frames))
                    
            except EOFError:
                # Ya no hay más frames
                pass
            
            if len(self.frames) == 0:
                print("⚠️ No se pudieron extraer frames del GIF")
                return False
            
            print(f"✅ GIF cargado: {len(self.frames)} frames")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar GIF: {e}")
            return False
    
    def animar_gif(self):
        """Animar el GIF mostrando frames secuencialmente"""
        if not self.animando or not self.frames:
            return
        
        try:
            # Mostrar frame actual
            self.label_gif.config(image=self.frames[self.frame_actual])
            
            # Avanzar al siguiente frame (loop)
            self.frame_actual = (self.frame_actual + 1) % len(self.frames)
            
            # Programar siguiente frame (60ms = ~16 FPS)
            self.ventana.after(60, self.animar_gif)
            
        except Exception as e:
            print(f"⚠️ Error en animación: {e}")
            self.animando = False
    
    def cerrar(self):
        """Cerrar la pantalla inicial"""
        self.animando = False
        
        if self.ventana:
            try:
                self.ventana.destroy()
            except:
                pass
        
        # Llamar callback si existe
        if self.callback_completado:
            self.callback_completado()
    
    def esperar(self):
        """Esperar a que el usuario presione una tecla o haga clic"""
        if self.ventana:
            # Agregar texto de instrucción
            label_instruccion = tk.Label(
                self.ventana,
                text="Presiona cualquier tecla o haz clic para continuar",
                font=('Arial', 16),
                fg='white',
                bg='black'
            )
            label_instruccion.pack(side='bottom', pady=50)
            
            # Eventos para continuar
            self.ventana.bind('<Key>', lambda e: self.cerrar())
            self.ventana.bind('<Button-1>', lambda e: self.cerrar())


def mostrar_pantalla_inicial(duracion=10):
    """
    Función helper para mostrar la pantalla inicial
    
    Args:
        duracion: Segundos a mostrar (0 = esperar interacción del usuario)
    """
    pantalla = PantallaInicial()
    
    if duracion == 0:
        # Esperar interacción
        pantalla.crear(duracion_segundos=0)
        pantalla.esperar()
    else:
        # Mostrar por tiempo específico
        pantalla.crear(duracion_segundos=duracion)


if __name__ == "__main__":
    # Prueba
    mostrar_pantalla_inicial(duracion=5)
