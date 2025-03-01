import os
import whisper

print("Loading whisper model...")
model = whisper.load_model("tiny")
print("Whisper model loaded.")


def transcribe_audio(audio_file_path, delete_file = False):
    transcription_result = model.transcribe(audio_file_path, fp16=False)
    if delete_file:
        os.remove(audio_file_path)
    return transcription_result.get("text", "")
