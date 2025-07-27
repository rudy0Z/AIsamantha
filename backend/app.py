# app_enhanced.py - Groq API + Scalable Memory + Advanced Emotional Intelligence (XTTS v2 Primary)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import os
import torch
from transformers import pipeline
from groq import Groq
from TTS.api import TTS

# Fix PyTorch weights loading for XTTS compatibility
import torch.serialization
torch.serialization.add_safe_globals([
    'TTS.tts.configs.xtts_config.XttsConfig',
    'TTS.vocoder.configs.hifigan_config.HifiganConfig',
    'TTS.tts.configs.tacotron2_config.Tacotron2Config'
])

# Ensure these imports are valid and files (memory.py, personality.py) exist
from memory import ScalableMemoryManager
from personality import SamanthaPersonality
import time
import uuid
import traceback # For detailed error logging

app = Flask(__name__)
CORS(app)

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Groq API Configuration - Load from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None
    print("🔑 WARNING: GROQ_API_KEY is not set. LLM functionality will be disabled.")

# Initialize Scalable Memory and Personality Systems
memory_system = ScalableMemoryManager(BASE_DIR, max_active_memories=30)
samantha_personality = SamanthaPersonality()

print("🧠 Advanced Samantha with Scalable Memory & Emotional Intelligence")
print("📊 Memory Management: Automatic cleanup, importance scoring, clustering")
print("Device allocation - LLM: Groq Cloud, Emotion: CPU, XTTS: GPU if available, Whisper: CPU")

# --- Model Loading ---

# Load Whisper ASR Model (CPU only)
try:
    print("Loading Whisper ASR model...")
    asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base.en", device="cpu")
    print("✅ Whisper ASR model loaded on CPU.")
except Exception as e:
    print(f"❌ Error loading Whisper ASR: {e}")
    asr_pipeline = None

# Load Emotion Detection Model (CPU only)
try:
    print("Loading Emotion Detection model...")
    emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device="cpu", return_all_scores=False)
    print("✅ Emotion Detection model loaded on CPU.")
except Exception as e:
    print(f"❌ Error loading Emotion Detection: {e}")
    emotion_pipeline = None

# --- XTTS v2 Model Loading (Primary Attempt) ---
tts_model = None
SAMANTHA_VOICE_CONFIG = {}
current_tts_model_type = "none" # To track which TTS model is active

def get_xtts_model():
    """Load XTTS v2 model with proper error handling"""
    print("Loading TTS model for Samantha...")
    
    # Define paths for speaker WAVs
    samantha_neutral_voice_path = os.path.join(BASE_DIR, "voices", "samantha_neutral.wav")
    samantha_happy_voice_path = os.path.join(BASE_DIR, "voices", "samantha_happy.wav")
    samantha_sad_voice_path = os.path.join(BASE_DIR, "voices", "samantha_sad.wav")
    samantha_angry_voice_path = os.path.join(BASE_DIR, "voices", "samantha_angry.wav")
    samantha_fear_voice_path = os.path.join(BASE_DIR, "voices", "samantha_fear.wav")
    samantha_surprise_voice_path = os.path.join(BASE_DIR, "voices", "samantha_surprise.wav")

    # Check if neutral voice reference exists
    if os.path.exists(samantha_neutral_voice_path):
        print(f"📂 Voice reference found at: {samantha_neutral_voice_path}")
        try:
            print("🎯 Attempting XTTS v2 with voice cloning...")
            os.environ["COQUI_TOS_AGREED"] = "1"
            
            # Load XTTS v2 model
            model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())
            
            # Test XTTS with a simple phrase
            test_text = "Testing XTTS"
            model.tts(text=test_text, speaker_wav=samantha_neutral_voice_path, language="en")
            
            print("✅ XTTS v2 voice cloning loaded successfully!")
            return model, "xtts_v2", {
                'model_type': "xtts_v2",
                'language': 'en',
                'reference_voices': {
                    'neutral': samantha_neutral_voice_path,
                    'joy': samantha_happy_voice_path if os.path.exists(samantha_happy_voice_path) else samantha_neutral_voice_path,
                    'happiness': samantha_happy_voice_path if os.path.exists(samantha_happy_voice_path) else samantha_neutral_voice_path,
                    'sadness': samantha_sad_voice_path if os.path.exists(samantha_sad_voice_path) else samantha_neutral_voice_path,
                    'anger': samantha_angry_voice_path if os.path.exists(samantha_angry_voice_path) else samantha_neutral_voice_path,
                    'fear': samantha_fear_voice_path if os.path.exists(samantha_fear_voice_path) else samantha_neutral_voice_path,
                    'surprise': samantha_surprise_voice_path if os.path.exists(samantha_surprise_voice_path) else samantha_neutral_voice_path,
                    'love': samantha_neutral_voice_path,
                    'excitement': samantha_happy_voice_path if os.path.exists(samantha_happy_voice_path) else samantha_neutral_voice_path,
                    'compassion': samantha_neutral_voice_path,
                    'curiosity': samantha_neutral_voice_path,
                    'playful': samantha_happy_voice_path if os.path.exists(samantha_happy_voice_path) else samantha_neutral_voice_path,
                },
                'emotion_text_mods': {
                    'joy': lambda t: f"{t}!" if not t.endswith('!') else t,
                    'sadness': lambda t: f"*soft voice* {t}",
                    'anger': lambda t: f"*gentle but firm* {t}",
                    'fear': lambda t: f"*reassuring tone* {t}",
                    'surprise': lambda t: f"Oh! {t}",
                    'neutral': lambda t: t,
                    'happiness': lambda t: f"*cheerful* {t}!",
                    'love': lambda t: f"*warm, affectionate* {t}",
                    'excitement': lambda t: f"*energetic* {t}!",
                    'compassion': lambda t: f"*understanding* {t}",
                    'curiosity': lambda t: f"*interested* Hmm, {t}",
                    'playful': lambda t: f"*playful giggle* {t}!"
                }
            }
        except Exception as e:
            print(f"❌ XTTS v2 failed: {e}")
    else:
        print(f"📂 No voice reference found at: {samantha_neutral_voice_path}")
        print("   Place a 3-10 second WAV file there to enable XTTS voice cloning.")

    # Fallback to Tacotron2
    print("🔄 Falling back to reliable Tacotron2 model...")
    try:
        model = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=torch.cuda.is_available())
        print("✅ Tacotron2 model loaded successfully for Samantha's voice.")
        return model, "tacotron2", {
            'model_type': "tacotron2",
            'language': 'en',
            'emotion_text_mods': {
                'joy': lambda t: f"*excited* {t}!" if not t.endswith('!') else f"*excited* {t}",
                'sadness': lambda t: f"*soft, caring voice* {t}",
                'anger': lambda t: f"*gentle but firm tone* {t}",
                'fear': lambda t: f"*reassuring, comforting voice* {t}",
                'surprise': lambda t: f"Oh wow! {t}",
                'neutral': lambda t: t,
                'happiness': lambda t: f"*cheerful* {t}!",
                'love': lambda t: f"*warm, affectionate* {t}",
                'excitement': lambda t: f"*energetic* {t}!",
                'compassion': lambda t: f"*understanding* {t}",
                'curiosity': lambda t: f"*interested* Hmm, {t}",
                'playful': lambda t: f"*playful giggle* {t}!"
            }
        }
    except Exception as fallback_e:
        print(f"❌ Fallback Tacotron2 also failed: {fallback_e}")
        return None, "none", {}

try:
    tts_model, current_tts_model_type, SAMANTHA_VOICE_CONFIG = get_xtts_model()
    print(f"🎭 Configured Samantha's hybrid voice system ({current_tts_model_type})")

except Exception as e:
    print(f"❌ Error loading TTS: {e}")
    tts_model, current_tts_model_type, SAMANTHA_VOICE_CONFIG = None, "none", {}

if tts_model is None:
    print("❗ No TTS model could be loaded. Speech synthesis will use dummy audio.")

# --- Enhanced LLM Generation with Memory & Emotional Intelligence ---
def generate_llm_response_with_memory(user_text: str, detected_emotion: str, chat_history: list = None) -> str:
    """Generate emotionally intelligent response with scalable memory"""
    if groq_client is None:
        print("❌ Groq client not initialized. Cannot generate LLM response.")
        return "Sorry, my brain isn't quite connected right now. Please check the Groq API key."
    try:
        # 1. Retrieve relevant memories using optimized RAG
        relevant_memories = memory_system.retrieve_relevant_memories_scalable(
            user_text, detected_emotion, limit=8
        )

        # 2. Get conversation summary for context (optimized)
        conversation_summary = f"Recent interactions: {len(relevant_memories)} relevant memories found"

        # 3. Generate emotionally intelligent prompt with memory limits
        system_prompt = samantha_personality.generate_emotional_prompt(
            user_text=user_text,
            emotion=detected_emotion,
            relevant_memories=relevant_memories[:5],
            conversation_summary=conversation_summary
        )

        # 4. Build conversation messages with token management
        messages = [{"role": "system", "content": system_prompt}]

        # Add recent chat history (session context) - limited for performance
        if chat_history:
            for turn in chat_history[-2:]:
                messages.append({"role": "user", "content": turn.get("user", "")})
                messages.append({"role": "assistant", "content": turn.get("ai", "")})

        # Add current user input
        messages.append({"role": "user", "content": user_text})

        print(f"🤖 Generating response with {len(relevant_memories)} relevant memories (importance-filtered)")

        # 5. Call Groq API with optimized context
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            temperature=0.8,
            max_tokens=150,
            top_p=0.9,
            stop=None,
            stream=False,
        )

        ai_response = chat_completion.choices[0].message.content.strip()

        # 6. Enhance response with memory if needed
        enhanced_response = samantha_personality.enhance_response_with_memory(
            ai_response, relevant_memories
        )

        # 7. Store conversation with importance scoring and session tracking
        session_id = "session_" + str(hash(user_text))[:8]
        memory_system.store_conversation_scalable(user_text, enhanced_response, detected_emotion, session_id)

        print(f"✅ Generated response with scalable memory: {enhanced_response[:80]}...")
        return enhanced_response

    except Exception as e:
        print(f"❌ Error with enhanced generation: {e}")
        # Fallback with emotional intelligence
        fallback_response = samantha_personality.get_response_template(detected_emotion, 'validation')
        return fallback_response

# --- API Endpoints ---

@app.route('/transcribe', methods=['POST'])
def transcribe_audio_endpoint():
    """Convert speech to text using Whisper"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    if asr_pipeline is None:
        return jsonify({"error": "Whisper model not loaded"}), 500

    audio_file = request.files['audio']
    audio_bytes = audio_file.read()

    temp_audio_path = os.path.join(BASE_DIR, "temp_audio.wav")
    with open(temp_audio_path, "wb") as f:
        f.write(audio_bytes)

    try:
        transcript = asr_pipeline(temp_audio_path)["text"]
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        print(f"🎤 Transcription: {transcript}")
        return jsonify({"text": transcript})
    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        print(f"❌ Error in transcription: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion_endpoint():
    """Detect emotion from text using BERT"""
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if emotion_pipeline is None:
        return jsonify({"error": "Emotion model not loaded"}), 500

    try:
        emotion_result = emotion_pipeline(text)[0]
        emotion_label = emotion_result['label']
        confidence = emotion_result['score']
        print(f"😊 Detected emotion: {emotion_label} (confidence: {confidence:.2f})")
        return jsonify({"emotion": emotion_label, "confidence": confidence})
    except Exception as e:
        print(f"❌ Error in emotion detection: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_response', methods=['POST'])
def generate_response_endpoint():
    """Generate AI response using Groq API with memory and emotional intelligence"""
    data = request.get_json()
    user_text = data.get('user_text', '')
    detected_emotion = data.get('detected_emotion', 'neutral')
    chat_history = data.get('chat_history', [])

    if not user_text:
        return jsonify({"error": "No user text provided"}), 400

    ai_response = generate_llm_response_with_memory(user_text, detected_emotion, chat_history)
    return jsonify({"response": ai_response})

@app.route('/synthesize_speech', methods=['POST'])
def synthesize_speech_endpoint():
    """Convert text to speech using XTTS with emotional modulation"""
    data = request.get_json()
    text = data.get('text', '')
    emotion = data.get('emotion', 'neutral')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if tts_model is None:
        # Fallback dummy audio if no TTS model loaded
        from pydub import AudioSegment
        from pydub.generators import Sine
        print("⚠️ No TTS model loaded, returning dummy audio.")
        sine_wave = Sine(440).to_audio_segment(duration=1000)
        audio_buffer = io.BytesIO()
        sine_wave.export(audio_buffer, format="wav")
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype="audio/wav")

    try:
        print(f"🔊 Synthesizing Samantha's emotional speech: '{text}' (emotion: {emotion})")

        unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
        temp_audio_path = os.path.join(BASE_DIR, f"samantha_voice_{unique_id}.wav")

        # Get enhanced text based on emotion
        emotion_mods = SAMANTHA_VOICE_CONFIG['emotion_text_mods']
        modified_text = emotion_mods.get(emotion.lower(), emotion_mods['neutral'])(text)
        print(f"🎭 Enhanced text for {emotion} ({current_tts_model_type}): \"{modified_text[:60]}...\"")

        # --- Dynamic TTS Synthesis based on loaded model type ---
        if current_tts_model_type == "xtts_v2":
            ref_voice_path = SAMANTHA_VOICE_CONFIG['reference_voices'].get(emotion.lower(), SAMANTHA_VOICE_CONFIG['reference_voices']['neutral'])
            if not os.path.exists(ref_voice_path):
                print(f"Warning: XTTSv2 reference voice for '{emotion}' not found, using neutral: {ref_voice_path}")
                ref_voice_path = SAMANTHA_VOICE_CONFIG['reference_voices']['neutral']

            tts_model.tts_to_file(
                text=modified_text,
                file_path=temp_audio_path,
                speaker_wav=ref_voice_path,
                language=SAMANTHA_VOICE_CONFIG['language']
            )
            print("✅ XTTS v2 synthesis successful.")
        elif current_tts_model_type == "tacotron2":
            tts_model.tts_to_file(
                text=modified_text,
                file_path=temp_audio_path
            )
            print("✅ Tacotron2 synthesis successful.")
        else:
            raise Exception(f"Unknown TTS model type: {current_tts_model_type}. Cannot synthesize.")

        # Verify the audio was created successfully
        if not os.path.exists(temp_audio_path):
            raise Exception("Audio file was not created by TTS model.")

        file_size = os.path.getsize(temp_audio_path)
        print(f"Generated audio file size: {file_size:,} bytes")
        if file_size < 1000: # Very small file likely indicates an issue
            print("⚠️ Warning: Audio file seems unusually small (less than 1KB), might be empty or corrupted.")

        # Read and return audio
        with open(temp_audio_path, "rb") as f:
            audio_data = f.read()

        # Clean up temporary file
        try:
            os.remove(temp_audio_path)
        except Exception as cleanup_error:
            print(f"Warning: Could not clean up {temp_audio_path}: {cleanup_error}")

        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype="audio/wav")

    except Exception as e:
        traceback.print_exc()
        print(f"❌ Speech synthesis failed: {e}")
        # Fallback to dummy audio on synthesis failure
        from pydub import AudioSegment
        from pydub.generators import Sine
        sine_wave = Sine(440).to_audio_segment(duration=1000)
        audio_buffer = io.BytesIO()
        sine_wave.export(audio_buffer, format="wav")
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype="audio/wav")

@app.route('/memory_stats', methods=['GET'])
def memory_stats_endpoint():
    """Get comprehensive memory statistics and health"""
    try:
        stats = memory_system.get_memory_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/memory_cleanup', methods=['POST'])
def memory_cleanup_endpoint():
    """Trigger manual memory cleanup"""
    try:
        memory_system.periodic_memory_cleanup()
        return jsonify({"status": "Memory cleanup completed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "models": {
            "whisper": asr_pipeline is not None,
            "emotion": emotion_pipeline is not None,
            "tts": tts_model is not None,
            "current_tts_type": current_tts_model_type, # Add this for debugging
            "groq": bool(GROQ_API_KEY),
            "memory_system": memory_system is not None,
            "personality_system": samantha_personality is not None
        },
        "features": [
            "Scalable Persistent Memory",
            "Importance-Based Memory Prioritization",
            "Automatic Memory Cleanup & Archiving",
            "RAG-based Context Retrieval",
            "Advanced Emotional Intelligence",
            "Groq API Integration",
            "Samantha's Sweet Female Voice with Hybrid TTS (Tacotron2/XTTSv2)",
            "Enhanced Emotional Voice Variations (via text mods & XTTSv2 if active)",
            "Memory Health Monitoring"
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced Samantha Backend!")
    print("💝 Features: Persistent Memory + Emotional Intelligence + RAG")
    if GROQ_API_KEY:
        print("🔑 GROQ_API_KEY is configured and ready.")
    else:
        print("🔑 WARNING: GROQ_API_KEY is not set. The application will not run.")
    app.run(host='0.0.0.0', port=5000, debug=True)