import base64
import os
import requests
import tempfile


def text_to_base64_audio(text):
    try:
        # Call ElevenLabs API for text-to-speech
        voice_id = "IKne3meq5aSn9XLyUdCD"
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": os.getenv('ELEVENLABS_API_KEY')
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            },
            stream=True
        )
        if response.status_code != 200:
            raise Exception(
                f"ElevenLabs API error: {response.status_code} {response.text}")

        # Save TTS response to a temporary file
        CHUNK_SIZE = 1024
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as output_audio_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    output_audio_file.write(chunk)
            output_audio_path = output_audio_file.name

        # Read the audio file and encode it as Base64
        with open(output_audio_path, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

        return encoded_audio

    except Exception as e:
        raise Exception(f"Error converting text to audio: {e}")

    finally:
        # Clean up temporary files
        if 'output_audio_path' in locals() and os.path.exists(output_audio_path):
            os.remove(output_audio_path)
