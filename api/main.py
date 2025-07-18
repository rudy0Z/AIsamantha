import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# --- Setup and Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from a .env file
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Configure the Google Generative AI client
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")
    genai.configure(api_key=api_key)
except Exception as e:
    logging.error(f"Failed to configure Generative AI: {e}")
    # We allow the app to start, but API calls will fail.
    # This helps in debugging server setup issues without a key.

# --- Helper Functions ---
def load_prompt(filename: str) -> str:
    """Loads a prompt from a file in the 'prompts' directory."""
    try:
        # Construct path relative to the script's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(base_dir, 'prompts', filename)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Prompt file not found: {filename}")
        return "" # Return empty string if prompt is missing

def format_conversation_history(history: list) -> str:
    """Formats the conversation history for the prompt."""
    if not history:
        return "No conversation history yet."
    
    formatted_lines = []
    for message in history:
        sender = "AI" if message.get('sender') == 'ai' else "User"
        formatted_lines.append(f"{sender}: {message.get('text', '')}")
        
    return "\n".join(formatted_lines)

# --- Main API Endpoint ---
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles chat requests, interacts with the Gemini API, and returns a response."""
    if not genai.get_model('gemini-2.5-flash'):
        return jsonify({"error": "Generative AI client not configured. Is the API key valid?"}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON in request"}), 400

        user_message = data.get('message')
        history = data.get('history', [])
        reflection_answer_context = data.get('reflectionAnswer')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Decide whether to ask a reflection question or give a standard response.
        # We ask a reflection question every 3 user messages, but not if the user
        # is currently answering a reflection question.
        user_turns = len([msg for msg in history if msg.get('sender') == 'user'])
        should_reflect = (user_turns > 0 and user_turns % 3 == 0 and not reflection_answer_context)

        model = genai.GenerativeModel('gemini-2.5-flash')

        if should_reflect:
            # --- Generate a Reflection Question ---
            logging.info("Generating a reflection question.")
            conversation_context = format_conversation_history(history + [{'sender': 'user', 'text': user_message}])
            reflection_prompt_template = load_prompt('reflection_prompt.txt')
            prompt = reflection_prompt_template.format(conversation_context=conversation_context)
            
            response = model.generate_content(prompt)
            
            # The reflection response is just the question text
            return jsonify({
                "response": response.text.strip(),
                "emotion": "curious",
                "type": "reflection"
            })

        else:
            # --- Generate a Standard Empathetic Response ---
            logging.info("Generating a standard response.")
            conversation_context = format_conversation_history(history)
            persona_prompt_template = load_prompt('compassionate_persona.txt')
            
            prompt = (
                f"{persona_prompt_template}\n\n"
                f"CONVERSATION HISTORY:\n---\n{conversation_context}\n---\n\n"
                f"USER'S LATEST MESSAGE: {user_message}"
            )

            response = model.generate_content(prompt)
            
            # The AI is instructed to return a JSON object. We need to parse it.
            try:
                # Clean up the response text before parsing
                cleaned_text = response.text.strip().replace('```json', '').replace('```', '')
                ai_response_data = json.loads(cleaned_text)
                
                return jsonify({
                    "response": ai_response_data.get("response", "I'm not sure how to respond to that."),
                    "emotion": ai_response_data.get("emotion", "neutral"),
                    "type": "standard"
                })

            except (json.JSONDecodeError, AttributeError) as e:
                logging.error(f"Failed to parse AI response JSON: {e}. Raw response: {response.text}")
                # Fallback if the AI doesn't return valid JSON
                return jsonify({
                    "response": response.text,
                    "emotion": "neutral",
                    "type": "standard"
                })

    except Exception as e:
        logging.error(f"An unexpected error occurred in /api/chat: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

# --- Main Execution Block ---
if __name__ == '__main__':
    # Use Gunicorn or another production server in a real deployment
    app.run(host='0.0.0.0', port=5000, debug=True)