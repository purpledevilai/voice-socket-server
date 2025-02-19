import whisper

print("Loading whisper model...")
model = whisper.load_model("tiny")
print("Whisper model loaded.")


def transcribe_audio(audio_file_path):
    transcription_result = model.transcribe(audio_file_path, fp16=False)
    return transcription_result.get("text", "")
