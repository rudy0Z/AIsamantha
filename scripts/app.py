import streamlit as st
import asyncio
import threading
import time
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Import our custom modules
from voice_processor import VoiceProcessor
from emotion_detector import EmotionDetector
from ai_brain import AIBrain
from memory_manager import MemoryManager
from tts_engine import TTSEngine
from reflection_mode import ReflectionMode

# Configure Streamlit page
st.set_page_config(
    page_title="Samantha AI - Your Emotional Companion",
    page_icon="💝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Her-inspired design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ff6b6b;
        font-size: 3rem;
        font-weight: 300;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .emotion-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .memory-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff6b6b;
        margin: 0.5rem 0;
    }
    .voice-status {
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .listening {
        background: linear-gradient(45deg, #ff6b6b, #ffa500);
        color: white;
        animation: pulse 2s infinite;
    }
    .speaking {
        background: linear-gradient(45deg, #4ecdc4, #44a08d);
        color: white;
    }
    .idle {
        background: #f0f0f0;
        color: #666;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

class SamanthaAI:
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.emotion_detector = EmotionDetector()
        self.ai_brain = AIBrain()
        self.memory_manager = MemoryManager()
        self.tts_engine = TTSEngine()
        self.reflection_mode = ReflectionMode()
        
        # Initialize session state
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'current_emotion' not in st.session_state:
            st.session_state.current_emotion = None
        if 'voice_status' not in st.session_state:
            st.session_state.voice_status = 'idle'
        if 'daily_checkin_done' not in st.session_state:
            st.session_state.daily_checkin_done = False
        if 'reflection_active' not in st.session_state:
            st.session_state.reflection_active = False

    def run(self):
        # Header
        st.markdown('<h1 class="main-header">💝 Samantha AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Your emotionally intelligent AI companion</p>', unsafe_allow_html=True)
        
        # Main layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_main_interface()
        
        with col2:
            self.render_sidebar()

    def render_main_interface(self):
        # Voice status indicator
        status_class = st.session_state.voice_status
        status_text = {
            'idle': '🎤 Ready to listen',
            'listening': '👂 Listening...',
            'processing': '🧠 Thinking...',
            'speaking': '🗣️ Speaking...'
        }
        
        st.markdown(f'''
        <div class="voice-status {status_class}">
            <h3>{status_text.get(status_class, "Ready")}</h3>
        </div>
        ''', unsafe_allow_html=True)
        
        # Voice controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🎤 Start Listening", key="listen_btn"):
                self.start_listening()
        
        with col2:
            if st.button("⏹️ Stop", key="stop_btn"):
                self.stop_listening()
        
        with col3:
            if st.button("🧘 Reflection Mode", key="reflection_btn"):
                st.session_state.reflection_active = True
                self.start_reflection()
        
        with col4:
            if st.button("📝 Daily Check-in", key="checkin_btn"):
                self.daily_checkin()
        
        # Text input as alternative
        st.markdown("---")
        text_input = st.text_area("Or type your message here:", height=100)
        if st.button("Send Message") and text_input:
            self.process_text_input(text_input)
        
        # Conversation display
        self.render_conversation()

    def render_sidebar(self):
        st.sidebar.header("🧠 Emotional State")
        
        # Current emotion display
        if st.session_state.current_emotion:
            emotion = st.session_state.current_emotion
            st.sidebar.markdown(f'''
            <div class="emotion-card">
                <h4>Current Mood</h4>
                <p><strong>Sentiment:</strong> {emotion['sentiment']}</p>
                <p><strong>Emotions:</strong> {', '.join(emotion['emotions'])}</p>
                <p><strong>Intensity:</strong> {emotion['intensity']}/10</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.sidebar.info("Start talking to detect emotions...")
        
        # Memory section
        st.sidebar.header("💭 Memory Bank")
        memories = self.memory_manager.get_recent_memories(5)
        
        for memory in memories:
            st.sidebar.markdown(f'''
            <div class="memory-card">
                <small>{memory['timestamp']}</small>
                <p><strong>You:</strong> {memory['user_input'][:50]}...</p>
                <p><strong>Me:</strong> {memory['ai_response'][:50]}...</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Settings
        st.sidebar.header("⚙️ Settings")
        voice_enabled = st.sidebar.checkbox("Voice Output", value=True)
        emotion_sensitivity = st.sidebar.slider("Emotion Sensitivity", 0.1, 1.0, 0.7)
        
        # Stats
        st.sidebar.header("📊 Stats")
        total_conversations = len(st.session_state.conversation_history)
        st.sidebar.metric("Conversations Today", total_conversations)
        
        if memories:
            avg_emotion = sum([m.get('emotion', {}).get('intensity', 5) for m in memories]) / len(memories)
            st.sidebar.metric("Average Mood", f"{avg_emotion:.1f}/10")

    def start_listening(self):
        st.session_state.voice_status = 'listening'
        
        # Simulate voice processing (in real implementation, this would use actual audio)
        with st.spinner("Listening for your voice..."):
            time.sleep(2)  # Simulate listening time
            
            # For demo purposes, we'll use a placeholder
            st.info("Voice input detected! (In production, this would process actual audio)")
            
            # Simulate transcription
            sample_inputs = [
                "I'm feeling really stressed about work today",
                "I had such a wonderful day with my family",
                "I'm not sure what I want to do with my life",
                "I feel lonely sometimes, especially at night",
                "I'm excited about my new project"
            ]
            
            import random
            transcribed_text = random.choice(sample_inputs)
            st.success(f"Heard: '{transcribed_text}'")
            
            self.process_text_input(transcribed_text)

    def stop_listening(self):
        st.session_state.voice_status = 'idle'
        st.info("Stopped listening")

    def process_text_input(self, text):
        st.session_state.voice_status = 'processing'
        
        # Detect emotion
        emotion = self.emotion_detector.analyze_emotion(text)
        st.session_state.current_emotion = emotion
        
        # Get AI response with emotional context
        response = self.ai_brain.generate_response(
            text, 
            emotion, 
            st.session_state.conversation_history,
            self.memory_manager.get_relevant_context(text)
        )
        
        # Add to conversation history
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': text,
            'ai_response': response,
            'emotion': emotion
        }
        
        st.session_state.conversation_history.append(conversation_entry)
        
        # Save to memory
        self.memory_manager.save_memory(conversation_entry)
        
        # Simulate TTS (in production, this would generate actual audio)
        st.session_state.voice_status = 'speaking'
        st.success(f"Samantha: {response}")
        
        # Reset status after "speaking"
        time.sleep(1)
        st.session_state.voice_status = 'idle'
        
        st.rerun()

    def start_reflection(self):
        reflection_prompt = self.reflection_mode.get_reflection_prompt()
        st.info(f"Reflection Mode: {reflection_prompt}")
        
        # Add reflection prompt to conversation
        self.process_text_input(f"[REFLECTION MODE] {reflection_prompt}")

    def daily_checkin(self):
        if not st.session_state.daily_checkin_done:
            checkin_questions = [
                "How are you feeling today?",
                "What's been on your mind lately?",
                "Tell me about something that made you smile today",
                "How would you rate your energy level today?",
                "What are you grateful for right now?"
            ]
            
            import random
            question = random.choice(checkin_questions)
            st.info(f"Daily Check-in: {question}")
            
            self.process_text_input(f"[DAILY CHECKIN] {question}")
            st.session_state.daily_checkin_done = True
        else:
            st.info("You've already completed your daily check-in today!")

    def render_conversation(self):
        st.markdown("### 💬 Conversation")
        
        if not st.session_state.conversation_history:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #666;">
                <h4>👋 Hello! I'm Samantha</h4>
                <p>I'm here to listen and understand. Start by clicking the microphone or typing a message.</p>
                <p>I can detect your emotions and respond with empathy, just like a close friend would.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for entry in st.session_state.conversation_history[-10:]:  # Show last 10 messages
                # User message
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; margin-left: 2rem;">
                    <strong>You:</strong> {entry['user_input']}
                    <br><small style="color: #666;">{entry['timestamp'][:19]}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # AI response
                st.markdown(f"""
                <div style="background: #fce4ec; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; margin-right: 2rem;">
                    <strong>Samantha:</strong> {entry['ai_response']}
                    <br><small style="color: #666;">Emotion detected: {entry['emotion']['sentiment']} ({entry['emotion']['intensity']}/10)</small>
                </div>
                """, unsafe_allow_html=True)

# Initialize and run the app
if __name__ == "__main__":
    app = SamanthaAI()
    app.run()
