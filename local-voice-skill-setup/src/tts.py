"""
TTS (Text-to-Speech) module using Kokoro TTS
"""

import requests
import logging
from typing import Optional, Union, Generator, List
from pathlib import Path


class LocalTTS:
    """Local TTS using Kokoro TTS via FastAPI"""

    def __init__(
        self,
        base_url: str = "http://localhost:8880/v1",
        default_voice: str = "af_bella",
        default_format: str = "mp3",
        timeout: int = 30
    ):
        """
        Initialize Kokoro TTS client

        Args:
            base_url: Base URL for Kokoro-FastAPI server
            default_voice: Default voice to use
            default_format: Default audio format (mp3, wav, opus, flac, m4a, pcm)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.default_voice = default_voice
        self.default_format = default_format
        self.timeout = timeout
        self.session = requests.Session()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Test connection
        try:
            self.get_voices()
            self.logger.info(
                f"Connected to Kokoro TTS at {base_url} "
                f"(default voice: {default_voice})"
            )
        except Exception as e:
            self.logger.warning(f"Could not connect to Kokoro TTS: {e}")

    def get_voices(self) -> List[str]:
        """Get list of available voices"""
        try:
            response = self.session.get(
                f"{self.base_url}/audio/voices",
                timeout=self.timeout
            )
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
        response_format: Optional[str] = None,
        speed: float = 1.0,
        stream: bool = False
    ) -> Optional[bytes]:
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
        response_format = response_format or self.default_format

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
                stream=stream,
                timeout=self.timeout
            )
            response.raise_for_status()

            if output_file:
                with open(output_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                self.logger.info(
                    f"Saved audio to {output_file} "
                    f"({len(text)} chars, voice: {voice})"
                )
                return None
            else:
                return response.content

        except Exception as e:
            self.logger.error(f"Failed to synthesize: {e}")
            raise

    def synthesize_streaming(
        self,
        text: str,
        voice: Optional[str] = None,
        chunk_size: int = 1024
    ) -> Generator[bytes, None, None]:
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
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    yield chunk

        except Exception as e:
            self.logger.error(f"Failed to synthesize stream: {e}")
            raise

    def test(self) -> bool:
        """Test if TTS service is working"""
        try:
            test_text = "Hello, this is a test."
            audio = self.synthesize(test_text)
            success = audio is not None and len(audio) > 0

            if success:
                self.logger.info(f"TTS test passed ({len(audio)} bytes)")
            else:
                self.logger.warning("TTS test failed")

            return success

        except Exception as e:
            self.logger.error(f"TTS test failed: {e}")
            return False


def quick_synthesize(
    text: str,
    output_file: str,
    voice: str = "af_bella",
    format: str = "mp3",
    base_url: str = "http://localhost:8880/v1"
) -> str:
    """
    Quick synthesis function

    Args:
        text: Text to synthesize
        output_file: Path to save audio
        voice: Voice to use
        format: Audio format
        base_url: Kokoro TTS base URL

    Returns:
        Path to output file
    """
    tts = LocalTTS(base_url=base_url, default_voice=voice)
    tts.synthesize(text, output_file=output_file, response_format=format)
    return output_file


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python tts.py <text> <output_file> [voice]")
        sys.exit(1)

    text = sys.argv[1]
    output = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "af_bella"

    # Test TTS
    tts = LocalTTS()
    if tts.test():
        # Synthesize
        tts.synthesize(text, output_file=output, voice=voice)
        print(f"\n✓ Synthesized to {output}")
        print(f"✓ Available voices: {', '.join(tts.get_voices()[:5])}...")
    else:
        print("\n✗ TTS test failed - check Kokoro TTS is running")
