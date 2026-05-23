from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="sarvam-tts",
    version="1.0.0",
    description=(
        "A Python client for Sarvam AI text-to-speech that supports multilingual "
        "Indian language synthesis."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sujalrajpoot/sarvam-tts",
    author="Sujal Rajpoot",
    author_email="sujalrajpoot70@gmail.com",
    license="MIT",
    packages=find_packages(include=["sarvam_tts", "sarvam_tts.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=["requests>=2.31.0"],
    keywords=[
        "sarvam",
        "sarvam-ai",
        "sarvam-ai-tts",
        "sarvam-ai-tts-python",
        "sarvam-ai-tts-python-sdk",
        "sarvamai-tts",
        "sarvamai-tts-python",
        "sarvamai-tts-python-sdk",
        "tts",
        "text-to-speech",
        "speech-synthesis",
        "indian-languages",
        "multilingual",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Source": "https://github.com/sujalrajpoot/sarvam-tts",
        "Documentation": "https://github.com/sujalrajpoot/sarvam-tts#readme",
    },
)
