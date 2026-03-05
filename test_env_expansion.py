#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice-messaging-skill'))
from src.voice_handler import _expand_env_vars

# Test env var expansion
cfg = {'api_key': '${OPENAI_API_KEY}', 'nested': {'key': '${OPENAI_API_KEY}'}}
print('Before:', cfg)
print('After:', _expand_env_vars(cfg))
print('API key from env:', os.environ.get('OPENAI_API_KEY', 'NOT SET')[:10] + '...')
