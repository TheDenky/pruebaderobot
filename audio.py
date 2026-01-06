"""
AUDIO MODIFICADO - Con notificaciones a la interfaz y grabación organizada por usuario
Notifica cuando empieza y termina de hablar para mostrar eyes.gif
Graba audios organizados por carpeta de usuario con formato específico
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

# Imports para sounddevice
import sounddevice as sd
import soundfile as sf

# ElevenLabs
from elevenlabs import ElevenLabs
from dotenv import load_dotenv


class AudioSystemConInterfaz:
    """Sistema de audio que notifica a la interfaz cuando habla y graba de forma organizada"""
    
    def __init__(self, interfaz=None):
        # Cargar variables de entorno
        load_dotenv()
        
        # Referencia a la interfaz para mostrar eyes.gif cuando habla
        self.interfaz = interfaz
        
        # Reconocimiento de voz
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = Config.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = False
        
        # Síntesis de voz
        self.elevenlabs_client = None
        self.gtts_disponible = False
        self.elevenlabs_disponible = False
        self.mpg123_disponible = False
        self.espeak_disponible = False
        self.sox_disponible = False
        
        # Verificar sounddevice
        self.sounddevice_disponible = self._verificar_sounddevice()
        
        # Inicializar TTS
        #self._inicializar_elevenlabs()
        self._inicializar_gtts_mpg123()
        self._verificar_sox()
        
        if not self.elevenlabs_disponible:
            self._inicializar_gtts_mpg123()
        
        if not self.elevenlabs_disponible and not self.gtts_disponible:
            self._inicializar_espeak()
        
        # Crear carpeta de audio principal
        if not os.path.exists(Config.AUDIO_FOLDER):
            os.makedirs(Config.AUDIO_FOLDER)
            print(f"✅ Carpeta de audios creada: {Config.AUDIO_FOLDER}")
        
        # Mensaje de estado
        self._mostrar_estado_tts()
        self._mostrar_estado_grabacion()
    
    def set_interfaz(self, interfaz):
        """Configurar la interfaz para notificaciones"""
        self.interfaz = interfaz
    
    def _verificar_sounddevice(self):
        """Verifica que sounddevice esté disponible"""
        try:
            devices = sd.query_devices()
            return True
        except Exception as e:
            print(f"⚠️ sounddevice no disponible: {e}")
            return False
    
    def _verificar_sox(self):
        """Verifica que sox esté disponible"""
        try:
            result = subprocess.run(['which', 'sox'], 
                                  capture_output=True, 
                                  text=True)
            if result.returncode == 0:
                self.sox_disponible = True
                return True
            else:
                return False
        except Exception:
            return False
    
    def _inicializar_elevenlabs(self):
        """Inicializar ElevenLabs"""
        try:
            api_key = os.getenv('ELEVENLABS_API_KEY')
            
            if not api_key:
                print("⚠️ ELEVENLABS_API_KEY no encontrada en .env")
                return False
            
            self.elevenlabs_client = ElevenLabs(api_key=api_key)
            self.elevenlabs_disponible = True
            return True
            
        except ImportError:
            print("⚠️ elevenlabs no está instalado")
            return False
        except Exception as e:
            print(f"⚠️ Error al inicializar ElevenLabs: {e}")
            return False
    
    def _inicializar_gtts_mpg123(self):
        """Inicializar gTTS + mpg123"""
        try:
            from gtts import gTTS
            self.gTTS = gTTS
            
            result = subprocess.run(['which', 'mpg123'], 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                self.mpg123_disponible = True
                self.gtts_disponible = True
                return True
            else:
                print("⚠️ mpg123 no está instalado")
                return False
                
        except ImportError:
            print("⚠️ gTTS no está instalado")
            return False
        except Exception as e:
            print(f"⚠️ Error al verificar gTTS/mpg123: {e}")
            return False
    
    def _inicializar_espeak(self):
        """Inicializar espeak"""
        try:
            result = subprocess.run(['which', 'espeak'], 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                self.espeak_disponible = True
                return True
            else:
                print("⚠️ espeak no está instalado")
                return False
                
        except Exception as e:
            print(f"⚠️ Error al verificar espeak: {e}")
            return False
    
    def _mostrar_estado_tts(self):
        """Mostrar estado del sistema TTS"""
        if self.elevenlabs_disponible:
            velocidad_msg = " (con control de velocidad)" if self.sox_disponible else " (velocidad básica)"
            print(f"✅ Sistema TTS: ElevenLabs - CALIDAD ULTRA PREMIUM 🎙️{velocidad_msg}")
        elif self.gtts_disponible and self.mpg123_disponible:
            print("✅ Sistema TTS: Google (gTTS + mpg123) - CALIDAD PREMIUM")
        elif self.espeak_disponible:
            print("✅ Sistema TTS: espeak - Funcional")
        else:
            print("⚠️ Sistema TTS: No disponible")
    
    def _mostrar_estado_grabacion(self):
        """Mostrar estado del sistema de grabación"""
        if self.sounddevice_disponible:
            print("✅ Sistema de Grabación: sounddevice - ÓPTIMO")
        else:
            print("⚠️ Sistema de Grabación: No disponible")
    
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
    
    # ========== SÍNTESIS DE VOZ CON NOTIFICACIÓN ==========
    
    def hablar(self, texto: str, velocidad: float = 1.0):
        """
        Convierte texto a voz y MUESTRA EYES.GIF durante la reproducción
        """
        # SIEMPRE imprimir en consola
        print(f"🤖 Robot dice: {texto}")
        
        # NOTIFICAR A LA INTERFAZ: Empezar a hablar (mostrar eyes.gif)
        if self.interfaz:
            self.interfaz.mostrar_eyes()
        
        # Intentar con ElevenLabs primero
        if self.elevenlabs_disponible:
            if self._hablar_con_elevenlabs(texto, velocidad):
                # NOTIFICAR: Terminó de hablar
                self._termino_de_hablar()
                return
        
        # Si falló, intentar con gTTS + mpg123
        if self.gtts_disponible and self.mpg123_disponible:
            if self._hablar_con_gtts_mpg123(texto):
                self._termino_de_hablar()
                return
        
        # Si falló, intentar con espeak
        if self.espeak_disponible:
            if self._hablar_con_espeak(texto, velocidad):
                self._termino_de_hablar()
                return
        
        # Si todos fallaron, el mensaje ya se imprimió
        self._termino_de_hablar()
    
    def _termino_de_hablar(self):
        """Notificar que terminó de hablar"""
        # No hacemos nada aquí, la interfaz permanece en eyes.gif
        # hasta que explícitamente cambie a otro estado
        pass
    
    def _hablar_con_elevenlabs(self, texto: str, velocidad: float = 1.0) -> bool:
        """Hablar usando ElevenLabs API"""
        try:
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                voice_id="pNInz6obpgDQGcFmaJgB",
                text=texto,
                model_id="eleven_multilingual_v2"
            )
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name
                
                for chunk in audio_generator:
                    if chunk:
                        temp_file.write(chunk)
            
            reproduccion_exitosa = False
            
            # Intentar con sox + mpg123
            if velocidad != 1.0 and self.sox_disponible:
                try:
                    proceso_sox = subprocess.Popen(['sox', temp_filename, '-t', 'mp3', '-', 
                                                   'tempo', str(velocidad)],
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.DEVNULL)
                    subprocess.run(['mpg123', '-q', '-'], 
                                 stdin=proceso_sox.stdout,
                                 check=True,
                                 stderr=subprocess.DEVNULL)
                    proceso_sox.wait()
                    reproduccion_exitosa = True
                except:
                    pass
            
            # Fallback a mpg123 solo
            if not reproduccion_exitosa:
                try:
                    subprocess.run(['mpg123', '-q', temp_filename], 
                                 check=True, 
                                 stderr=subprocess.DEVNULL)
                    reproduccion_exitosa = True
                except:
                    pass
            
            try:
                os.remove(temp_filename)
            except:
                pass
            
            return reproduccion_exitosa
            
        except Exception as e:
            print(f"⚠️ ElevenLabs falló: {e}")
            return False
    
    def _hablar_con_gtts_mpg123(self, texto: str) -> bool:
        """Hablar usando gTTS + mpg123"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            tts = self.gTTS(text=texto, lang='es', slow=False)
            tts.save(temp_filename)
            
            subprocess.run(['mpg123', '-q', temp_filename], check=True)
            
            try:
                os.remove(temp_filename)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"⚠️ gTTS falló: {e}")
            return False
    
    def _hablar_con_espeak(self, texto: str, velocidad: float = 1.0) -> bool:
        """Hablar usando espeak"""
        try:
            velocidad_espeak = int(Config.TTS_RATE * velocidad)
            comando = ['espeak', '-v', 'es', '-s', str(velocidad_espeak), texto]
            subprocess.run(comando, check=True)
            return True
            
        except Exception as e:
            print(f"⚠️ espeak falló: {e}")
            return False
    
    # ========== GRABACIÓN MEJORADA ==========
    
    def grabar(self, duracion: int, person_id: int, exercise_id: int, 
               ejercicio_nombre: str = None, nivel_actual: str = None, 
               numero_sesion: int = None) -> Optional[str]:
        """
        Graba audio usando sounddevice con estructura organizada por usuario
        
        Estructura de carpetas:
        audio_registros/
            {person_id}/
                {nombre_ejercicio}_{nivel_actual}_{numero_sesion}_{fecha}.wav
        
        Args:
            duracion: Duración en segundos
            person_id: ID del niño
            exercise_id: ID del ejercicio
            ejercicio_nombre: Nombre del ejercicio (opcional, para formato mejorado)
            nivel_actual: Nivel actual del niño (opcional, para formato mejorado)
            numero_sesion: Número de sesión actual (opcional, para formato mejorado)
            
        Returns:
            Ruta del archivo grabado o None si falla
        """
        if not self.sounddevice_disponible:
            print("❌ sounddevice no está disponible para grabar")
            return None
        
        try:
            # Crear carpeta del usuario si no existe
            carpeta_usuario = os.path.join(Config.AUDIO_FOLDER, str(person_id))
            os.makedirs(carpeta_usuario, exist_ok=True)
            
            # Generar nombre del archivo según formato solicitado
            fecha = datetime.now().strftime('%Y-%m-%d')
            
            if ejercicio_nombre and nivel_actual and numero_sesion is not None:
                # Formato completo: {nombre_ejercicio}_{nivel_actual}_{numero_sesion}_{fecha}.wav
                nombre_limpio = ejercicio_nombre.replace(' ', '_').replace('/', '_')
                nivel_limpio = nivel_actual.replace(' ', '_')
                nombre_archivo = f"{nombre_limpio}_{nivel_limpio}_sesion{numero_sesion}_{fecha}.wav"
            else:
                # Formato fallback con timestamp
                timestamp = datetime.now().strftime('%H%M%S')
                nombre_archivo = f"ejercicio_{exercise_id}_{fecha}_{timestamp}.wav"
            
            ruta_completa = os.path.join(carpeta_usuario, nombre_archivo)
            
            # Configuración de grabación
            sample_rate = 44100
            channels = 1
            
            print(f"🎙️ Grabando {duracion} segundos en: {ruta_completa}")
            
            # Grabar audio
            audio_data = sd.rec(
                int(duracion * sample_rate),
                samplerate=sample_rate,
                channels=channels,
                dtype='int16'
            )
            
            sd.wait()
            
            # Guardar archivo
            sf.write(ruta_completa, audio_data, sample_rate)
            
            print(f"✅ Audio guardado: {nombre_archivo}")
            return ruta_completa
            
        except Exception as e:
            print(f"⚠️ Error al grabar audio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def grabar_y_escuchar(self, duracion: int, person_id: int, exercise_id: int,
                          ejercicio_nombre: str = None, nivel_actual: str = None,
                          numero_sesion: int = None) -> tuple:
        """
        Graba audio Y reconoce voz simultáneamente
        
        Returns:
            (texto_reconocido, audio_path)
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
                audio_path = self.grabar(
                    duracion, person_id, exercise_id,
                    ejercicio_nombre, nivel_actual, numero_sesion
                )
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
            subprocess.run(['killall', 'mpg123'], stderr=subprocess.DEVNULL)
            subprocess.run(['killall', 'espeak'], stderr=subprocess.DEVNULL)
            subprocess.run(['killall', 'play'], stderr=subprocess.DEVNULL)
            sd.stop()
        except:
            pass


# Alias para compatibilidad
AudioSystem = AudioSystemConInterfaz