import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import pyaudio

load_dotenv()

class TTS:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))

        # Voz recomendada para español
        self.voice_id = "FGY2WhTYpPnrIDTdsKH5"  # Laura

        # Inicializar pyaudio
        self.p = pyaudio.PyAudio()

    def hablar(self, texto: str):
        try:
            # Solicitar audio en streaming
            stream_gen = self.client.text_to_speech.convert_as_stream(
                voice_id=self.voice_id,
                text=texto,
                model_id="eleven_multilingual_v2",
            )

            # Abrir stream de audio en PyAudio
            audio_stream = self.p.open(
                format=self.p.get_format_from_width(2),  # 16-bit
                channels=1,
                rate=22050,
                output=True
            )

            for chunk in stream_gen:
                audio_stream.write(chunk)

            audio_stream.stop_stream()
            audio_stream.close()

        except Exception as e:
            print(f"❌ Error al generar voz: {e}")

    def __del__(self):
        self.p.terminate()


# Uso rápido
if __name__ == "__main__":
    tts = TTS()
    tts.hablar("Hola, soy Laura. Estoy lista para ayudarte con lo que necesites.")
