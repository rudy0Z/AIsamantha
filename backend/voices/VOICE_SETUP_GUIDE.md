# 🎭 Voice Cloning Setup Guide

## 📁 Place Your Voice File Here:
Save your voice reference as: `samantha_neutral.wav` in this directory

## 🎙️ Recording Requirements:
- **Format**: WAV file
- **Duration**: 3-10 seconds
- **Quality**: Clear, no background noise
- **Content**: Natural speech (can be anything)

## 📝 Suggested Recording Scripts:
1. "Hello, I'm Samantha. I'm here to help you with whatever you need."
2. "Hi there! I'm your AI assistant, ready to chat and help out."
3. "Welcome! I'm excited to be your personal AI companion."

## 🔧 Recording Options:
1. **Windows Voice Recorder** (Start Menu → Voice Recorder)
2. **Online**: voicerecorder.io or similar
3. **Phone**: Record → Convert to WAV
4. **Audacity** (free audio editor)

## ⚡ After Adding Voice File:
1. Restart the backend server
2. The system will automatically detect and use XTTS
3. Your bot will now speak with the cloned voice!

## 🎯 Current Status:
- Directory ready: ✅
- Voice file: ❌ (Place `samantha_neutral.wav` here)
- Fallback: Tacotron2 (working perfectly)
