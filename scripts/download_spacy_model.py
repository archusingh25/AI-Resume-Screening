"""
Script to download spaCy model
Run this before starting the application
"""
import subprocess
import sys
from app.core.config import settings


def download_spacy_model():
    """Download the required spaCy model"""
    model_name = settings.SPACY_MODEL
    print(f"Downloading spaCy model: {model_name}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "spacy", "download", model_name
        ])
        print(f"Successfully downloaded {model_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_spacy_model()

