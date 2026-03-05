#!/usr/bin/env python3
import os
import sys

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

try:
    import whisper

    print("Loading model...", flush=True)
    model = whisper.load_model("base")
    print("Model loaded!", flush=True)

    audio_path = r"C:\Users\yepyy\.openclaw\media\inbound\file_15---5c8ab86b-6d28-437c-869b-b7cdfc9a33a2.ogg"
    print(f"Transcribing: {audio_path}", flush=True)

    result = model.transcribe(audio_path)
    print("Transcription:", flush=True)
    print(result["text"], flush=True)

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
