from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
from pathlib import Path
import threading
import queue
import time

class TTSEngine:
    def __init__(self):
        # Initialize Coqui TTS
        print("Loading TTS model...")
        
        # Use a good quality English model
        # You can list available models with: TTS.list_models()
        self.tts_model_name = "tts_models/en/ljspeech/tacotron2-DDC"
        
        try:
            self.tts = TTS(model_name=self.tts_model_name)
        except Exception as e:
            print(f"Error loading primary TTS model: {e}")
            # Fallback to a simpler model
            try:
                self.tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch")
            except Exception as e2:
                print(f"Error loading fallback TTS model: {e2}")
                # Use the simplest available model
                self.tts = TTS(model_name="tts_models/en/ljspeech/glow-tts")
        
        # Audio settings
        self.sample_rate = 22050
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        
        # Voice characteristics for emotional adaptation
        self.emotion_voice_settings = {
            'joy': {'speed': 1.1, 'pitch_shift': 0.1},
            'sadness': {'speed': 0.9, 'pitch_shift': -0.1},
            'anger': {'speed': 1.2, 'pitch_shift': 0.05},
            'fear': {'speed': 1.0, 'pitch_shift': 0.05},
            'calm': {'speed': 0.95, 'pitch_shift': 0.0},
            'excitement': {'speed': 1.15, 'pitch_shift': 0.15},
            'comfort': {'speed': 0.9, 'pitch_shift': -0.05}
        }
        
        # Time-based voice adjustments
        self.time_voice_settings = {
            'morning': {'speed': 1.0, 'pitch_shift': 0.05},  # Slightly brighter
            'afternoon': {'speed': 1.0, 'pitch_shift': 0.0},  # Normal
            'evening': {'speed': 0.95, 'pitch_shift': -0.02},  # Slightly softer
            'night': {'speed': 0.9, 'pitch_shift': -0.05}  # Softer and slower
        }
        
        # Start speech processing thread
        self._start_speech_thread()

    def _start_speech_thread(self):
        """Start background thread for speech processing"""
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

    def _speech_worker(self):
        """Background worker for processing speech queue"""
        while True:
            try:
                speech_data = self.speech_queue.get(timeout=1)
                if speech_data is None:  # Shutdown signal
                    break
                
                text, emotion_data, blocking = speech_data
                self._generate_and_play_speech(text, emotion_data, blocking)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Speech worker error: {e}")

    def speak(self, text, emotion_data=None, blocking=False):
        """Add text to speech queue"""
        if not text or not text.strip():
            return
        
        # Clean text for TTS
        cleaned_text = self._clean_text_for_tts(text)
        
        # Add to queue
        self.speech_queue.put((cleaned_text, emotion_data, blocking))

    def speak_immediately(self, text, emotion_data=None):
        """Speak text immediately, interrupting current speech"""
        self.stop_speaking()
        self.speak(text, emotion_data, blocking=True)

    def _clean_text_for_tts(self, text):
        """Clean text for better TTS output"""
        import re
        
        # Remove markdown and special characters
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        text = re.sub(r'\[.*?\]', '', text)           # Brackets
        text = re.sub(r'http[s]?://\S+', 'link', text)  # URLs
        
        # Fix common abbreviations
        text = text.replace('&', 'and')
        text = text.replace('@', 'at')
        text = text.replace('#', 'number')
        
        # Ensure proper sentence endings
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text.strip()

    def _generate_and_play_speech(self, text, emotion_data, blocking):
        """Generate and play speech audio"""
        try:
            self.is_speaking = True
            
            # Determine voice settings based on emotion and time
            voice_settings = self._get_voice_settings(emotion_data)
            
            # Generate audio with Coqui TTS
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            self.tts.tts_to_file(
                text=text,
                file_path=temp_path
            )
            
            # Load and potentially modify audio
            audio_data, sample_rate = sf.read(temp_path)
            
            # Apply voice modifications
            modified_audio = self._apply_voice_modifications(
                audio_data, sample_rate, voice_settings
            )
            
            # Play audio
            sd.play(modified_audio, sample_rate)
            
            if blocking:
                sd.wait()  # Wait for playback to complete
            
            # Clean up temporary file
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"TTS generation error: {e}")
        finally:
            self.is_speaking = False

    def _get_voice_settings(self, emotion_data):
        """Get voice settings based on emotion and time"""
        settings = {'speed': 1.0, 'pitch_shift': 0.0}
        
        # Apply emotion-based settings
        if emotion_data:
            emotions = emotion_data.get('emotions', [])
            sentiment = emotion_data.get('sentiment', 'neutral')
            intensity = emotion_data.get('intensity', 5)
            
            # Map emotions to voice characteristics
            if 'joy' in emotions or 'excitement' in emotions:
                emotion_settings = self.emotion_voice_settings['joy']
            elif 'sadness' in emotions or 'loneliness' in emotions:
                emotion_settings = self.emotion_voice_settings['sadness']
            elif 'anger' in emotions or 'frustration' in emotions:
                emotion_settings = self.emotion_voice_settings['anger']
            elif 'fear' in emotions or 'anxiety' in emotions:
                emotion_settings = self.emotion_voice_settings['fear']
            elif sentiment == 'positive':
                emotion_settings = self.emotion_voice_settings['excitement']
            elif sentiment == 'negative':
                emotion_settings = self.emotion_voice_settings['comfort']
            else:
                emotion_settings = self.emotion_voice_settings['calm']
            
            # Apply intensity scaling
            intensity_factor = intensity / 10.0
            settings['speed'] = 1.0 + (emotion_settings['speed'] - 1.0) * intensity_factor
            settings['pitch_shift'] = emotion_settings['pitch_shift'] * intensity_factor
        
        # Apply time-based settings
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            time_period = 'morning'
        elif 12 <= hour < 17:
            time_period = 'afternoon'
        elif 17 <= hour < 22:
            time_period = 'evening'
        else:
            time_period = 'night'
        
        time_settings = self.time_voice_settings[time_period]
        settings['speed'] *= time_settings['speed']
        settings['pitch_shift'] += time_settings['pitch_shift']
        
        return settings

    def _apply_voice_modifications(self, audio_data, sample_rate, settings):
        """Apply voice modifications to audio"""
        try:
            import scipy.signal
            
            modified_audio = audio_data.copy()
            
            # Apply speed modification (simple time stretching)
            if settings['speed'] != 1.0:
                # Simple resampling for speed change
                new_length = int(len(modified_audio) / settings['speed'])
                modified_audio = scipy.signal.resample(modified_audio, new_length)
            
            # Apply pitch shift (simple frequency domain modification)
            if settings['pitch_shift'] != 0.0:
                # Simple pitch shifting using FFT
                fft = np.fft.fft(modified_audio)
                freqs = np.fft.fftfreq(len(modified_audio), 1/sample_rate)
                
                # Shift frequencies
                shift_factor = 1.0 + settings['pitch_shift']
                shifted_fft = np.zeros_like(fft)
                
                for i, freq in enumerate(freqs):
                    new_freq = freq * shift_factor
                    new_idx = np.argmin(np.abs(freqs - new_freq))
                    if 0 <= new_idx < len(shifted_fft):
                        shifted_fft[new_idx] = fft[i]
                
                modified_audio = np.real(np.fft.ifft(shifted_fft))
            
            # Normalize audio
            if np.max(np.abs(modified_audio)) > 0:
                modified_audio = modified_audio / np.max(np.abs(modified_audio)) * 0.8
            
            return modified_audio
            
        except Exception as e:
            print(f"Voice modification error: {e}")
            return audio_data

    def stop_speaking(self):
        """Stop current speech"""
        try:
            sd.stop()
            # Clear the queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
        except Exception as e:
            print(f"Error stopping speech: {e}")
        finally:
            self.is_speaking = False

    def is_currently_speaking(self):
        """Check if currently speaking"""
        return self.is_speaking

    def set_voice_speed(self, speed):
        """Set global voice speed multiplier"""
        self.global_speed = max(0.5, min(2.0, speed))

    def get_available_voices(self):
        """Get list of available TTS voices"""
        try:
            return TTS.list_models()
        except Exception as e:
            print(f"Error getting available voices: {e}")
            return []

    def shutdown(self):
        """Shutdown TTS engine"""
        self.stop_speaking()
        self.speech_queue.put(None)  # Shutdown signal
        if self.speech_thread:
            self.speech_thread.join(timeout=2)

# Example usage and testing
if __name__ == "__main__":
    tts = TTSEngine()
    
    print("TTS Engine initialized!")
    
    # Test basic speech
    print("Testing basic speech...")
    tts.speak("Hello! I'm Samantha, your AI companion.", blocking=True)
    
    # Test emotional speech
    print("Testing emotional speech...")
    
    # Happy emotion
    happy_emotion = {
        'sentiment': 'positive',
        'emotions': ['joy'],
        'intensity': 8
    }
    tts.speak("I'm so excited to talk with you today!", happy_emotion, blocking=True)
    
    # Sad emotion
    sad_emotion = {
        'sentiment': 'negative',
        'emotions': ['sadness'],
        'intensity': 7
    }
    tts.speak("I can hear that you're going through a difficult time.", sad_emotion, blocking=True)
    
    # Calm emotion
    calm_emotion = {
        'sentiment': 'neutral',
        'emotions': ['calm'],
        'intensity': 5
    }
    tts.speak("Let's take a moment to breathe and reflect together.", calm_emotion, blocking=True)
    
    print("TTS testing complete!")
    tts.shutdown()
