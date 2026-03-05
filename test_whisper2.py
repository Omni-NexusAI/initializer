#!/usr/bin/env python3
import os
import sys
import traceback

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

try:
    from faster_whisper import WhisperModel

    print("Loading model...", flush=True)
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("Model loaded!", flush=True)

    audio_path = r"C:\Users\yepyy\.openclaw\media\inbound\file_15---5c8ab86b-6d28-437c-869b-b7cdfc9a33a2.ogg"
    print(f"Transcribing: {audio_path}", flush=True)

    segments, info = model.transcribe(audio_path, beam_size=5)

    print("Transcription:", flush=True)
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text), flush=True)

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
