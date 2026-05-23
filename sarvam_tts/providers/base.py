"""Base classes for TTS providers."""

from abc import ABC, abstractmethod
from typing import Optional

from sarvam_tts.config import TTSConfig


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    def __init__(self, config: Optional[TTSConfig] = None) -> None:
        self.config = config or TTSConfig()

    def _resolve_config(self, config: Optional[TTSConfig] = None) -> TTSConfig:
        return config or self.config

    @abstractmethod
    def speak(self, text: str, config: Optional[TTSConfig] = None) -> str:
        """Convert text to speech and save to file.

        Args:
            text: The text to convert to speech
            config: Configuration settings for the TTS operation

        Returns:
            str: Path to the generated audio file

        Raises:
            TTSException: If there's an error during the conversion process
        """
        pass
