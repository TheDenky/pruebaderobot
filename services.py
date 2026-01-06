"""
SERVICES CON INTERFAZ UNIFICADA Y GRABACIÓN DE AUDIO
Usa los diferentes estados de la interfaz según el flujo
Graba automáticamente los audios de cada ejercicio de forma organizada
"""
import time
from typing import Optional, List
from datetime import datetime
from models import Persona, Ejercicio, Sesion, ResultadoEjercicio, NivelTerapia
from database import Database

# Importar sistema de IA
from chatopenai import (
    consultar, validar_si_no, validar_nombre, validar_edad,
    comparar_palabras, detectar_salir, feedback_motivador
)
from sistema_reintentos import (
    preguntar_con_reintentos, escuchar_con_reintentos,
    confirmar_con_usuario, pedir_nombre_con_reintentos,
    pedir_edad_con_reintentos, evaluacion_ejercicio_con_ia,
    manejar_frustracion, ConfigReintentos
)


class Config:
    """Configuración simplificada"""
    MIN_AGE = 1
    MAX_AGE = 18
    RECORDING_DURATION = 5
    LEVEL_UP_THRESHOLD = 0.80


class RobotServiceInterfazUnificada:
    """Servicio que usa interfaz unificada y graba audios"""
    
    def __init__(self, db: Database, audio):
        self.db = db
        self.audio = audio
        self.interfaz = None
        self.estrellas_sesion = 0
        self.numero_sesion_actual = 0
        print("✅ RobotService inicializado con interfaz unificada y grabación de audio")
    
    def set_interfaz(self, interfaz):
        """Configurar la interfaz unificada"""
        self.interfaz = interfaz
        # También configurar en audio
        if self.audio:
            self.audio.set_interfaz(interfaz)
    
    # ========== RF1: EVALUACIÓN INICIAL ==========
    
    def preguntar_primera_vez(self) -> bool:
        """Pregunta si es la primera vez (mostrar eyes.gif mientras habla)"""
        print("\n🎯 Preguntando si es primera vez...")
        
        def validador(respuesta: str):
            return validar_si_no(respuesta)
        
        # La interfaz mostrará eyes.gif automáticamente cuando audio.hablar() se ejecute
        
        exito, resultado = preguntar_con_reintentos(
            audio_system=self.audio,
            pregunta="¿Es la primera vez que vienes?",
            validador=validador,
            mensajes_reintento=[
                "¿Es tu primera vez aquí? Di sí o no.",
                "¿Primera vez? Sí o no.",
                "Dime solo: sí o no."
            ],
            max_intentos=3,
            permitir_salir=False,
            interfaz=None  # No usamos interfaz de texto
        )
        
        if not exito:
            print("⚠️ No se pudo determinar. Asumiendo primera vez.")
            return True
        
        es_primera = (resultado == 'si')
        print(f"✅ Es primera vez: {es_primera}")
        return es_primera
    
    def registrar_nuevo_usuario(self) -> Optional[Persona]:
        """RF1.1: Registrar nuevo niño - Muestra eyes.gif mientras habla"""
        print("\n📝 === REGISTRO NUEVO USUARIO ===")
        
        # Saludo personalizado
        saludo = consultar("Di un saludo corto para un niño nuevo que viene a terapia de habla")
        self.audio.hablar(saludo)  # Automáticamente muestra eyes.gif
        time.sleep(1)
        
        # === NOMBRE ===
        nombre = pedir_nombre_con_reintentos(
            audio_system=self.audio,
            interfaz=None
        )
        
        if not nombre:
            self.audio.hablar("Lo siento, no pude entender tu nombre.")
            return None
        
        print(f"✅ Nombre obtenido: {nombre}")
        
        # MOSTRAR EL NOMBRE EN LA INTERFAZ
        if self.interfaz:
            self.interfaz.mostrar_nombre(nombre)
            time.sleep(2)  # Dar tiempo para ver el nombre
        
        # Confirmar nombre (mostrará eyes.gif al hablar)
        self.audio.hablar(f"Mucho gusto, {nombre}.")
        time.sleep(0.5)
        
        # === APELLIDO ===
        def validador_apellido(respuesta: str):
            es_valido, apellido = validar_nombre(respuesta)
            return es_valido, apellido
        
        exito, apellido = preguntar_con_reintentos(
            audio_system=self.audio,
            pregunta="¿Cuál es tu apellido?",
            validador=validador_apellido,
            mensajes_reintento=[
                "No entendí tu apellido. ¿Cuál es?",
                "Tu apellido, por favor.",
                "Dime tu apellido una vez más."
            ],
            max_intentos=3,
            permitir_salir=False,
            interfaz=None
        )
        
        if not exito or not apellido:
            apellido = ""
            print("⚠️ No se obtuvo apellido")
        else:
            print(f"✅ Apellido obtenido: {apellido}")
        
        nombre_completo = f"{nombre} {apellido}".strip()
        
        # MOSTRAR NOMBRE COMPLETO
        if self.interfaz:
            self.interfaz.mostrar_nombre(nombre_completo)
            time.sleep(2)
        
        # === EDAD ===
        edad = pedir_edad_con_reintentos(
            audio_system=self.audio,
            interfaz=None
        )
        
        if not edad:
            self.audio.hablar("No pude entender tu edad. Pero está bien, sigamos.")
            return None
        
        print(f"✅ Edad obtenida: {edad} años")
        
        # === CONFIRMACIÓN ===
        confirmado = confirmar_con_usuario(
            audio_system=self.audio,
            mensaje_confirmacion=f"Tu nombre es {nombre_completo}, tienes {edad} años. ¿Es correcto?",
            interfaz=None
        )
        
        if not confirmado:
            self.audio.hablar("Está bien. Podemos intentar de nuevo después.")
            return None
        
        # === GUARDAR EN BASE DE DATOS ===
        self.audio.hablar("Perfecto. Guardando tus datos.")
        
        persona = Persona(name=nombre_completo, age=edad)
        person_id = self.db.crear_persona(persona)
        persona.person_id = person_id
        
        if person_id:
            mensaje_exito = feedback_motivador("exito")
            self.audio.hablar(mensaje_exito)
            
            print(f"✅ Usuario registrado con ID: {person_id}\n")
            return persona
        else:
            self.audio.hablar("Hubo un error al guardar. Pero puedes continuar.")
            return None
    
    def realizar_test_diagnostico(self, persona: Persona) -> NivelTerapia:
        """RF1.2 y RF1.3: Test diagnóstico"""
        print("\n🎯 === TEST DIAGNÓSTICO ===")
        
        self.audio.hablar(f"Hola {persona.name}. Vamos a hacer un pequeño test.")
        time.sleep(1)
        
        # Test simplificado
        preguntas_test = [
            ("Di la palabra: CASA", "casa"),
            ("Di la palabra: PELOTA", "pelota"),
            ("Di la palabra: MARIPOSA", "mariposa")
        ]
        
        aciertos = 0
        total = len(preguntas_test)
        
        for i, (pregunta, palabra_esperada) in enumerate(preguntas_test, 1):
            print(f"\n--- Test {i}/{total}: {palabra_esperada.upper()} ---")
            
            # Hacer la pregunta (mostrará eyes.gif)
            self.audio.hablar(pregunta)
            
            # Evaluar con IA
            correcto, respuesta, feedback_ia = evaluacion_ejercicio_con_ia(
                audio_system=self.audio,
                palabra_esperada=palabra_esperada,
                interfaz=None,
                max_intentos=2
            )
            
            if correcto:
                aciertos += 1
            
            # Dar feedback (mostrará eyes.gif)
            self.audio.hablar(feedback_ia)
            time.sleep(1)
        
        # Clasificación
        tasa_exito = aciertos / total
        print(f"\n📊 Resultado test: {aciertos}/{total} ({tasa_exito*100:.0f}%)")
        
        if tasa_exito >= 0.8:
            nivel = NivelTerapia.INTERMEDIO
        elif tasa_exito >= 0.5:
            nivel = NivelTerapia.BASICO
        else:
            nivel = NivelTerapia.INICIAL
        
        # Almacenar nivel
        self.db.actualizar_nivel_persona(persona.person_id, nivel)
        persona.nivel_actual = nivel
        
        self.audio.hablar(f"Muy bien. Tu nivel es: {nivel.name}")
        
        print(f"✅ Nivel asignado: {nivel.name}\n")
        return nivel
    
    # ========== RF3: RECONOCIMIENTO DE USUARIO ==========
    
    def buscar_usuario_existente(self) -> Optional[Persona]:
        """RF3.1: Identificar al niño"""
        print("\n🔍 === BÚSQUEDA DE USUARIO ===")
        
        nombre = pedir_nombre_con_reintentos(
            audio_system=self.audio,
            interfaz=None
        )
        
        if not nombre:
            self.audio.hablar("No pude entender tu nombre.")
            return None
        
        print(f"🔍 Buscando: {nombre}")
        
        # MOSTRAR NOMBRE MIENTRAS BUSCA
        if self.interfaz:
            self.interfaz.mostrar_nombre(nombre)
            time.sleep(1)
        
        # Buscar en base de datos
        persona = self.db.buscar_persona_por_nombre(nombre)
        
        if persona:
            # Recuperar progreso
            ultima_sesion = self.db.obtener_ultima_sesion(persona.person_id)
            if ultima_sesion:
                persona.nivel_actual = ultima_sesion.nivel
            
            # MOSTRAR NOMBRE COMPLETO
            if self.interfaz:
                self.interfaz.mostrar_nombre(persona.name)
                time.sleep(2)
            
            # Saludo personalizado (mostrará eyes.gif)
            saludo = consultar(
                f"Di un saludo corto de bienvenida para {persona.name}, un niño que regresa a terapia",
                contexto=f"El niño está en nivel {persona.nivel_actual.name}"
            )
            self.audio.hablar(saludo)
            
            print(f"✅ Usuario encontrado: {persona.name} - Nivel {persona.nivel_actual.name}\n")
            return persona
        else:
            self.audio.hablar("No te encontré en mi memoria. Vamos a registrarte.")
            print("❌ Usuario no encontrado\n")
            return None
    
    # ========== RF2: ASIGNACIÓN Y EJECUCIÓN DE TERAPIAS ==========
    
    def realizar_sesion_ejercicios(self, persona: Persona):
        """RF2: Sesión completa - Muestra ejercicios con imágenes y GRABA AUDIOS"""
        print("\n🎯 === SESIÓN DE EJERCICIOS ===")
        
        # Calcular número de sesión
        sesiones_previas = self.db.obtener_sesiones_por_persona(persona.person_id)
        self.numero_sesion_actual = len(sesiones_previas) + 1
        print(f"📊 Sesión número: {self.numero_sesion_actual}")
        
        # Mensaje inicial (mostrará eyes.gif)
        intro = consultar(
            "Di una frase muy corta motivando a un niño a hacer ejercicios de habla",
            contexto="Debe ser entusiasta y positivo"
        )
        self.audio.hablar(intro)
        time.sleep(1)
        
        # Obtener ejercicios del nivel
        ejercicios = self.db.obtener_ejercicios_por_nivel(persona.nivel_actual)
        
        if not ejercicios:
            print("⚠️ No hay ejercicios para este nivel")
            ejercicios = self.db.obtener_todos_ejercicios()
            if not ejercicios:
                self.audio.hablar("No hay ejercicios disponibles ahora.")
                return
        
        print(f"📋 Total ejercicios: {len(ejercicios)}")
        
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
            print(f"\n{'='*60}")
            print(f"Ejercicio {i}/{len(ejercicios)}: {ejercicio.word}")
            print('='*60)
            
            # Verificar si quiere continuar
            if not manejar_frustracion(self.audio, sesion, None):
                print("ℹ️ Sesión terminada por el usuario")
                break
            
            # Ejecutar ejercicio CON IMAGEN Y GRABACIÓN DE AUDIO
            resultado = self._ejecutar_ejercicio_con_ia_y_grabacion(
                ejercicio, persona, i, len(ejercicios)
            )
            
            if resultado:
                sesion.ejercicios_completados.append(resultado)
            else:
                print("ℹ️ Usuario decidió terminar")
                break
            
            time.sleep(0.5)
        
        # Volver a eyes.gif
        if self.interfaz:
            self.interfaz.mostrar_eyes()
        
        # RF4.1: Registrar sesión
        if sesion.total_ejercicios > 0:
            sesion_id = self.db.crear_sesion(sesion)
            sesion.sesion_id = sesion_id
            
            # RF4.3: Evaluar progreso
            self._evaluar_progreso_con_ia(persona, sesion)
        
        print(f"\n{'='*60}")
        print(f"✅ Sesión finalizada")
        print(f"📊 Correctos: {sesion.ejercicios_correctos}/{sesion.total_ejercicios}")
        print(f"📈 Tasa éxito: {sesion.tasa_exito*100:.1f}%")
        print(f"⭐ Estrellas: {self.estrellas_sesion}")
        print(f"🎙️ Audios grabados en: audio_registros/{persona.person_id}/")
        print('='*60 + "\n")
    
    def _ejecutar_ejercicio_con_ia_y_grabacion(
        self, ejercicio: Ejercicio, persona: Persona, 
        num: int, total: int
    ) -> Optional[ResultadoEjercicio]:
        """
        Ejecutar ejercicio individual CON GRABACIÓN DE AUDIO
        MUESTRA: imagen + palabra mientras usuario responde
        MUESTRA: eyes.gif cuando robot habla
        GRABA: audio del usuario con formato organizado
        """
        
        # MOSTRAR EJERCICIO (imagen + palabra)
        if self.interfaz:
            ruta_imagen = ejercicio.apoyo_visual if ejercicio.apoyo_visual else None
            self.interfaz.mostrar_ejercicio(
                palabra=ejercicio.word,
                ruta_imagen=ruta_imagen
            )
        
        # Dar instrucción (mostrará eyes.gif automáticamente)
        self.audio.hablar(f"Repite: {ejercicio.word}")
        
        # VOLVER A MOSTRAR EJERCICIO después de hablar
        if self.interfaz:
            ruta_imagen = ejercicio.apoyo_visual if ejercicio.apoyo_visual else None
            self.interfaz.mostrar_ejercicio(
                palabra=ejercicio.word,
                ruta_imagen=ruta_imagen
            )
        
        time.sleep(0.5)
        
        # === GRABAR Y EVALUAR SIMULTÁNEAMENTE ===
        inicio = time.time()
        
        # Preparar parámetros para grabación
        ejercicio_nombre = ejercicio.word
        nivel_actual = persona.nivel_actual.name
        numero_sesion = self.numero_sesion_actual
        
        print(f"🎙️ Grabando audio: {ejercicio_nombre}_{nivel_actual}_sesion{numero_sesion}")
        
        # Usar grabar_y_escuchar para hacer ambas cosas a la vez
        respuesta, audio_path = self.audio.grabar_y_escuchar(
            duracion=Config.RECORDING_DURATION,
            person_id=persona.person_id,
            exercise_id=ejercicio.exercise_id,
            ejercicio_nombre=ejercicio_nombre,
            nivel_actual=nivel_actual,
            numero_sesion=numero_sesion
        )
        
        tiempo_respuesta = time.time() - inicio
        
        # Si no obtuvimos texto reconocido, dar otra oportunidad
        intentos = 1
        if not respuesta:
            print("⚠️ Primera grabación sin texto reconocido, dando otra oportunidad...")
            self.audio.hablar("No te escuché bien. Intenta una vez más.")
            
            # Segundo intento
            respuesta, audio_path_2 = self.audio.grabar_y_escuchar(
                duracion=Config.RECORDING_DURATION,
                person_id=persona.person_id,
                exercise_id=ejercicio.exercise_id,
                ejercicio_nombre=ejercicio_nombre,
                nivel_actual=nivel_actual,
                numero_sesion=numero_sesion
            )
            intentos = 2
            
            # Usar la ruta del segundo audio si existe
            if audio_path_2:
                audio_path = audio_path_2
        
        # Evaluar respuesta con IA
        if respuesta:
            correcto, confianza, feedback_ia = comparar_palabras(ejercicio.word, respuesta)
            print(f"📊 Evaluación: correcto={correcto}, confianza={confianza:.2f}")
            print(f"💬 Feedback IA: {feedback_ia}")
        else:
            correcto = False
            feedback_ia = "No logré escucharte, pero está bien. Sigamos."
            print("⚠️ No se pudo evaluar (sin texto reconocido)")
        
        # Feedback visual EN EL EJERCICIO
        if self.interfaz:
            self.interfaz.mostrar_feedback_ejercicio(correcto)
        
        if correcto:
            self.estrellas_sesion += 1
        
        # Dar feedback verbal (mostrará eyes.gif)
        self.audio.hablar(feedback_ia)
        time.sleep(0.5)
        
        # Crear resultado con la ruta del audio
        return ResultadoEjercicio(
            ejercicio_id=ejercicio.exercise_id,
            respuesta=respuesta or "",
            correcto=correcto,
            tiempo_respuesta=tiempo_respuesta,
            intentos=intentos,
            audio_path=audio_path  # ¡IMPORTANTE! Guardar la ruta del audio
        )
    
    def _evaluar_progreso_con_ia(self, persona: Persona, sesion: Sesion):
        """RF4.3 y RF4.4: Evaluar progreso con celebración"""
        
        if not sesion.fue_exitosa():
            print("ℹ️ Sesión no alcanzó umbral de éxito")
            return
        
        if not persona.puede_subir_nivel(sesion.tasa_exito):
            print("ℹ️ No alcanzó umbral para subir de nivel")
            return
        
        # Subir de nivel
        niveles = list(NivelTerapia)
        indice_actual = niveles.index(persona.nivel_actual)
        
        if indice_actual < len(niveles) - 1:
            nuevo_nivel = niveles[indice_actual + 1]
            
            # RF4.4: Actualizar nivel
            self.db.actualizar_nivel_persona(persona.person_id, nuevo_nivel)
            persona.nivel_actual = nuevo_nivel
            
            # Celebración (mostrará eyes.gif al hablar)
            mensaje = consultar(
                f"Celebra que {persona.name} subió al nivel {nuevo_nivel.name}",
                contexto="Debe ser muy motivador y celebratorio"
            )
            self.audio.hablar(mensaje)
            
            print(f"🎉 ¡SUBIÓ DE NIVEL! → {nuevo_nivel.name}")
            time.sleep(2)


# Alias para compatibilidad
RobotService = RobotServiceInterfazUnificada