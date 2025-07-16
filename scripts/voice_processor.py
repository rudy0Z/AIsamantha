import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
from pathlib import Path

class VoiceProcessor:
    def __init__(self):
        # Load Whisper model (using base model for balance of speed/accuracy)
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = np.float32
        
    def record_audio(self, duration=5):
        """Record audio from microphone"""
        print(f"Recording for {duration} seconds...")
        
        # Record audio
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype
        )
        sd.wait()  # Wait until recording is finished
        
        return audio_data.flatten()
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, audio_data, self.sample_rate)
                temp_path = temp_file.name
            
            # Transcribe using Whisper
            result = self.whisper_model.transcribe(temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return result["text"].strip()
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def transcribe_file(self, file_path):
        """Transcribe audio from file"""
        try:
            result = self.whisper_model.transcribe(str(file_path))
            return result["text"].strip()
        except Exception as e:
            print(f"File transcription error: {e}")
            return ""
    
    def is_speech_detected(self, audio_data, threshold=0.01):
        """Simple voice activity detection"""
        rms = np.sqrt(np.mean(audio_data**2))
        return rms > threshold
    
    def record_and_transcribe(self, duration=5):
        """Record audio and transcribe in one step"""
        audio_data = self.record_audio(duration)
        
        if self.is_speech_detected(audio_data):
            return self.transcribe_audio(audio_data)
        else:
            return ""

# Example usage and testing
if __name__ == "__main__":
    processor = VoiceProcessor()
    
    print("Voice Processor initialized!")
    print("Testing transcription...")
    
    # Test with a sample (this would normally be real audio)
    print("Say something for 3 seconds...")
    text = processor.record_and_transcribe(3)
    print(f"Transcribed: '{text}'")
