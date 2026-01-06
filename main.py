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
        respuesta = consultar("Di un saludo corto que no sea hola, luego indica que si te necesita solo te salude")
        self.audio.hablar(respuesta, velocidad=1)
        
        imprimir_seccion("ROBOT EN MODO ESCUCHA")
    
    def modo_escucha(self):
        """Modo de escucha continua en segundo plano"""
        
        def escucha_continua():
            """Función que corre en hilo separado"""
            while self.activo:
                try:
                    hora = datetime.now().strftime('%H:%M:%S')
                    print(f"[{hora}] 👂 Escuchando... (di '{Config.ACTIVATION_WORD}' o 'adiós')")
                    
                    texto = self.audio.escuchar(timeout=Config.AUDIO_TIMEOUT)
                    
                    if texto:
                        texto_lower = texto.lower()
                        print(f"[{hora}] 📢 Escuché: '{texto}'")
                        
                        # Detectar palabras de salida
                        if any(palabra in texto_lower for palabra in Config.EXIT_WORDS):
                            print(f"[{hora}] 👋 ¡COMANDO DE SALIDA!\n")
                            self.apagar()
                            break
                        
                        # Detectar palabra de activación
                        elif Config.ACTIVATION_WORD in texto_lower:
                            print(f"[{hora}] ✅ ¡ROBOT ACTIVADO!\n")
                            # Ejecutar modo activo en el mismo hilo
                            self.modo_activo()
                        else:
                            print(f"[{hora}] ⭕ Esperando '{Config.ACTIVATION_WORD}'...\n")
                    else:
                        print(f"[{hora}] ⏱️ Silencio...\n")
                    
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"\n⚠️ Error en escucha: {e}\n")
                    time.sleep(1)
        
        # Iniciar escucha en hilo separado
        self.hilo_escucha = threading.Thread(target=escucha_continua, daemon=True)
        self.hilo_escucha.start()
    
    def modo_activo(self):
        """Modo activo: proceso completo de identificación y ejercicios"""
        
        print("╔" + "═"*68 + "╗")
        print("║" + " "*25 + "ROBOT ACTIVADO" + " "*29 + "║")
        print("╚" + "═"*68 + "╝\n")
        
        # Saludo (mostrará eyes.gif)
        self.audio.hablar("Hola, aquí estoy.")
        time.sleep(0.5)
        
        try:
            # PASO 1: Identificación (mostrará nombre cuando se obtenga)
            persona = self.identificar_usuario()
            
            if persona:
                # PASO 2: Ejercicios (mostrará imágenes + palabras)
                self.service.realizar_sesion_ejercicios(persona)
                
                # PASO 3: Despedida (volverá a eyes.gif)
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