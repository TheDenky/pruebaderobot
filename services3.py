"""
SERVICES MEJORADO - Lógica de negocio adaptada a la nueva interfaz
Incluye integración con gamificación y animaciones
"""
import time
from typing import Optional, List
from datetime import datetime
from models import Persona, Ejercicio, Sesion, ResultadoEjercicio, NivelTerapia
from database import Database

# Nota: audio debe ser implementado según tu sistema
# from audio import AudioSystem

from utils import extraer_numero, mensaje_positivo_aleatorio, mensaje_animo_aleatorio


class Config:
    """Configuración simplificada"""
    MIN_AGE = 1
    MAX_AGE = 18
    RECORDING_DURATION = 5
    LEVEL_UP_THRESHOLD = 0.80


class RobotServiceMejorado:
    """Servicio principal del robot con integración de UI mejorada"""
    
    def __init__(self, db: Database, audio):
        self.db = db
        self.audio = audio
        self.interfaz = None
        self.estrellas_sesion = 0
    
    # ========== RF1: EVALUACIÓN INICIAL ==========
    
    def preguntar_primera_vez(self) -> bool:
        """Pregunta si es la primera vez que asiste"""
        if self.interfaz:
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar("¿Es la primera vez que vienes? 🌟")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        respuesta = self.audio.escuchar(timeout=10, phrase_time_limit=5)
        
        if respuesta:
            respuesta_lower = respuesta.lower()
            return any(palabra in respuesta_lower for palabra in ['si', 'sí', 'primera'])
        return False
    
    def registrar_nuevo_usuario(self) -> Optional[Persona]:
        """RF1.1: Registrar nuevo niño con datos personales (versión mejorada)"""
        
        # NOMBRE
        if self.interfaz:
            self.interfaz.actualizar_estado("🎤 Escuchando tu nombre...")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar("¡Hola! ¿Cuál es tu nombre?")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        nombre = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not nombre or len(nombre) < 1:
            self.audio.hablar("No escuché bien tu nombre. ¿Puedes repetir?")
            return None
        
        nombre = nombre.title()
        
        if self.interfaz:
            self.interfaz.actualizar_texto_escuchado(f"Nombre: {nombre}")
        
        print(f"✅ Nombre: {nombre}")
        time.sleep(0.5)
        
        # APELLIDO
        if self.interfaz:
            self.interfaz.actualizar_estado("🎤 Escuchando tu apellido...")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar("¿Cuál es tu apellido?")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        apellido = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not apellido or len(apellido) < 2:
            self.audio.hablar("No escuché bien tu apellido.")
            return None
        
        apellido = apellido.title()
        nombre_completo = f"{nombre} {apellido}"
        
        if self.interfaz:
            self.interfaz.actualizar_texto_escuchado(f"Apellido: {apellido}")
        
        print(f"✅ Apellido: {apellido}")
        time.sleep(0.5)
        
        # EDAD
        if self.interfaz:
            self.interfaz.actualizar_estado("🎤 Escuchando tu edad...")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar("¿Cuántos años tienes?")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        edad_texto = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not edad_texto:
            self.audio.hablar("No escuché tu edad.")
            return None
        
        if self.interfaz:
            self.interfaz.actualizar_texto_escuchado(f"Edad: {edad_texto}")
        
        try:
            edad = extraer_numero(edad_texto)
            if edad < Config.MIN_AGE or edad > Config.MAX_AGE:
                self.audio.hablar(f"La edad debe estar entre {Config.MIN_AGE} y {Config.MAX_AGE} años.")
                return None
            print(f"✅ Edad: {edad} años")
        except:
            self.audio.hablar("No entendí tu edad.")
            return None
        
        time.sleep(0.5)
        
        # CONFIRMAR
        if self.interfaz:
            self.interfaz.actualizar_estado("✓ Confirmando datos...")
            self.interfaz.actualizar_texto_escuchado(f"{nombre_completo}, {edad} años")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar(f"Tu nombre es {nombre_completo}, tienes {edad} años. ¿Es correcto?")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        confirmacion = self.audio.escuchar(timeout=10, phrase_time_limit=5)
        
        if confirmacion and any(palabra in confirmacion.lower() for palabra in ['si', 'sí']):
            # GUARDAR EN BASE DE DATOS
            if self.interfaz:
                self.interfaz.actualizar_estado("💾 Guardando datos...")
                self.interfaz.robot_hablando(True)
            
            self.audio.hablar("Perfecto, guardando tus datos.")
            
            if self.interfaz:
                self.interfaz.robot_hablando(False)
            
            persona = Persona(name=nombre_completo, age=edad)
            person_id = self.db.crear_persona(persona)
            persona.person_id = person_id
            
            if person_id:
                if self.interfaz:
                    self.interfaz.actualizar_estado("✅ ¡Listo! Datos guardados")
                    self.interfaz.actualizar_usuario(nombre_completo)
                    self.interfaz.robot_hablando(True)
                
                self.audio.hablar("¡Excelente! Ya estás registrado.")
                
                if self.interfaz:
                    self.interfaz.robot_hablando(False)
                
                print(f"✅ Usuario registrado con ID: {person_id}\n")
                return persona
            else:
                self.audio.hablar("Hubo un error al guardar.")
                return None
        else:
            self.audio.hablar("Registro cancelado.")
            return None
    
    def realizar_test_diagnostico(self, persona: Persona) -> NivelTerapia:
        """RF1.2 y RF1.3: Test diagnóstico inicial y clasificación (mejorado)"""
        if self.interfaz:
            self.interfaz.actualizar_estado("🎯 Test inicial...")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar(f"Hola {persona.name}, vamos a hacer un pequeño test para conocerte mejor. ¡No te preocupes!")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        time.sleep(1)
        
        # Test simplificado (3 palabras)
        preguntas_test = [
            ("Repite: CASA", "casa"),
            ("Repite: PELOTA", "pelota"),
            ("Repite: MARIPOSA", "mariposa")
        ]
        
        aciertos = 0
        for i, (pregunta, respuesta_esperada) in enumerate(preguntas_test, 1):
            if self.interfaz:
                self.interfaz.actualizar_estado(f"🎯 Pregunta {i}/{len(preguntas_test)}")
                self.interfaz.robot_hablando(True)
            
            self.audio.hablar(pregunta)
            
            if self.interfaz:
                self.interfaz.robot_hablando(False)
            
            respuesta = self.audio.escuchar(timeout=5, phrase_time_limit=5)
            
            if respuesta and respuesta_esperada in respuesta.lower():
                aciertos += 1
                
                if self.interfaz:
                    self.interfaz.celebrar_exito()
                    self.interfaz.robot_hablando(True)
                
                self.audio.hablar("¡Muy bien! ⭐")
                
                if self.interfaz:
                    self.interfaz.robot_hablando(False)
            else:
                if self.interfaz:
                    self.interfaz.mostrar_error()
            
            time.sleep(1)
        
        # RF1.3: Clasificación en nivel terapéutico
        tasa_exito = aciertos / len(preguntas_test)
        
        if tasa_exito >= 0.8:
            nivel = NivelTerapia.INTERMEDIO
        elif tasa_exito >= 0.5:
            nivel = NivelTerapia.BASICO
        else:
            nivel = NivelTerapia.INICIAL
        
        # RF1.4: Almacenar nivel en perfil
        self.db.actualizar_nivel_persona(persona.person_id, nivel)
        persona.nivel_actual = nivel
        
        if self.interfaz:
            self.interfaz.actualizar_estado(f"📊 Nivel asignado: {nivel.name}")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar(f"¡Muy bien! Tu nivel es: {nivel.name}")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        return nivel
    
    # ========== RF3: RECONOCIMIENTO DE USUARIO ==========
    
    def buscar_usuario_existente(self) -> Optional[Persona]:
        """RF3.1: Identificar al niño mediante nombre (mejorado)"""
        if self.interfaz:
            self.interfaz.actualizar_estado("🎤 ¿Cuál es tu nombre?")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar("¡Hola de nuevo! ¿Cuál es tu nombre?")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        nombre = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not nombre:
            self.audio.hablar("No escuché tu nombre.")
            return None
        
        nombre = nombre.title()
        
        if self.interfaz:
            self.interfaz.actualizar_texto_escuchado(f"Buscando: {nombre}")
        
        print(f"🔍 Buscando: {nombre}")
        
        # Buscar en base de datos
        if self.interfaz:
            self.interfaz.actualizar_estado("🔍 Buscando en la base de datos...")
        
        persona = self.db.buscar_persona_por_nombre(nombre)
        
        if persona:
            # RF3.2 y RF3.3: Recuperar progreso
            ultima_sesion = self.db.obtener_ultima_sesion(persona.person_id)
            if ultima_sesion:
                persona.nivel_actual = ultima_sesion.nivel
            
            if self.interfaz:
                self.interfaz.actualizar_estado(f"✅ ¡Te encontré!")
                self.interfaz.actualizar_usuario(persona.name)
                self.interfaz.robot_hablando(True)
            
            self.audio.hablar(f"¡Te encontré, {persona.name}! Bienvenido de nuevo. 🎉")
            
            if self.interfaz:
                self.interfaz.robot_hablando(False)
            
            print(f"✅ Usuario encontrado: {persona.name} (ID: {persona.person_id})\n")
            return persona
        else:
            if self.interfaz:
                self.interfaz.actualizar_estado("❌ No te encontré")
            
            self.audio.hablar("No te encontré en mi memoria.")
            print(f"❌ Usuario no encontrado\n")
            return None
    
    # ========== RF2: ASIGNACIÓN Y EJECUCIÓN DE TERAPIAS ==========
    
    def realizar_sesion_ejercicios(self, persona: Persona):
        """RF2: Realizar sesión completa de ejercicios (mejorado)"""
        
        if self.interfaz:
            self.interfaz.actualizar_estado("🎯 ¡Iniciando ejercicios!")
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar("Ahora vamos a hacer ejercicios divertidos. ¡Vamos a aprender juntos!")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
            # Resetear estrellas
            self.interfaz.estrellas.reset()
        
        time.sleep(1)
        
        # RF2.1: Obtener ejercicios del nivel
        ejercicios = self.db.obtener_ejercicios_por_nivel(persona.nivel_actual)
        
        if not ejercicios:
            print("❌ No hay ejercicios disponibles\n")
            ejercicios = self.db.obtener_todos_ejercicios()
            if not ejercicios:
                self.audio.hablar("No hay ejercicios disponibles ahora.")
                return
        
        print(f"📋 Total de ejercicios: {len(ejercicios)}\n")
        
        # Actualizar progreso inicial
        if self.interfaz:
            self.interfaz.actualizar_progreso(0, len(ejercicios))
        
        # Crear sesión
        sesion = Sesion(
            person_id=persona.person_id,
            nivel=persona.nivel_actual,
            fecha=datetime.now(),
            ejercicios_completados=[]
        )
        
        self.estrellas_sesion = 0
        
        # Ejecutar cada ejercicio
        for i, ejercicio in enumerate(ejercicios, 1):
            print(f"--- Ejercicio {i}/{len(ejercicios)} ---")
            print(f"Palabra: {ejercicio.word}")
            
            # RF2.2 y RF2.3: Ejecutar ejercicio con apoyo multimodal
            resultado = self._ejecutar_ejercicio_mejorado(ejercicio, persona, i, len(ejercicios))
            sesion.ejercicios_completados.append(resultado)
            
            # Actualizar progreso
            if self.interfaz:
                self.interfaz.actualizar_progreso(i, len(ejercicios))
            
            # RF4.2: Detectar frustración
            if self._detectar_frustracion(sesion.ejercicios_completados):
                if self.interfaz:
                    self.interfaz.actualizar_estado("😊 Pequeño descanso...")
                    self.interfaz.robot_hablando(True)
                
                self.audio.hablar("Vamos a hacer un pequeño descanso. Estás haciendo un gran trabajo. 💪")
                
                if self.interfaz:
                    self.interfaz.robot_hablando(False)
                
                time.sleep(2)
            
            print()
            time.sleep(1)
        
        # Limpiar pantalla
        if self.interfaz:
            self.interfaz.limpiar_ejercicio()
            self.interfaz.actualizar_estado(
                f"✅ ¡Completado! {sesion.ejercicios_correctos}/{sesion.total_ejercicios} correctos"
            )
        
        # RF4.1: Registrar sesión
        sesion_id = self.db.crear_sesion(sesion)
        sesion.sesion_id = sesion_id
        
        # RF4.3: Evaluar progreso
        self._evaluar_progreso_mejorado(persona, sesion)
        
        print(f"✅ Sesión completada: {sesion.ejercicios_correctos} correctos de {sesion.total_ejercicios}")
        print(f"📊 Tasa de éxito: {sesion.tasa_exito*100:.1f}%")
        print(f"⭐ Estrellas ganadas: {self.estrellas_sesion}\n")
    
    def _ejecutar_ejercicio_mejorado(self, ejercicio: Ejercicio, persona: Persona, 
                                     num: int, total: int) -> ResultadoEjercicio:
        """Ejecutar un ejercicio individual con interfaz mejorada"""
        
        # Mostrar en pantalla - RF2.2
        if self.interfaz:
            self.interfaz.limpiar_ejercicio()
            time.sleep(0.3)
            self.interfaz.mostrar_ejercicio(ejercicio.word)
            self.interfaz.actualizar_estado(f"🎯 Ejercicio {num}/{total}: {ejercicio.word}")
        
        # RF2.2: Apoyo multimodal - voz
        if self.interfaz:
            self.interfaz.robot_hablando(True)
        
        self.audio.hablar(f"Repite la palabra: {ejercicio.word}")
        
        if self.interfaz:
            self.interfaz.robot_hablando(False)
        
        time.sleep(1)
        
        # Grabar y escuchar simultáneamente
        if self.interfaz:
            self.interfaz.actualizar_estado(f"🎤 Escuchando...")
        
        inicio = time.time()
        respuesta, archivo_audio = self.audio.grabar_y_escuchar(
            duracion=Config.RECORDING_DURATION,
            person_id=persona.person_id,
            exercise_id=ejercicio.exercise_id
        )
        tiempo_respuesta = time.time() - inicio
        
        # Actualizar interfaz
        if respuesta:
            if self.interfaz:
                self.interfaz.actualizar_texto_escuchado(f"Dijiste: {respuesta}")
            print(f"📢 Respuesta: '{respuesta}'")
        else:
            if self.interfaz:
                self.interfaz.actualizar_texto_escuchado("(No se detectó respuesta)")
            print(f"📢 Respuesta: (silencio)")
        
        if archivo_audio:
            print(f"💾 Audio guardado: {archivo_audio}")
        
        # Evaluar respuesta
        correcto = False
        if respuesta:
            correcto = ejercicio.word.lower() in respuesta.lower()
        
        # RF2.3: Retroalimentación empática con animaciones
        if correcto:
            if self.interfaz:
                self.interfaz.celebrar_exito()
                self.interfaz.robot_hablando(True)
            
            mensaje = mensaje_positivo_aleatorio()
            self.audio.hablar(mensaje)
            
            if self.interfaz:
                self.interfaz.robot_hablando(False)
            
            self.estrellas_sesion += 1
        else:
            if self.interfaz:
                self.interfaz.mostrar_error()
                self.interfaz.robot_hablando(True)
            
            mensaje = mensaje_animo_aleatorio()
            self.audio.hablar(mensaje)
            
            if self.interfaz:
                self.interfaz.robot_hablando(False)
        
        time.sleep(0.5)
        
        # RF4.1: Crear resultado
        return ResultadoEjercicio(
            ejercicio_id=ejercicio.exercise_id,
            respuesta=respuesta or "",
            correcto=correcto,
            tiempo_respuesta=tiempo_respuesta,
            intentos=1,
            audio_path=archivo_audio
        )
    
    # ========== RF4: MONITOREO Y APRENDIZAJE ADAPTATIVO ==========
    
    def _detectar_frustracion(self, resultados: List[ResultadoEjercicio]) -> bool:
        """RF4.2: Detectar señales de frustración"""
        if len(resultados) < 3:
            return False
        
        # Tres fallos consecutivos pueden indicar frustración
        ultimos_tres = resultados[-3:]
        return all(not r.correcto for r in ultimos_tres)
    
    def _evaluar_progreso_mejorado(self, persona: Persona, sesion: Sesion):
        """RF4.3 y RF4.4: Evaluar si debe subir de nivel con celebración"""
        
        if not sesion.fue_exitosa():
            return
        
        if not persona.puede_subir_nivel(sesion.tasa_exito):
            return
        
        # Subir de nivel
        niveles = list(NivelTerapia)
        indice_actual = niveles.index(persona.nivel_actual)
        
        if indice_actual < len(niveles) - 1:
            nuevo_nivel = niveles[indice_actual + 1]
            
            # RF4.4: Actualizar y almacenar nuevo nivel
            self.db.actualizar_nivel_persona(persona.person_id, nuevo_nivel)
            persona.nivel_actual = nuevo_nivel
            
            # Celebración especial
            if self.interfaz:
                self.interfaz.actualizar_estado("🎉 ¡NIVEL NUEVO!")
                self.interfaz.robot_hablando(True)
            
            self.audio.hablar(f"¡Felicidades! ¡Has subido al nivel {nuevo_nivel.name}! Eres increíble. 🏆")
            
            if self.interfaz:
                self.interfaz.robot_hablando(False)
                # Agregar estrellas bonus
                for _ in range(3):
                    self.interfaz.estrellas.agregar_estrella()
                    time.sleep(0.2)
            
            print(f"🎉 ¡Subió al nivel {nuevo_nivel.name}!")
            time.sleep(2)


# Alias para compatibilidad
RobotService = RobotServiceMejorado
