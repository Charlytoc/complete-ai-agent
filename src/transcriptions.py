import whisper_timestamped as whisper

WHISPER_MODEL = "tiny"

def transcribe_timestamped(audio_file_path, output_format="vtt") -> str:
    audio = whisper.load_audio(audio_file_path)
    model = whisper.load_model(WHISPER_MODEL, device="cpu")
    result = whisper.transcribe(model, audio, compute_word_confidence=False)
    return result