# voz_eleven.py
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import os

# Cargar .env
load_dotenv()

# Cliente ElevenLabs
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def hablar(texto: str):
    """
    Genera voz con ElevenLabs y la reproduce directo (PCM sin archivo).
    """
    try:
        # Obtener audio en formato PCM RAW
        generador = client.text_to_speech.convert(
            voice_id="Sarah",
            model_id="eleven_multilingual_v2",
            text=texto,
            output_format="pcm_16000"   # <--- formato correcto
        )

        # Unir chunks
        audio_bytes = b"".join(chunk for chunk in generador)

        # Convertir RAW PCM en numpy
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

        # Reproducir a 16 kHz mono
        sd.play(audio_np, 16000)
        sd.wait()

    except Exception as e:
        print("❌ Error generando o reproduciendo voz:", e)
