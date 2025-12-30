"""
AUDIO - Sistema completo de audio
BASADO EN TESTS FUNCIONALES:
1. gTTS + mpg123 (principal - mejor calidad)
2. espeak (fallback - funciona siempre)
3. Solo texto (si ambos fallan)

GRABACIÓN: sounddevice + soundfile (método más confiable)
"""
import os
import sys
import speech_recognition as sr
from datetime import datetime
from typing import Optional
import threading
import subprocess
import tempfile
from config import Config

# Nuevos imports para sounddevice
import sounddevice as sd
import soundfile as sf


class AudioSystem:
    """Sistema completo de audio: reconocimiento, TTS y grabación"""
    
    def __init__(self):
        # Reconocimiento de voz
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = Config.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = False
        
        # Síntesis de voz - Sistema híbrido
        self.gtts_disponible = False
        self.mpg123_disponible = False
        self.espeak_disponible = False
        
        # Verificar sounddevice para grabación
        self.sounddevice_disponible = self._verificar_sounddevice()
        
        # Intentar cargar gTTS + mpg123 primero
        self._inicializar_gtts_mpg123()
        
        # Si gTTS no está disponible, verificar espeak
        if not self.gtts_disponible:
            self._inicializar_espeak()
        
        # Crear carpeta de audio
        if not os.path.exists(Config.AUDIO_FOLDER):
            os.makedirs(Config.AUDIO_FOLDER)
        
        # Mensaje de estado
        self._mostrar_estado_tts()
        self._mostrar_estado_grabacion()
    
    def _verificar_sounddevice(self):
        """Verifica que sounddevice esté disponible"""
        try:
            # Verificar que podemos acceder a dispositivos de audio
            devices = sd.query_devices()
            return True
        except Exception as e:
            print(f"⚠️ sounddevice no disponible: {e}")
            return False
    
    def _inicializar_gtts_mpg123(self):
        """Inicializar gTTS + mpg123 (MÉTODO QUE FUNCIONA EN TUS TESTS)"""
        try:
            # Verificar que gTTS esté instalado
            from gtts import gTTS
            self.gTTS = gTTS
            
            # Verificar que mpg123 esté disponible
            result = subprocess.run(['which', 'mpg123'], 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                self.mpg123_disponible = True
                self.gtts_disponible = True
                return True
            else:
                print("⚠️ mpg123 no está instalado. Instalar con: sudo apt-get install mpg123")
                return False
                
        except ImportError:
            print("⚠️ gTTS no está instalado. Instalar con: pip install gTTS")
            return False
        except Exception as e:
            print(f"⚠️ Error al verificar gTTS/mpg123: {e}")
            return False
    
    def _inicializar_espeak(self):
        """Inicializar espeak como fallback (MÉTODO DE TU TEST_V2)"""
        try:
            # Verificar que espeak esté disponible
            result = subprocess.run(['which', 'espeak'], 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                self.espeak_disponible = True
                return True
            else:
                print("⚠️ espeak no está instalado. Instalar con: sudo apt-get install espeak")
                return False
                
        except Exception as e:
            print(f"⚠️ Error al verificar espeak: {e}")
            return False
    
    def _mostrar_estado_tts(self):
        """Mostrar estado del sistema TTS"""
        if self.gtts_disponible and self.mpg123_disponible:
            print("✅ Sistema TTS: Google (gTTS + mpg123) - CALIDAD PREMIUM")
        elif self.espeak_disponible:
            print("✅ Sistema TTS: espeak - Funcional")
        else:
            print("⚠️ Sistema TTS: No disponible")
            print("   El robot funcionará solo con texto en consola")
            print("   Para habilitar voz:")
            print("   1. gTTS: pip install gTTS && sudo apt-get install mpg123")
            print("   2. espeak: sudo apt-get install espeak")
    
    def _mostrar_estado_grabacion(self):
        """Mostrar estado del sistema de grabación"""
        if self.sounddevice_disponible:
            print("✅ Sistema de Grabación: sounddevice - ÓPTIMO")
        else:
            print("⚠️ Sistema de Grabación: No disponible")
            print("   Instalar con: pip install sounddevice soundfile")
    
    # ========== RECONOCIMIENTO DE VOZ ==========
    
    def escuchar(self, timeout: int = 10, phrase_time_limit: int = 10) -> Optional[str]:
        """Escucha y retorna texto reconocido"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                texto = self.recognizer.recognize_google(audio, language=Config.SPEECH_LANGUAGE)
                return texto
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"❌ Error de reconocimiento: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None
    
    # ========== SÍNTESIS DE VOZ (TTS) HÍBRIDA ==========
    
    def hablar(self, texto: str, velocidad: float = 1.0):
        """
        Convierte texto a voz usando sistema híbrido:
        1. Intenta con gTTS + mpg123 (Google) - MEJOR CALIDAD
        2. Si falla, usa espeak
        3. Si ambos fallan, solo imprime
        """
        # SIEMPRE imprimir en consola
        print(f"🤖 Robot dice: {texto}")
        
        # Intentar con gTTS + mpg123 primero
        if self.gtts_disponible and self.mpg123_disponible:
            if self._hablar_con_gtts_mpg123(texto):
                return  # Éxito con gTTS
        
        # Si gTTS falló, intentar con espeak
        if self.espeak_disponible:
            if self._hablar_con_espeak(texto, velocidad):
                return  # Éxito con espeak
        
        # Si ambos fallaron, el mensaje ya se imprimió en consola
    
    def _hablar_con_gtts_mpg123(self, texto: str) -> bool:
        """
        Hablar usando gTTS + mpg123 (MÉTODO DE TU TEST)
        Este es el método que funciona en test_01_hablar_gtts.py
        """
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Generar audio con gTTS
            tts = self.gTTS(text=texto, lang='es', slow=False)
            tts.save(temp_filename)
            
            # Reproducir con mpg123 (en modo silencioso con -q)
            subprocess.run(['mpg123', '-q', temp_filename], check=True)
            
            # Eliminar archivo temporal
            try:
                os.remove(temp_filename)
            except:
                pass
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error ejecutando mpg123: {e}")
            return False
        except Exception as e:
            print(f"⚠️ gTTS falló: {e}. Intentando con espeak...")
            return False
    
    def _hablar_con_espeak(self, texto: str, velocidad: float = 1.0) -> bool:
        """
        Hablar usando espeak (MÉTODO DE TU TEST_V2)
        Este es el método que funciona en test_01_hablar_v2.py
        """
        try:
            # Calcular velocidad para espeak (palabras por minuto)
            # Config.TTS_RATE es aprox 150, ajustamos con el factor velocidad
            velocidad_espeak = int(Config.TTS_RATE * velocidad)
            
            # Comando espeak
            comando = ['espeak', '-v', 'es', '-s', str(velocidad_espeak), texto]
            
            # Ejecutar espeak
            subprocess.run(comando, check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error ejecutando espeak: {e}")
            return False
        except FileNotFoundError:
            print("⚠️ espeak no encontrado")
            return False
        except Exception as e:
            print(f"⚠️ espeak falló: {e}")
            return False
    
    # ========== GRABACIÓN CON SOUNDDEVICE ==========
    
    def grabar(self, duracion: int, person_id: int, exercise_id: int) -> Optional[str]:
        """
        Graba audio usando sounddevice y retorna path del archivo
        MÉTODO MEJORADO: sounddevice + soundfile
        """
        if not self.sounddevice_disponible:
            print("❌ sounddevice no está disponible. No se puede grabar.")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"{Config.AUDIO_FOLDER}/audio_{person_id}_{exercise_id}_{timestamp}.wav"
        
        try:
            # Parámetros de grabación
            sample_rate = 44100
            channels = 1
            
            print(f"🎙️ Grabando {duracion} segundos...")
            
            # Grabar audio
            audio_data = sd.rec(
                int(duracion * sample_rate),
                samplerate=sample_rate,
                channels=channels,
                dtype='int16'
            )
            
            # Esperar a que termine la grabación
            sd.wait()
            
            # Guardar archivo WAV
            sf.write(nombre_archivo, audio_data, sample_rate)
            
            print(f"✅ Audio grabado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"⚠️ Error al grabar audio: {e}")
            return None
    
    # ========== OPERACIÓN COMBINADA ==========
    
    def grabar_y_escuchar(self, duracion: int, person_id: int, exercise_id: int) -> tuple:
        """
        Graba audio Y reconoce voz simultáneamente
        ACTUALIZADO para usar sounddevice en grabación
        """
        texto_reconocido = None
        audio_path = None
        
        def escuchar_thread():
            nonlocal texto_reconocido
            try:
                texto_reconocido = self.escuchar(timeout=duracion, phrase_time_limit=duracion)
            except:
                pass
        
        def grabar_thread():
            nonlocal audio_path
            try:
                audio_path = self.grabar(duracion, person_id, exercise_id)
            except:
                pass
        
        hilo_escucha = threading.Thread(target=escuchar_thread)
        hilo_grabacion = threading.Thread(target=grabar_thread)
        
        hilo_escucha.start()
        hilo_grabacion.start()
        
        hilo_escucha.join()
        hilo_grabacion.join()
        
        return (texto_reconocido, audio_path)
    
    def detener(self):
        """Detener reproducción de audio"""
        try:
            # Intentar matar procesos de mpg123 o espeak si están corriendo
            subprocess.run(['killall', 'mpg123'], stderr=subprocess.DEVNULL)
            subprocess.run(['killall', 'espeak'], stderr=subprocess.DEVNULL)
            
            # Detener sounddevice si está reproduciendo
            sd.stop()
        except:
            pass