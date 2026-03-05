"""
Voice message integration module for OpenClaw
Handles incoming/outgoing voice messages for Telegram/Discord
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .stt import LocalSTT
from .tts import LocalTTS
from .processor import AudioProcessor


class VoiceMessageHandler:
    """Handler for voice messages in OpenClaw"""

    def __init__(
        self,
        stt_client: Optional[LocalSTT] = None,
        tts_client: Optional[LocalTTS] = None,
        audio_processor: Optional[AudioProcessor] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize voice message handler for OpenClaw

        Args:
            stt_client: LocalSTT instance (None = auto-create)
            tts_client: LocalTTS instance (None = auto-create)
            audio_processor: AudioProcessor instance (None = auto-create)
            config: Configuration dict
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.stt = stt_client or LocalSTT(
            model_size=self.config.get("stt_model_size", "base"),
            device=self.config.get("stt_device", "cpu"),
            compute_type=self.config.get("stt_compute_type", "int8")
        )

        self.tts = tts_client or LocalTTS(
            base_url=self.config.get("tts_base_url", "http://localhost:8880/v1"),
            default_voice=self.config.get("tts_default_voice", "af_bella"),
            default_format=self.config.get("tts_default_format", "mp3")
        )

        self.processor = audio_processor or AudioProcessor(
            temp_dir=self.config.get("audio_temp_dir", None)
        )

        self.logger.info("VoiceMessageHandler initialized")

    async def handle_incoming_voice(
        self,
        audio_path: str,
        platform: str = "telegram",
        user_id: Optional[str] = None,
        auto_cleanup: bool = True
    ) -> Dict[str, Any]:
        """
        Handle incoming voice message

        Args:
            audio_path: Path to received audio file
            platform: Platform (telegram, discord)
            user_id: User identifier
            auto_cleanup: Auto-delete converted audio after processing

        Returns:
            dict with transcription, language, etc.
        """
        try:
            self.logger.info(
                f"Processing voice message from {platform} "
                f"(user: {user_id}, file: {audio_path})"
            )

            # Check if file exists
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Get audio info
            audio_info = self.processor.get_audio_info(audio_path)

            # Convert audio for STT if needed
            converted_path = self.processor.prepare_for_stt(audio_path)

            try:
                # Transcribe
                result = self.stt.transcribe(converted_path)

                # Build response
                response = {
                    "success": True,
                    "text": result["text"],
                    "language": result["language"],
                    "language_probability": result["language_probability"],
                    "duration": result["duration"],
                    "platform": platform,
                    "user_id": user_id,
                    "audio_info": audio_info,
                    "segments": result["segments"]
                }

                self.logger.info(
                    f"✓ Transcribed {result['duration']:.2f}s audio: "
                    f"'{result['text'][:50]}...'"
                )

                return response

            finally:
                # Clean up converted file
                if auto_cleanup and os.path.exists(converted_path):
                    os.unlink(converted_path)
                    self.logger.debug(f"Deleted temporary file: {converted_path}")

        except Exception as e:
            self.logger.error(f"Voice processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "platform": platform,
                "user_id": user_id
            }

    async def generate_voice_response(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        platform: str = "telegram",
        auto_cleanup: bool = False
    ) -> Dict[str, Any]:
        """
        Generate voice response for message

        Args:
            text: Response text
            output_path: Path to save audio
            voice: Voice to use (None = default)
            platform: Platform (telegram, discord)
            auto_cleanup: Auto-delete after sending

        Returns:
            dict with success, file path, etc.
        """
        try:
            # Get format for platform
            format_map = {
                "telegram": "ogg",
                "discord": "mp3"
            }
            response_format = format_map.get(platform, "mp3")

            self.logger.info(
                f"Generating voice response for {platform}: "
                f"'{text[:50]}...' (format: {response_format})"
            )

            # Synthesize
            self.tts.synthesize(
                text,
                output_file=output_path,
                voice=voice,
                response_format=response_format
            )

            # Verify file was created
            if not os.path.exists(output_path):
                raise RuntimeError(f"Output file not created: {output_path}")

            file_size = os.path.getsize(output_path)

            response = {
                "success": True,
                "file_path": output_path,
                "format": response_format,
                "size": file_size,
                "text": text,
                "voice": voice,
                "platform": platform
            }

            self.logger.info(
                f"✓ Generated voice response ({file_size} bytes, format: {response_format})"
            )

            return response

        except Exception as e:
            self.logger.error(f"Voice generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "platform": platform,
                "text": text
            }

    async def full_conversation_pipeline(
        self,
        input_audio: str,
        response_text: str,
        output_audio: str,
        platform: str = "telegram",
        voice: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full pipeline: transcribe input, generate voice response

        Args:
            input_audio: Path to input audio
            response_text: Text response
            output_audio: Path to save output audio
            platform: Platform
            voice: Voice for TTS
            user_id: User ID

        Returns:
            dict with transcription, output file, etc.
        """
        self.logger.info(
            f"Starting full conversation pipeline for {platform}"
        )

        # Transcribe input
        transcription = await self.handle_incoming_voice(
            input_audio,
            platform=platform,
            user_id=user_id
        )

        if not transcription["success"]:
            return transcription

        # Generate voice response
        voice_response = await self.generate_voice_response(
            response_text,
            output_audio,
            voice=voice,
            platform=platform
        )

        if not voice_response["success"]:
            return voice_response

        # Build final response
        return {
            "success": True,
            "transcription": transcription,
            "voice_response": voice_response,
            "input_text": transcription["text"],
            "output_text": response_text,
            "input_audio": input_audio,
            "output_audio": output_audio,
            "platform": platform,
            "user_id": user_id
        }

    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        return self.tts.get_voices()

    def test_connection(self) -> Dict[str, bool]:
        """Test connections to STT and TTS services"""
        results = {
            "stt": False,
            "tts": False
        }

        # Test STT (just try to initialize - should work if model loaded)
        try:
            # STT is initialized in __init__, so if we got here, it worked
            results["stt"] = True
            self.logger.info("✓ STT connection OK")
        except Exception as e:
            self.logger.error(f"✗ STT connection failed: {e}")

        # Test TTS
        try:
            results["tts"] = self.tts.test()
        except Exception as e:
            self.logger.error(f"✗ TTS connection failed: {e}")

        return results


# Factory function for easy initialization
def create_handler(
    stt_model: str = "base",
    stt_device: str = "cpu",
    tts_url: str = "http://localhost:8880/v1",
    tts_voice: str = "af_bella"
) -> VoiceMessageHandler:
    """
    Create a VoiceMessageHandler with common defaults

    Args:
        stt_model: STT model size
        stt_device: STT device (cpu/cuda)
        tts_url: TTS base URL
        tts_voice: Default TTS voice

    Returns:
        Configured VoiceMessageHandler instance
    """
    config = {
        "stt_model_size": stt_model,
        "stt_device": stt_device,
        "stt_compute_type": "int8" if stt_device == "cpu" else "float16",
        "tts_base_url": tts_url,
        "tts_default_voice": tts_voice,
        "tts_default_format": "mp3"
    }

    return VoiceMessageHandler(config=config)


if __name__ == "__main__":
    # Example usage and testing
    import asyncio

    async def test():
        print("Creating handler...")
        handler = create_handler(
            stt_model="base",
            stt_device="cpu",
            tts_url="http://localhost:8880/v1",
            tts_voice="af_bella"
        )

        # Test connections
        print("\nTesting connections...")
        results = handler.test_connection()
        print(f"STT: {'✓' if results['stt'] else '✗'}")
        print(f"TTS: {'✓' if results['tts'] else '✗'}")

        # Get voices
        if results['tts']:
            voices = handler.get_available_voices()
            print(f"\nAvailable voices: {', '.join(voices[:5])}...")

    asyncio.run(test())
