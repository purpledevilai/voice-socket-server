import base64
import numpy as np
from models.AIVoiceChat import AIVoiceChat


async def handle_audio_data(voice_chat: AIVoiceChat, data: dict):

    # Audio data
    base64_audio = data.get("base64_audio")
    if base64_audio == None:
        raise Exception("No base64_audio provided")

    # PCM data
    pcm_data = np.frombuffer(base64.b64decode(base64_audio), dtype=np.int16)

    # Pass audio data to voice chat instance
    voice_chat.on_audio_data(pcm_data)