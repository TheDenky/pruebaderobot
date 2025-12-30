from openai import OpenAI
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

class Asistente:
    def __init__(self):
        try:
            self.client = OpenAI()
        except Exception as e:
            print("❌ Error inicializando OpenAI:", e)
            raise

    def consultar(self, texto: str) -> str:
        # Validación básica
        if not texto or not texto.strip():
            return "Dime algo y te ayudaré 😊"

        try:
            respuesta = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un asistente amable para niños con problemas del habla. "
                            "Usa frases cortas, simples y muy claras."
                        )
                    },
                    {"role": "user", "content": texto}
                ],
                max_tokens=50,
                temperature=0.4
            )

            return respuesta.choices[0].message.content
        
        except Exception as e:
            print("❌ Error al consultar la API:", e)
            return "Lo siento, tuve un problema. ¿Puedes intentar otra vez?"

# Instancia global
_asistente = Asistente()

# Función simplificada para el usuario
def consultar(texto: str) -> str:
    return _asistente.consultar(texto)
