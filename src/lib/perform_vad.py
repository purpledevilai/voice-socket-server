import numpy as np
from lib.create_wav_from_pcm import create_wav_from_pcm
from stores.connections import connections
import webrtcvad
import asyncio



async def perform_vad(context_id):

    # Tuning parameters
    vad_aggresiveness = 3 # integer between 0 and 3. 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive
    wait_length_for_more_samples = 0.05 # The length of time to wait for more samples to arrive
    pause_length_ms = 2000 # The length of silence to wait for before ending the VAD

    # VAD Setup
    frame_durration_ms = 30
    sample_rate = connections[context_id]["sample_rate"]
    samples_per_frame = sample_rate * frame_durration_ms // 1000
    vad = webrtcvad.Vad()
    vad.set_mode(vad_aggresiveness)

    # PCM samples
    pcm_samples = connections[context_id]["pcm_samples"] 

    # VAD Loop
    sample_index = 0
    has_begun_speaking = False
    speech_start_index = 0
    speech_end_index = 0
    pause_samples_to_wait = pause_length_ms // frame_durration_ms
    pause_sample_count = 0

    while True:
        # Wait till we have enough samples
        if sample_index + samples_per_frame > len(pcm_samples):
            await asyncio.sleep(wait_length_for_more_samples)  # Wait briefly for more samples to arrive
            continue

        # Get the frame
        frame = np.array(pcm_samples[sample_index:sample_index + samples_per_frame]).tobytes()

        # Detect if frame is speech
        is_speech = vad.is_speech(frame, sample_rate)

        # Track voice activity
        if is_speech:
            # Speech detected: start if not already started, reset pause count
            if not has_begun_speaking:
                print("Started speaking")
                has_begun_speaking = True
                speech_start_index = sample_index
            pause_sample_count = 0 # Reset pause count if speaking
        else:
            # No speech detected: increment pause count if speaking
            if has_begun_speaking:
                pause_sample_count += 1
                if pause_sample_count >= pause_samples_to_wait:
                    print("Stopped speaking")
                    speech_end_index = sample_index
                    break # End VAD
            
        # Increment step
        sample_index += samples_per_frame

    wav_file_path = create_wav_from_pcm(pcm_samples[speech_start_index:speech_end_index], sample_rate)
    print(f"Wav file created: {wav_file_path}")

    