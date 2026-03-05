# Local Voice Skill for OpenClaw

Complete local speech-to-text (STT) and text-to-speech (TTS) integration for OpenClaw.

- **STT**: faster-whisper (4x faster than original Whisper)
- **TTS**: Kokoro-82M (production quality, 54 voices)
- **Platforms**: Telegram, Discord
- **Privacy**: 100% local, no cloud APIs

## 🚀 Quick Start (5 minutes)

### Prerequisites

You already have:
- ✅ Kokoro TTS running in Docker on GPU (port 8880)
- ✅ OpenClaw installed

You need:
- Python 3.9+
- FFmpeg
- faster-whisper

### Installation

```bash
# 1. Install dependencies
pip install faster-whisper pyav requests

# 2. Install FFmpeg (if not already installed)
# Linux:   sudo apt install ffmpeg
# macOS:   brew install ffmpeg
# Windows: choco install ffmpeg

# 3. Copy skill files to OpenClaw skills directory
# (See Step 2 below)
```

### Step 2: Install the Skill

```bash
# Copy to OpenClaw skills directory
mkdir -p ~/.openclaw/skills/local-voice/src
cp -r SKILL.md CONFIG.md README.md ~/.openclaw/skills/local-voice/
cp -r src/* ~/.openclaw/skills/local-voice/src/

# Install skill in OpenClaw
openclaw skills install ~/.openclaw/skills/local-voice
```

### Step 3: Test It

```bash
# Test STT
cd ~/.openclaw/skills/local-voice/src
python stt.py test_audio.wav

# Test TTS
python tts.py "Hello world!" test_output.mp3 af_bella

# Test integration
python integration.py
```

## 📖 Usage

### Method 1: Direct Python Usage

```python
from local_voice.src.integration import create_handler

# Create handler
handler = create_handler(
    stt_model="base",
    stt_device="cpu",
    tts_url="http://localhost:8880/v1",
    tts_voice="af_bella"
)

# Transcribe voice message
result = await handler.handle_incoming_voice(
    "voice_message.ogg",
    platform="telegram"
)

print(f"Transcription: {result['text']}")

# Generate voice response
response = await handler.generate_voice_response(
    "I received your message!",
    "response.ogg",
    voice="af_bella",
    platform="telegram"
)

print(f"Generated: {response['file_path']}")
```

### Method 2: From OpenClaw Agent

The skill will be available to your OpenClaw agent. When you send a voice message:

1. **Telegram/Discord receives voice message** → saves audio file
2. **OpenClaw agent receives file** → passes to local-voice skill
3. **STT transcribes audio** → returns text
4. **Agent processes text** → generates response
5. **TTS synthesizes response** → returns audio file
6. **Agent sends audio** → back to Telegram/Discord

### Method 3: CLI Tools

```bash
# Transcribe audio
python -c "
from local_voice.src.stt import quick_transcribe
text = quick_transcribe('voice.ogg', model_size='base')
print(text)
"

# Synthesize audio
python -c "
from local_voice.src.tts import quick_synthesize
quick_synthesize('Hello!', 'output.mp3', voice='af_bella')
"

# Convert audio format
python -c "
from local_voice.src.processor import quick_convert
quick_convert('input.mp3')
"
```

## ⚙️ Configuration

Edit `CONFIG.md` or set environment variables:

```bash
export LOCAL_VOICE_STT_MODEL="base"
export LOCAL_VOICE_STT_DEVICE="cpu"
export LOCAL_VOICE_TTS_URL="http://localhost:8880/v1"
export LOCAL_VOICE_TTS_VOICE="af_bella"
```

## 🎭 Available Voices

```python
from local_voice.src.tts import LocalTTS

tts = LocalTTS()
voices = tts.get_voices()
print("Available voices:")
for voice in voices:
    print(f"  - {voice}")
```

Common American English voices:
- `af_bella` - Female, friendly (default)
- `af_heart` - Female, warm
- `af_sky` - Female, calm
- `af_nicole` - Female, professional
- `af_sarah` - Female, gentle
- `af_michael` - Male, professional
- `af_adam` - Male, casual
- `af_joe` - Male, friendly

## 📊 Performance

### STT (faster-whisper)

| Model | CPU Speed | GPU Speed | VRAM |
|-------|-----------|-----------|------|
| tiny | 3-5x | 50-100x | ~1 GB |
| base | 2-3x | 30-60x | ~1.5 GB |
| small | 1.5-2x | 15-30x | ~2.5 GB |

### TTS (Kokoro)

| Setup | Speed | 30s audio |
|-------|-------|-----------|
| GPU | 100x | ~0.3s |
| CPU | 10-35x | ~1-3s |

### Full Pipeline (STT + TTS)
- **With GPU**: < 2 seconds
- **CPU-only**: 5-15 seconds

## 🔧 Troubleshooting

### Issue: "FFmpeg not found"

```bash
# Install FFmpeg
# Linux:   sudo apt install ffmpeg
# macOS:   brew install ffmpeg
# Windows: choco install ffmpeg
```

### Issue: "Kokoro TTS not responding"

```bash
# Check if Docker container is running
docker ps | grep kokoro

# Check logs
docker logs <container_name>

# Restart if needed
docker restart <container_name>

# Or start manually
docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest
```

### Issue: "STT model download slow"

```python
# Set HuggingFace cache directory
import os
os.environ['HF_HUB_CACHE'] = '/path/to/cache'

# Or manually download
from huggingface_hub import snapshot_download
snapshot_download("Systran/faster-whisper-base")
```

### Issue: "Out of memory"

```python
# Use smaller STT model
handler = create_handler(stt_model="tiny")

# Or use int8 quantization (default for CPU)
# Already enabled by default!
```

### Issue: "Audio format not supported"

```python
from local_voice.src.processor import AudioProcessor

processor = AudioProcessor()

# Convert to Whisper-compatible format
converted = processor.prepare_for_stt("input.ogg")
```

## 🎯 Best Practices

1. **Start with base model** - Good balance of speed/accuracy
2. **Use GPU if available** - 10-20x faster
3. **Auto-cleanup temp files** - Prevent disk space issues
4. **Handle errors gracefully** - Network issues, missing files
5. **Test with sample audio** - Before production use
6. **Monitor logs** - Debug issues quickly

## 📚 API Reference

### VoiceMessageHandler

```python
handler = VoiceMessageHandler(
    stt_client=LocalSTT(...),
    tts_client=LocalTTS(...),
    audio_processor=AudioProcessor(...),
    config={...}
)

# Handle incoming voice
result = await handler.handle_incoming_voice(audio_path, platform)

# Generate voice response
response = await handler.generate_voice_response(text, output_path)

# Full pipeline
result = await handler.full_conversation_pipeline(
    input_audio,
    response_text,
    output_audio,
    platform
)
```

### LocalSTT

```python
stt = LocalSTT(model_size="base", device="cpu")

# Transcribe
result = stt.transcribe(audio_path)
print(result["text"])

# With word timestamps
result = stt.transcribe(audio_path, word_timestamps=True)

# Streaming
stt.transcribe_streaming(audio_path, callback)
```

### LocalTTS

```python
tts = LocalTTS(base_url="http://localhost:8880/v1")

# Synthesize to file
tts.synthesize("Hello!", output_file="output.mp3")

# Get bytes
audio = tts.synthesize("Hello!", response_format="mp3")

# Streaming
for chunk in tts.synthesize_streaming("Hello!"):
    # Process chunk
    pass
```

## 🔗 Integration with OpenClaw

This skill integrates naturally with OpenClaw's messaging system:

1. **Skill Installation**: Use `openclaw skills install`
2. **Message Handling**: Automatically processes voice messages
3. **File Conversion**: Handles Telegram (OGG) and Discord (MP3/OGG)
4. **Response Generation**: Returns audio in correct format for platform

The skill provides:
- Automatic voice message transcription
- Voice response generation
- Audio format conversion
- Error handling and logging

## 📄 License

MIT License - Free to use and modify

## 🤝 Contributing

Feel free to submit issues and pull requests!

## 📞 Support

- Report issues in OpenClaw Discord
- Check logs for detailed error messages
- Test with sample audio files first

---

**Status**: Ready for production use ✅
**Last Updated**: February 14, 2026
**Version**: 1.0.0
