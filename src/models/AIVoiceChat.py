import json
import os
import numpy as np
from lib.sentence_stream import sentence_stream
from lib.log import log
import asyncio
from lib.perform_vad import perform_vad
from lib.transcribe_audio import transcribe_audio
from models.AgentChatStream import AgentChatStream
from lib.text_to_base64_audio import text_to_base64_audio


class AIVoiceChat:
    def __init__(self, websocket, agent_chat_stream: AgentChatStream, sample_rate=16000):
        self.websocket = websocket
        self.agent_chat_stream = agent_chat_stream
        self.sample_rate = sample_rate
        self.pcm_samples = []
        self.collecting_audio = True
        self.has_started_vad = False
        self.start_listening()

    def start_listening(self):
        log("AIVoiceChat:", "Starting to listen")
        self.pcm_samples = []
        self.collecting_audio = True
        
    def stop_listening(self):
        log("AIVoiceChat:", "Stopping listening")
        self.collecting_audio = False
        self.has_started_vad = False

    def on_audio_data(self, data: np.array):
        if self.collecting_audio:
            self.pcm_samples.extend(data)
            if not self.has_started_vad:
                self.has_started_vad = True
                log("AIVoiceChat:", "Starting VAD")
                asyncio.create_task(perform_vad(
                    sample_rate=self.sample_rate,
                    pcm_samples=self.pcm_samples,
                    on_detected_audio_file=self.on_detected_audio_file
                ))
                

    def on_detected_audio_file(self, file_path: str):

        # Stop listening while we process the audio
        self.stop_listening()

        # Transcribe the audio
        transcription = transcribe_audio(file_path)
        os.remove(file_path)

        # If no transcription, start listening again
        if not transcription:
            log("AIVoiceChat:", f"Detected audio file with no transcription")
            self.start_listening()
            return
        
        # Inform the client that we have transcribed the audio
        asyncio.create_task(self.websocket.send(json.dumps({
            "type": "transcription",
            "transcription": transcription
        })))
        
        # Invoke the agent with the transcription
        asyncio.create_task(self.invoke_agent(transcription))

        print("Invoking agent with transcription:", transcription)

    async def invoke_agent(self, text: str):

        # Add the human message and and get the token generator
        token_generator = self.agent_chat_stream.add_human_message_and_invoke(text)

        # Iterate through the token generator
        sentence_index = 0 # To get last audio index
        for sentence in sentence_stream(token_generator):

            print("Sentence:", sentence)

            # create audio from text the and send
            asyncio.create_task(self.tts_and_send(sentence, sentence_index))

            sentence_index += 1

        # Last sentence processed. Send the last audio index
        await self.websocket.send(json.dumps({
            "type": "last_audio_index",
            "index": sentence_index - 1  # -1 because we incremented before exiting the loop
        }))

        # Start listening again
        self.start_listening()

    async def tts_and_send(self, text: str, index: int):
        try:
            base64_audio = text_to_base64_audio(text)
            await self.websocket.send(json.dumps({
                "type": "audio",
                "index": index,
                "base64_audio": base64_audio
            }))
            print("Audio sent", index)
        except Exception as e:
            log("AIVoiceChat:", f"Error sending audio: {e}")
