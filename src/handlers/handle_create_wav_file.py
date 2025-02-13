from stores.connections import connections
from lib.create_wav_from_pcm import create_wav_from_pcm


async def handle_create_wav_file(data):
    # Context ID
    context_id = data["context_id"]

    # PCM samples
    pcm_samples = connections[context_id]["pcm_samples"]

    # Create wav file
    wav_file_path = create_wav_from_pcm(pcm_samples, connections[context_id]["sample_rate"])
    print(f"Wav file created: {wav_file_path}")