"""
ROBOT DODO - Sistema de Registro y Ejercicios por Voz
VERSIÓN SIMPLIFICADA - Arquitectura organizada

Punto de entrada principal del sistema
"""
import sys
import time
from datetime import datetime
from chatopenai import consultar

# Importar módulos
from config import Config
from database import Database
from audio import AudioSystem
from ui import InterfazEjercicios
from services import RobotService
from utils import imprimir_encabezado, imprimir_seccion


class RobotDodo:
    """Controlador principal del Robot DODO"""
    
    def __init__(self):
        self.activo = True
        self.db = None
        self.audio = None
        self.service = None
        self.interfaz = None
    
    def inicializar(self):
        """Inicializar todos los componentes"""
        imprimir_encabezado("🤖 ROBOT DODO 🤖")
        
        print("Inicializando componentes...")
        
        # Crear carpetas necesarias
        Config.crear_carpetas()
        
        # Base de datos
        print("📊 Conectando a base de datos...")
        self.db = Database(Config.DATABASE_PATH)
        
        # Sistema de audio
        print("🎤 Inicializando sistema de audio...")
        self.audio = AudioSystem()
        
        # Servicio principal
        print("⚙️ Configurando servicios...")
        self.service = RobotService(self.db, self.audio)
        
        print("\n✅ ROBOT LISTO\n")
        print("="*70 + "\n")
        
        # Mensaje inicial
        respuesta = consultar("Di un saludo corto que no sea hola, luego indica que si te necesita solo te salude")
        #print("Asistente:", respuesta)
        self.audio.hablar(respuesta, velocidad=1)
        #self.audio.hablar("Hola, soy el Robot Dodo.", velocidad=1)
        #time.sleep(0.5)
        #self.audio.hablar(f"Estoy esperando que digas {Config.ACTIVATION_WORD} para comenzar.")
        
        imprimir_seccion("ROBOT EN MODO ESCUCHA")
    
    def modo_escucha(self):
        """Modo de escucha continua esperando palabra de activación"""
        
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
                        self.modo_activo()
                    else:
                        print(f"[{hora}] ⭕ Esperando '{Config.ACTIVATION_WORD}'...\n")
                else:
                    print(f"[{hora}] ⏱️ Silencio...\n")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"\n⚠️ Error en escucha: {e}\n")
                time.sleep(1)
    
    def modo_activo(self):
        """Modo activo: proceso completo de identificación y ejercicios"""
        
        print("╔" + "═"*68 + "╗")
        print("║" + " "*25 + "ROBOT ACTIVADO" + " "*29 + "║")
        print("╚" + "═"*68 + "╝\n")
        
        # Saludo
        self.audio.hablar("Hola, aquí estoy.")
        time.sleep(0.5)
        
        # Crear interfaz de ejercicios
        self.interfaz = InterfazEjercicios()
        self.interfaz.crear()
        self.service.interfaz = self.interfaz
        time.sleep(0.3)
        
        try:
            # PASO 1: Identificación
            persona = self.identificar_usuario()
            
            if persona:
                # PASO 2: Ejercicios
                self.service.realizar_sesion_ejercicios(persona)
                
                # PASO 3: Despedida
                self.despedida()
        
        except Exception as e:
            print(f"\n❌ Error en modo activo: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cerrar interfaz
            if self.interfaz:
                self.interfaz.cerrar()
                time.sleep(0.5)
            
            print("\n" + "─"*70)
            print("  Volviendo al modo escucha...")
            print("─"*70 + "\n")
            time.sleep(2)
    
    def identificar_usuario(self):
        """Identificar si es primera vez o usuario registrado"""
        from utils import imprimir_seccion
        
        imprimir_seccion("IDENTIFICACIÓN DE USUARIO")
        
        self.interfaz.actualizar_estado("❓ ¿Es tu primera vez?")
        
        # Preguntar si es primera vez
        es_primera_vez = self.service.preguntar_primera_vez()
        
        if es_primera_vez:
            print("➡️ PRIMERA VEZ - Registro nuevo\n")
            self.interfaz.actualizar_estado("📝 Registro nuevo")
            
            # RF1.1: Registrar nuevo usuario
            persona = self.service.registrar_nuevo_usuario()
            
            if persona:
                self.interfaz.actualizar_usuario(persona.name)
                
                # RF1.2 y RF1.3: Test diagnóstico
                nivel = self.service.realizar_test_diagnostico(persona)
                print(f"✅ Usuario registrado - Nivel: {nivel.name}\n")
            
            return persona
        else:
            print("➡️ NO ES PRIMERA VEZ - Búsqueda en BD\n")
            self.interfaz.actualizar_estado("🔍 Buscando usuario")
            
            # RF3.1: Buscar usuario existente
            persona = self.service.buscar_usuario_existente()
            
            if persona:
                self.interfaz.actualizar_usuario(persona.name)
                print(f"✅ Usuario encontrado: {persona.name} - Nivel: {persona.nivel_actual.name}\n")
                return persona
            else:
                # Si no se encuentra, registrar como nuevo
                print("➡️ No encontrado - Registrando como nuevo\n")
                self.audio.hablar("Vamos a registrarte.")
                return self.service.registrar_nuevo_usuario()
    
    def despedida(self):
        """Despedida después de completar sesión"""
        self.interfaz.actualizar_estado("👋 Finalizando sesión...")
        
        self.audio.hablar("Has completado todos los ejercicios. ¡Excelente trabajo!")
        time.sleep(1)
        self.audio.hablar(f"Nos vemos pronto. Si me necesitas, di {Config.ACTIVATION_WORD}.")
        time.sleep(2)
    
    def apagar(self):
        """Apagar sistema de forma ordenada"""
        imprimir_encabezado("👋 CERRANDO SISTEMA")
        
        self.activo = False
        
        self.audio.hablar("Hasta luego. Adiós.")
        time.sleep(0.5)
        
        if self.db:
            print(f"📊 Total personas en base de datos: {self.db.contar_personas()}")
            self.db.cerrar()
        
        print("\n✅ Robot apagado\n")
        print("="*70 + "\n")
        
        sys.exit(0)
    
    def ejecutar(self):
        """Ejecutar el robot"""
        try:
            self.inicializar()
            self.modo_escucha()
            
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


def main():
    """Función principal"""
    robot = RobotDodo()
    robot.ejecutar()


if __name__ == "__main__":
    main()