# Local Voice Skill

OpenClaw skill for local speech-to-text (STT) and text-to-speech (TTS) using faster-whisper and Kokoro TTS.

## Purpose

This skill enables OpenClaw agents to:
- Transcribe voice messages from Telegram/Discord (STT)
- Generate voice responses (TTS)
- Process audio formats automatically
- Handle full voice conversation pipelines

## Features

- **STT**: faster-whisper (4x faster than original Whisper)
- **TTS**: Kokoro-82M via Kokoro-FastAPI (54 voices)
- **Automatic audio conversion** for platform compatibility
- **Voice message handling** for Telegram and Discord
- **Streaming support** for low-latency responses

## Requirements

- Docker running Kokoro-FastAPI (TTS) on port 8880
- Python 3.9+
- faster-whisper installed
- FFmpeg for audio conversion

## Quick Start

1. Install dependencies:
   ```bash
   pip install faster-whisper pyav requests
   ```

2. Start Kokoro TTS (if not already running):
   ```bash
   docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest
   ```

3. Install skill:
   ```bash
   openclaw skills install ~/.openclaw/skills/local-voice
   ```

## Usage

### Transcribe Voice Message

```python
from local_voice.src.stt import LocalSTT

stt = LocalSTT(model_size="base", device="cpu", compute_type="int8")
result = stt.transcribe("voice_message.ogg")
print(result["text"])
```

### Generate Voice Response

```python
from local_voice.src.tts import LocalTTS

tts = LocalTTS(base_url="http://localhost:8880/v1")
tts.synthesize(
    "Hello world!",
    output_file="output.mp3",
    voice="af_bella"
)
```

### Full Conversation Pipeline

```python
from local_voice.src.integration import VoiceMessageHandler
from local_voice.src.stt import LocalSTT
from local_voice.src.tts import LocalTTS
from local_voice.src.processor import AudioProcessor

# Initialize components
stt = LocalSTT()
tts = LocalTTS()
processor = AudioProcessor()
handler = VoiceMessageHandler(stt, tts, processor)

# Handle incoming voice message
result = await handler.handle_incoming_voice(
    "voice.ogg",
    platform="telegram"
)

# Generate voice response
response = await handler.generate_voice_response(
    "I received your message!",
    "response.ogg",
    platform="telegram"
)
```

## Configuration

Edit `CONFIG.md` to customize:
- STT model size and device (CPU/GPU)
- TTS voice and format
- Audio processing settings
- Platform-specific settings

## License

MIT License - Free to use and modify
