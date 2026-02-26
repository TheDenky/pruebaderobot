"""
ROBOT DODO - Versión con Interfaz Unificada
Una sola ventana que se mantiene abierta durante toda la ejecución
"""
import sys
import time
import threading
from datetime import datetime
from chatopenai import consultar

# Importar módulos
from config import Config
from database import Database
from audio import AudioSystem
from ui import InterfazUnificada
from services import RobotService
from utils import imprimir_encabezado, imprimir_seccion


class RobotDodoUnificado:
    """Controlador principal con interfaz unificada"""
    
    def __init__(self):
        self.activo = True
        self.db = None
        self.audio = None
        self.service = None
        self.interfaz = None
        self.hilo_escucha = None
        self.modo_administrador = False
        self.panel_admin = None
    
    def inicializar(self):
        """Inicializar todos los componentes"""
        imprimir_encabezado("🤖 ROBOT DODO 🤖")
        
        print("Inicializando componentes...")
        
        # Crear carpetas necesarias
        Config.crear_carpetas()
        
        # PASO 1: Crear interfaz PRIMERO
        print("🖥️  Creando interfaz unificada...")
        self.interfaz = InterfazUnificada()
        self.interfaz.crear()
        # Interfaz empieza mostrando eyes.gif automáticamente
        
        # PASO 2: Base de datos
        print("📊 Conectando a base de datos...")
        self.db = Database(Config.DATABASE_PATH)
        
        # PASO 3: Sistema de audio (con referencia a interfaz)
        print("🎤 Inicializando sistema de audio...")
        self.audio = AudioSystem(interfaz=self.interfaz)
        
        # PASO 4: Servicio principal
        print("⚙️ Configurando servicios...")
        self.service = RobotService(self.db, self.audio)
        self.service.set_interfaz(self.interfaz)
        
        print("\n✅ ROBOT LISTO\n")
        print("="*70 + "\n")
        
        # Mensaje inicial por voz (mostrará eyes.gif)
        
        descripcion = ("¡Hola amiguito! Soy DODO, un robot muy especial que va a ser tu amigo en esta aventura. Vamos a jugar juntos practicando palabras. Es muy fácil y divertido. Te voy a enseñar imágenes súper bonitas de animales, objetos y muchas cosas más. Tú solo tienes que decir qué es lo que ves. Cuando lo hagas bien, ganarás estrellas. Tengo cuatro niveles, desde el más fácil hasta el más difícil. Empezarás con cositas simples como las vocales A, E, I, O, U, y poco a poco iremos practicando palabras más grandes. Lo mejor es que voy a grabar tu voz para que puedas escuchar cómo vas mejorando cada día. Eso es súper emocionante. Cuando te sientas listo para empezar nuestra aventura de hoy, solo di la palabra mágica: hola robot.")
        presentacion = consultar("Haz una descripcion corta de lo que haces para niños")
        presentacion = "¡Hola! Soy el robot DODO. Ayudo a niños a hablar mejor. Juntos, aprendemos y nos divertimos. ¡Tú puedes!"
        self.audio.hablar(presentacion, velocidad=1)
        
        respuesta = consultar("Di un saludo corto que no sea hola, luego indica que si te necesita solo te salude")
        respuesta = "Si me necesitas, solo dime: hola robot. ¡Estoy aquí para ayudar!"
        self.audio.hablar(respuesta, velocidad=1)
        
        imprimir_seccion("ROBOT EN MODO ESCUCHA")
    
    def modo_escucha(self):
        """Modo de escucha continua en segundo plano"""
        
        def escucha_continua():
            """Función que corre en hilo separado"""
            from chatopenai import detectar_panel_admin
            import time as time_module
            ultima_actividad = time_module.time()
            sleeping = False
            
            while self.activo:
                try:
                    # VERIFICAR MODO ADMINISTRADOR
                    if self.modo_administrador:
                        # Esperar a que se cierre el panel
                        if self.panel_admin and self.panel_admin.modo_admin_activo:
                            time_module.sleep(1)
                            continue
                        else:
                            # Panel cerrado, desactivar modo admin
                            print("\n✅ Panel cerrado - volviendo a modo normal\n")
                            self.modo_administrador = False
                            ultima_actividad = time_module.time()
                            
                            if self.interfaz:
                                self.interfaz.mostrar_eyes()
                            sleeping = False
                            
                            self.audio.hablar("Volviendo a modo normal. Di hola robot si me necesitas.")
                            time_module.sleep(2)
                            continue
                    
                    hora = datetime.now().strftime('%H:%M:%S')
                    print(f"[{hora}] 👂 Escuchando... (di '{Config.ACTIVATION_WORD}' o 'adiós')")
                    
                    texto = self.audio.escuchar(
                        timeout=Config.AUDIO_TIMEOUT,
                        phrase_time_limit=Config.AUDIO_PHRASE_LIMIT
                    )

                    # Verificar inactividad
                    tiempo_inactivo = time_module.time() - ultima_actividad
                    if tiempo_inactivo >= 60 and not sleeping:
                        hora = datetime.now().strftime('%H:%M:%S')
                        print(f"[{hora}] 💤 Inactividad detectada. Modo sleeping...")
                        if self.interfaz:
                            self.interfaz.mostrar_eyes_sleeping()
                        sleeping = True

                    if texto:
                        texto_lower = texto.lower()
                        print(f"[{hora}] 📢 Escuché: '{texto}'")
                        
                        # ===== DETECCIÓN CON IA: PANEL DE TERAPEUTA =====
                        if detectar_panel_admin(texto):
                            print(f"[{hora}] 🩺 ¡DETECTADA INTENCIÓN DE ABRIR PANEL!\n")
                            ultima_actividad = time_module.time()
                            
                            if sleeping:
                                if self.interfaz:
                                    self.interfaz.mostrar_eyes()
                                sleeping = False
                            
                            self.abrir_panel_terapeuta()
                            continue
                        # ===============================================
                        
                        # Detectar palabras de salida
                        elif any(palabra in texto_lower for palabra in Config.EXIT_WORDS):
                            print(f"[{hora}] 👋 ¡COMANDO DE SALIDA!\n")
                            self.apagar()
                            break
                        
                        # Detectar palabra de activación
                        elif Config.ACTIVATION_WORD in texto_lower:
                            ultima_actividad = time_module.time()
                            
                            if sleeping:
                                hora = datetime.now().strftime('%H:%M:%S')
                                print(f"[{hora}] 👁️ Despertando...")
                                if self.interfaz:
                                    self.interfaz.mostrar_eyes()
                                sleeping = False
                                
                            print(f"[{hora}] ✅ ¡ROBOT ACTIVADO!\n")
                            self.modo_activo()
                        else:
                            print(f"[{hora}] ⭕ Esperando '{Config.ACTIVATION_WORD}'...\n")
                    else:
                        print(f"[{hora}] ⏱️ Silencio...\n")
                    
                    time_module.sleep(0.3)
                    
                except Exception as e:
                    print(f"\n⚠️ Error en escucha: {e}\n")
                    time_module.sleep(1)
        
        # Iniciar escucha en hilo separado
        self.hilo_escucha = threading.Thread(target=escucha_continua, daemon=True)
        self.hilo_escucha.start()
    
    def modo_activo(self):
        """Modo activo: proceso completo de identificación y ejercicios"""
        
        # VERIFICAR MODO ADMINISTRADOR
        if self.modo_administrador:
            print("⚠️ Modo administrador activo - bloqueando proceso normal")
            self.audio.hablar("Primero debes cerrar el panel de administrador.")
            return
        
        print("╔" + "═"*68 + "╗")
        print("║" + " "*25 + "ROBOT ACTIVADO" + " "*29 + "║")
        print("╚" + "═"*68 + "╝\n")
        
        # Saludo (mostrará eyes.gif)
        self.audio.hablar("Hola, aquí estoy.")
        time.sleep(0.5)
        
        try:
            # PASO 1: Identificación
            persona = self.identificar_usuario()
            
            if persona:
                # Calcular número de sesión
                sesiones_previas = self.db.obtener_sesiones_por_persona(persona.person_id)
                numero_sesion = len(sesiones_previas) + 1
                
                # ========== AHORA SÍ PREGUNTAR ESTADO (CON GRABACIÓN) ==========
                self._preguntar_estado_animo(persona, numero_sesion)
                # ================================================================
                
                # PASO 2: Ejercicios
                self.service.realizar_sesion_ejercicios(persona)
                
                # ========== PREGUNTAR OPINIÓN (CON GRABACIÓN) ==========
                self._preguntar_opinion_sesion(persona, numero_sesion)
                # ========================================================
                
                # PASO 3: Despedida
                self.despedida()
        
        except Exception as e:
            print(f"\n❌ Error en modo activo: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Volver a eyes.gif
            if self.interfaz:
                self.interfaz.mostrar_eyes()
            
            print("\n" + "─"*70)
            print("  Volviendo al modo escucha...")
            print("─"*70 + "\n")
            time.sleep(2)
    
    def _preguntar_estado_animo(self, persona, numero_sesion):
        """Preguntar al niño cómo se encuentra y GRABAR su respuesta"""
        from chatopenai import consultar
        
        print("\n💬 === PREGUNTA DE ÁNIMO (CON GRABACIÓN) ===")
        
        # Hacer la pregunta
        if self.interfaz:
            self.interfaz.mostrar_eyes()
        
        pregunta = consultar(
            "Di una pregunta muy breve para preguntar a un niño cómo se siente hoy. "
            "Máximo 1 frase corta.",
            contexto="Eres un robot amigable"
        )

        self.audio.hablar(pregunta)
        
        # ========== GRABAR Y ESCUCHAR SIMULTÁNEAMENTE ==========
        print(f"🎙️ Grabando comentario inicial...")
        respuesta, audio_path = self.audio.grabar_y_escuchar(
            duracion=5,  # 10 segundos para dar tiempo a responder
            person_id=persona.person_id,
            exercise_id=0,  # 0 porque no es un ejercicio
            ejercicio_nombre="COMENTARIO_INICIAL",
            nivel_actual=persona.nivel_actual.name,
            numero_sesion=numero_sesion
        )
        
        if respuesta:
            print(f"📢 El niño dijo: '{respuesta}'")
            if audio_path:
                print(f"✅ Audio guardado en: {audio_path}")
            
            # Generar respuesta de ánimo personalizada con IA
            if "triste" in respuesta.lower() or "mal" in respuesta.lower():
                mensaje_animo = consultar(
                    "El niño está triste o no se siente bien. "
                    "Dale palabras de consuelo y ánimo muy breves."
                    "Da una respuesta sin hacer preguntas y breve"
                )
            elif "bien" in respuesta.lower() or "feliz" in respuesta.lower():
                mensaje_animo = consultar(
                    "El niño está bien o feliz. "
                    "Celébralo y mantén su energía positiva."
                    "Da una respuesta sin hacer preguntas y breve"
                )
            else:
                mensaje_animo = consultar(
                    f"El niño respondió: '{respuesta}'. "
                    "Da una respuesta apropiada sin hacer preguntas y breve."
                )
            
            print(f"🤖 Respuesta generada: {mensaje_animo}")
            
            # Dar la respuesta de ánimo
            self.audio.hablar(mensaje_animo)
            time.sleep(0.2)
        else:
            print("⚠️ No se escuchó respuesta")
            if audio_path:
                print(f"⚠️ Audio grabado pero sin texto reconocido: {audio_path}")
            # Mensaje genérico si no responde
            self.audio.hablar("Está bien. Vamos a empezar entonces.")
            time.sleep(0.2)
        
        print()
    
    def _preguntar_opinion_sesion(self, persona, numero_sesion):
        """Preguntar al niño qué le pareció la sesión y GRABAR su respuesta"""
        from chatopenai import consultar
        
        print("\n💬 === OPINIÓN DE LA SESIÓN (CON GRABACIÓN) ===")
        
        # Hacer la pregunta
        if self.interfaz:
            self.interfaz.mostrar_eyes()
        
        pregunta = consultar(
            "Di una pregunta muy breve para preguntar a un niño qué le pareció la sesión de ejercicios. "
            "Máximo 1 frase corta.",
            contexto="Eres un robot amigable que quiere saber cómo se sintió el niño"
        )
        
        self.audio.hablar(pregunta)
        
        # ========== GRABAR Y ESCUCHAR SIMULTÁNEAMENTE ==========
        print(f"🎙️ Grabando comentario final...")
        respuesta, audio_path = self.audio.grabar_y_escuchar(
            duracion=5,  # 10 segundos para dar tiempo a responder
            person_id=persona.person_id,
            exercise_id=0,  # 0 porque no es un ejercicio
            ejercicio_nombre="COMENTARIO_FINAL",
            nivel_actual=persona.nivel_actual.name,
            numero_sesion=numero_sesion
        )
        
        if respuesta:
            print(f"📢 El niño dijo: '{respuesta}'")
            if audio_path:
                print(f"✅ Audio guardado en: {audio_path}")
            
            # Generar respuesta apropiada con IA
            if any(palabra in respuesta.lower() for palabra in ["bien", "bueno", "me gustó", "divertido", "genial"]):
                mensaje_respuesta = consultar(
                    "El niño disfrutó la sesión. "
                    "Celebra su opinión positiva de forma breve."
                )
            elif any(palabra in respuesta.lower() for palabra in ["difícil", "cansado", "aburrido", "no me gustó"]):
                mensaje_respuesta = consultar(
                    "El niño encontró la sesión difícil o no le gustó mucho. "
                    "Dale ánimo y dile que mejorará con práctica. Respuesta breve."
                )
            else:
                mensaje_respuesta = consultar(
                    f"El niño respondió sobre la sesión: '{respuesta}'. "
                    "Da una respuesta apropiada y motivadora. Breve."
                )
            
            print(f"🤖 Respuesta generada: {mensaje_respuesta}")
            
            # Dar la respuesta
            self.audio.hablar(mensaje_respuesta)
            time.sleep(0.2)
        else:
            print("⚠️ No se escuchó respuesta")
            if audio_path:
                print(f"⚠️ Audio grabado pero sin texto reconocido: {audio_path}")
            # Mensaje genérico si no responde
            self.audio.hablar("Está bien. Espero que hayas disfrutado la sesión.")
            time.sleep(0.2)
        
        print()
        
    def identificar_usuario(self):
        """Identificar si es primera vez o usuario registrado"""
        from utils import imprimir_seccion
        
        imprimir_seccion("IDENTIFICACIÓN DE USUARIO")
        
        # Preguntar si es primera vez (mostrará eyes.gif al hablar)
        es_primera_vez = self.service.preguntar_primera_vez()
        
        if es_primera_vez:
            print("➡️ PRIMERA VEZ - Registro nuevo\n")
            
            # RF1.1: Registrar nuevo usuario (mostrará nombre cuando se obtenga)
            persona = self.service.registrar_nuevo_usuario()
            
            if persona:
                # RF1.2 y RF1.3: Test diagnóstico
                nivel = self.service.realizar_test_diagnostico(persona)
                print(f"✅ Usuario registrado - Nivel: {nivel.name}\n")
            
            return persona
        else:
            print("➡️ NO ES PRIMERA VEZ - Búsqueda en BD\n")
            
            # RF3.1: Buscar usuario existente (mostrará nombre cuando se encuentre)
            persona = self.service.buscar_usuario_existente()
            
            if persona:
                print(f"✅ Usuario encontrado: {persona.name} - Nivel: {persona.nivel_actual.name}\n")
                return persona
            else:
                # Si no se encuentra, registrar como nuevo
                print("➡️ No encontrado - Registrando como nuevo\n")
                self.audio.hablar("Vamos a registrarte.")
                return self.service.registrar_nuevo_usuario()
    
    def abrir_panel_terapeuta(self):
        """Abrir panel de administración del terapeuta"""
        print("\n🩺 === ABRIENDO PANEL DE TERAPEUTA ===\n")
        
        # Activar modo administrador (bloquea proceso normal)
        self.modo_administrador = True
        
        # Confirmación por voz
        self.audio.hablar("Abriendo panel de terapeuta.")
        
        try:
            from panel_terapeuta import PanelTerapeuta
            
            # Crear panel con referencia al audio
            self.panel_admin = PanelTerapeuta(self.db, self.audio)
            self.panel_admin.crear()
            
            print("✅ Panel de terapeuta abierto")
            print("⚠️ Modo administrador ACTIVO - proceso normal bloqueado")
            print("   Di 'salir' o 'cerrar' para volver al modo normal\n")
            
            # Esperar a que se cierre el panel
            # (el panel tiene su propio mainloop)
            
        except Exception as e:
            print(f"❌ Error al abrir panel: {e}")
            import traceback
            traceback.print_exc()
            self.modo_administrador = False
    
    def despedida(self):
        """Despedida después de completar sesión"""
        # Mostrará eyes.gif al hablar
        self.audio.hablar("Has completado todos los ejercicios. ¡Excelente trabajo!")
        time.sleep(1)
        self.audio.hablar(f"Nos vemos pronto. Si me necesitas, di {Config.ACTIVATION_WORD}.")
        time.sleep(2)
    
    def apagar(self):
        """Apagar sistema de forma ordenada"""
        imprimir_encabezado("👋 CERRANDO SISTEMA")
        
        self.activo = False
        
        # Despedida (mostrará eyes.gif)
        self.audio.hablar("Hasta luego. Adiós.")
        time.sleep(0.5)
        
        if self.db:
            print(f"📊 Total personas en base de datos: {self.db.contar_personas()}")
            self.db.cerrar()
        
        print("\n✅ Robot apagado\n")
        print("="*70 + "\n")
        
        # Cerrar interfaz
        if self.interfaz:
            self.interfaz.cerrar()
        
        sys.exit(0)
    
    def ejecutar(self):
        """Ejecutar el robot con interfaz unificada"""
        try:
            self.inicializar()
            self.modo_escucha()
            
            # Mantener el programa corriendo (la interfaz tiene su propio loop)
            self.interfaz.mainloop()
            
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("  🛑 APAGANDO ROBOT (Ctrl+C)")
            print("="*70)
            self.apagar()
        
        except Exception as e:
            print(f"\n❌ Error crítico: {e}")
            import traceback
            traceback.print_exc()
            
            if self.db:
                self.db.cerrar()
            
            if self.interfaz:
                self.interfaz.cerrar()


def main():
    """Función principal"""
    
    print("\n" + "="*70)
    print("  🚀 ROBOT DODO - INTERFAZ UNIFICADA")
    print("  Una sola ventana, flujo continuo")
    print("="*70 + "\n")
    
    # Crear y ejecutar robot
    robot = RobotDodoUnificado()
    robot.ejecutar()


if __name__ == "__main__":
    main()