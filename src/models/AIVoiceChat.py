import os
import numpy as np
from lib.log import log
import asyncio
from lib.perform_vad import perform_vad
from lib.transcribe_audio import transcribe_audio


class AIVoiceChat:
    def __init__(self, websocket, sample_rate = 16000):
        self.websocket = websocket
        self.sample_rate = sample_rate
        self.pcm_samples = []
        self.collecting_audio = True
        self.start_listening()

    def start_listening(self):
        #log("AIVoiceChat:", "Starting to listen")
        self.pcm_samples = []
        self.collecting_audio = True
        asyncio.create_task(perform_vad(
            sample_rate=self.sample_rate,
            pcm_samples=self.pcm_samples,
            on_detected_audio_file=self.on_detected_audio_file
        ))

    def on_audio_data(self, data: np.array):
        if self.collecting_audio:
            self.pcm_samples.extend(data)

    def on_detected_audio_file(self, file_path: str):
        #log("AIVoiceChat:", f"Detected audio file: {file_path}")
        self.stop_listening() 
        transcription = transcribe_audio(file_path)
        os.remove(file_path)
        if transcription:
            print(f"Transcription: {transcription}")
        self.start_listening()

    def stop_listening(self):
        self.collecting_audio = False