"""
CONFIGURACIÓN DEL SISTEMA - VERSIÓN MEJORADA
Configuración optimizada para interfaz infantil moderna
"""
from pathlib import Path


class Config:
    """Configuración general del sistema"""
    
    # === BASE DE DATOS ===
    DATABASE_PATH = "data.db"
    
    # === AUDIO ===
    AUDIO_FOLDER = "audio_registros"
    AUDIO_TIMEOUT = 8
    AUDIO_PHRASE_LIMIT = 5
    ENERGY_THRESHOLD = 200
    RECORDING_DURATION = 5 # segundos
    
    # === VOZ ===
    TTS_RATE = 150
    TTS_VOLUME = 1.0
    SPEECH_LANGUAGE = 'es-ES'
    
    # === INTERFAZ MEJORADA ===
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # Paleta de colores para niños - Alegre y brillante
    COLOR_FONDO = '#E8F4FF'  # Azul cielo muy claro
    COLOR_FONDO_OSCURO = '#4A90E2'  # Azul más oscuro para contraste
    COLOR_PRIMARIO = '#FF6B9D'  # Rosa brillante
    COLOR_SECUNDARIO = '#FFA500'  # Naranja
    COLOR_TERCIARIO = '#9B59B6'  # Púrpura
    COLOR_TEXTO = '#2C3E50'  # Gris oscuro para texto
    COLOR_TEXTO_CLARO = '#FFFFFF'
    COLOR_EXITO = '#2ECC71'  # Verde brillante
    COLOR_ERROR = '#E74C3C'  # Rojo
    COLOR_ADVERTENCIA = '#F39C12'  # Amarillo/Naranja
    COLOR_INFO = '#3498DB'  # Azul
    
    # Colores adicionales para elementos
    COLOR_AMARILLO = '#FFD93D'
    COLOR_VERDE_AGUA = '#6BCF7F'
    COLOR_MORADO_CLARO = '#C77DFF'
    COLOR_ROSA_CLARO = '#FFB3D9'
    
    # Configuración de fuentes
    FUENTE_PRINCIPAL = "Comic Sans MS"  # Fuente amigable para niños
    FUENTE_ALTERNATIVA = "Arial Rounded MT Bold"
    FUENTE_FALLBACK = "Arial"
    
    # Tamaños de fuente
    FUENTE_TITULO = 36
    FUENTE_SUBTITULO = 24
    FUENTE_NORMAL = 18
    FUENTE_EJERCICIO = 96  # Muy grande para que los niños vean bien
    FUENTE_PEQUEÑA = 14
    
    # === SISTEMA ===
    ACTIVATION_WORD = 'hola'
    EXIT_WORDS = ['adiós', 'adios', 'chao']
    MIN_AGE = 1
    MAX_AGE = 18
    MIN_SUCCESS_RATE = 0.70
    LEVEL_UP_THRESHOLD = 0.80
    
    # === ANIMACIONES ===
    ANIMATION_SPEED = 10  # ms entre frames
    PULSE_DURATION = 1000  # ms para animación de pulso
    CELEBRATION_DURATION = 2000  # ms para celebración
    
    # === GAMIFICACIÓN ===
    ESTRELLAS_POR_EJERCICIO = 1
    ESTRELLAS_BONUS_PERFECTO = 2
    
    # === MENSAJES MEJORADOS ===
    MENSAJES_POSITIVOS = [
        "¡Increíble! 🌟",
        "¡Eres un campeón! 🏆",
        "¡Perfecto! ⭐⭐⭐",
        "¡Lo hiciste genial! 🎉",
        "¡Súper bien! 🚀",
        "¡Wow, excelente! 🌈",
        "¡Bravo! 👏",
        "¡Fantástico! 🎊"
    ]
    
    MENSAJES_ANIMO = [
        "¡Casi lo logras! 💪",
        "Buen intento, sigamos 😊",
        "¡Vamos a intentarlo otra vez! 🌟",
        "¡Tú puedes! 💫",
        "Muy cerca, sigue así 🎯",
        "No te rindas, lo harás mejor 🌈"
    ]
    
    MENSAJES_BIENVENIDA = [
        "¡Hola! Soy DODO, tu amigo robot 🤖",
        "¡Qué alegría verte! Vamos a aprender juntos 🎈",
        "¡Hola amiguito! Preparado para divertirnos 🌟"
    ]
    
    # === EMOJIS Y SÍMBOLOS ===
    EMOJI_ROBOT = "🤖"
    EMOJI_ESTRELLA = "⭐"
    EMOJI_TROFEO = "🏆"
    EMOJI_COHETE = "🚀"
    EMOJI_CORAZON = "❤️"
    EMOJI_MICRÓFONO = "🎤"
    EMOJI_CELEBRACION = "🎉"
    
    @classmethod
    def crear_carpetas(cls):
        """Crear carpetas necesarias"""
        Path(cls.AUDIO_FOLDER).mkdir(exist_ok=True)
    
    @classmethod
    def obtener_fuente_disponible(cls):
        """Obtener la primera fuente disponible del sistema"""
        import tkinter.font as tkfont
        fuentes_sistema = tkfont.families()
        
        for fuente in [cls.FUENTE_PRINCIPAL, cls.FUENTE_ALTERNATIVA, cls.FUENTE_FALLBACK]:
            if fuente in fuentes_sistema:
                return fuente
        return "Arial"  # Fallback final
