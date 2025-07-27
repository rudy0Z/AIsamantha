# backend_app.py (Updated for LLM)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import os
import torch
from transformers import pipeline
from ctransformers import AutoModelForCausalLM, AutoTokenizer # Import ctransformers
from TTS.api import TTS # XTTS integration

app = Flask(__name__)
CORS(app) # Enable CORS for frontend to backend communication

# --- Configuration ---
# Path to your downloaded GGUF model (using absolute path)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "mistral-7b-instruct-v0.2.Q5_K_M.gguf")
LLM_MODEL_TYPE = "mistral" # Specify the model type for ctransformers

# Device allocation strategy:
# - LLM: GPU (primary compute task, benefits most from GPU acceleration)
# - Emotion Detection (BERT): CPU (smaller model, saves VRAM for LLM and XTTS)
# - XTTS: GPU if available (audio generation benefits from GPU)
# - Whisper ASR: CPU (fast enough on CPU, saves VRAM)

DEVICE_GPU = 0 if torch.cuda.is_available() else "cpu"
DEVICE_CPU = "cpu"
print(f"GPU available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
print(f"Device allocation - LLM: GPU, Emotion: CPU, XTTS: GPU, Whisper: CPU")

# --- Model Loading ---

# Load Whisper ASR Model
try:
    print("Loading Whisper ASR model for backend...")
    # Using a smaller model for ASR to save VRAM for LLM - keeping on CPU
    asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base.en", device=DEVICE_CPU)
    print("Whisper ASR model loaded on CPU.")
except Exception as e:
    print(f"Error loading Whisper ASR on CPU: {e}")
    asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base.en", device="cpu")

# Load Emotion Detection Model
try:
    print("Loading Emotion Detection model for backend...")
    # Running on CPU to save VRAM for LLM and XTTS
    emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device=DEVICE_CPU, return_all_scores=False)
    print("Emotion Detection model loaded on CPU.")
except Exception as e:
    print(f"Error loading Emotion Detection on CPU: {e}")
    emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device="cpu", return_all_scores=False)

# Load LLM Model (Mistral 7B Instruct)
llm_model = None
try:
    print(f"Loading LLM model from: {LLM_MODEL_PATH}")
    print(f"Model file exists: {os.path.exists(LLM_MODEL_PATH)}")
    
    # Reduced GPU layers for better compatibility
    llm_model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL_PATH,
        model_type=LLM_MODEL_TYPE,
        gpu_layers=20, # Reduced from 30 to 20 for better compatibility
        hf=True # Use Hugging Face style API for generation
    )
    print("✅ LLM model loaded successfully on GPU!")
except Exception as e:
    print(f"❌ Error loading LLM model: {str(e)}")
    print(f"Model path: {LLM_MODEL_PATH}")
    print(f"Model exists: {os.path.exists(LLM_MODEL_PATH)}")
    print("LLM will not be available. Check model path, type, and GPU layers.")
    llm_model = None # Ensure llm_model is None if loading fails

# Load XTTS Model
try:
    print("Loading XTTS v2 model...")
    # Set environment variable to accept license automatically
    import os
    os.environ["COQUI_TOS_AGREED"] = "1"
    
    # Fix for PyTorch 2.6 weights_only issue with TTS
    import torch
    
    # Create a monkeypatch to bypass weights_only restriction for TTS
    original_load = torch.load
    def patched_load(*args, **kwargs):
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = patched_load
    
    # Initialize XTTS v2 model with multilingual support
    tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())
    
    # Restore original torch.load
    torch.load = original_load
    
    print("XTTS v2 model loaded successfully.")
except Exception as e:
    print(f"Error loading XTTS model: {e}")
    print("XTTS will not be available. Falling back to dummy audio.")
    tts_model = None


# --- LLM Generation Function ---
def generate_llm_response_text(user_text, detected_emotion, chat_history):
    if llm_model is None:
        return "Sorry, the AI model is not loaded. Please check the backend logs."

    # Construct the prompt for the LLM
    # This prompt is crucial for guiding the LLM's behavior as an empathetic companion.
    # We'll use a simple chat format for Mistral Instruct.
    # The chat_history from the frontend is a list of {"user": "...", "ai": "..."} dicts.

    messages = [
        {"role": "system", "content": "You are Samantha, a warm, empathetic, and supportive AI companion. Your goal is to listen attentively, understand the user's emotions, and respond in a caring and helpful manner. Keep your responses concise and personal. Focus on emotional connection, not providing factual information or solving complex problems. If the user expresses a strong emotion, acknowledge it. Maintain continuity by referencing past conversation if relevant."}
    ]

    # Add previous chat history for RAG (simple context injection)
    for turn in chat_history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["ai"]})

    # Add the current user input with emotion context
    messages.append({"role": "user", "content": f"User's detected emotion: {detected_emotion}. User says: '{user_text}'"})

    # Format messages for Mistral Instruct
    # Mistral Instruct uses specific tokens for turns: <s>[INST] User message [/INST] Model response</s>
    # We'll manually format this for simplicity with ctransformers generate.
    prompt_parts = []
    for msg in messages:
        if msg["role"] == "system":
            prompt_parts.append(f"<s>[INST] <<SYS>>\n{msg['content']}\n<</SYS>>\n\n")
        elif msg["role"] == "user":
            prompt_parts.append(f"{msg['content']} [/INST]")
        elif msg["role"] == "assistant":
            prompt_parts.append(f" {msg['content']}</s>") # Note the space before content for model's natural start

    # The last part is the current user input, so it should end with [/INST]
    final_prompt = "".join(prompt_parts)
    if not final_prompt.endswith("[/INST]"): # Ensure it ends correctly for new model response
        final_prompt += " [/INST]"


    print(f"Sending prompt to LLM:\n{final_prompt}\n---")

    try:
        # Generate response using ctransformers
        # Use simpler parameter set to avoid compatibility issues
        ai_response = llm_model(
            final_prompt,
            max_new_tokens=100,
            temperature=0.7,
            stop=["</s>", "[INST]", "[/INST]"]
        )

        # Clean up response (remove any leftover prompt parts or unwanted tokens)
        # Mistral might sometimes repeat the instruction or add extra tokens
        ai_response = ai_response.split("</s>")[0].strip() # Remove end token if present
        ai_response = ai_response.replace("<<SYS>>", "").replace("<</SYS>>", "").strip()
        ai_response = ai_response.replace("[INST]", "").strip() # Remove any leftover instruction tags

        print(f"LLM Raw Response: {ai_response}")
        return ai_response

    except Exception as e:
        print(f"Error during LLM generation: {e}")
        return f"Sorry, I had trouble generating a response. ({e})"


# --- API Endpoints ---

@app.route('/transcribe', methods=['POST'])
def transcribe_audio_endpoint():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    audio_file = request.files['audio']
    audio_bytes = audio_file.read()

    # Use absolute path for temp file
    temp_audio_path = os.path.join(BASE_DIR, "temp_audio.wav")
    with open(temp_audio_path, "wb") as f:
        f.write(audio_bytes)

    try:
        transcript = asr_pipeline(temp_audio_path)["text"]
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return jsonify({"text": transcript})
    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        print(f"Error in transcription endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion_endpoint():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        emotion_result = emotion_pipeline(text)[0]
        emotion_label = emotion_result['label']
        return jsonify({"emotion": emotion_label})
    except Exception as e:
        print(f"Error in emotion detection endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_response', methods=['POST']) # New endpoint for LLM
def generate_response_endpoint():
    data = request.get_json()
    user_text = data.get('user_text', '')
    detected_emotion = data.get('detected_emotion', 'neutral')
    chat_history = data.get('chat_history', []) # Receive chat history from frontend

    if not user_text:
        return jsonify({"error": "No user text provided for LLM"}), 400

    ai_response = generate_llm_response_text(user_text, detected_emotion, chat_history)
    return jsonify({"response": ai_response})


@app.route('/synthesize_speech', methods=['POST'])
def synthesize_speech_endpoint():
    data = request.get_json()
    text = data.get('text', '')
    emotion = data.get('emotion', 'neutral')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if tts_model is None:
        # Fallback for when XTTS model is not loaded
        from pydub import AudioSegment
        from pydub.generators import Sine
        print("XTTS model not loaded, returning dummy audio.")
        sine_wave = Sine(440).to_audio_segment(duration=1000)
        audio_buffer = io.BytesIO()
        sine_wave.export(audio_buffer, format="wav")
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype="audio/wav")

    try:
        # --- XTTS Integration with Emotion ---
        print(f"Synthesizing speech with XTTS: '{text}' (emotion: {emotion})")
        
        # Create temporary file path for output (use absolute path)
        temp_audio_path = os.path.join(BASE_DIR, "temp_xtts_output.wav")
        
        # Map emotions to XTTS parameters for voice modulation
        emotion_configs = {
            'joy': {'speed': 1.1, 'language': 'en'},
            'sadness': {'speed': 0.8, 'language': 'en'},
            'anger': {'speed': 1.2, 'language': 'en'},
            'fear': {'speed': 0.9, 'language': 'en'},
            'surprise': {'speed': 1.0, 'language': 'en'},
            'neutral': {'speed': 1.0, 'language': 'en'}
        }
        
        # Get emotion-specific config
        config = emotion_configs.get(emotion.lower(), emotion_configs['neutral'])
        
        # Adjust text for emotional expression
        if emotion.lower() == 'joy':
            text = f"{text}!"  # Add excitement
        elif emotion.lower() == 'sadness':
            text = f"Oh... {text}"  # Add empathy
        elif emotion.lower() == 'anger':
            text = f"I understand you're upset. {text}"  # Add calming tone
        
        # Use XTTS to synthesize speech (try without speaker parameter first)
        try:
            tts_model.tts_to_file(
                text=text,
                file_path=temp_audio_path,
                language=config['language']
            )
        except Exception as speaker_error:
            # If that fails, try with different speaker configurations
            print(f"First attempt failed: {speaker_error}")
            try:
                # Try with speaker_idx for multi-speaker models
                tts_model.tts_to_file(
                    text=text,
                    file_path=temp_audio_path,
                    language=config['language'],
                    speaker_idx=0
                )
            except Exception as speaker_idx_error:
                print(f"Speaker idx attempt failed: {speaker_idx_error}")
                # Last resort - try with empty speaker_wav
                tts_model.tts_to_file(
                    text=text,
                    file_path=temp_audio_path,
                    language=config['language'],
                    speaker_wav=""
                )
        
        # Read the generated audio file
        with open(temp_audio_path, "rb") as f:
            audio_data = f.read()
        
        # Clean up temporary file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        # Create audio buffer for response
        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.seek(0)
        
        print("XTTS speech synthesis completed successfully.")
        return send_file(audio_buffer, mimetype="audio/wav")

    except Exception as e:
        print(f"Error in XTTS speech synthesis: {e}")
        # Fallback to dummy audio on error
        from pydub import AudioSegment
        from pydub.generators import Sine
        sine_wave = Sine(440).to_audio_segment(duration=1000)
        audio_buffer = io.BytesIO()
        sine_wave.export(audio_buffer, format="wav")
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype="audio/wav")

if __name__ == '__main__':
    print("Starting Flask backend. Ensure LLM model path is correct and XTTS is configured.")
    app.run(host='0.0.0.0', port=5000, debug=True)