"""
CHATGPT/OPENAI - Sistema Mejorado de Interacción con IA
Funciones especializadas para entender y validar respuestas de niños
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Tuple, Optional

# Cargar las variables del archivo .env
load_dotenv()


class AsistenteInteligente:
    """Asistente con IA para interacción mejorada con niños"""
    
    def __init__(self):
        try:
            self.client = OpenAI()
            print("✅ Asistente IA inicializado")
        except Exception as e:
            print("❌ Error inicializando OpenAI:", e)
            raise
    
    def consultar(self, texto: str, contexto: str = "") -> str:
        """Consulta general al asistente"""
        if not texto or not texto.strip():
            return "Dime algo y te ayudaré 😊"
        
        system_prompt = (
            "Eres DODO, un robot asistente amable para niños con problemas del habla causados por labio leporino. "
            "Usa frases MUY cortas, simples y claras. "
            "Sé paciente, motivador y positivo siempre. "
            "Usa emojis ocasionalmente para ser más amigable."
        )
        
        if contexto:
            system_prompt += f"\n\nContexto adicional: {contexto}"
        
        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto}
                ],
                max_tokens=80,
                temperature=0.5
            )
            return respuesta.choices[0].message.content
        except Exception as e:
            print(f"❌ Error en consulta IA: {e}")
            return "Lo siento, no te escuché bien. ¿Puedes repetir?"
    
    def validar_si_no(self, texto: str) -> Tuple[bool, str]:
        """
        Valida si una respuesta es SÍ o NO usando IA
        
        Returns:
            (es_valido, resultado) donde resultado es 'si', 'no', o 'unclear'
        """
        if not texto or not texto.strip():
            return False, "unclear"
        
        prompt = f"""
Analiza esta respuesta de un niño y determina si quiso decir SÍ o NO.
Respuesta del niño: "{texto}"

Responde SOLO con una de estas palabras: si, no, unclear

Considera variaciones como:
- SÍ: "sí", "si", "sep", "aja", "claro", "ok", "está bien", "dale"
- NO: "no", "nop", "nope", "no quiero", "mejor no"
- UNCLEAR: cualquier otra cosa que no sea clara

Respuesta:"""

        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            resultado = respuesta.choices[0].message.content.strip().lower()
            
            if resultado in ['si', 'sí']:
                return True, 'si'
            elif resultado == 'no':
                return True, 'no'
            else:
                return False, 'unclear'
                
        except Exception as e:
            print(f"❌ Error en validar_si_no: {e}")
            # Fallback a validación simple
            texto_lower = texto.lower()
            if any(palabra in texto_lower for palabra in ['si', 'sí', 'sep', 'aja', 'claro', 'ok']):
                return True, 'si'
            elif any(palabra in texto_lower for palabra in ['no', 'nop', 'nope']):
                return True, 'no'
            return False, 'unclear'
    
    def validar_nombre(self, texto: str) -> Tuple[bool, Optional[str]]:
        """
        Valida y extrae un nombre usando IA
        
        Returns:
            (es_valido, nombre_extraido)
        """
        if not texto or not texto.strip():
            return False, None
        
        prompt = f"""
Extrae el NOMBRE de esta respuesta de un niño.
Respuesta: "{texto}"

Reglas:
- Si hay un nombre claro, devuélvelo en formato Title Case (Primera Letra Mayúscula)
- Si no hay nombre, responde: NONE
- Ignora palabras como "me llamo", "soy", "mi nombre es"
- Solo extrae el nombre, nada más

Ejemplos:
"me llamo juan" → Juan
"soy maría" → María
"pedro" → Pedro
"ana luisa" → Ana Luisa
"blablabla" → NONE

Respuesta:"""

        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.1
            )
            
            nombre = respuesta.choices[0].message.content.strip()
            
            if nombre == "NONE" or len(nombre) < 2:
                return False, None
            
            return True, nombre
            
        except Exception as e:
            print(f"❌ Error en validar_nombre: {e}")
            # Fallback simple
            texto_limpio = texto.strip().title()
            if len(texto_limpio) >= 2:
                return True, texto_limpio
            return False, None
    
    def validar_edad(self, texto: str) -> Tuple[bool, Optional[int]]:
        """
        Valida y extrae una edad usando IA
        
        Returns:
            (es_valido, edad)
        """
        if not texto or not texto.strip():
            return False, None
        
        prompt = f"""
Extrae la EDAD en números de esta respuesta.
Respuesta: "{texto}"

Reglas:
- Si hay una edad clara entre 1 y 18, devuélvela como número
- Si no hay edad válida, responde: NONE
- Convierte palabras a números: "cinco" → 5, "diez" → 10

Ejemplos:
"tengo 7 años" → 7
"cinco" → 5
"8" → 8
"no sé" → NONE
"veinte" → NONE (fuera de rango)

Responde SOLO con el número o NONE:"""

        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            resultado = respuesta.choices[0].message.content.strip()
            
            if resultado == "NONE":
                return False, None
            
            try:
                edad = int(resultado)
                if 1 <= edad <= 18:
                    return True, edad
            except:
                pass
            
            return False, None
            
        except Exception as e:
            print(f"❌ Error en validar_edad: {e}")
            # Fallback: buscar números en el texto
            import re
            numeros = re.findall(r'\d+', texto)
            if numeros:
                try:
                    edad = int(numeros[0])
                    if 1 <= edad <= 18:
                        return True, edad
                except:
                    pass
            return False, None
    
    def comparar_palabras(self, palabra_esperada: str, palabra_dicha: str) -> Tuple[bool, float, str]:
        """
        Compara si la palabra dicha es similar a la esperada usando IA
        
        Returns:
            (es_correcto, confianza, feedback)
        """
        if not palabra_dicha or not palabra_dicha.strip():
            return False, 0.0, "No escuché nada"
        
        prompt = f"""
Compara estas dos palabras y determina si el niño dijo la palabra correcta.
Palabra esperada: "{palabra_esperada}"
Palabra que dijo: "{palabra_dicha}"

Ten en cuenta:
- El niño tiene problemas del habla (labio leporino)
- Puede tener dificultad con R, L, S, y sonidos complejos
- Pequeñas variaciones son aceptables
- Considera la fonética, no solo la ortografía

Responde en este formato exacto:
RESULTADO: correcto/incorrecto
CONFIANZA: 0.0-1.0
FEEDBACK: un comentario breve y motivador

Ejemplo:
RESULTADO: correcto
CONFIANZA: 0.9
FEEDBACK: ¡Muy bien! Lo dijiste casi perfecto
"""

        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            texto_respuesta = respuesta.choices[0].message.content
            
            # Parsear respuesta
            es_correcto = 'correcto' in texto_respuesta.lower().split('\n')[0]
            
            # Extraer confianza
            confianza = 0.5
            for linea in texto_respuesta.split('\n'):
                if 'CONFIANZA' in linea.upper():
                    try:
                        confianza = float(linea.split(':')[1].strip())
                    except:
                        pass
            
            # Extraer feedback
            feedback = "¡Buen intento!"
            for i, linea in enumerate(texto_respuesta.split('\n')):
                if 'FEEDBACK' in linea.upper():
                    feedback = linea.split(':', 1)[1].strip()
                    break
            
            return es_correcto, confianza, feedback
            
        except Exception as e:
            print(f"❌ Error en comparar_palabras: {e}")
            # Fallback simple
            similar = palabra_esperada.lower() in palabra_dicha.lower()
            return similar, 0.8 if similar else 0.3, "¡Buen intento!" if similar else "Casi lo logras"
    
    def detectar_intencion_salir(self, texto: str) -> bool:
        """
        Detecta si el niño quiere salir/terminar
        
        Returns:
            True si quiere salir, False en caso contrario
        """
        if not texto or not texto.strip():
            return False
        
        # Palabras clave directas
        palabras_salida = ['adiós', 'adios', 'chao', 'chau', 'bye', 'hasta luego', 
                          'me voy', 'ya no quiero', 'no quiero más', 'no quiero mas',
                          'ya basta', 'terminar', 'salir', 'parar']
        
        texto_lower = texto.lower()
        for palabra in palabras_salida:
            if palabra in texto_lower:
                return True
        
        # Usar IA para casos ambiguos
        prompt = f"""
¿El niño quiere TERMINAR/SALIR del programa con esta frase?
Frase: "{texto}"

Responde SOLO: si o no

Considera frases como:
- "ya no quiero", "me cansé", "quiero irme" → si
- "no entiendo", "no sé", "otra vez" → no
"""

        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.1
            )
            
            return 'si' in respuesta.choices[0].message.content.lower()
            
        except Exception as e:
            print(f"❌ Error en detectar_intencion_salir: {e}")
            return False
    
    def generar_feedback_motivador(self, contexto: str) -> str:
        """
        Genera feedback motivador según el contexto
        
        Args:
            contexto: "exito", "error", "reintento", "frustracion"
        """
        prompts = {
            "exito": "Genera una frase MUY corta de celebración para un niño que acertó. Usa un emoji.",
            "error": "Genera una frase MUY corta de ánimo para un niño que falló, pero motivándolo a seguir.",
            "reintento": "Genera una frase MUY corta pidiendo al niño que intente de nuevo, con paciencia.",
            "frustracion": "Genera una frase MUY corta reconfortante para un niño frustrado, ofreciendo un descanso."
        }
        
        prompt = prompts.get(contexto, prompts["exito"])
        
        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres DODO, un robot amigable. Responde con UNA frase muy corta (máximo 10 palabras)."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,
                temperature=0.8
            )
            
            return respuesta.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error en generar_feedback: {e}")
            # Fallbacks
            fallbacks = {
                "exito": "¡Excelente! Lo hiciste muy bien 🌟",
                "error": "¡Buen intento! Vamos otra vez 💪",
                "reintento": "Inténtalo de nuevo, con calma 😊",
                "frustracion": "Descansemos un momento, está bien 💙"
            }
            return fallbacks.get(contexto, fallbacks["exito"])


# Instancia global
_asistente_inteligente = AsistenteInteligente()


# ========== FUNCIONES DE ACCESO RÁPIDO ==========

def consultar(texto: str, contexto: str = "") -> str:
    """Consulta general al asistente"""
    return _asistente_inteligente.consultar(texto, contexto)


def validar_si_no(texto: str) -> Tuple[bool, str]:
    """Valida respuesta de sí/no"""
    return _asistente_inteligente.validar_si_no(texto)


def validar_nombre(texto: str) -> Tuple[bool, Optional[str]]:
    """Valida y extrae nombre"""
    return _asistente_inteligente.validar_nombre(texto)


def validar_edad(texto: str) -> Tuple[bool, Optional[int]]:
    """Valida y extrae edad"""
    return _asistente_inteligente.validar_edad(texto)


def comparar_palabras(esperada: str, dicha: str) -> Tuple[bool, float, str]:
    """Compara palabra esperada con la dicha"""
    return _asistente_inteligente.comparar_palabras(esperada, dicha)


def detectar_salir(texto: str) -> bool:
    """Detecta si el niño quiere salir"""
    return _asistente_inteligente.detectar_intencion_salir(texto)


def feedback_motivador(contexto: str) -> str:
    """Genera feedback motivador"""
    return _asistente_inteligente.generar_feedback_motivador(contexto)
