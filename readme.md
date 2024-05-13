# Run a complete AI agent locally
With this small project you can run Ollama with llama-3-8b model locally. Also, it uses [Whisper Timestamped](https://github.com/linto-ai/whisper-timestamped) to receive the audio from a microphone of your choose. When the completion (streamed in the console) is ready, the output is then read using the library pyttsx3 (in the future planning to change it for a local AI voice generator also open-source and locally :)

### [Video tutorial: How to Run LLAMA 3 locally](https://youtu.be/5jtGHk7xths?si=3WyyUmXC6t39m87w)
![image](https://github.com/Charlytoc/complete-ai-agent/assets/107764250/00c30c0b-44e9-4cba-937c-e1f89ccbacd8)

### [Retrieval Augmented Generation local with Llama and Chroma video](https://www.youtube.com/watch?v=vjQAxJ7OVxw)


1. You must have Python to run this project. If you don't have it, you can download it [here](https://www.python.org/downloads/).

2. Install Ollama from its website: [Ollama](https://ollama.com/download)

3. Execute the installer for your operating system
Just click the installer and press "install" or something

Create a new environment with the following command:
```bash
py -m venv venv
```

Activate the environment with the following command:
```bash
source venv/Scripts/activate
```

Install the required packages with the following command:
```bash
pip install -r requirements.txt
```

Run the application with the following command:
```bash
python main.py
```

