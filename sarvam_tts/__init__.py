"""
Sarvam TTS - A Python library for using Sarvam's text-to-speech API.
"""

from sarvam_tts.providers.sarvam import SarvamTTS
from sarvam_tts.config import TTSConfig
from sarvam_tts.exceptions import TTSException, TTSRequestError

__all__ = ['SarvamTTS', 'TTSConfig', 'TTSException', 'TTSRequestError']