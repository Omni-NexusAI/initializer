# STT & TTS Investigation - Executive Summary

**Date**: February 14, 2026
**Status**: Complete

---

## Quick Recommendation

**Recommended Stack**: faster-whisper (STT) + Kokoro TTS (TTS)

**Why**:
- 4x faster than original Whisper (same accuracy)
- Production-quality TTS (82M parameters)
- Fully local (no cloud APIs)
- Open source (MIT + Apache 2.0)
- Easy Python integration

**Hardware**: CPU-only works, but GPU recommended for real-time

---

## Key Findings

### Kokoro TTS
- **What it is**: 82M parameter TTS model with commercial-quality output
- **Installation**: Docker recommended (single command)
- **Speed**: 100x realtime (GPU), 10-35x (CPU)
- **Quality**: Comparable to commercial TTS services
- **Cost**: Free to use, <$1 per million characters on cloud
- **License**: Apache 2.0 (commercial use allowed)
- **Features**: 54 voices, voice mixing, streaming, OpenAI-compatible API

**Quick Start**:
```bash
docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

### faster-whisper (STT) - RECOMMENDED
- **What it is**: Whisper reimplementation using CTranslate2
- **Speed**: 4x faster than OpenAI Whisper (same accuracy)
- **Memory**: 2-4x less memory than original
- **Features**: Batched transcription, VAD, word-level timestamps
- **License**: MIT
- **Performance**: 13 min audio in 17 seconds (GPU, batch=16)

**Quick Start**:
```bash
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.mp3")
```

### Alternative: whisper.cpp
- C++ implementation (minimal dependencies)
- 2-4x faster than original
- Cross-platform (including mobile)
- Quantization support
- Less familiar API

### Alternative: OpenAI Whisper
- Original implementation
- Best accuracy
- Easiest Python API
- Slower, higher memory

---

## Hardware Requirements

### Minimum (CPU-only)
- CPU: 4-core
- RAM: 8GB
- Storage: 10GB
- Latency: 5-15 seconds

### Recommended (GPU)
- GPU: NVIDIA RTX 4060 Ti 16GB+
- CPU: 8+ cores
- RAM: 16GB
- Storage: 20GB SSD
- Latency: < 2 seconds

### Model Recommendations
- **Personal use**: `base` STT model (good balance)
- **Production**: `small` STT model (better accuracy)
- **Real-time**: `tiny` STT model with GPU

---

## Integration with OpenClaw

### Current State
- OpenClaw has `tts` tool (ElevenLabs based, per AGENTS.md)
- Can extend with custom skill for local processing
- OpenAI-compatible API makes integration easy

### Proposed Integration
Create `local-voice/` skill with:

**Components**:
- `stt.py` - faster-whisper wrapper
- `tts.py` - Kokoro TTS client
- `processor.py` - Audio conversion pipeline
- `integration.py` - OpenClaw message handlers

**Key Features**:
- Handle Telegram/Discord voice messages
- Convert audio formats automatically
- Transcribe (STT) and synthesize (TTS)
- Full conversation pipeline support

**Audio Format Handling**:
- Telegram: OGG Opus (16kHz, mono)
- Discord: MP3 or OGG Opus
- Whisper requires: WAV (16kHz, mono, PCM)

---

## Installation Plan

### Step 1: Install Dependencies
```bash
# Install Docker, FFmpeg, Python
pip install faster-whisper pyav requests
```

### Step 2: Deploy Kokoro TTS
```bash
docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

### Step 3: Test TTS
```python
import requests
response = requests.post(
    "http://localhost:8880/v1/audio/speech",
    json={
        "model": "kokoro",
        "input": "Hello world!",
        "voice": "af_bella",
        "response_format": "mp3"
    }
)
with open("test.mp3", "wb") as f:
    f.write(response.content)
```

### Step 4: Test STT
```python
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("test.wav")
for segment in segments:
    print(f"[{segment.start:.2f}s] {segment.text}")
```

### Step 5: Create OpenClaw Skill
- Use code from full report (Section 3)
- Install skill in OpenClaw
- Configure endpoints

---

## Performance Summary

### STT (faster-whisper)
| Model | GPU Speed | CPU Speed | Realtime? |
|-------|-----------|-----------|-----------|
| tiny | 50-100x | 3-5x | ✓ Yes |
| base | 30-60x | 2-3x | ✓ Yes |
| small | 15-30x | 1.5-2x | ✓ Yes |
| medium | 8-15x | 0.8-1.2x | Borderline |
| large-v3 | 4-8x | 0.4-0.6x | ✗ No |

### TTS (Kokoro)
| Setup | Speed | 30s audio |
|-------|-------|-----------|
| GPU | 100x | ~0.3s |
| CPU | 10-35x | ~1-3s |

### Full Pipeline (STT + TTS)
- **With GPU**: < 2 seconds
- **CPU-only**: 5-15 seconds

---

## Pros & Cons

### Recommended Stack (faster-whisper + Kokoro)

**Pros**:
✅ 4x faster STT
✅ Production-quality TTS
✅ Fully local (no cloud)
✅ Open source
✅ Easy Python API
✅ GPU acceleration
✅ Multiple voices (54 available)
✅ VAD built-in
✅ Word-level timestamps
✅ Streaming support
✅ Low latency with GPU
✅ Commercial use allowed

**Cons**:
⚠️ Requires setup
⚠️ GPU recommended (not required)
⚠️ Initial setup time
⚠️ Model download required

---

## Alternatives Considered

### whisper.cpp + Kokoro
- Pros: C++, minimal dependencies
- Cons: Less familiar API

### OpenAI Whisper + Kokoro
- Pros: Best accuracy, easy API
- Cons: Slower, higher memory

### ElevenLabs (Cloud) + Whisper (Local)
- Pros: Best TTS quality, easy
- Cons: Not local, costs money

---

## Troubleshooting

**Issue 1**: Kokoro Docker won't start
```bash
docker ps  # Check Docker is running
docker logs kokoro-tts  # Check logs
docker compose up --build  # Rebuild
```

**Issue 2**: Model download fails
```bash
# Set cache directory
export HF_HUB_CACHE=/path/to/cache
```

**Issue 3**: Audio conversion fails
```bash
ffmpeg -version  # Check FFmpeg installed
```

**Issue 4**: Out of memory
```python
# Use smaller model
model = WhisperModel("base", device="cpu", compute_type="int8")
```

---

## Resources

**Kokoro TTS**:
- GitHub: https://github.com/remsky/Kokoro-FastAPI
- Hugging Face: https://huggingface.co/hexgrad/Kokoro-82M
- Demo: https://hf.co/spaces/hexgrad/Kokoro-TTS

**faster-whisper**:
- GitHub: https://github.com/SYSTRAN/faster-whisper
- PyPI: https://pypi.org/project/faster-whisper/

**whisper.cpp**:
- GitHub: https://github.com/ggml-org/whisper.cpp

---

## Next Steps

1. ✓ **Set up Kokoro TTS**: Docker deployment (5 min)
2. ✓ **Test TTS**: Verify audio quality (5 min)
3. ✓ **Setup faster-whisper**: Install and test (5 min)
4. ⏳ **Create OpenClaw skill**: Implement integration (1-2 hours)
5. ⏳ **Test with real messages**: End-to-end test (30 min)
6. ⏳ **Optimize**: Fine-tune parameters (1 hour)
7. ⏳ **Deploy**: Background services (30 min)

---

## Conclusion

The recommended stack (faster-whisper + Kokoro) provides:
- Best balance of performance, quality, and ease of use
- Fully local operation (no cloud dependencies)
- Production-quality results
- Open source with permissive licenses
- Easy integration with OpenClaw
- Scalable from CPU to GPU

**Total setup time**: ~2-3 hours
**Total cost**: $0 (free software)
**Latency**: < 2 seconds (GPU) or 5-15 seconds (CPU)

---

## Report Files

- **Full Report**: `stt-tts-investigation-report.md` (43KB, comprehensive details)
- **Summary**: This file

**Report prepared by**: OpenClaw subagent (investigate-stt-tts)
**Date**: February 14, 2026
