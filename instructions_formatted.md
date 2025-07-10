# RealtimeVoiceChat: Mac (Apple Silicon) Setup Instructions

## Prerequisites
- **Python** 3.9+ (but <3.13; recommend 3.10 or 3.11 for best compatibility)
- **Homebrew** (for easy package management)
- **No NVIDIA GPU:** You will be running everything on CPU, which will be slower for AI tasks, but it will work.
- **Docker (Optional):** You can try Docker, but GPU acceleration is not available on Mac, so manual install is often easier for debugging.

---

## 1. Install Homebrew (if not installed)
Run the following command in your terminal:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 2. Install Python (if needed)
```bash
brew install python@3.10  # or python@3.11
```

---

## 3. Clone the Repository (or cd into repository if already installed)
```bash
git clone https://github.com/KoljaB/RealtimeVoiceChat.git
cd RealtimeVoiceChat
```

---

## 4. Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

---

## 5. Upgrade pip
```bash
pip install --upgrade pip
```

---

## 6. Install PyTorch (CPU-only for Apple Silicon)
```bash
pip install torch torchvision torchaudio
```

---

## 7. Install Other Requirements
```bash
pip install -r requirements.txt
```
- If you get errors with `deepspeed`, you can skip it for now (it's mainly for TTS speedup and not required for basic functionality on CPU).

---

## 8. Install PortAudio for Microphone Support (if not already installed)
```bash
brew install portaudio
pip install pyaudio
```
- If you get errors about missing libraries (e.g. `libomp`) try:
  ```bash
  brew install libomp
  ```
- If you get errors with `pyaudio`, ensure `portaudio` is installed via Homebrew.
- If you get errors with `deepspeed`, you can comment it out in `requirements.txt` and try again.

---

## 9. Deepspeed Errors
- Change all instances of `use_deepspeed=True` to `False` in the codebase.
- In `server.py`, comment out the `TTS_START_ENGINE="coqui"` and switch it to a different model (e.g., `kokoro` or `orpheus`).

---

## 10. Download and Install Ollama (if not already installed)
- Download from: [https://ollama.com/download](https://ollama.com/download)
- After installing, run the Ollama server in a terminal:
  ```bash
  ollama serve
  ```
- Make sure it's running and accessible at [http://127.0.0.1:11434](http://127.0.0.1:11434)

---

## 11. Pull the Mistral Model for Ollama
```bash
ollama pull mistral
```
- This will download a ~4.1GB local model (required for Mac/CPU use).

---

## 12. Update Model References in the Code
- Change all instances of the model `"hf.co/bartowski/huihui-ai_Mistral-Small-24B-Instruct-2501-abliterated-GGUF:Q4_K_M"` to `"mistral"` (in `server.py` and `speech_pipeline_manager.py`).

---

## 13. Optimize Transcription for CPU
- Change two instances of `base.en` at the top of `transcribe.py` to `tiny.en` for better performance running on CPU.

---

## 14. (Optional) Update System Prompt
- Edit `system_prompt.txt` to change the chatbot's persona or instructions.
- For better performance on CPU, keep the prompt shorter.

---

## 15. Disable Wake Words (Apple Silicon Macs)
- In `transcribe.py`, set:
  ```python
  "wake_words": "",
  "wakeword_backend": None,
  ```
  (This disables wake word detection, which is not supported on Apple Silicon Macs.)

---

## 16. Run the Server
```bash
python server.py
```

---

## 17. Access the Web Interface
- Open [http://localhost:8000](http://localhost:8000) in your browser to access the real-time voice chat interface.

---
