"""
Audio processor module for format conversion and audio handling
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple


class AudioProcessor:
    """Audio format converter and processor"""

    def __init__(self, temp_dir: Optional[str] = None, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize audio processor

        Args:
            temp_dir: Directory for temporary files (None = system temp)
            ffmpeg_path: Path to ffmpeg executable
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.ffmpeg_path = ffmpeg_path

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Verify ffmpeg is available
        self._check_ffmpeg()

    def _check_ffmpeg(self) -> None:
        """Check if ffmpeg is installed"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                self.logger.info(f"Found FFmpeg: {version}")
            else:
                raise RuntimeError("FFmpeg not found")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not installed. Install with: apt/brew/choco install ffmpeg")

    def convert_audio(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        format: str = "wav",
        codec: str = "pcm_s16le"
    ) -> str:
        """
        Convert audio file

        Args:
            input_path: Input audio file path
            output_path: Output audio file path (None = auto-generate)
            sample_rate: Target sample rate (16000 for Whisper)
            channels: Number of audio channels
            format: Output format (wav, mp3, ogg, etc.)
            codec: Audio codec (pcm_s16le, libmp3lame, libopus, etc.)

        Returns:
            Output file path
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Generate output path if not provided
        if output_path is None:
            input_path_obj = Path(input_path)
            output_path = str(
                input_path_obj.parent / f"{input_path_obj.stem}_converted.{format}"
            )

        # Build ffmpeg command
        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-c:a", codec,
            "-y",  # Overwrite existing file
            output_path
        ]

        try:
            self.logger.info(
                f"Converting: {input_path} -> {output_path} "
                f"({sample_rate}Hz, {channels}ch, {format})"
            )

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg conversion failed: {result.stderr}"
                )

            if not os.path.exists(output_path):
                raise RuntimeError("Output file not created")

            # Get file info
            file_size = os.path.getsize(output_path)
            self.logger.info(
                f"✓ Converted successfully ({file_size} bytes)"
            )

            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio conversion timed out")
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {e}")
            raise

    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get audio file information

        Args:
            audio_path: Path to audio file

        Returns:
            dict with duration, sample_rate, channels, format
        """
        try:
            result = subprocess.run(
                [
                    self.ffmpeg_path,
                    "-i", audio_path,
                    "-f", "null",
                    "-"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse output to get duration
            stderr = result.stderr
            info = {}

            # Extract duration
            if "Duration:" in stderr:
                duration_line = [line for line in stderr.split('\n') if "Duration:" in line][0]
                duration_str = duration_line.split("Duration:")[1].split(",")[0].strip()
                # Parse HH:MM:SS.mmm
                parts = duration_str.split(":")
                if len(parts) == 3:
                    hours, minutes, seconds = parts
                    info["duration"] = float(hours) * 3600 + float(minutes) * 60 + float(seconds)

            info["path"] = audio_path
            info["size"] = os.path.getsize(audio_path)

            return info

        except Exception as e:
            self.logger.error(f"Failed to get audio info: {e}")
            return {"path": audio_path, "error": str(e)}

    def prepare_for_stt(
        self,
        input_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Prepare audio file for STT (Whisper format)

        Args:
            input_path: Input audio file
            output_path: Output path (None = auto-generate)

        Returns:
            Path to STT-ready audio file
        """
        return self.convert_audio(
            input_path,
            output_path,
            sample_rate=16000,
            channels=1,
            format="wav",
            codec="pcm_s16le"
        )

    def prepare_for_tts_input(self, audio_path: str) -> Tuple[str, dict]:
        """
        Get audio info for TTS processing

        Args:
            audio_path: Audio file path

        Returns:
            Tuple of (audio_path, info_dict)
        """
        info = self.get_audio_info(audio_path)
        return audio_path, info

    def cleanup_temp_files(self, pattern: Optional[str] = None, max_age_hours: int = 24) -> int:
        """
        Clean up temporary audio files

        Args:
            pattern: File pattern to match (None = all temp files with certain suffixes)
            max_age_hours: Maximum age of files to delete

        Returns:
            Number of files deleted
        """
        deleted_count = 0
        temp_path = Path(self.temp_dir)

        try:
            # Common temp audio patterns
            patterns = [pattern] if pattern else [
                "*_converted.wav",
                "*_converted.mp3",
                "*_converted.ogg",
                "*_temp.wav",
                "*_temp.mp3"
            ]

            for pattern_str in patterns:
                for file in temp_path.glob(pattern_str):
                    try:
                        # Check file age
                        file_age_hours = (
                            (file.stat().st_mtime - time.time()) / 3600
                        ) if 'time' in globals() else 0

                        if max_age_hours == 0 or file_age_hours > max_age_hours:
                            file.unlink()
                            deleted_count += 1
                            self.logger.debug(f"Deleted temp file: {file.name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to delete {file.name}: {e}")

            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} temp file(s)")

            return deleted_count

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return 0


def quick_convert(input_path: str, sample_rate: int = 16000) -> str:
    """
    Quick audio conversion function

    Args:
        input_path: Input audio file path
        sample_rate: Target sample rate

    Returns:
        Path to converted file
    """
    processor = AudioProcessor()
    return processor.prepare_for_stt(input_path)


if __name__ == "__main__":
    # Example usage
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage: python processor.py <audio_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None

    # Get info
    processor = AudioProcessor()
    info = processor.get_audio_info(input_file)
    print(f"\nAudio Info:")
    print(f"  Path: {info['path']}")
    print(f"  Size: {info['size']} bytes")
    if 'duration' in info:
        print(f"  Duration: {info['duration']:.2f}s")

    # Convert
    converted = processor.prepare_for_stt(input_file, output)
    print(f"\n✓ Converted to: {converted}")

    # Get converted info
    info2 = processor.get_audio_info(converted)
    print(f"  Size: {info2['size']} bytes")
