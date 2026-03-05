"""
STT (Speech-to-Text) module using faster-whisper
"""

from faster_whisper import WhisperModel, BatchedInferencePipeline
import os
import logging
from typing import Optional, Dict, Any, Generator


class LocalSTT:
    """Local STT using faster-whisper"""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        beam_size: int = 5
    ):
        """
        Initialize faster-whisper STT model

        Args:
            model_size: Model size (tiny, base, small, medium, large-v3, turbo)
            device: 'cpu' or 'cuda'
            compute_type: 'int8', 'float16', 'float32'
            beam_size: Beam search size (1-10)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size

        # Initialize model
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        self.batched_model = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"Initialized faster-whisper {model_size} on {device} ({compute_type})"
        )

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        word_timestamps: bool = False,
        batch: bool = False,
        vad_filter: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code (None = auto-detect)
            word_timestamps: Return word-level timestamps
            batch: Use batched inference for speed
            vad_filter: Use Voice Activity Detection

        Returns:
            dict with 'text', 'language', 'segments', 'duration'
        """
        model = self.batched_model if batch and self.batched_model else self.model

        try:
            segments, info = model.transcribe(
                audio_path,
                language=language,
                word_timestamps=word_timestamps,
                beam_size=self.beam_size,
                vad_filter=vad_filter
            )

            # Collect results
            segments_list = []
            full_text = []

            for segment in segments:
                segment_dict = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }

                if word_timestamps and hasattr(segment, 'words'):
                    segment_dict["words"] = [
                        {"start": w.start, "end": w.end, "word": w.word}
                        for w in segment.words
                    ]

                segments_list.append(segment_dict)
                full_text.append(segment.text)

            result = {
                "text": " ".join(full_text).strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": segments_list,
                "duration": segments_list[-1]["end"] if segments_list else 0
            }

            self.logger.info(
                f"Transcribed {result['duration']:.2f}s of audio: "
                f"'{result['text'][:50]}...'"
            )

            return result

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise

    def transcribe_streaming(
        self,
        audio_path: str,
        callback: callable
    ) -> None:
        """
        Transcribe with streaming results

        Args:
            audio_path: Path to audio file
            callback: Function to call for each segment
        """
        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=self.beam_size,
                vad_filter=True
            )

            for segment in segments:
                callback({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "language": info.language
                })

        except Exception as e:
            self.logger.error(f"Streaming transcription failed: {e}")
            raise

    def enable_batched(self, batch_size: int = 16) -> None:
        """Enable batched inference for faster processing"""
        self.batched_model = BatchedInferencePipeline(
            model=self.model,
            batch_size=batch_size
        )
        self.logger.info(f"Enabled batched inference (batch_size={batch_size})")


def quick_transcribe(
    audio_path: str,
    model_size: str = "base",
    device: str = "cpu"
) -> str:
    """
    Quick transcription function

    Args:
        audio_path: Path to audio file
        model_size: Model size (tiny, base, small, medium, large-v3, turbo)
        device: 'cpu' or 'cuda'

    Returns:
        Transcribed text
    """
    stt = LocalSTT(model_size=model_size, device=device)
    result = stt.transcribe(audio_path)
    return result["text"]


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python stt.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    text = quick_transcribe(audio_file, model_size="base", device="cpu")
    print(f"\nTranscription:\n{text}")
