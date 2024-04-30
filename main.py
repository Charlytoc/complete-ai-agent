import os
import time
import sounddevice as sd
import numpy as np
import wavio
import pyttsx3
from src.completions import create_completion_ollama
from src.transcriptions import transcribe_timestamped

# Initialize the text-to-speech engine
engine = pyttsx3.init()
# Print available devices and their IDs
MIC_ID = None

if not MIC_ID:
    print("\033[92mAvailable audio devices:\033[0m")  # Green color start
    device_info = sd.query_devices()
    for i, device in enumerate(device_info):
        print(f"ID: \033[92m{i}\033[0m, Name: {device['name']}")  # Green color end

mic_id = MIC_ID or int(
    input("\033[92mEnter the microphone ID: \033[0m")
)  # User inputs the correct device ID

fs = 44100  # Sample rate
channels = 1  # Number of channels

# Create a directory inside recording_sessions with the date in milliseconds as name
session_dir = f"recording_sessions/{int(time.time() * 1000)}"
os.makedirs(session_dir, exist_ok=True)

recording_counter = 0
language_map = {
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "it": "italian",
    "pt": "portuguese",
    "nl": "dutch",
    "pl": "polish",
    "ru": "russian",
    "ja": "japanese",
    "ko": "korean",
    "zh": "chinese",
    "ar": "arabic",
}

while True:
    try:
        # Create a list to store the recording chunks
        recording_chunks = []

        # Define the callback function to store data
        def callback(indata, frames, time, status):
            if status:
                print(status)
            recording_chunks.append(indata.copy())

        # Ask the user to press Enter to start recording
        input("\nPress Enter to start recording")
        print("\033[91m👂🏻 Listening...\033[0m")
        # Start recording with the selected microphone
        stream = sd.InputStream(
            samplerate=fs, channels=channels, callback=callback, device=mic_id
        )
        with stream:
            input("Press Enter to stop recording")
            stream.stop()

        # Concatenate all the recording chunks
        myrecording = np.concatenate(recording_chunks, axis=0)

        RECORDING_OUTPUT = f"{session_dir}/recording_{recording_counter}.wav"

        # Save the recording to a file
        wavio.write(RECORDING_OUTPUT, myrecording, fs, sampwidth=2)

        transcription = transcribe_timestamped(RECORDING_OUTPUT)
        # Save the transcription to a file
        with open(f"{session_dir}/transcription.txt", "a") as file:
            _content = f"Recording {recording_counter}\n\n{transcription['text']}\n\n"
            file.write(_content)

        voices = engine.getProperty("voices")
        for voice in voices:
            if (
                language_map[transcription["language"]] in voice.name.lower()
            ):  # Check if the language is in the voice name
                engine.setProperty("voice", voice.id)
                break

        completion = create_completion_ollama(transcription["text"], stream=True)
        with open(f"{session_dir}/transcription.txt", "w") as file:
            _content = f"AI Message: {recording_counter}\n\n{transcription['text']}\n\n"
            file.write(_content)
        # Read aloud the transcription
        engine.say(completion)
        engine.runAndWait()

        # Save the completion to a file
        # Later, when saving the AI completion:
        with open(f"{session_dir}/transcription.txt", "a") as file:
            _content = f"AI Message: {recording_counter}\n\n{completion}\n\n"
            file.write(_content)

        # Increment the counter for the next recording
        recording_counter += 1

    except KeyboardInterrupt:
        print("\nRecording loop terminated by user.")
        break
