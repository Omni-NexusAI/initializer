#!/usr/bin/env python3
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from faster_whisper import WhisperModel

print("Loading model...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Model loaded!")

audio_path = r"C:\Users\yepyy\.openclaw\media\inbound\file_15---5c8ab86b-6d28-437c-869b-b7cdfc9a33a2.ogg"
print(f"Transcribing: {audio_path}")

segments, info = model.transcribe(audio_path, beam_size=5)

print("Transcription:")
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
