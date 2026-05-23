"""Configuration classes for TTS functionality."""

from dataclasses import dataclass
from enum import Enum
import os
from typing import Dict, List

from sarvam_tts.exceptions import TTSConfigurationError

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "bengali": "bn-IN",
    "tamil": "ta-IN",
    "telugu": "te-IN",
    "kannada": "kn-IN",
    "malayalam": "ml-IN",
    "marathi": "mr-IN",
    "gujarati": "gu-IN",
    "punjabi": "pa-IN",
    "odia": "od-IN",
}

VALID_SAMPLE_RATES = {22050, 8000, 48000}
DEFAULT_API_URL = "https://www.sarvam.ai/api/playground/tts"


@dataclass
class TTSConfig:
    """Configuration class for Text-to-Speech settings."""

    timeout: int = 30
    verbose: bool = True
    output_path: str = os.path.join(os.getcwd(), "output.mp3")
    language: str = "english"
    voice: str = "shreya"
    pace: float = 1.0
    temperature: float = 0.6
    sample_rate: int = 22050
    api_url: str = DEFAULT_API_URL

    def __post_init__(self) -> None:
        self.language = self._normalize_language(self.language)
        self.voice = self._normalize_voice(self.voice)
        self._validate_numeric_fields()

    @staticmethod
    def _normalize_language(language: str) -> str:
        normalized = (language or "english").strip().lower()
        if normalized not in SUPPORTED_LANGUAGES:
            raise TTSConfigurationError(
                f"Unsupported language '{language}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        return normalized

    @staticmethod
    def _normalize_voice(voice: str) -> str:
        normalized = voice.strip().lower()
        if not normalized:
            raise TTSConfigurationError("Voice must be a non-empty string.")
        return normalized

    def _validate_numeric_fields(self) -> None:
        if self.timeout <= 0:
            raise TTSConfigurationError("Timeout must be greater than zero.")

        if not 0.5 <= self.pace <= 2.0:
            raise TTSConfigurationError("Pace must be between 0.5 and 2.0.")

        if not 0.0 <= self.temperature <= 1.0:
            raise TTSConfigurationError("Temperature must be between 0.0 and 1.0.")

        if self.sample_rate not in VALID_SAMPLE_RATES:
            raise TTSConfigurationError(
                f"Sample rate must be one of {sorted(VALID_SAMPLE_RATES)}."
            )

        if not self.output_path:
            raise TTSConfigurationError("Output path must be a non-empty string.")
