import base64
import numpy as np
from datetime import datetime
from stores.connections import connections


def measure_sample_rate(context_id, number_of_samples):
    connection = connections[context_id]

    if connection["first_sample_time_stamp"] == None:
        connection["first_sample_time_stamp"] = datetime.now()

    connection["last_sample_time_stamp"] = datetime.now()

    connection["total_samples"] += number_of_samples


async def handle_audio_data(data):

    # Context ID
    context_id = data["context_id"]

    # Audio data
    base64_audio = data.get("base64_audio")
    if base64_audio == None:
        raise Exception("No base64_audio provided")

    # PCM data
    pcm_data = np.frombuffer(base64.b64decode(base64_audio), dtype=np.int16)

    # Measure sample rate
    # measure_sample_rate(context_id, len(pcm_data))

    # Store audio data
    connections[context_id]["pcm_samples"].extend(pcm_data)

    print(f"Audio data received: {len(pcm_data)} samples")
