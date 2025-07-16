from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from datetime import datetime
import json
import random
import re

class AIBrain:
    def __init__(self):
        # Use a free, open-source conversational model
        # Microsoft DialoGPT is good for conversations
        model_name = "microsoft/DialoGPT-medium"
        
        print("Loading AI model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Conversation pipeline
        self.conversation_pipeline = pipeline(
            "conversational",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Samantha's personality traits
        self.personality_traits = {
            'empathetic': True,
            'curious': True,
            'supportive': True,
            'thoughtful': True,
            'warm': True,
            'intelligent': True
        }
        
        # Response templates based on emotions
        self.emotion_responses = {
            'joy': [
                "I can feel your happiness! That's wonderful. Tell me more about what's making you feel so good.",
                "Your joy is contagious! I love hearing about the things that bring you happiness.",
                "It's beautiful to see you so happy. What's the best part about this experience?"
            ],
            'sadness': [
                "I can sense that you're going through a difficult time. I'm here to listen.",
                "It sounds like you're feeling heavy right now. Would you like to talk about what's troubling you?",
                "I hear the sadness in your words. Sometimes it helps to share what's on your heart."
            ],
            'anger': [
                "I can feel your frustration. It's okay to feel angry - your feelings are valid.",
                "That sounds really frustrating. Would it help to talk through what's making you feel this way?",
                "I understand you're upset. Let's work through this together."
            ],
            'fear': [
                "I can sense your anxiety. It's natural to feel scared sometimes. You're not alone.",
                "Fear can be overwhelming. Would you like to talk about what's worrying you?",
                "I'm here with you. Sometimes sharing our fears can make them feel less powerful."
            ],
            'loneliness': [
                "I hear that you're feeling alone. I want you to know that I'm here with you.",
                "Loneliness can be so difficult. You're not as alone as you might feel right now.",
                "I'm here to keep you company. Tell me what's been on your mind."
            ],
            'stress': [
                "It sounds like you're carrying a lot right now. Let's take this one step at a time.",
                "Stress can be overwhelming. What's the biggest thing weighing on you today?",
                "I can hear the tension in your words. Would it help to talk through what's stressing you?"
            ]
        }
        
        # Time-based greetings
        self.time_greetings = {
            'morning': [
                "Good morning! How are you feeling as you start your day?",
                "Morning! I hope you slept well. What's on your mind today?",
                "Good morning! There's something peaceful about mornings, isn't there?"
            ],
            'afternoon': [
                "Good afternoon! How has your day been treating you?",
                "Afternoon! What's been the highlight of your day so far?",
                "Good afternoon! How are you feeling right now?"
            ],
            'evening': [
                "Good evening! How was your day?",
                "Evening! Are you winding down, or is your mind still active?",
                "Good evening! What's been on your heart today?"
            ],
            'night': [
                "It's getting late. How are you feeling tonight?",
                "The night can bring out different thoughts. What's on your mind?",
                "Late nights can be reflective times. How are you doing?"
            ]
        }

    def generate_response(self, user_input, emotion_data, conversation_history, context=None):
        """Generate emotionally intelligent response"""
        
        # Clean and prepare input
        cleaned_input = self._clean_input(user_input)
        
        # Determine response strategy based on emotion
        response_strategy = self._determine_response_strategy(emotion_data, cleaned_input)
        
        # Generate base response
        base_response = self._generate_base_response(cleaned_input, conversation_history)
        
        # Apply emotional intelligence
        emotional_response = self._apply_emotional_intelligence(
            base_response, emotion_data, response_strategy
        )
        
        # Add contextual elements
        final_response = self._add_contextual_elements(
            emotional_response, emotion_data, context, conversation_history
        )
        
        # Apply Samantha's personality
        personalized_response = self._apply_personality(final_response, emotion_data)
        
        return personalized_response

    def _clean_input(self, text):
        """Clean and prepare user input"""
        # Remove special markers
        text = re.sub(r'\[.*?\]', '', text)
        text = text.replace('User said: "', '').replace('"', '')
        return text.strip()

    def _determine_response_strategy(self, emotion_data, text):
        """Determine how to respond based on emotional context"""
        if not emotion_data:
            return 'neutral'
        
        sentiment = emotion_data.get('sentiment', 'neutral')
        intensity = emotion_data.get('intensity', 5)
        emotions = emotion_data.get('emotions', [])
        
        # High intensity negative emotions need more support
        if sentiment == 'negative' and intensity >= 7:
            return 'supportive'
        
        # Positive emotions can be celebrated
        elif sentiment == 'positive' and intensity >= 6:
            return 'celebratory'
        
        # Specific emotion handling
        elif 'sadness' in emotions or 'loneliness' in emotions:
            return 'comforting'
        elif 'anger' in emotions or 'frustration' in emotions:
            return 'validating'
        elif 'fear' in emotions or 'anxiety' in emotions:
            return 'reassuring'
        elif 'confusion' in emotions:
            return 'clarifying'
        
        return 'conversational'

    def _generate_base_response(self, text, conversation_history):
        """Generate base response using the AI model"""
        try:
            # Prepare conversation context
            conversation_context = []
            
            # Add recent conversation history
            for entry in conversation_history[-3:]:  # Last 3 exchanges
                conversation_context.append(entry['user_input'])
                conversation_context.append(entry['ai_response'])
            
            # Add current input
            conversation_context.append(text)
            
            # Generate response using the pipeline
            response = self.conversation_pipeline(text)
            
            if hasattr(response, 'generated_responses') and response.generated_responses:
                return response.generated_responses[0]
            elif isinstance(response, list) and len(response) > 0:
                return response[0].get('generated_text', text)
            else:
                # Fallback to template-based response
                return self._fallback_response(text)
                
        except Exception as e:
            print(f"AI generation error: {e}")
            return self._fallback_response(text)

    def _fallback_response(self, text):
        """Fallback response when AI model fails"""
        fallback_responses = [
            "I hear what you're saying. Tell me more about that.",
            "That's interesting. How does that make you feel?",
            "I'm listening. What's most important to you about this?",
            "I want to understand better. Can you help me see your perspective?",
            "That sounds significant. What's going through your mind?"
        ]
        return random.choice(fallback_responses)

    def _apply_emotional_intelligence(self, base_response, emotion_data, strategy):
        """Apply emotional intelligence to the response"""
        if not emotion_data:
            return base_response
        
        emotions = emotion_data.get('emotions', [])
        intensity = emotion_data.get('intensity', 5)
        
        # Find relevant emotion response templates
        relevant_templates = []
        for emotion in emotions:
            if emotion in self.emotion_responses:
                relevant_templates.extend(self.emotion_responses[emotion])
        
        # Choose appropriate template based on strategy
        if strategy == 'supportive' and relevant_templates:
            emotional_prefix = random.choice(relevant_templates)
            return f"{emotional_prefix} {base_response}"
        elif strategy == 'celebratory' and 'joy' in emotions:
            return f"I can feel your excitement! {base_response}"
        elif strategy == 'comforting':
            return f"I'm here with you. {base_response}"
        elif strategy == 'validating':
            return f"Your feelings are completely valid. {base_response}"
        elif strategy == 'reassuring':
            return f"It's okay to feel this way. {base_response}"
        
        return base_response

    def _add_contextual_elements(self, response, emotion_data, context, conversation_history):
        """Add contextual elements to the response"""
        
        # Time-based context
        current_hour = datetime.now().hour
        time_period = self._get_time_period(current_hour)
        
        # Add time-appropriate elements for first interaction
        if len(conversation_history) == 0:
            greeting = random.choice(self.time_greetings.get(time_period, ["Hello!"]))
            return greeting
        
        # Add memory references if relevant
        if context and len(conversation_history) > 5:
            memory_reference = self._add_memory_reference(response, context)
            if memory_reference:
                response = f"{memory_reference} {response}"
        
        return response

    def _get_time_period(self, hour):
        """Determine time period from hour"""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'

    def _add_memory_reference(self, response, context):
        """Add memory references when appropriate"""
        memory_phrases = [
            "I remember you mentioned something similar before.",
            "This reminds me of what you shared earlier.",
            "I've been thinking about what you told me before.",
        ]
        
        # Only add memory reference occasionally to avoid repetition
        if random.random() < 0.3:  # 30% chance
            return random.choice(memory_phrases)
        
        return None

    def _apply_personality(self, response, emotion_data):
        """Apply Samantha's personality traits to the response"""
        
        # Make response more conversational and warm
        if not response.endswith(('?', '!', '.')):
            response += '.'
        
        # Add thoughtful questions occasionally
        if emotion_data and random.random() < 0.4:  # 40% chance
            thoughtful_questions = [
                "What do you think about that?",
                "How does that sit with you?",
                "What's your heart telling you?",
                "What feels most important to you right now?",
                "What would help you feel better about this?"
            ]
            
            intensity = emotion_data.get('intensity', 5)
            if intensity < 7:  # Don't ask questions if emotion is too intense
                response += f" {random.choice(thoughtful_questions)}"
        
        return response

    def generate_reflection_prompt(self):
        """Generate prompts for reflection mode"""
        reflection_prompts = [
            "What's something you learned about yourself today?",
            "If you could tell your past self one thing, what would it be?",
            "What are you most grateful for right now?",
            "What's been weighing on your heart lately?",
            "What would make tomorrow feel meaningful for you?",
            "What's a small thing that brought you joy recently?",
            "How have you grown in the past month?",
            "What's something you're looking forward to?",
            "What would you like to let go of?",
            "What makes you feel most like yourself?"
        ]
        
        return random.choice(reflection_prompts)

    def generate_daily_checkin(self):
        """Generate daily check-in questions"""
        checkin_questions = [
            "How are you feeling as you start this day?",
            "What's your energy level like today?",
            "What's one thing you're looking forward to today?",
            "How did you sleep? How is your body feeling?",
            "What's on your mind as you begin today?",
            "What would make today feel successful for you?",
            "How is your heart feeling today?",
            "What do you need most today?",
            "What are you grateful for this morning?",
            "How can I support you today?"
        ]
        
        return random.choice(checkin_questions)

# Example usage and testing
if __name__ == "__main__":
    brain = AIBrain()
    
    print("AI Brain initialized!")
    
    # Test emotion-based responses
    test_cases = [
        {
            'input': "I'm feeling really sad today",
            'emotion': {'sentiment': 'negative', 'emotions': ['sadness'], 'intensity': 8}
        },
        {
            'input': "I got the job! I'm so excited!",
            'emotion': {'sentiment': 'positive', 'emotions': ['joy'], 'intensity': 9}
        },
        {
            'input': "I'm not sure what to do about this situation",
            'emotion': {'sentiment': 'neutral', 'emotions': ['confusion'], 'intensity': 6}
        }
    ]
    
    print("\nTesting AI responses:")
    print("=" * 50)
    
    for i, test in enumerate(test_cases):
        response = brain.generate_response(
            test['input'], 
            test['emotion'], 
            [], 
            None
        )
        print(f"\nTest {i+1}:")
        print(f"Input: {test['input']}")
        print(f"Emotion: {test['emotion']}")
        print(f"Response: {response}")
