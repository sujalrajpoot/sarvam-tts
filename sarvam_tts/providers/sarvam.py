import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import List, Optional

import requests

from sarvam_tts.config import SUPPORTED_LANGUAGES, TTSConfig
from sarvam_tts.exceptions import TTSAPIError, TTSOutputError, TTSRequestError, TTSValidationError
from sarvam_tts.providers.base import TTSProvider
from sarvam_tts.utils import MultilingualSentenceTokenizer


class SarvamTTS(TTSProvider):
    def __init__(self, config: Optional[TTSConfig] = None, verbose: Optional[bool] = None) -> None:
        super().__init__(config)

        if verbose is not None:
            self.config.verbose = verbose

        self.verbose = self.config.verbose
        self.api_url = self.config.api_url
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.7",
            "content-type": "application/json",
            "origin": "https://www.sarvam.ai",
            "priority": "u=1, i",
            "referer": "https://www.sarvam.ai/apis/text-to-speech",
            "sec-ch-ua": '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        }
        self.tokenizer = MultilingualSentenceTokenizer()

    def get_voices(self) -> List[str]:
        voices = [
            "shreya",
            "shubh",
            "manan",
            "ishita",
            "priya",
            "suhani",
            "ashutosh",
            "ritu",
            "amit",
            "sumit",
            "pooja",
            "simran",
            "rahul",
            "kavya",
            "ratan",
            "shruti",
            "aditya",
            "soham",
            "rehan",
            "vijay",
            "tarun",
            "anand",
            "aayan",
            "rohan",
            "dev",
            "sunny",
            "kabir",
            "varun",
            "neha",
            "mani",
            "mohit",
            "rupali",
            "advait",
            "roopa",
            "tanya",
            "gokul",
            "kavitha",
        ]

        return f"Available voices: {', '.join(voices)}"

    def get_languages(self) -> str:
        return f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}"

    def _ensure_output_directory(self, output_filepath: str) -> None:
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    def _save_audio(self, audio_data: bytes, output_filepath: str) -> None:
        try:
            self._ensure_output_directory(output_filepath)
            with open(output_filepath, "wb") as handle:
                handle.write(audio_data)
            if self.verbose:
                print(f"Audio saved to {output_filepath}")
        except OSError as exc:
            raise TTSOutputError(f"Failed to save audio to '{output_filepath}': {exc}") from exc

    def _split_into_sentences(self, text: str, language: str) -> List[str]:
        return self.tokenizer.tokenize(text.strip(), language=language)

    def _extract_audio(self, response: requests.Response, part_number: int) -> bytes:
        if response.status_code >= 400:
            error_message = response.text.strip() or f"HTTP {response.status_code}"
            raise TTSRequestError(f"Request failed for chunk {part_number}: {error_message}")

        if not response.content:
            raise TTSRequestError(f"No data received for chunk {part_number}.")

        try:
            payload = response.json()
        except ValueError:
            return response.content

        if isinstance(payload, dict):
            if payload.get("error"):
                raise TTSAPIError(f"API error for chunk {part_number}: {payload.get('error')}")
            if payload.get("message") and payload.get("status") != "success":
                raise TTSAPIError(f"API error for chunk {part_number}: {payload.get('message')}")

        return response.content

    def _generate_audio_for_chunk(self, part_text: str, part_number: int, config: TTSConfig) -> bytes:
        payload = {
            "text": part_text,
            "target_language_code": SUPPORTED_LANGUAGES[config.language],
            "speaker": config.voice,
            "model": "bulbul:v3-beta",
            "pace": config.pace,
            "speech_sample_rate": config.sample_rate,
            "temperature": config.temperature,
            "enable_preprocessing": True,
            "output_audio_codec": "mp3",
        }

        for attempt in range(1, 4):
            try:
                response = requests.post(
                    config.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=config.timeout,
                )
                return self._extract_audio(response, part_number)
            except (requests.RequestException, TTSRequestError, TTSAPIError) as exc:
                if attempt == 3:
                    if isinstance(exc, TTSAPIError):
                        raise
                    raise TTSRequestError(f"Failed to generate audio for chunk {part_number}: {exc}") from exc
                if self.verbose:
                    print(f"Attempt {attempt} failed for chunk {part_number}: {exc}. Retrying...")
                time.sleep(1)

        raise TTSRequestError(f"Failed to generate audio for chunk {part_number} after retries.")

    def tts(
        self,
        text: str,
        language: Optional[str] = None,
        voice: Optional[str] = None,
        pace: Optional[float] = None,
        temperature: Optional[float] = None,
        sample_rate: Optional[int] = None,
        output_filepath: Optional[str] = None,
    ) -> str:
        """Convert text to speech using the SarvamTTS API and save it to a file."""
        if not text or not text.strip():
            raise TTSValidationError("Text input cannot be empty.")

        config = TTSConfig(
            timeout=self.config.timeout,
            verbose=self.config.verbose,
            output_path=output_filepath or self.config.output_path,
            language=language or self.config.language,
            voice=voice or self.config.voice,
            pace=pace if pace is not None else self.config.pace,
            temperature=temperature if temperature is not None else self.config.temperature,
            sample_rate=sample_rate if sample_rate is not None else self.config.sample_rate,
            api_url=self.config.api_url,
        )

        sentences = self._split_into_sentences(text, config.language)
        if not sentences:
            raise TTSValidationError("Text input produced no sentences for synthesis.")

        if self.verbose:
            for index, sentence in enumerate(sentences, start=1):
                print(f"{index}. Sentence: {sentence}")

        audio_chunks = {}

        try:
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._generate_audio_for_chunk, sentence.strip(), chunk_num, config): chunk_num
                    for chunk_num, sentence in enumerate(sentences, start=1)
                }

                for future in as_completed(futures):
                    chunk_num = futures[future]
                    audio_data = future.result()
                    audio_chunks[chunk_num] = audio_data

            combined_audio = BytesIO()
            for chunk_num in sorted(audio_chunks):
                combined_audio.write(audio_chunks[chunk_num])
                if self.verbose:
                    print(f"Added chunk {chunk_num} to the combined file.")

            self._save_audio(combined_audio.getvalue(), config.output_path)
            if self.verbose:
                print(f"Final Audio Saved as {config.output_path}.")
            return config.output_path
        except (TTSRequestError, TTSAPIError, TTSOutputError):
            raise
        except Exception as exc:
            raise TTSRequestError(f"Failed to perform the operation: {exc}") from exc

    def speak(self, text: str, config: Optional[TTSConfig] = None) -> str:
        resolved_config = self._resolve_config(config)
        return self.tts(
            text=text,
            language=resolved_config.language,
            voice=resolved_config.voice,
            pace=resolved_config.pace,
            temperature=resolved_config.temperature,
            sample_rate=resolved_config.sample_rate,
            output_filepath=resolved_config.output_path,
        )
