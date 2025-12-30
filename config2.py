"""
CONFIGURACIÓN DEL SISTEMA
Todas las constantes y configuraciones en un solo lugar
"""
from pathlib import Path


class Config:
    """Configuración general del sistema"""
    
    # === BASE DE DATOS ===
    DATABASE_PATH = "data.db"
    
    # === AUDIO ===
    AUDIO_FOLDER = "audio_registros"
    AUDIO_TIMEOUT = 10
    AUDIO_PHRASE_LIMIT = 10
    ENERGY_THRESHOLD = 300
    RECORDING_DURATION = 5  # segundos
    
    # === VOZ ===
    TTS_RATE = 150
    TTS_VOLUME = 1.0
    SPEECH_LANGUAGE = 'es-ES'
    
    # === INTERFAZ ===
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 700
    COLOR_FONDO = '#1a1a2e'
    COLOR_PRIMARIO = '#00d9ff'
    COLOR_SECUNDARIO = '#ff3366'
    COLOR_TEXTO = '#ffffff'
    COLOR_EXITO = '#00ff88'
    COLOR_ADVERTENCIA = '#ffd700'
    
    # === SISTEMA ===
    ACTIVATION_WORD = 'hola'
    EXIT_WORDS = ['adiós', 'adios', 'chao']
    MIN_AGE = 1
    MAX_AGE = 18
    MIN_SUCCESS_RATE = 0.70
    LEVEL_UP_THRESHOLD = 0.80
    
    # === MENSAJES ===
    MENSAJES_POSITIVOS = [
        "¡Muy bien! Excelente",
        "¡Perfecto! Lo hiciste genial",
        "¡Súper! Eres increíble",
        "¡Fantástico! Sigue así"
    ]
    
    MENSAJES_ANIMO = [
        "Casi lo logras, vamos a intentar de nuevo",
        "Buen intento, lo harás mejor la próxima vez",
        "No te preocupes, sigue intentando",
        "Muy cerca, inténtalo otra vez"
    ]
    
    @classmethod
    def crear_carpetas(cls):
        """Crear carpetas necesarias"""
        Path(cls.AUDIO_FOLDER).mkdir(exist_ok=True)