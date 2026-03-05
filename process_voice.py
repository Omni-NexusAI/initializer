#!/usr/bin/env python3
"""Process a voice message through the STT -> TTS pipeline"""

import os
# Fix OpenMP library conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
import os

# Add the workspace to sys.path so we can import the src package
workspace_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(workspace_path, 'voice-messaging-skill'))

# Now import from the src package
from src.voice_handler import VoiceHandler

config_path = os.path.join(workspace_path, 'agent-voice-messaging', 'config.toml')
handler = VoiceHandler.from_config(config_path)

if len(sys.argv) < 3:
    print("Usage: python process_voice.py <input_audio> <output_audio>")
    sys.exit(1)

input_audio = sys.argv[1]
output_audio = sys.argv[2]

# Transcribe
text = handler.transcribe(input_audio)
# Synthesize response using same text (echo)
handler.synthesize(text, output_audio)
print(f"Transcription: {text}")
print(f"Output saved to: {output_audio}")
