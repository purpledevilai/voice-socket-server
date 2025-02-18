import base64
import numpy as np
import asyncio
from stores.connections import connections
from lib.perform_vad import perform_vad



async def handle_audio_data(data):

    # Context ID
    context_id = data["context_id"]

    # Audio data
    base64_audio = data.get("base64_audio")
    if base64_audio == None:
        raise Exception("No base64_audio provided")

    # PCM data
    pcm_data = np.frombuffer(base64.b64decode(base64_audio), dtype=np.int16)

    # Store audio data
    connections[context_id]["pcm_samples"].extend(pcm_data)

    if not connections[context_id]["is_doing_vad"]:
        print("Starting VAD")
        connections[context_id]["is_doing_vad"] = True
        asyncio.create_task(perform_vad(context_id))