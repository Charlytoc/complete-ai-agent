import os
import time
import sounddevice as sd
import numpy as np
import wavio
import pyttsx3
from src.completions import create_completion_ollama
from src.transcriptions import transcribe_timestamped
from src.vectors import ChromaManager
from src.utils.print_in_color import print_in_color

def get_system_prompt(context: str, language: str = "English"):
    return f"""You are an useful assistant. Your task is just talk with the user and help him solve his task.
    
    This context may be useful for your task:
    '''
    {context}
    '''
    
    You MUST answer in {language} language. This is mandatory.

    The user message is the only one thing the user said. You must generate a completion based on that message and use the context if necessary. If you DON'T have a context, don't say anything you are not sure about, tell the user you don't have enough information to answer the question.
    """

chroma = ChromaManager()

# Ask the user to choose the conversation type
conversation_type = input("Choose conversation type (text/voice): ").lower()

if conversation_type == "text":
    while True:
        try:
            user_message = input("\nEnter your message: ")
            if user_message.lower() == "exit":
                print("Exiting text conversation.")
                break

            # Process the text message as needed
            # For example, generate a response using an AI model
            # This is a placeholder for the response generation logic
            context = chroma.get_context_from_query(query_text=user_message, n_results=5)

            print("---------------------")
            print(context)
            print("---------------------")
            # Generate a completion based on the transcription and the context
            completion = create_completion_ollama(prompt=user_message,
                                                  system_prompt=get_system_prompt(context, "autodetect"), stream=True)
            

        except KeyboardInterrupt:
            print("\nText conversation terminated by user.")
            break

elif conversation_type == "voice":

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

            # Use Whisper to transcribe the audio
            transcription = transcribe_timestamped(RECORDING_OUTPUT)

            print_in_color(f"Transcription {recording_counter}: \n{transcription['text']}", "green")
            # Save the transcription to a file
            with open(f"{session_dir}/transcription.txt", "a") as file:
                _content = f"User message {recording_counter}:\n{transcription['text']}\n\n"
                file.write(_content)

            # Set the voice for the text-to-speech engine based on the language of the transcription
            voices = engine.getProperty("voices")
            for voice in voices:
                if (
                    language_map[transcription["language"]] in voice.name.lower()
                ):  # Check if the language is in the voice name
                    engine.setProperty("voice", voice.id)
                    break

            context = chroma.get_context_from_query(query_text=transcription["text"], n_results=5)

            # Generate a completion based on the transcription and the context
            completion = create_completion_ollama(prompt=transcription["text"],
                                                  system_prompt=get_system_prompt(context, transcription["language"]), stream=True)

            # Save the completion to a file
            with open(f"{session_dir}/transcription.txt", "a", encoding="utf-8") as file:
                _content = f"AI Message {recording_counter}:\n{completion}\n\n"
                file.write(_content)

            # Read aloud the completion
            engine.say(completion)
            engine.runAndWait()

            # Increment the counter for the next recording
            recording_counter += 1

        except KeyboardInterrupt:
            print("\nRecording loop terminated by user.")
            break
