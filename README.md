# Sarvam TTS

**sarvam-tts** is a Python client for the Sarvam AI text-to-speech API. It provides a clean `SarvamTTS` interface for multilingual Indian language synthesis, configurable output settings, and chunked request handling for reliable audio generation.

> ⚠️ This project is provided for educational and research purposes only. Please comply with Sarvam AI's terms of service and acceptable use policies when using the API.

## ✨ Features

- Multi-language TTS support for Indian languages
- Simple `SarvamTTS` API for generating MP3 output
- Configurable `TTSConfig` for language, voice, pace, temperature, sample rate, and timeout
- Concurrent chunk generation for long texts
- Package metadata and install support via `setup.py`

## 📁 Project Structure

```text
sarvam-tts/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── example.py
├── sarvam_tts/
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── utils.py
│   └── providers/
│       ├── __init__.py
│       ├── base.py
└───────└── sarvam.py
```

### Package contents

- `sarvam_tts/__init__.py` exports the public API: `SarvamTTS`, `TTSConfig`, `TTSException`, and `TTSRequestError`
- `sarvam_tts/config.py` contains supported languages, default API URL, and configuration validation
- `sarvam_tts/providers/sarvam.py` implements the Sarvam AI request flow and audio saving logic
- `sarvam_tts/providers/base.py` defines the provider abstraction
- `sarvam_tts/utils.py` contains the multilingual sentence tokenizer
- `example.py` demonstrates basic usage

## 🛠️ Installation

**Using PyPI (Recommended)**
```bash
pip install sarvam-tts
```

**Clone Locally**
```bash
git clone https://github.com/sujalrajpoot/sarvam-tts.git
cd sarvam-tts
pip install -r requirements.txt
```

## 🧪 Quick Start

```python
from sarvam_tts import SarvamTTS

client = SarvamTTS()

output_path = client.tts(
    text="Hello from Sarvam TTS!",
    language="english",
    voice="shreya",
    pace=1.0,
    temperature=0.6,
    sample_rate=22050,
    output_filepath="output.mp3",
)

print(output_path)
```

You can also customize the configuration directly:

```python
from sarvam_tts import TTSConfig, SarvamTTS

config = TTSConfig(
    language="hindi",
    voice="shreya",
    pace=1.0,
    temperature=0.4,
    sample_rate=22050,
    output_path="demo/output.mp3",
)

client = SarvamTTS(config=config)
client.tts("नमस्ते, यह एक उदाहरण है।")
```

## 🧠 Supported Languages

- `english`
- `hindi`
- `bengali`
- `tamil`
- `telugu`
- `kannada`
- `malayalam`
- `marathi`
- `gujarati`
- `punjabi`
- `odia`

## 🎤 Example Voice Names

The library supports common voice names such as:

- `shreya`
- `shubh`
- `manan`
- `ishita`
- `priya`
- `suhani`
- `ashutosh`
- `ritu`
- `amit`
- `sumit`
- `pooja`
- `simran`
- `rahul`
- `kavya`
- `ratan`
- `shruti`
- `aditya`
- `soham`
- `rehan`
- `vijay`
- `tarun`
- `anand`
- `aayan`
- `rohan`
- `dev`
- `sunny`
- `kabir`
- `varun`
- `neha`
- `mani`
- `mohit`
- `rupali`
- `advait`
- `roopa`
- `tanya`
- `gokul`
- `kavitha`

## 🔧 API Reference

### `SarvamTTS.tts(...)`

Parameters:

- `text` – text to synthesize
- `language` – optional override for the language
- `voice` – optional override for the voice
- `pace` – optional override for speaking pace
- `temperature` – optional override for voice variability
- `sample_rate` – optional override for sample rate
- `output_filepath` – optional output path

### `TTSConfig`

The configuration object provides defaults for:

- `timeout`
- `verbose`
- `output_path`
- `language`
- `voice`
- `pace`
- `temperature`
- `sample_rate`
- `api_url`

## 🖼️ How It Works

1. `SarvamTTS` accepts text and configuration values.
2. The text is split into sentence-level chunks.
3. Each chunk is sent to the Sarvam AI endpoint concurrently.
4. Audio responses are merged into a single MP3 payload.
5. The final audio is saved to the requested output path.

## 🧪 Running the Example

```bash
python example.py
```

The script generates sample audio files in a `Test/` directory.

## 🤝 Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
