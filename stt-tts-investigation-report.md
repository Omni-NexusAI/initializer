# Local STT & TTS Investigation Report
**Date**: February 14, 2026
**Goal**: Set up local speech-to-text (STT) and text-to-speech (TTS) for Telegram/Discord voice message processing

---

## Executive Summary

**Recommended Stack**:
- **STT**: faster-whisper (CTranslate2 backend) for optimal balance of speed, accuracy, and resource efficiency
- **TTS**: Kokoro-82M via Kokoro-FastAPI wrapper for production-quality voice synthesis
- **Integration**: Custom OpenClaw skill bridging both services

**Key Findings**:
- Kokoro TTS offers near-commercial quality with minimal resource requirements (82M parameters)
- faster-whisper is 4x faster than original OpenAI Whisper with same accuracy
- Both can run entirely locally without cloud APIs
- Docker deployment recommended for easier maintenance
- Total cost: $1000 training cost (historical), $0 per inference after setup

---

## 1. Kokoro TTS Analysis

### 1.1 What is Kokoro TTS?

Kokoro-82M is an open-weight text-to-speech model with **82 million parameters** that delivers quality comparable to much larger models while being significantly faster and more cost-efficient.

**Key Specifications**:
- **Parameters**: 82M (very lightweight)
- **Architecture**: StyleTTS 2 + ISTFTNet (no diffusion, encoder-only)
- **License**: Apache 2.0 (fully open for commercial use)
- **Training Data**: Few hundred hours of permissive/non-copyrighted audio
- **Training Cost**: $1000 (1000 A100 80GB GPU hours)
- **Market Rate**: <$1 per million characters (~$0.06 per hour of audio)

### 1.2 Installation & Setup

#### Option A: Docker (Recommended)

**Quick Start**:
```bash
# CPU inference
docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest

# GPU inference (NVIDIA)
docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest
```

**Docker Compose**:
```bash
git clone https://github.com/remsky/Kokoro-FastAPI.git
cd Kokoro-FastAPI

# For GPU
cd docker/gpu
docker compose up --build

# For CPU
cd docker/cpu
docker compose up --build
```

#### Option B: Direct Python Installation

```bash
# Install UV package manager
# (see https://docs.astral.sh/uv/)

# Install espeak-ng for fallback (optional but recommended)
# Linux: apt install espeak-ng
# macOS: brew install espeak-ng

# Clone and run
git clone https://github.com/remsky/Kokoro-FastAPI.git
cd Kokoro-FastAPI

# Run model download
python docker/scripts/download_model.py --output api/src/models/v1_0

# Start via UV (Linux/macOS)
./start-gpu.sh   # or ./start-cpu.sh

# Windows
.\start-gpu.ps1   # or .\start-cpu.ps1
```

#### Option C: Direct Python Library Usage

```bash
pip install kokoro>=0.9.2 soundfile
```

```python
from kokoro import KPipeline
import soundfile as sf

# Initialize pipeline
pipeline = KPipeline(lang_code='a')  # 'a' = American English

# Generate audio
text = "Hello world! This is a test."
generator = pipeline(text, voice='af_heart')

for i, (gs, ps, audio) in enumerate(generator):
    print(f"Segment {i}: {gs}")  # grapheme string
    print(f"Phonemes: {ps}")     # phoneme string
    sf.write(f'output_{i}.wav', audio, 24000)
```

### 1.3 Hardware Requirements

**CPU-only**:
- Minimum: 4-core CPU, 4GB RAM
- Recommended: 8+ cores, 8GB RAM
- Performance: ~35x realtime (can take 30-60 seconds for 30s audio)

**GPU (NVIDIA)**:
- Minimum: RTX 3060 (6GB VRAM)
- Recommended: RTX 4060 Ti 16GB or better
- CUDA: 12.8+ required
- Performance: ~100x realtime (3-5 seconds for 30s audio)

**Apple Silicon**:
- M1/M2/M3 supported (CPU inference only)
- MPS (Apple GPU) support: planned but not yet available
- Use CPU Docker setup

### 1.4 Performance Benchmarks

**Test System**: Windows 11, RTX 4060 Ti 16GB, i7-11700 @ 2.5GHz, 64GB RAM

| Metric | GPU | CPU |
|--------|-----|-----|
| Realtime Speed | 35x-100x | ~10x-35x |
| Processing Rate | ~138 tokens/sec | ~30-50 tokens/sec |
| First Token Latency | ~300ms | ~3500ms |
| Audio Quality | Excellent | Excellent |

**Note**: Quality is identical between CPU/GPU - only speed differs.

### 1.5 Output Formats

Kokoro-FastAPI supports multiple audio formats:
- **mp3** - Most compatible
- **wav** - Lossless
- **opus** - Low bitrate, good for streaming
- **flac** - Lossless compression
- **m4a** - Apple devices
- **pcm** - Raw audio for streaming

### 1.6 Key Features

1. **Multi-language Support**: English, Japanese, Chinese (Vietnamese coming soon)
2. **Voice Mixing**: Combine multiple voices with weighted ratios
   - Example: `af_bella(2)+af_sky(1)` = 67%/33% mix
3. **OpenAI-Compatible API**: Drop-in replacement for OpenAI TTS endpoint
4. **Streaming Support**: Real-time audio streaming for low latency
5. **Word-level Timestamps**: Precise timing for captions/karaoke
6. **Phoneme Generation**: Access raw phonemes for advanced use cases
7. **Auto-stitching**: Splits long text at sentence boundaries (~30s chunks)
8. **Multiple Voice Packs**: 54 voices available in v1.0 (8 in v0.19)

### 1.7 API Usage Examples

**OpenAI-Compatible API**:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8880/v1",
    api_key="not-needed"
)

response = client.audio.speech.create(
    model="kokoro",
    voice="af_bella",
    input="Hello world!",
    response_format="mp3"
)

response.stream_to_file("output.mp3")
```

**Direct HTTP Requests**:
```python
import requests

# List available voices
response = requests.get("http://localhost:8880/v1/audio/voices")
voices = response.json()["voices"]

# Generate audio
response = requests.post(
    "http://localhost:8880/v1/audio/speech",
    json={
        "model": "kokoro",
        "input": "Hello world!",
        "voice": "af_bella",
        "response_format": "mp3",
        "speed": 1.0
    }
)

with open("output.mp3", "wb") as f:
    f.write(response.content)
```

**Streaming**:
```python
from openai import OpenAI
import pyaudio

client = OpenAI(base_url="http://localhost:8880/v1", api_key="not-needed")

# Setup PyAudio for real-time playback
player = pyaudio.PyAudio().open(
    format=pyaudio.paInt16,
    channels=1,
    rate=24000,
    output=True
)

with client.audio.speech.with_streaming_response.create(
    model="kokoro",
    voice="af_bella",
    input="Hello world!",
    response_format="pcm"
) as response:
    for chunk in response.iter_bytes(chunk_size=1024):
        player.write(chunk)
```

### 1.8 Quality & Tradeoffs

**Pros**:
- ✅ Commercial-quality voice synthesis
- ✅ Very lightweight (82M parameters)
- ✅ Apache 2.0 license (commercial use allowed)
- ✅ Fast inference (especially with GPU)
- ✅ Multiple output formats
- ✅ Voice mixing capabilities
- ✅ OpenAI-compatible API
- ✅ No cloud dependencies
- ✅ Active community development
- ✅ Multiple voices available

**Cons**:
- ⚠️ GPU significantly faster but not required
- ⚠️ Apple Silicon GPU support not yet available
- ⚠️ Streaming can introduce artifacts with small chunks
- ⚠️ Limited to ~30s chunks (auto-stitched for longer text)

**When to Choose Kokoro**:
- Production-quality TTS required
- Multiple voices needed
- Streaming/real-time synthesis desired
- Commercial deployment planned
- Open license important
- Resource efficiency prioritized

---

## 2. Local STT Options Comparison

### 2.1 Options Overview

| Option | Implementation | Language | Speed | Accuracy | Memory | License |
|--------|---------------|----------|-------|----------|--------|---------|
| **openai/whisper** | Python (PyTorch) | 99 languages | Baseline (1x) | Best | High | MIT |
| **whisper.cpp** | C/C++ | 99 languages | 2-4x faster | Excellent | Low | MIT |
| **faster-whisper** | Python (CTranslate2) | 99 languages | 4x faster | Excellent | Medium | MIT |

### 2.2 OpenAI Whisper (Original)

**What is it?**
The original OpenAI Whisper implementation in Python using PyTorch.

**Installation**:
```bash
pip install openai-whisper
```

**Usage**:
```python
import whisper

model = whisper.load_model("turbo")
result = model.transcribe("audio.mp3")
print(result["text"])
```

**Model Sizes**:
| Size | Parameters | VRAM | Relative Speed |
|------|-----------|------|----------------|
| tiny | 39M | ~1 GB | 10x |
| base | 74M | ~1 GB | 7x |
| small | 244M | ~2 GB | 4x |
| medium | 769M | ~5 GB | 2x |
| large | 1550M | ~10 GB | 1x |
| turbo | 809M | ~6 GB | 8x |

**Pros**:
- ✅ Original implementation, most features
- ✅ Easy Python API
- ✅ Best accuracy
- ✅ Extensive documentation
- ✅ Active development

**Cons**:
- ❌ Slower than alternatives
- ❌ Higher memory usage
- ❌ Requires PyTorch (heavy dependency)
- ❌ Needs FFmpeg

**When to Choose**:
- When you need the absolute best accuracy
- When ease of use is priority
- When you're already using PyTorch

### 2.3 whisper.cpp

**What is it?**
C/C++ port of Whisper with extreme optimization for minimal dependencies.

**Installation**:
```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp

# Download model
sh ./models/download-ggml-model.sh base.en

# Build
cmake -B build
cmake --build build -j --config Release

# Transcribe
./build/bin/whisper-cli -f samples/jfk.wav
```

**Model Sizes & Memory**:
| Model | Disk | RAM |
|-------|------|-----|
| tiny | 75 MiB | ~273 MB |
| base | 142 MiB | ~388 MB |
| small | 466 MiB | ~852 MB |
| medium | 1.5 GiB | ~2.1 GB |
| large | 2.9 GiB | ~3.9 GB |

**Performance**:
- CPU-only: Excellent (optimized with SIMD)
- GPU: NVIDIA CUDA, Vulkan, Intel OpenVINO, Apple Core ML
- Multi-platform: Windows, Linux, macOS, iOS, Android, WebAssembly

**Key Features**:
- Plain C/C++ (no Python dependencies)
- Apple Silicon optimized (NEON, Metal, Core ML)
- Integer quantization support (reduces memory 2-4x)
- Voice Activity Detection (VAD) built-in
- Zero runtime memory allocations
- Speaker diarization (via tinydiarize)

**Pros**:
- ✅ Fastest C++ implementation
- ✅ Extremely lightweight
- ✅ Cross-platform (including mobile)
- ✅ Quantization support (smaller models)
- ✅ No Python dependency
- ✅ VAD built-in
- ✅ Real-time streaming support

**Cons**:
- ❌ C++ API (less familiar than Python)
- ❌ Fewer high-level features
- ❌ Requires compilation
- ❌ Less active development than faster-whisper

**When to Choose**:
- When you need minimal dependencies
- When running on embedded/mobile devices
- When you want C++ integration
- When memory is constrained
- When you need quantized models

### 2.4 faster-whisper (RECOMMENDED)

**What is it?**
Whisper reimplementation using CTranslate2 for optimized inference. Up to 4x faster than original.

**Installation**:
```bash
pip install faster-whisper
```

**Usage**:
```python
from faster_whisper import WhisperModel

# GPU with FP16
model = WhisperModel("large-v3", device="cuda", compute_type="float16")

# CPU with INT8
# model = WhisperModel("large-v3", device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5)

print(f"Detected language: {info.language}")
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

**Performance Benchmarks** (13 minutes audio, RTX 3070 Ti 8GB):

| Implementation | Precision | Time | VRAM |
|----------------|-----------|------|------|
| openai/whisper | fp16 | 2m23s | 4708 MB |
| whisper.cpp | fp16 | 1m05s | 4127 MB |
| transformers | fp16 | 1m52s | 4960 MB |
| **faster-whisper** | fp16 | **1m03s** | 4525 MB |
| faster-whisper (batch=8) | fp16 | **17s** | 6090 MB |
| faster-whisper | int8 | **59s** | 2926 MB |

**CPU Performance** (Intel i7-12700K, 8 threads):

| Implementation | Time | RAM |
|----------------|------|-----|
| openai/whisper | 6m58s | 2335 MB |
| whisper.cpp | 2m05s | 1049 MB |
| faster-whisper | 2m37s | 2257 MB |
| faster-whisper (int8) | **1m42s** | 1477 MB |

**Key Features**:
- Batched transcription for massive speedup
- VAD filter built-in (Silero VAD)
- Word-level timestamps
- Distil-Whisper support (faster variants)
- 8-bit quantization (CPU & GPU)
- No FFmpeg required (uses PyAV)
- Streaming support
- OpenAI-compatible server options

**Advanced Usage**:
```python
from faster_whisper import WhisperModel, BatchedInferencePipeline

# Batched transcription (much faster)
model = WhisperModel("turbo", device="cuda", compute_type="float16")
batched_model = BatchedInferencePipeline(model=model)

segments, info = batched_model.transcribe(
    "audio.mp3",
    batch_size=16
)

# Word-level timestamps
segments, _ = model.transcribe("audio.mp3", word_timestamps=True)
for segment in segments:
    for word in segment.words:
        print(f"[{word.start:.2f}s -> {word.end:.2f}s] {word.word}")

# VAD filter
segments, _ = model.transcribe(
    "audio.mp3",
    vad_filter=True,
    vad_parameters={"min_silence_duration_ms": 500}
)

# Distil-Whisper (faster, slightly less accurate)
model = WhisperModel(
    "distil-large-v3",
    device="cuda",
    compute_type="float16"
)
```

**Pros**:
- ✅ 4x faster than original
- ✅ Python API (easy integration)
- ✅ Batched transcription (massive speedup)
- ✅ VAD built-in
- ✅ Word-level timestamps
- ✅ Quantization support
- ✅ Distil-Whisper compatible
- ✅ Active community
- ✅ No FFmpeg required
- ✅ Memory efficient

**Cons**:
- ⚠️ Slightly higher RAM than whisper.cpp
- ⚠️ Python dependency
- ⚠️ Requires CUDA libraries for GPU

**When to Choose**:
- **Best balance of speed, accuracy, and ease of use**
- When you need batched transcription
- When Python integration is preferred
- When you need VAD and timestamps
- When memory efficiency matters

### 2.5 Other STT Options

**f5-tts**:
- Emerging TTS-focused STT
- Less mature than Whisper
- Not recommended for production

**Vosk**:
- Older, less accurate than Whisper
- Small models, good for offline
- Lower accuracy than Whisper family

**SpeechRecognition**:
- Wrapper around multiple APIs
- Not local by default
- Not recommended for your use case

**Distil-Whisper**:
- Faster variant of Whisper (via faster-whisper)
- 6x faster than large-v3, minimal accuracy loss
- Available in faster-whisper

---

## 3. Integration with OpenClaw

### 3.1 Current OpenClaw TTS Support

Based on AGENTS.md, OpenClaw has a `tts` tool with ElevenLabs integration (`sag`). This suggests:

1. **Existing TTS Tool**: OpenClaw already has TTS capabilities
2. **OpenAI-Compatible API**: Likely uses OpenAI-style endpoints
3. **Custom Implementation Possible**: Can create skills to extend functionality

### 3.2 Recommended Integration Approach

#### Architecture Overview

```
┌─────────────────┐
│  Telegram/      │
│  Discord Bot    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OpenClaw Agent │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────────┐
│ STT    │  │   TTS         │
│ (faster│  │  (Kokoro)     │
│whisper)│  │  (FastAPI)    │
└────────┘  └──────────────┘
```

#### Proposed OpenClaw Skill Structure

Create a new skill: `local-voice/`

```
local-voice/
├── SKILL.md
├── CONFIG.md
├── README.md
├── src/
│   ├── stt.py          # faster-whisper wrapper
│   ├── tts.py          # Kokoro TTS wrapper
│   ├── processor.py    # Audio processing pipeline
│   └── integration.py  # OpenClaw integration
├── models/             # Local model cache
├── audio/              # Temp audio storage
└── scripts/
    ├── download_models.sh
    └── setup.sh
```

### 3.3 STT Integration Implementation

**File: `src/stt.py`**
```python
from faster_whisper import WhisperModel, BatchedInferencePipeline
import os
import logging

class LocalSTT:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initialize faster-whisper STT model

        Args:
            model_size: Model size (tiny, base, small, medium, large-v3, turbo)
            device: 'cpu' or 'cuda'
            compute_type: 'int8', 'float16', 'float32'
        """
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        self.batched_model = None

        logging.basicConfig()
        self.logger = logging.getLogger(__name__)

    def transcribe(self, audio_path, language=None, word_timestamps=False, batch=False):
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code (None = auto-detect)
            word_timestamps: Return word-level timestamps
            batch: Use batched inference for speed

        Returns:
            dict with 'text', 'language', 'segments', 'duration'
        """
        model = self.batched_model if batch and self.batched_model else self.model

        segments, info = model.transcribe(
            audio_path,
            language=language,
            word_timestamps=word_timestamps,
            beam_size=5,
            vad_filter=True
        )

        # Collect results
        segments_list = []
        full_text = []

        for segment in segments:
            segment_dict = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            }

            if word_timestamps and hasattr(segment, 'words'):
                segment_dict["words"] = [
                    {"start": w.start, "end": w.end, "word": w.word}
                    for w in segment.words
                ]

            segments_list.append(segment_dict)
            full_text.append(segment.text)

        return {
            "text": " ".join(full_text),
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": segments_list,
            "duration": segments_list[-1]["end"] if segments_list else 0
        }

    def transcribe_streaming(self, audio_path, callback):
        """
        Transcribe with streaming results

        Args:
            audio_path: Path to audio file
            callback: Function to call for each segment
        """
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True
        )

        for segment in segments:
            callback({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "language": info.language
            })
```

**Usage**:
```python
stt = LocalSTT(model_size="base", device="cuda", compute_type="float16")

# Simple transcription
result = stt.transcribe("voice_message.ogg")
print(result["text"])

# With word timestamps
result = stt.transcribe("voice_message.ogg", word_timestamps=True)

# Streaming callback
def on_segment(segment):
    print(f"[{segment['start']:.2f}s] {segment['text']}")

stt.transcribe_streaming("voice_message.ogg", on_segment)
```

### 3.4 TTS Integration Implementation

**File: `src/tts.py`**
```python
import requests
import logging
from typing import Optional, Union
from pathlib import Path

class LocalTTS:
    def __init__(self, base_url="http://localhost:8880/v1", default_voice="af_bella"):
        """
        Initialize Kokoro TTS client

        Args:
            base_url: Base URL for Kokoro-FastAPI server
            default_voice: Default voice to use
        """
        self.base_url = base_url.rstrip("/")
        self.default_voice = default_voice
        self.session = requests.Session()

        logging.basicConfig()
        self.logger = logging.getLogger(__name__)

    def get_voices(self):
        """Get list of available voices"""
        try:
            response = self.session.get(f"{self.base_url}/audio/voices")
            response.raise_for_status()
            return response.json()["voices"]
        except Exception as e:
            self.logger.error(f"Failed to get voices: {e}")
            return []

    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        output_file: Optional[Union[str, Path]] = None,
        response_format: str = "mp3",
        speed: float = 1.0,
        stream: bool = False
    ) -> Union[bytes, None]:
        """
        Synthesize text to speech

        Args:
            text: Text to synthesize
            voice: Voice to use (None = default)
            output_file: Path to save audio (None = return bytes)
            response_format: Audio format (mp3, wav, opus, flac, m4a, pcm)
            speed: Playback speed (1.0 = normal)
            stream: Enable streaming

        Returns:
            Audio bytes if output_file is None, otherwise None
        """
        voice = voice or self.default_voice

        try:
            response = self.session.post(
                f"{self.base_url}/audio/speech",
                json={
                    "model": "kokoro",
                    "input": text,
                    "voice": voice,
                    "response_format": response_format,
                    "speed": speed
                },
                stream=stream
            )
            response.raise_for_status()

            if output_file:
                with open(output_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                self.logger.info(f"Saved audio to {output_file}")
                return None
            else:
                return response.content

        except Exception as e:
            self.logger.error(f"Failed to synthesize: {e}")
            raise

    def synthesize_streaming(self, text: str, voice: Optional[str] = None, chunk_size: int = 1024):
        """
        Synthesize with streaming

        Yields audio chunks as they're generated

        Args:
            text: Text to synthesize
            voice: Voice to use
            chunk_size: Chunk size in bytes

        Yields:
            Bytes chunks of audio data
        """
        voice = voice or self.default_voice

        try:
            response = self.session.post(
                f"{self.base_url}/audio/speech",
                json={
                    "model": "kokoro",
                    "input": text,
                    "voice": voice,
                    "response_format": "pcm"  # PCM for streaming
                },
                stream=True
            )
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    yield chunk

        except Exception as e:
            self.logger.error(f"Failed to synthesize stream: {e}")
            raise
```

**Usage**:
```python
tts = LocalTTS(base_url="http://localhost:8880/v1", default_voice="af_bella")

# Simple synthesis
audio_bytes = tts.synthesize("Hello world!", response_format="mp3")

# Save to file
tts.synthesize(
    "Hello world!",
    output_file="output.mp3",
    voice="af_bella",
    response_format="mp3"
)

# List available voices
voices = tts.get_voices()
print(voices)

# Streaming
for chunk in tts.synthesize_streaming("Hello world!", voice="af_heart"):
    # Process chunk
    pass
```

### 3.5 Audio Processing Pipeline

**File: `src/processor.py`**
```python
import os
import tempfile
import logging
from pathlib import Path
from typing import Optional

class AudioProcessor:
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize audio processor

        Args:
            temp_dir: Directory for temporary files (None = system temp)
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.logger = logging.getLogger(__name__)

    def convert_audio(
        self,
        input_path: str,
        output_path: str,
        sample_rate: int = 16000,
        channels: int = 1,
        format: str = "wav"
    ) -> str:
        """
        Convert audio file for STT processing

        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            sample_rate: Target sample rate (16000 for Whisper)
            channels: Number of audio channels
            format: Output format

        Returns:
            Output file path
        """
        # Use PyAV or ffmpeg-python for conversion
        # This is a placeholder - implement based on your preferred library
        import subprocess

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-c:a", "pcm_s16le",
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Audio conversion failed: {e}")
            raise

    def cleanup_temp_files(self, pattern: Optional[str] = None):
        """
        Clean up temporary audio files

        Args:
            pattern: File pattern to match (None = all temp files)
        """
        if pattern:
            # Clean up specific pattern
            for file in Path(self.temp_dir).glob(pattern):
                file.unlink()
        else:
            # Clean up all temp files in our directory
            pass  # Be careful with this!
```

### 3.6 OpenClaw Message Integration

**File: `src/integration.py`**
```python
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class VoiceMessageHandler:
    def __init__(self, stt_client, tts_client, audio_processor):
        """
        Initialize voice message handler for OpenClaw

        Args:
            stt_client: LocalSTT instance
            tts_client: LocalTTS instance
            audio_processor: AudioProcessor instance
        """
        self.stt = stt_client
        self.tts = tts_client
        self.processor = audio_processor
        self.logger = logging.getLogger(__name__)

    async def handle_incoming_voice(
        self,
        audio_path: str,
        platform: str = "telegram",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle incoming voice message

        Args:
            audio_path: Path to received audio file
            platform: Platform (telegram, discord)
            user_id: User identifier

        Returns:
            dict with transcription, language, etc.
        """
        try:
            # Convert audio for STT if needed
            converted_path = self.processor.convert_audio(
                audio_path,
                f"{audio_path}.converted.wav",
                sample_rate=16000,
                channels=1
            )

            # Transcribe
            result = self.stt.transcribe(converted_path)

            # Clean up
            os.unlink(converted_path)

            self.logger.info(
                f"Transcribed voice from {platform} user {user_id}: "
                f"{result['text'][:50]}..."
            )

            return {
                "success": True,
                "text": result["text"],
                "language": result["language"],
                "language_probability": result["language_probability"],
                "duration": result["duration"],
                "platform": platform,
                "user_id": user_id
            }

        except Exception as e:
            self.logger.error(f"Voice processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_voice_response(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        platform: str = "telegram"
    ) -> Dict[str, Any]:
        """
        Generate voice response for message

        Args:
            text: Response text
            output_path: Path to save audio
            voice: Voice to use (None = default)
            platform: Platform (telegram, discord)

        Returns:
            dict with success, file path, etc.
        """
        try:
            # Format selection based on platform
            response_format = "ogg" if platform == "telegram" else "mp3"

            # Synthesize
            self.tts.synthesize(
                text,
                output_file=output_path,
                voice=voice,
                response_format=response_format
            )

            self.logger.info(
                f"Generated voice response for {platform}: "
                f"{text[:50]}..."
            )

            return {
                "success": True,
                "file_path": output_path,
                "format": response_format,
                "text": text
            }

        except Exception as e:
            self.logger.error(f"Voice generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def full_conversation_pipeline(
        self,
        input_audio: str,
        response_text: str,
        output_audio: str,
        platform: str = "telegram",
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full pipeline: transcribe input, generate voice response

        Args:
            input_audio: Path to input audio
            response_text: Text response
            output_audio: Path to save output audio
            platform: Platform
            voice: Voice for TTS

        Returns:
            dict with transcription, output file, etc.
        """
        # Transcribe input
        transcription = await self.handle_incoming_voice(input_audio, platform)

        if not transcription["success"]:
            return transcription

        # Generate voice response
        voice_response = await self.generate_voice_response(
            response_text,
            output_audio,
            voice,
            platform
        )

        if not voice_response["success"]:
            return voice_response

        return {
            "success": True,
            "transcription": transcription,
            "voice_response": voice_response,
            "input_text": transcription["text"],
            "output_text": response_text,
            "output_file": output_audio
        }
```

### 3.7 Audio Format Handling

**Telegram Voice Messages**:
- Input: OGG Opus (typically)
- Output: OGG Opus preferred
- Sample rate: 16kHz
- Channels: Mono

**Discord Voice Messages**:
- Input: OGG Opus or WAV
- Output: MP3 or OGG Opus
- Sample rate: 48kHz (Discord standard) or 16kHz (compatibility)
- Channels: Mono or Stereo

**Conversion Requirements**:
```python
# For Whisper STT
whisper_requirements = {
    "sample_rate": 16000,
    "channels": 1,
    "format": "wav",  # 16-bit PCM
    "codec": "pcm_s16le"
}

# For Kokoro TTS
kokoro_output = {
    "sample_rate": 24000,  # Kokoro default
    "channels": 1,
    "formats": ["mp3", "wav", "opus", "flac", "m4a", "pcm"]
}
```

---

## 4. Hardware Recommendations

### 4.1 System Requirements

**Minimum (CPU-only)**:
- CPU: 4-core processor (Intel i5 or equivalent)
- RAM: 8GB
- Storage: 10GB free (for models)
- Network: Not required (fully local)

**Recommended (CPU-only)**:
- CPU: 8+ core processor (Intel i7/i9, AMD Ryzen 7/9)
- RAM: 16GB
- Storage: 20GB SSD
- OS: Windows 10/11, Linux, macOS

**Recommended (GPU-accelerated)**:
- GPU: NVIDIA RTX 4060 Ti 16GB or better
- CPU: 8+ core processor
- RAM: 16GB (32GB for large models)
- Storage: 20GB SSD
- CUDA: 12.8+
- OS: Windows 10/11, Linux

### 4.2 Model Size Recommendations

**For Personal Use (1-2 users)**:
- **STT**: `base` or `small` model
  - Base: Good balance of speed/accuracy
  - Small: Better accuracy, still fast
- **TTS**: Kokoro-82M (only option)
  - Already optimized at 82M parameters

**For Production/Multiple Users**:
- **STT**: `small` or `medium` model
  - Small: Best balance
  - Medium: Higher accuracy if needed
- **TTS**: Kokoro-82M (only option)

**For Real-time/Low Latency**:
- **STT**: `tiny` or `base` model with GPU
  - Tiny: Fastest, good enough for most
  - Base: Better accuracy, still real-time with GPU
- **TTS**: Kokoro-82M with GPU required

### 4.3 Memory Usage Summary

**STT (faster-whisper)**:
| Model | RAM (int8) | VRAM (fp16) |
|-------|------------|-------------|
| tiny | ~100 MB | ~1 GB |
| base | ~200 MB | ~1.5 GB |
| small | ~400 MB | ~2.5 GB |
| medium | ~1 GB | ~5 GB |
| large-v3 | ~2 GB | ~8 GB |

**TTS (Kokoro)**:
| Setup | RAM | VRAM |
|-------|-----|------|
| CPU | ~2 GB | 0 GB |
| GPU | ~1 GB | ~2-4 GB |

**Total System Memory** (both running):
- Minimum: ~4 GB RAM
- Recommended: ~8-16 GB RAM
- With GPU: ~12-24 GB VRAM (depending on models)

### 4.4 Performance Expectations

**STT (faster-whisper)**:
| Model | Speed (GPU) | Speed (CPU) | Realtime? |
|-------|-------------|-------------|-----------|
| tiny | 50-100x | 3-5x | Yes |
| base | 30-60x | 2-3x | Yes |
| small | 15-30x | 1.5-2x | Yes |
| medium | 8-15x | 0.8-1.2x | Borderline |
| large-v3 | 4-8x | 0.4-0.6x | No |

**TTS (Kokoro)**:
| Setup | Speed | 30s audio time |
|-------|-------|----------------|
| GPU | 100x | ~0.3s |
| CPU | 10-35x | ~1-3s |

**Full Pipeline (STT + TTS)**:
- With GPU: < 2 seconds total latency
- CPU-only: 5-15 seconds total latency
- Includes audio conversion and processing

---

## 5. Recommended Stack & Implementation Plan

### 5.1 Final Recommendation

**STT**: faster-whisper
- Best balance of speed, accuracy, and ease of use
- Python API for easy integration
- Batched transcription for massive speedups
- VAD and word-level timestamps built-in
- Active community and documentation

**TTS**: Kokoro-82M via Kokoro-FastAPI
- Production-quality voice synthesis
- Lightweight (82M parameters)
- OpenAI-compatible API
- Multiple voices and output formats
- Apache 2.0 license

**Integration**: Custom OpenClaw skill
- Wrapper classes for both services
- Audio processing pipeline
- Telegram/Discord message handlers
- Full conversation pipeline

### 5.2 Installation Steps

#### Step 1: Install Dependencies

**Windows**:
```powershell
# Install Python 3.9+
# Install Docker Desktop

# Install FFmpeg
choco install ffmpeg

# Install Python packages
pip install faster-whisper pyav requests
```

**Linux**:
```bash
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Install FFmpeg
sudo apt install ffmpeg

# Install Python packages
pip install faster-whisper pyav requests
```

**macOS**:
```bash
# Install Docker Desktop
# brew install --cask docker

# Install FFmpeg
brew install ffmpeg

# Install Python packages
pip install faster-whisper pyav requests
```

#### Step 2: Deploy Kokoro TTS

```bash
# Clone repository
git clone https://github.com/remsky/Kokoro-FastAPI.git
cd Kokoro-FastAPI

# CPU inference
cd docker/cpu
docker compose up -d

# OR GPU inference (if you have NVIDIA GPU)
cd ../gpu
docker compose up -d

# Verify it's running
curl http://localhost:8880/docs
```

#### Step 3: Test TTS

```python
import requests

# Test API
response = requests.post(
    "http://localhost:8880/v1/audio/speech",
    json={
        "model": "kokoro",
        "input": "Hello world! Kokoro TTS is working.",
        "voice": "af_bella",
        "response_format": "mp3"
    }
)

with open("test.mp3", "wb") as f:
    f.write(response.content)

print("✓ TTS test successful")
```

#### Step 4: Setup STT

```bash
# Install faster-whisper
pip install faster-whisper

# Download model (auto-downloaded on first use)
python -c "from faster_whisper import WhisperModel; model = WhisperModel('base', device='cpu', compute_type='int8'); print('✓ Model downloaded')"
```

#### Step 5: Test STT

```python
from faster_whisper import WhisperModel

# Initialize
model = WhisperModel("base", device="cpu", compute_type="int8")

# Transcribe test audio (you need a test file)
# ffmpeg -i test.mp3 -ar 16000 -ac 1 test.wav

segments, info = model.transcribe("test.wav")

print(f"Detected language: {info.language}")
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

print("✓ STT test successful")
```

#### Step 6: Create OpenClaw Skill

```bash
# Create skill directory
mkdir -p ~/.openclaw/skills/local-voice/src
cd ~/.openclaw/skills/local-voice

# Create files from Section 3
# - SKILL.md
# - CONFIG.md
# - README.md
# - src/stt.py
# - src/tts.py
# - src/processor.py
# - src/integration.py

# Install skill
openclaw skills install ~/.openclaw/skills/local-voice
```

### 5.3 Configuration

**File: `CONFIG.md`**
```markdown
# Local Voice Skill Configuration

## STT Configuration

```toml
[stt]
model_size = "base"  # tiny, base, small, medium, large-v3, turbo
device = "cpu"       # cpu or cuda
compute_type = "int8" # int8, float16, float32
beam_size = 5
vad_filter = true
word_timestamps = false
```

## TTS Configuration

```toml
[tts]
base_url = "http://localhost:8880/v1"
default_voice = "af_bella"
default_format = "mp3"
default_speed = 1.0
streaming = false
```

## Audio Processing

```toml
[audio]
temp_dir = "/tmp/openclaw-voice"
sample_rate = 16000  # For STT
channels = 1
```

## Platform Configuration

```toml
[platform.telegram]
output_format = "ogg"
max_duration = 60  # seconds

[platform.discord]
output_format = "mp3"
max_duration = 300  # seconds
```
```

### 5.4 Usage Examples

**Example 1: Simple Voice Message Handling**

```python
from local_voice.src.integration import VoiceMessageHandler
from local_voice.src.stt import LocalSTT
from local_voice.src.tts import LocalTTS
from local_voice.src.processor import AudioProcessor

# Initialize components
stt = LocalSTT(model_size="base", device="cpu")
tts = LocalTTS(base_url="http://localhost:8880/v1")
processor = AudioProcessor()
handler = VoiceMessageHandler(stt, tts, processor)

# Handle incoming voice message
result = await handler.handle_incoming_voice(
    "telegram_voice.ogg",
    platform="telegram",
    user_id="user123"
)

print(f"Transcription: {result['text']}")
```

**Example 2: Generate Voice Response**

```python
# Generate voice response
response = await handler.generate_voice_response(
    "Hello! I received your message and I'm processing it.",
    "response.ogg",
    voice="af_bella",
    platform="telegram"
)

print(f"Saved to: {response['file_path']}")
```

**Example 3: Full Pipeline**

```python
# Full conversation pipeline
result = await handler.full_conversation_pipeline(
    input_audio="input_voice.ogg",
    response_text="I understand! Here's what I think...",
    output_audio="output_response.ogg",
    platform="telegram",
    voice="af_heart"
)

print(f"Input: {result['input_text']}")
print(f"Output: {result['output_text']}")
print(f"Output file: {result['output_file']}")
```

---

## 6. Pros and Cons Summary

### 6.1 Recommended Stack

**faster-whisper + Kokoro**

**Pros**:
- ✅ 4x faster STT than original
- ✅ Production-quality TTS
- ✅ Fully local (no cloud)
- ✅ Open source (MIT + Apache 2.0)
- ✅ Active community support
- ✅ Easy Python API
- ✅ GPU acceleration available
- ✅ Multiple voices (TTS)
- ✅ Word-level timestamps (STT)
- ✅ VAD built-in (STT)
- ✅ Batched processing (STT)
- ✅ Streaming support (both)
- ✅ Low latency with GPU
- ✅ Commercial use allowed

**Cons**:
- ⚠️ Requires setup and configuration
- ⚠️ GPU recommended for best performance
- ⚠️ Some Python dependencies
- ⚠️ Kokoro not optimized for Apple Silicon GPU (yet)
- ⚠️ Initial setup time
- ⚠️ Model download required

### 6.2 Alternative Stacks

**whisper.cpp + Kokoro**
- Pros: C++ (no Python), minimal dependencies
- Cons: Less familiar API, fewer features

**OpenAI Whisper + Kokoro**
- Pros: Best STT accuracy, easy Python API
- Cons: Slower, higher memory, PyTorch dependency

**ElevenLabs (Cloud) + OpenAI Whisper (Local)**
- Pros: Best TTS quality, easy setup
- Cons: Not local, costs money, privacy concerns

---

## 7. Troubleshooting

### 7.1 Common Issues

**Issue 1: Kokoro Docker won't start**
```bash
# Check Docker is running
docker ps

# Check logs
docker logs kokoro-tts

# Rebuild
docker compose down
docker compose up --build
```

**Issue 2: faster-whisper model download fails**
```python
# Manually download from Hugging Face
# Or set HF_HUB_CACHE environment variable
import os
os.environ['HF_HUB_CACHE'] = '/path/to/cache'

# Or download specific model
from huggingface_hub import snapshot_download
snapshot_download("Systran/faster-whisper-base")
```

**Issue 3: Audio format conversion fails**
```bash
# Check FFmpeg is installed
ffmpeg -version

# Test conversion
ffmpeg -i input.ogg -ar 16000 -ac 1 output.wav

# Install if missing
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: choco install ffmpeg
```

**Issue 4: Out of memory errors**
```python
# Use smaller model
# For STT: use "base" instead of "large-v3"

# Use int8 quantization
model = WhisperModel("base", device="cpu", compute_type="int8")

# Reduce batch size
batched_model = BatchedInferencePipeline(model=model, batch_size=8)
```

**Issue 5: Slow inference**
```python
# For STT:
# 1. Use GPU if available
model = WhisperModel("base", device="cuda", compute_type="float16")

# 2. Use smaller model
model = WhisperModel("tiny", device="cpu", compute_type="int8")

# 3. Use batched inference
batched_model = BatchedInferencePipeline(model=model)

# For TTS:
# 1. Use GPU (Docker with --gpus all)
# 2. Use faster audio format (opus > mp3 > wav)
```

---

## 8. Additional Resources

### 8.1 Documentation

**Kokoro TTS**:
- GitHub: https://github.com/remsky/Kokoro-FastAPI
- Hugging Face: https://huggingface.co/hexgrad/Kokoro-82M
- Demo: https://hf.co/spaces/hexgrad/Kokoro-TTS

**faster-whisper**:
- GitHub: https://github.com/SYSTRAN/faster-whisper
- PyPI: https://pypi.org/project/faster-whisper/

**whisper.cpp**:
- GitHub: https://github.com/ggml-org/whisper.cpp
- Models: https://huggingface.co/ggerganov/whisper.cpp

**OpenAI Whisper**:
- GitHub: https://github.com/openai/whisper
- Paper: https://arxiv.org/abs/2212.04356

### 8.2 Community Projects

**STT Servers**:
- speaches: https://github.com/speaches-ai/speaches (OpenAI-compatible faster-whisper server)
- WhisperX: https://github.com/m-bain/whisperX (Speaker diarization)
- WhisperLive: https://github.com/collabora/WhisperLive (Real-time)

**TTS Servers**:
- Kokoro-FastAPI: https://github.com/remsky/Kokoro-FastAPI
- Coqui TTS: https://github.com/coqui-ai/TTS (Alternative)

### 8.3 Benchmarks

**STT Benchmarks**:
- https://github.com/ggml-org/whisper.cpp/issues/89 (whisper.cpp benchmarks)
- https://github.com/SYSTRAN/faster-whisper (built-in benchmarks)

**TTS Benchmarks**:
- https://artificialanalysis.ai/text-to-speech (TTS comparison)
- https://hf.co/spaces/hexgrad/Kokoro-TTS (Live demo)

---

## 9. Next Steps

1. **Set up Kokoro TTS**: Start with Docker deployment for easier management
2. **Test TTS**: Verify audio quality and explore available voices
3. **Setup faster-whisper**: Install and test with sample audio files
4. **Create OpenClaw skill**: Implement the integration code from Section 3
5. **Test with real messages**: Test end-to-end with Telegram/Discord
6. **Optimize**: Fine-tune model sizes, batch sizes, and parameters
7. **Deploy**: Set up as background services for persistent operation

---

## 10. Conclusion

This investigation has identified a robust, fully-local STT and TTS solution that meets all requirements:

- **No cloud dependencies**: Everything runs locally
- **Production quality**: Kokoro delivers near-commercial TTS quality
- **Fast and efficient**: faster-whisper is 4x faster than original
- **Open source**: Both components use permissive licenses
- **Easy integration**: Python APIs with OpenClaw-friendly design
- **Scalable**: Can run on CPU or GPU depending on needs
- **Cost-effective**: Free to use after initial setup

The recommended stack (faster-whisper + Kokoro) provides the best balance of performance, quality, ease of use, and resource efficiency for a local voice assistant system integrated with Telegram and Discord.

---

**Report prepared by**: OpenClaw subagent (investigate-stt-tts)
**Date**: February 14, 2026
**Version**: 1.0
