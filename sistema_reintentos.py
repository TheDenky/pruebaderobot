"""
SISTEMA DE REINTENTOS INTELIGENTE
Funciones helper para manejar audio, reintentos y validación con IA
"""

import time
from typing import Optional, Tuple, Callable, Any


class ConfigReintentos:
    """Configuración del sistema de reintentos"""
    MAX_INTENTOS_AUDIO = 3  # Máximo de intentos cuando no se escucha nada
    MAX_INTENTOS_VALIDACION = 3  # Máximo de intentos cuando respuesta no es válida
    TIMEOUT_ESCUCHA = 8  # Segundos para escuchar
    PHRASE_LIMIT = 6  # Límite de frase en segundos
    PAUSA_ENTRE_INTENTOS = 0.2  # Segundos de pausa entre intentos


def preguntar_con_reintentos(
    audio_system,
    pregunta: str,
    validador: Callable[[str], Tuple[bool, Any]],
    mensajes_reintento: list = None,
    max_intentos: int = ConfigReintentos.MAX_INTENTOS_VALIDACION,
    permitir_salir: bool = True,
    interfaz = None
) -> Tuple[bool, Optional[Any]]:
    """
    Hacer una pregunta con reintentos inteligentes
    
    Args:
        audio_system: Sistema de audio para hablar/escuchar
        pregunta: Pregunta a hacer
        validador: Función que valida la respuesta (retorna (es_valido, resultado))
        mensajes_reintento: Lista de mensajes para reintentos
        max_intentos: Número máximo de intentos
        permitir_salir: Si True, detecta cuando el niño quiere salir
        interfaz: Interfaz gráfica opcional
    
    Returns:
        (exito, resultado) donde resultado es None si falló o si el usuario quiere salir
    """
    from chatopenai import detectar_salir, feedback_motivador
    
    if mensajes_reintento is None:
        mensajes_reintento = [
            "No te escuché bien. ¿Puedes repetir?",
            "Hmm, no entendí. Intenta de nuevo, con calma.",
            "Está bien, una vez más. Habla claro, sin prisa."
        ]
    
    for intento in range(max_intentos):
        # Hacer la pregunta
        if interfaz:
            interfaz.robot_hablando(True)
        
        if intento == 0:
            audio_system.hablar(pregunta)
        else:
            # Usar mensaje de reintento apropiado
            idx_mensaje = min(intento - 1, len(mensajes_reintento) - 1)
            audio_system.hablar(mensajes_reintento[idx_mensaje])
        
        if interfaz:
            interfaz.robot_hablando(False)
            interfaz.actualizar_estado(f"🎤 Escuchando... (Intento {intento + 1}/{max_intentos})")
        
        # Escuchar respuesta
        respuesta = audio_system.escuchar(
            timeout=ConfigReintentos.TIMEOUT_ESCUCHA,
            phrase_time_limit=ConfigReintentos.PHRASE_LIMIT
        )
        
        # Caso 1: No se escuchó nada
        if not respuesta or len(respuesta.strip()) == 0:
            print(f"⚠️ Intento {intento + 1}: No se escuchó nada")
            
            if interfaz:
                interfaz.actualizar_texto_escuchado("(Silencio...)")
            
            # En el último intento, ofrecer opciones
            if intento == max_intentos - 1:
                if interfaz:
                    interfaz.robot_hablando(True)
                
                audio_system.hablar("No logro escucharte. ¿Quieres intentar otra vez o mejor lo dejamos?")
                
                if interfaz:
                    interfaz.robot_hablando(False)
                
                respuesta_final = audio_system.escuchar(timeout=6, phrase_time_limit=5)
                
                if respuesta_final and detectar_salir(respuesta_final):
                    print("ℹ️ El niño decidió salir")
                    return False, None
                
                # Si no quiere salir, damos una oportunidad más
                continue
            
            time.sleep(ConfigReintentos.PAUSA_ENTRE_INTENTOS)
            continue
        
        # Mostrar lo que se escuchó
        print(f"📢 Intento {intento + 1}: Escuché '{respuesta}'")
        
        if interfaz:
            interfaz.actualizar_texto_escuchado(f"Dijiste: {respuesta}")
        
        # Caso 2: Detectar si quiere salir
        if permitir_salir and detectar_salir(respuesta):
            print("ℹ️ Detectada intención de salir")
            
            if interfaz:
                interfaz.robot_hablando(True)
            
            audio_system.hablar("Entiendo. Podemos parar cuando quieras.")
            
            if interfaz:
                interfaz.robot_hablando(False)
            
            return False, None
        
        # Caso 3: Validar respuesta
        es_valido, resultado = validador(respuesta)
        
        if es_valido:
            print(f"✅ Respuesta válida: {resultado}")
            return True, resultado
        else:
            print(f"❌ Respuesta no válida")
            
            # Generar feedback apropiado
            if intento < max_intentos - 1:
                # No es el último intento, dar otra oportunidad
                time.sleep(ConfigReintentos.PAUSA_ENTRE_INTENTOS)
            else:
                # Último intento, feedback especial
                if interfaz:
                    interfaz.robot_hablando(True)
                
                mensaje = feedback_motivador("frustracion")
                audio_system.hablar(mensaje)
                
                if interfaz:
                    interfaz.robot_hablando(False)
    
    # Se agotaron los intentos
    print(f"⚠️ Se agotaron los {max_intentos} intentos")
    return False, None


def escuchar_con_reintentos(
    audio_system,
    mensaje_inicial: str = "Escuchando...",
    max_intentos: int = ConfigReintentos.MAX_INTENTOS_AUDIO,
    interfaz = None
) -> Optional[str]:
    """
    Escuchar con reintentos automáticos cuando hay silencio
    
    Returns:
        El texto escuchado o None si no se pudo escuchar después de todos los intentos
    """
    mensajes = [
        "Te escucho, habla con claridad.",
        "No te escuché. Acércate más al micrófono.",
        "Última oportunidad. Habla fuerte y claro."
    ]
    
    for intento in range(max_intentos):
        if interfaz:
            interfaz.actualizar_estado(f"🎤 {mensaje_inicial} (Intento {intento + 1}/{max_intentos})")
        
        respuesta = audio_system.escuchar(
            timeout=ConfigReintentos.TIMEOUT_ESCUCHA,
            phrase_time_limit=ConfigReintentos.PHRASE_LIMIT
        )
        
        if respuesta and len(respuesta.strip()) > 0:
            print(f"✅ Escuchado en intento {intento + 1}: '{respuesta}'")
            return respuesta
        
        print(f"⚠️ Intento {intento + 1}: Silencio")
        
        # Dar feedback y reintentar
        if intento < max_intentos - 1:
            if interfaz:
                interfaz.robot_hablando(True)
            
            audio_system.hablar(mensajes[intento])
            
            if interfaz:
                interfaz.robot_hablando(False)
            
            time.sleep(ConfigReintentos.PAUSA_ENTRE_INTENTOS)
    
    print("❌ No se pudo escuchar después de todos los intentos")
    return None


def confirmar_con_usuario(
    audio_system,
    mensaje_confirmacion: str,
    interfaz = None
) -> bool:
    """
    Pedir confirmación al usuario (Sí/No) con reintentos
    
    Returns:
        True si confirmó (dijo sí), False si no confirmó o si hubo error
    """
    from chatopenai import validar_si_no
    
    def validador(respuesta: str) -> Tuple[bool, str]:
        es_valido, resultado = validar_si_no(respuesta)
        return es_valido, resultado
    
    mensajes_reintento = [
        "Responde sí o no, por favor.",
        "Dime solo sí o no.",
        "¿Es sí o es no?"
    ]
    
    exito, resultado = preguntar_con_reintentos(
        audio_system=audio_system,
        pregunta=mensaje_confirmacion,
        validador=validador,
        mensajes_reintento=mensajes_reintento,
        max_intentos=3,
        permitir_salir=True,
        interfaz=interfaz
    )
    
    if not exito:
        return False
    
    return resultado == 'si'


def pedir_nombre_con_reintentos(
    audio_system,
    interfaz = None
) -> Optional[str]:
    """
    Pedir el nombre del niño con validación IA
    
    Returns:
        El nombre o None si no se pudo obtener
    """
    from chatopenai import validar_nombre
    
    def validador(respuesta: str) -> Tuple[bool, Optional[str]]:
        return validar_nombre(respuesta)
    
    mensajes_reintento = [
        "No entendí tu nombre. Dime solo tu nombre.",
        "Mmm, ¿cómo te llamas? Di tu nombre claro.",
        "Una vez más. Tu nombre, por favor."
    ]
    
    exito, nombre = preguntar_con_reintentos(
        audio_system=audio_system,
        pregunta="¿Cuál es tu nombre?",
        validador=validador,
        mensajes_reintento=mensajes_reintento,
        max_intentos=3,
        permitir_salir=False,  # No permitir salir durante registro
        interfaz=interfaz
    )
    
    return nombre if exito else None


def pedir_edad_con_reintentos(
    audio_system,
    interfaz = None
) -> Optional[int]:
    """
    Pedir la edad del niño con validación IA
    
    Returns:
        La edad o None si no se pudo obtener
    """
    from chatopenai import validar_edad
    
    def validador(respuesta: str) -> Tuple[bool, Optional[int]]:
        return validar_edad(respuesta)
    
    mensajes_reintento = [
        "No entendí tu edad. ¿Cuántos años tienes?",
        "Dime tu edad con un número. Por ejemplo: cinco o seis.",
        "Una vez más. ¿Cuántos años tienes?"
    ]
    
    exito, edad = preguntar_con_reintentos(
        audio_system=audio_system,
        pregunta="¿Cuántos años tienes?",
        validador=validador,
        mensajes_reintento=mensajes_reintento,
        max_intentos=3,
        permitir_salir=False,
        interfaz=interfaz
    )
    
    return edad if exito else None


def evaluacion_ejercicio_con_ia(
    audio_system,
    palabra_esperada: str,
    interfaz = None,
    max_intentos: int = 2
) -> Tuple[bool, Optional[str], str]:
    """
    Evaluar un ejercicio con reintentos y validación por IA
    
    Args:
        audio_system: Sistema de audio
        palabra_esperada: Palabra que se espera que el niño diga
        interfaz: Interfaz gráfica opcional
        max_intentos: Intentos permitidos para este ejercicio
    
    Returns:
        (correcto, respuesta, feedback)
    """
    from chatopenai import comparar_palabras, feedback_motivador
    
    for intento in range(max_intentos):
        # Escuchar respuesta
        respuesta = escuchar_con_reintentos(
            audio_system=audio_system,
            mensaje_inicial=f"Escuchando tu respuesta...",
            max_intentos=2,  # 2 intentos para escuchar
            interfaz=interfaz
        )
        
        if not respuesta:
            print("❌ No se pudo escuchar respuesta")
            
            if intento < max_intentos - 1:
                # Hay más intentos
                if interfaz:
                    interfaz.robot_hablando(True)
                
                audio_system.hablar("No te escuché. Vamos a intentar una vez más.")
                
                if interfaz:
                    interfaz.robot_hablando(False)
                
                time.sleep(0.3)
                continue
            else:
                # Último intento, asumir error
                feedback = "No logré escucharte bien, pero está bien. Sigamos."
                return False, None, feedback
        
        # Comparar con IA
        correcto, confianza, feedback = comparar_palabras(palabra_esperada, respuesta)
        
        print(f"📊 Evaluación: correcto={correcto}, confianza={confianza:.2f}")
        print(f"💬 Feedback IA: {feedback}")
        
        # Si la confianza es alta, aceptar el resultado
        if confianza >= 0.7:
            return correcto, respuesta, feedback
        
        # Si la confianza es baja y no es el último intento
        if intento < max_intentos - 1:
            if interfaz:
                interfaz.robot_hablando(True)
            
            audio_system.hablar("Hmm, no estoy seguro. Intenta decirlo más claro.")
            
            if interfaz:
                interfaz.robot_hablando(False)
            
            time.sleep(1)
        else:
            # Último intento, dar el beneficio de la duda si está cerca
            if confianza >= 0.5:
                return True, respuesta, "¡Buen esfuerzo! Lo hiciste bien"
            else:
                return False, respuesta, feedback
    
    # No debería llegar aquí
    return False, None, "Sigamos con el siguiente ejercicio"


def manejar_frustracion(
    audio_system,
    sesion_actual,
    interfaz = None
) -> bool:
    """
    Detectar y manejar frustración del niño
    
    Returns:
        True si quiere continuar, False si quiere parar
    """
    from chatopenai import feedback_motivador
    
    # Contar fallos recientes
    if len(sesion_actual.ejercicios_completados) < 3:
        return True
    
    ultimos_3 = sesion_actual.ejercicios_completados[-3:]
    fallos_seguidos = sum(1 for e in ultimos_3 if not e.correcto)
    
    if fallos_seguidos >= 3:
        print("⚠️ Detectada posible frustración (3 fallos seguidos)")
        
        if interfaz:
            interfaz.actualizar_estado("💙 Tomando un descanso...")
            interfaz.robot_hablando(True)
        
        mensaje = feedback_motivador("frustracion")
        audio_system.hablar(mensaje)
        time.sleep(1)
        audio_system.hablar("¿Quieres seguir o prefieres descansar?")
        
        if interfaz:
            interfaz.robot_hablando(False)
        
        respuesta = audio_system.escuchar(timeout=6, phrase_time_limit=5)
        
        if respuesta:
            from chatopenai import detectar_salir, validar_si_no
            
            if detectar_salir(respuesta):
                return False
            
            es_valido, resultado = validar_si_no(respuesta)
            if es_valido and resultado == 'no':
                return False
        
        # Por defecto, continuar con un mensaje de ánimo
        if interfaz:
            interfaz.robot_hablando(True)
        
        audio_system.hablar("¡Muy bien! Sigamos entonces. Tú puedes 💪")
        
        if interfaz:
            interfaz.robot_hablando(False)
        
        time.sleep(0.5)
    
    return True
