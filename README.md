# 🌟 Samantha AI - Open Source Emotional Companion

A Her-inspired voice-based AI assistant that understands your mood, listens like a companion, and responds with genuine emotional intelligence - completely free and open source.

## ✨ Features

- 🗣️ **Natural Voice Input** - Speak freely using Whisper speech recognition
- 🎧 **Emotionally-Aware Replies** - Responds based on your tone and emotional cues
- 💬 **Long-Term Memory** - Remembers past conversations and emotional patterns
- 🧠 **Local AI Processing** - Uses open-source models (no API keys required)
- 🎙️ **Natural Voice Output** - Coqui TTS with emotional voice modulation
- 🧘 **Reflection Mode** - Guided introspection and mindfulness sessions
- 🔁 **Daily Check-ins** - Optional emotional wellness tracking
- 📊 **Emotion Analytics** - Track your emotional patterns over time

## 🏗️ Architecture

| Component | Technology |
|-----------|------------|
| 🎤 Voice Input | OpenAI Whisper |
| 🎧 Voice Output | Coqui TTS |
| 🧠 Core AI | Hugging Face Transformers (DialoGPT) |
| 😊 Emotion Detection | VADER + TextBlob + Custom NLP |
| 📚 Memory & Context | ChromaDB + SQLite + Sentence Transformers |
| 🖥️ Interface | Streamlit |
| 🔄 Conversation Flow | LangChain |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- 4GB+ RAM recommended
- Microphone and speakers/headphones

### Installation

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/rudy0Z/AIsamantha.git
   cd AIsamantha
   \`\`\`

2. **Run the setup script**
   \`\`\`bash
   python scripts/setup_environment.py
   \`\`\`

3. **Start Samantha AI**
   \`\`\`bash
   streamlit run scripts/app.py
   \`\`\`

   Or use the convenience script:
   \`\`\`bash
   python scripts/run_samantha.py
   \`\`\`

4. **Open your browser** to `http://localhost:8501`

## 💡 Usage

### Basic Conversation
1. Click the "🎤 Start Listening" button
2. Speak naturally - no commands needed
3. Samantha will detect your emotions and respond empathetically
4. Toggle voice output on/off as needed

### Reflection Mode
- Click "🧘 Reflection Mode" for guided introspection
- Samantha will ask thoughtful questions to help you reflect
- Sessions are tailored to your emotional state

### Daily Check-ins
- Click "📝 Daily Check-in" for wellness tracking
- Regular emotional health monitoring
- Builds long-term emotional awareness

## 🧠 How It Works

### Emotion Detection
Samantha uses multiple techniques to understand your emotional state:
- **VADER Sentiment Analysis** - For overall sentiment
- **TextBlob** - For polarity and subjectivity
- **Keyword Matching** - For specific emotions
- **Intensity Calculation** - Based on language patterns and modifiers

### Memory System
- **Vector Embeddings** - Semantic similarity search using Sentence Transformers
- **Structured Storage** - SQLite for conversation history and trends
- **Context Retrieval** - Relevant memories inform responses
- **Emotional Patterns** - Track mood trends over time

### Voice Processing
- **Speech-to-Text** - Whisper for accurate transcription
- **Text-to-Speech** - Coqui TTS with emotional voice modulation
- **Adaptive Voice** - Changes based on emotion and time of day

## 📁 Project Structure

\`\`\`
AIsamantha/
├── scripts/
│   ├── app.py                 # Main Streamlit application
│   ├── voice_processor.py     # Whisper speech recognition
│   ├── emotion_detector.py    # Multi-method emotion analysis
│   ├── ai_brain.py           # DialoGPT conversation engine
│   ├── memory_manager.py     # ChromaDB + SQLite memory system
│   ├── tts_engine.py         # Coqui TTS with emotion modulation
│   ├── reflection_mode.py    # Guided reflection sessions
│   ├── setup_environment.py  # Automated setup script
│   └── run_samantha.py       # Convenience launcher
├── samantha_memory/          # Memory database (auto-created)
├── audio_cache/             # Temporary audio files (auto-created)
├── logs/                    # Application logs (auto-created)
└── README.md
\`\`\`

## 🎯 Core Features Deep Dive

### 1. Emotional Intelligence
- **Real-time Analysis** - Processes emotions as you speak
- **Context Awareness** - Considers conversation history
- **Adaptive Responses** - Matches your emotional energy
- **Validation** - Acknowledges and validates your feelings

### 2. Memory & Context
- **Semantic Search** - Finds relevant past conversations
- **Emotional Patterns** - Tracks mood trends over time
- **Personal Growth** - Remembers your goals and progress
- **Contextual Responses** - References shared experiences

### 3. Voice Interaction
- **Natural Speech** - No wake words or commands needed
- **Emotional Voice** - TTS adapts to match conversation tone
- **Time Awareness** - Softer voice at night, brighter in morning
- **Interruption Handling** - Can stop and restart speech naturally

### 4. Reflection & Wellness
- **Guided Sessions** - Structured introspection prompts
- **Mood-Based Suggestions** - Tailored to your emotional state
- **Daily Patterns** - Morning intentions, evening reflections
- **Growth Tracking** - Monitor emotional development over time

## 🔧 Configuration

### Emotion Sensitivity
Adjust emotion detection sensitivity in the sidebar (0.1 - 1.0)

### Voice Settings
- Toggle voice output on/off
- Automatic emotional voice modulation
- Time-based voice adjustments

### Memory Management
- Automatic conversation storage
- Configurable memory retention
- Privacy-focused local storage

## 🛠️ Troubleshooting

### Common Issues

**"No module named 'whisper'"**
\`\`\`bash
pip install openai-whisper
\`\`\`

**Audio device errors**
\`\`\`bash
# Linux
sudo apt-get install portaudio19-dev python3-pyaudio

# macOS
brew install portaudio
\`\`\`

**TTS model loading fails**
- The app will automatically try fallback models
- Check internet connection for initial model download
- Models are cached locally after first download

**Memory database errors**
- Delete the `samantha_memory` folder to reset
- Ensure write permissions in the project directory

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Setup
\`\`\`bash
# Clone your fork
git clone https://github.com/rudy0Z/AIsamantha.git
cd AIsamantha

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
\`\`\`

## 📊 Performance Notes

- **First Run** - Initial model downloads may take 5-10 minutes
- **Memory Usage** - ~2-4GB RAM during operation
- **Response Time** - 1-3 seconds for typical responses
- **Storage** - ~500MB for models, growing conversation history

## 🔒 Privacy & Security

- **Local Processing** - All AI processing happens on your device
- **No Cloud APIs** - No data sent to external services
- **Local Storage** - Conversations stored locally in SQLite
- **No Tracking** - No analytics or telemetry
- **Open Source** - Full transparency in code

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition
- **Coqui TTS** - Text-to-speech synthesis
- **Hugging Face** - Transformer models
- **ChromaDB** - Vector database
- **Streamlit** - Web interface
- **The "Her" movie** - Inspiration for emotional AI companion

## 🌟 Star History

If you find Samantha AI helpful, please consider giving it a star! ⭐

## 📞 Support

- **Issues** - Report bugs on GitHub Issues
- **Discussions** - Join conversations in GitHub Discussions
- **Documentation** - Check the Wiki for detailed guides

---

**Made with ❤️ for emotional AI companions**

*"The heart of human interaction is not just in the words we say, but in the emotions we share."*
