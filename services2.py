"""
SERVICES - Lógica de negocio principal
Todos los casos de uso y servicios en un solo archivo
"""
import time
from typing import Optional, List
from datetime import datetime
from models import Persona, Ejercicio, Sesion, ResultadoEjercicio, NivelTerapia
from database import Database
from audio import AudioSystem
from ui import InterfazEjercicios
from utils import extraer_numero, mensaje_positivo_aleatorio, mensaje_animo_aleatorio
from config import Config


class RobotService:
    """Servicio principal del robot con toda la lógica de negocio"""
    
    def __init__(self, db: Database, audio: AudioSystem):
        self.db = db
        self.audio = audio
        self.interfaz = None
    
    # ========== RF1: EVALUACIÓN INICIAL ==========
    
    def preguntar_primera_vez(self) -> bool:
        """Pregunta si es la primera vez que asiste"""
        self.audio.hablar("¿Es la primera vez que asistes?")
        respuesta = self.audio.escuchar(timeout=10, phrase_time_limit=5)
        
        if respuesta:
            respuesta_lower = respuesta.lower()
            return any(palabra in respuesta_lower for palabra in ['si', 'sí', 'primera'])
        return False
    
    def registrar_nuevo_usuario(self) -> Optional[Persona]:
        """RF1.1: Registrar nuevo niño con datos personales"""
        
        # NOMBRE
        self.interfaz.actualizar_estado("🎤 Escuchando tu nombre...")
        self.audio.hablar("¿Cuál es tu nombre?")
        nombre = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not nombre or len(nombre) < 1:
            self.audio.hablar("No escuché bien tu nombre.")
            return None
        
        nombre = nombre.title()
        self.interfaz.actualizar_texto_escuchado(f"Nombre: {nombre}")
        print(f"✅ Nombre: {nombre}")
        time.sleep(0.5)
        
        # APELLIDO
        self.interfaz.actualizar_estado("🎤 Escuchando tu apellido...")
        self.audio.hablar("¿Cuál es tu apellido?")
        apellido = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not apellido or len(apellido) < 2:
            self.audio.hablar("No escuché bien tu apellido.")
            return None
        
        apellido = apellido.title()
        nombre_completo = f"{nombre} {apellido}"
        self.interfaz.actualizar_texto_escuchado(f"Apellido: {apellido}")
        print(f"✅ Apellido: {apellido}")
        time.sleep(0.5)
        
        # EDAD
        self.interfaz.actualizar_estado("🎤 Escuchando tu edad...")
        self.audio.hablar("¿Cuántos años tienes?")
        edad_texto = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not edad_texto:
            self.audio.hablar("No escuché tu edad.")
            return None
        
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
        self.interfaz.actualizar_estado("❓ Confirmando datos...")
        self.interfaz.actualizar_texto_escuchado(f"{nombre_completo}, {edad} años")
        self.audio.hablar(f"Tu nombre es {nombre_completo}, tienes {edad} años. ¿Es correcto?")
        
        confirmacion = self.audio.escuchar(timeout=10, phrase_time_limit=5)
        
        if confirmacion and any(palabra in confirmacion.lower() for palabra in ['si', 'sí']):
            # GUARDAR EN BASE DE DATOS
            self.interfaz.actualizar_estado("💾 Guardando datos...")
            self.audio.hablar("Guardando tus datos.")
            
            persona = Persona(name=nombre_completo, age=edad)
            person_id = self.db.crear_persona(persona)
            persona.person_id = person_id
            
            if person_id:
                self.interfaz.actualizar_estado("✅ Datos guardados")
                self.interfaz.actualizar_usuario(nombre_completo)
                self.audio.hablar("Datos guardados correctamente.")
                print(f"✅ Usuario registrado con ID: {person_id}\n")
                return persona
            else:
                self.audio.hablar("Hubo un error al guardar.")
                return None
        else:
            self.audio.hablar("Registro cancelado.")
            return None
    
    def realizar_test_diagnostico(self, persona: Persona) -> NivelTerapia:
        """RF1.2 y RF1.3: Test diagnóstico inicial y clasificación"""
        self.audio.hablar(f"Hola {persona.name}, vamos a hacer un test inicial.")
        
        # Test simplificado (3 palabras)
        preguntas_test = [
            ("Repite: CASA", "casa"),
            ("Repite: PELOTA", "pelota"),
            ("Repite: MARIPOSA", "mariposa")
        ]
        
        aciertos = 0
        for pregunta, respuesta_esperada in preguntas_test:
            self.audio.hablar(pregunta)
            respuesta = self.audio.escuchar(timeout=5, phrase_time_limit=5)
            
            if respuesta and respuesta_esperada in respuesta.lower():
                aciertos += 1
                self.audio.hablar("Muy bien")
        
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
        
        self.audio.hablar(f"Tu nivel es: {nivel.name}")
        return nivel
    
    # ========== RF3: RECONOCIMIENTO DE USUARIO ==========
    
    def buscar_usuario_existente(self) -> Optional[Persona]:
        """RF3.1: Identificar al niño mediante nombre"""
        self.interfaz.actualizar_estado("🎤 ¿Cuál es tu nombre?")
        self.audio.hablar("¿Cuál es tu nombre?")
        nombre = self.audio.escuchar(timeout=10, phrase_time_limit=10)
        
        if not nombre:
            self.audio.hablar("No escuché tu nombre.")
            return None
        
        nombre = nombre.title()
        self.interfaz.actualizar_texto_escuchado(f"Buscando: {nombre}")
        print(f"🔍 Buscando: {nombre}")
        
        # Buscar en base de datos
        self.interfaz.actualizar_estado("🔍 Buscando en base de datos...")
        persona = self.db.buscar_persona_por_nombre(nombre)
        
        if persona:
            # RF3.2 y RF3.3: Recuperar progreso
            ultima_sesion = self.db.obtener_ultima_sesion(persona.person_id)
            if ultima_sesion:
                persona.nivel_actual = ultima_sesion.nivel
                self.audio.hablar(f"Continuaremos desde el nivel {persona.nivel_actual.name}")
            
            self.interfaz.actualizar_estado(f"✅ Encontrado: {persona.name}")
            self.interfaz.actualizar_usuario(persona.name)
            self.audio.hablar(f"Te encontré {persona.name}. Bienvenido de nuevo.")
            print(f"✅ Usuario encontrado: {persona.name} (ID: {persona.person_id})\n")
            return persona
        else:
            self.interfaz.actualizar_estado("❌ No encontrado")
            self.audio.hablar("No te encontré en la base de datos.")
            print(f"❌ Usuario no encontrado\n")
            return None
    
    # ========== RF2: ASIGNACIÓN Y EJECUCIÓN DE TERAPIAS ==========
    
    def realizar_sesion_ejercicios(self, persona: Persona):
        """RF2: Realizar sesión completa de ejercicios"""
        from utils import imprimir_seccion
        
        imprimir_seccion("EJERCICIOS DE VOZ")
        
        self.interfaz.actualizar_estado("🎯 Iniciando ejercicios...")
        self.audio.hablar("Ahora vamos a realizar unos ejercicios.")
        time.sleep(1)
        
        # RF2.1: Obtener ejercicios del nivel
        ejercicios = self.db.obtener_ejercicios_por_nivel(persona.nivel_actual)
        
        if not ejercicios:
            print("❌ No hay ejercicios disponibles\n")
            # Usar todos los ejercicios si no hay específicos del nivel
            ejercicios = self.db.obtener_todos_ejercicios()
            if not ejercicios:
                self.audio.hablar("No hay ejercicios disponibles.")
                return
        
        print(f"📋 Total de ejercicios: {len(ejercicios)}\n")
        
        # Crear sesión
        sesion = Sesion(
            person_id=persona.person_id,
            nivel=persona.nivel_actual,
            fecha=datetime.now(),
            ejercicios_completados=[]
        )
        
        # Ejecutar cada ejercicio
        for i, ejercicio in enumerate(ejercicios, 1):
            print(f"--- Ejercicio {i}/{len(ejercicios)} ---")
            print(f"Palabra: {ejercicio.word}")
            
            # RF2.2 y RF2.3: Ejecutar ejercicio con apoyo multimodal
            resultado = self._ejecutar_ejercicio(ejercicio, persona, i, len(ejercicios))
            sesion.ejercicios_completados.append(resultado)
            
            # RF4.2: Detectar frustración
            if self._detectar_frustracion(sesion.ejercicios_completados):
                self.audio.hablar("Vamos a hacer un pequeño descanso")
                time.sleep(2)
            
            print()
            time.sleep(1)
        
        # Limpiar pantalla
        self.interfaz.limpiar_ejercicio()
        self.interfaz.actualizar_estado(
            f"✅ Ejercicios completados: {sesion.ejercicios_correctos}/{sesion.total_ejercicios}"
        )
        
        # RF4.1: Registrar sesión
        sesion_id = self.db.crear_sesion(sesion)
        sesion.sesion_id = sesion_id
        
        # RF4.3: Evaluar progreso
        self._evaluar_progreso(persona, sesion)
        
        print(f"✅ Sesión completada: {sesion.ejercicios_correctos} correctos de {sesion.total_ejercicios}")
        print(f"📊 Tasa de éxito: {sesion.tasa_exito*100:.1f}%\n")
    
    def _ejecutar_ejercicio(self, ejercicio: Ejercicio, persona: Persona, 
                           num: int, total: int) -> ResultadoEjercicio:
        """Ejecutar un ejercicio individual"""
        
        # Mostrar en pantalla - RF2.2
        self.interfaz.limpiar_ejercicio()
        time.sleep(0.3)
        self.interfaz.mostrar_ejercicio(ejercicio.word)
        self.interfaz.actualizar_estado(f"🎯 Ejercicio {num}/{total}: {ejercicio.word}")
        
        # RF2.2: Apoyo multimodal - voz
        self.audio.hablar(f"Repite la palabra: {ejercicio.word}")
        time.sleep(1)
        
        # Grabar y escuchar simultáneamente
        self.interfaz.actualizar_estado(f"🎤 Escuchando y grabando...")
        
        inicio = time.time()
        respuesta, archivo_audio = self.audio.grabar_y_escuchar(
            duracion=Config.RECORDING_DURATION,
            person_id=persona.person_id,
            exercise_id=ejercicio.exercise_id
        )
        tiempo_respuesta = time.time() - inicio
        
        # Actualizar interfaz
        if respuesta:
            self.interfaz.actualizar_texto_escuchado(f"Dijiste: {respuesta}")
            print(f"📢 Respuesta: '{respuesta}'")
        else:
            self.interfaz.actualizar_texto_escuchado("(No se detectó respuesta)")
            print(f"📢 Respuesta: (silencio)")
        
        if archivo_audio:
            print(f"💾 Audio guardado: {archivo_audio}")
        
        # Evaluar respuesta
        correcto = False
        if respuesta:
            correcto = ejercicio.word.lower() in respuesta.lower()
        
        # RF2.3: Retroalimentación empática
        if correcto:
            self.audio.hablar(mensaje_positivo_aleatorio())
        else:
            self.audio.hablar(mensaje_animo_aleatorio())
        
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
    
    def _evaluar_progreso(self, persona: Persona, sesion: Sesion):
        """RF4.3 y RF4.4: Evaluar si debe subir de nivel"""
        
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
            
            self.audio.hablar(f"¡Felicidades! Has subido al nivel {nuevo_nivel.name}")
            print(f"🎉 ¡Subió al nivel {nuevo_nivel.name}!")