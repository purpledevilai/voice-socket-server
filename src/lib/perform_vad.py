import numpy as np
from lib.log import log
from lib.create_wav_from_pcm import create_wav_from_pcm
from lib.transcribe_audio import transcribe_audio
import webrtcvad
import asyncio



async def perform_vad(sample_rate: int, pcm_samples: list, on_detected_audio_file: callable):

    # Tuning parameters
    vad_aggresiveness = 3 # integer between 0 and 3. 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive
    wait_length_for_more_samples = 0.05 # The length of time to wait for more samples to arrive
    pause_length_ms = 500 # The length of silence to wait for before ending the VAD
    whisper_check_every_ms = 1000 # The length of time to wait between checking if a sample has a transcription
    empty_transcription_count_to_end = 3 # The number of empty transcriptions to wait for before ending the VAD


    # VAD Setup
    frame_durration_ms = 30
    samples_per_frame = sample_rate * frame_durration_ms // 1000
    vad = webrtcvad.Vad()
    vad.set_mode(vad_aggresiveness)

    # Whisper check detection
    samples_per_whisper_check = sample_rate * whisper_check_every_ms // 1000

    # VAD Loop
    sample_index = 0
    has_begun_speaking = False
    speech_start_index = 0
    speech_end_index = 0
    pause_samples_to_wait = sample_rate * pause_length_ms // 1000
    pause_sample_count = 0
    whisper_check_sample_count = 0
    empty_transcription_count = 0

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
                #log("perform_vad:", "Started speaking")
                has_begun_speaking = True
                speech_start_index = sample_index
            pause_sample_count = 0 # Reset pause count if speaking
        else:
            # No speech detected: increment pause count if speaking
            if has_begun_speaking:
                pause_sample_count += samples_per_frame
                if pause_sample_count >= pause_samples_to_wait:
                    #log("perform_vad:", "Stopped speaking")
                    speech_end_index = sample_index
                    break # End VAD

        # Whisper check
        whisper_check_sample_count += samples_per_frame
        if (whisper_check_sample_count >= samples_per_whisper_check):
            whisper_check_sample_count = 0
            whisper_check_wav = create_wav_from_pcm(pcm_samples[sample_index - samples_per_whisper_check: sample_index], sample_rate)
            transcription = transcribe_audio(whisper_check_wav, delete_file=True)
            if not transcription:
                empty_transcription_count += 1
            if empty_transcription_count >= empty_transcription_count_to_end:
                log("perform_vad:", "Stopped speaking due to empty transcriptions")
                speech_end_index = sample_index
                break # End VAD

            
        # Increment step
        sample_index += samples_per_frame

    # Create wav file
    wav_file_path = create_wav_from_pcm(pcm_samples[speech_start_index:speech_end_index], sample_rate)

    # Notify voice chat instance
    on_detected_audio_file(wav_file_path)

    