# Local Voice Skill Configuration

This file contains configuration settings for the local-voice skill.

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

**Model Sizes:**
- `tiny` (39M) - Fastest, good enough for most use cases
- `base` (74M) - Good balance of speed/accuracy (RECOMMENDED)
- `small` (244M) - Better accuracy, still fast
- `medium` (769M) - Higher accuracy for critical applications
- `large-v3` (1550M) - Best accuracy, slower
- `turbo` (809M) - Fast and accurate (6x faster than large)

**Compute Types:**
- `int8` - Best for CPU, minimal memory, slight accuracy loss
- `float16` - Best for GPU, good balance
- `float32` - Highest accuracy, more memory

## TTS Configuration

```toml
[tts]
base_url = "http://localhost:8880/v1"
default_voice = "af_bella"
default_format = "mp3"
default_speed = 1.0
streaming = false
timeout = 30
```

**Voices:**
Use `af_*` for American English voices (e.g., `af_bella`, `af_heart`, `af_sky`)

**Output Formats:**
- `mp3` - Most compatible
- `wav` - Lossless
- `opus` - Low bitrate, good for streaming/Telegram
- `flac` - Lossless compression
- `m4a` - Apple devices

## Audio Processing

```toml
[audio]
temp_dir = "/tmp/openclaw-voice"  # or None for system temp
sample_rate = 16000  # For STT
channels = 1
auto_cleanup = true
max_temp_age_hours = 24
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

## Example Python Config

```python
config = {
    # STT settings
    "stt_model_size": "base",
    "stt_device": "cpu",  # or "cuda" for GPU
    "stt_compute_type": "int8",

    # TTS settings
    "tts_base_url": "http://localhost:8880/v1",
    "tts_default_voice": "af_bella",
    "tts_default_format": "mp3",

    # Audio processing
    "audio_temp_dir": "/tmp/openclaw-voice",

    # Platform-specific
    "telegram_format": "ogg",
    "discord_format": "mp3"
}
```

## Environment Variables

You can also use environment variables:

```bash
export LOCAL_VOICE_STT_MODEL="base"
export LOCAL_VOICE_STT_DEVICE="cpu"
export LOCAL_VOICE_TTS_URL="http://localhost:8880/v1"
export LOCAL_VOICE_TTS_VOICE="af_bella"
```

## Recommended Configurations

### Minimum (CPU-only, slow)
```python
{
    "stt_model_size": "tiny",
    "stt_device": "cpu",
    "stt_compute_type": "int8"
}
```

### Balanced (CPU-only, good)
```python
{
    "stt_model_size": "base",
    "stt_device": "cpu",
    "stt_compute_type": "int8"
}
```

### Fast (GPU-accelerated)
```python
{
    "stt_model_size": "base",
    "stt_device": "cuda",
    "stt_compute_type": "float16"
}
```

### Production Quality (GPU)
```python
{
    "stt_model_size": "small",
    "stt_device": "cuda",
    "stt_compute_type": "float16"
}
```
