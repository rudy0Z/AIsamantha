#!/usr/bin/env python3
"""
Setup script for Samantha AI environment
This script will install dependencies and set up the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_system_dependencies():
    """Install system-level dependencies"""
    print("\n📦 Installing system dependencies...")
    
    # Check operating system
    import platform
    system = platform.system().lower()
    
    if system == "linux":
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y portaudio19-dev python3-pyaudio",
            "sudo apt-get install -y espeak espeak-data libespeak1 libespeak-dev",
            "sudo apt-get install -y ffmpeg"
        ]
        
        for cmd in commands:
            if not run_command(cmd, f"Running: {cmd}"):
                print("⚠️  Some system dependencies may not have installed correctly")
                print("You may need to install them manually")
    
    elif system == "darwin":  # macOS
        commands = [
            "brew install portaudio",
            "brew install espeak",
            "brew install ffmpeg"
        ]
        
        print("On macOS, please ensure you have Homebrew installed")
        for cmd in commands:
            run_command(cmd, f"Running: {cmd}")
    
    else:
        print("⚠️  Automatic system dependency installation not supported for your OS")
        print("Please install the following manually:")
        print("- PortAudio (for audio recording)")
        print("- espeak (for text-to-speech)")
        print("- FFmpeg (for audio processing)")

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n🐍 Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install PyTorch (CPU version for compatibility)
    torch_command = f"{sys.executable} -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu"
    run_command(torch_command, "Installing PyTorch (CPU version)")
    
    # Install other dependencies
    requirements = [
        "streamlit==1.28.0",
        "openai-whisper==20231117",
        "transformers==4.35.0",
        "sentence-transformers==2.2.2",
        "langchain==0.0.340",
        "langchain-community==0.0.1",
        "chromadb==0.4.15",
        "TTS==0.20.6",
        "numpy==1.24.3",
        "pandas==2.0.3",
        "scipy==1.11.3",
        "scikit-learn==1.3.0",
        "nltk==3.8.1",
        "textblob==0.17.1",
        "vaderSentiment==3.3.2",
        "sounddevice==0.4.6",
        "soundfile==0.12.1",
        "pyaudio==0.2.11",
        "pydub==0.25.1",
        "matplotlib==3.7.2",
        "plotly==5.17.0",
        "python-dotenv==1.0.0",
        "streamlit-webrtc==0.47.1",
        "av==10.0.0"
    ]
    
    for package in requirements:
        run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}")

def download_models():
    """Download required AI models"""
    print("\n🤖 Downloading AI models...")
    
    # Download NLTK data
    import nltk
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("✓ NLTK data downloaded")
    except Exception as e:
        print(f"⚠️  NLTK download warning: {e}")
    
    # Test model downloads
    try:
        print("Testing Whisper model download...")
        import whisper
        model = whisper.load_model("base")
        print("✓ Whisper model loaded successfully")
    except Exception as e:
        print(f"⚠️  Whisper model warning: {e}")
    
    try:
        print("Testing sentence transformer model...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Sentence transformer model loaded successfully")
    except Exception as e:
        print(f"⚠️  Sentence transformer warning: {e}")
    
    try:
        print("Testing TTS model...")
        from TTS.api import TTS
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
        print("✓ TTS model loaded successfully")
    except Exception as e:
        print(f"⚠️  TTS model warning: {e}")
        print("Trying fallback TTS model...")
        try:
            tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch")
            print("✓ Fallback TTS model loaded successfully")
        except Exception as e2:
            print(f"⚠️  Fallback TTS model warning: {e2}")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "samantha_memory",
        "audio_cache",
        "logs",
        "user_data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def run_tests():
    """Run basic tests to verify installation"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        import streamlit
        import whisper
        import transformers
        import chromadb
        import TTS
        import sounddevice
        import nltk
        print("✓ All major imports successful")
        
        # Test basic functionality
        from emotion_detector import EmotionDetector
        detector = EmotionDetector()
        result = detector.analyze_emotion("I'm feeling great today!")
        print("✓ Emotion detection test passed")
        
        from memory_manager import MemoryManager
        memory = MemoryManager("test_memory")
        print("✓ Memory manager test passed")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🌟 Welcome to Samantha AI Setup!")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python dependencies
    install_python_dependencies()
    
    # Create directories
    create_directories()
    
    # Download models
    download_models()
    
    # Run tests
    if run_tests():
        print("\n🎉 Setup completed successfully!")
        print("\nTo start Samantha AI, run:")
        print("streamlit run scripts/app.py")
        print("\nOr use the convenience script:")
        print("python scripts/run_samantha.py")
    else:
        print("\n⚠️  Setup completed with some warnings")
        print("You may still be able to run Samantha AI, but some features might not work")
        print("\nTo start anyway, run:")
        print("streamlit run scripts/app.py")

if __name__ == "__main__":
    main()
