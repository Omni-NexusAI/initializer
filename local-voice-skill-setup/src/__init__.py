"""
Local Voice Skill - OpenClaw integration for local STT and TTS

This module provides:
- STT: faster-whisper (Speech-to-Text)
- TTS: Kokoro TTS (Text-to-Speech)
- Audio processing and format conversion
- Telegram/Discord voice message handling
"""

from .stt import LocalSTT, quick_transcribe
from .tts import LocalTTS, quick_synthesize
from .processor import AudioProcessor, quick_convert
from .integration import VoiceMessageHandler, create_handler

__version__ = "1.0.0"
__all__ = [
    "LocalSTT",
    "quick_transcribe",
    "LocalTTS",
    "quick_synthesize",
    "AudioProcessor",
    "quick_convert",
    "VoiceMessageHandler",
    "create_handler"
]
