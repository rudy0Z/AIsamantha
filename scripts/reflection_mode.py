import random
from datetime import datetime, timedelta
import json

class ReflectionMode:
    def __init__(self):
        # Different types of reflection prompts
        self.reflection_categories = {
            'self_discovery': [
                "What's something new you learned about yourself recently?",
                "If you could describe yourself in three words today, what would they be?",
                "What's a strength you have that you sometimes forget about?",
                "What's something you're proud of that others might not know?",
                "How have you grown in the past month?",
                "What's a belief you hold that has changed over time?",
                "What makes you feel most like yourself?",
                "What's something you do that brings you genuine joy?"
            ],
            'gratitude': [
                "What are three things you're grateful for right now?",
                "Who is someone who made your day better recently?",
                "What's a small moment from today that you want to remember?",
                "What's something in your life that you might take for granted?",
                "What's a challenge you faced that you're now thankful for?",
                "What's something beautiful you noticed today?",
                "What's a skill or ability you have that you appreciate?",
                "What's a memory that always makes you smile?"
            ],
            'emotional_processing': [
                "What emotion have you been carrying with you lately?",
                "What's something that's been weighing on your heart?",
                "How are you really feeling, beyond the surface?",
                "What would you like to let go of?",
                "What's something you need to forgive yourself for?",
                "What fear has been holding you back?",
                "What's bringing you peace right now?",
                "What do you need more of in your life?"
            ],
            'future_focused': [
                "What's something you're looking forward to?",
                "What would make tomorrow feel meaningful for you?",
                "What's a goal that excites you?",
                "What kind of person do you want to become?",
                "What's one small step you could take toward something important?",
                "What would you do if you knew you couldn't fail?",
                "What legacy do you want to leave?",
                "What's a dream you've been putting off?"
            ],
            'relationships': [
                "Who in your life do you feel most connected to right now?",
                "What's something you'd like to tell someone but haven't?",
                "How do you show love to the people you care about?",
                "What's a relationship in your life that you're grateful for?",
                "What's something you've learned from someone close to you?",
                "How do you want to be remembered by those you love?",
                "What's a way you could be more present with others?",
                "Who has influenced you the most and how?"
            ],
            'mindfulness': [
                "What are you noticing about this moment right now?",
                "How does your body feel in this moment?",
                "What sounds do you hear around you?",
                "What's one thing you can see that you find beautiful?",
                "How is your breathing right now?",
                "What's something you can touch that brings you comfort?",
                "What's a scent that brings you good memories?",
                "What's happening in your mind right now without judgment?"
            ],
            'values_and_meaning': [
                "What matters most to you in life?",
                "What's a value you hold that guides your decisions?",
                "What gives your life meaning?",
                "What's something you stand for?",
                "What's a cause you care deeply about?",
                "What's your definition of a life well-lived?",
                "What's something you believe everyone should know?",
                "What's a principle you try to live by?"
            ]
        }
        
        # Guided reflection sessions
        self.guided_sessions = {
            'morning_intention': [
                "How do you want to feel today?",
                "What's one intention you want to set for today?",
                "What would make today feel successful for you?",
                "What energy do you want to bring to your day?"
            ],
            'evening_reflection': [
                "What went well today?",
                "What challenged you today and how did you handle it?",
                "What are you grateful for from today?",
                "What would you do differently if you could?"
            ],
            'weekly_review': [
                "What was the highlight of your week?",
                "What did you learn about yourself this week?",
                "What patterns do you notice in your week?",
                "What do you want to focus on next week?"
            ],
            'stress_processing': [
                "What's causing you the most stress right now?",
                "What's within your control in this situation?",
                "What would you tell a friend in your situation?",
                "What's one small thing you can do to feel better?"
            ],
            'decision_making': [
                "What decision are you facing right now?",
                "What are your options as you see them?",
                "What does your intuition tell you?",
                "What would you choose if there were no wrong answers?"
            ]
        }
        
        # Reflection techniques
        self.techniques = {
            'stream_of_consciousness': "For the next few minutes, just say whatever comes to mind without filtering or judging. Let your thoughts flow freely.",
            'body_scan': "Let's do a quick body scan. Starting from your head, notice how each part of your body feels right now.",
            'breathing_space': "Let's take three deep breaths together. With each breath, notice what you're experiencing right now.",
            'loving_kindness': "Think of someone you care about. What would you wish for them? Now, can you extend that same kindness to yourself?",
            'future_self': "Imagine yourself one year from now, looking back on today. What would that future self want to tell you?",
            'gratitude_spiral': "Let's start with one thing you're grateful for, and see where that leads us..."
        }

    def get_reflection_prompt(self, category=None, mood=None):
        """Get a reflection prompt based on category or mood"""
        
        # If no category specified, choose based on mood or randomly
        if not category:
            if mood:
                category = self._suggest_category_for_mood(mood)
            else:
                category = random.choice(list(self.reflection_categories.keys()))
        
        # Get prompt from selected category
        if category in self.reflection_categories:
            return random.choice(self.reflection_categories[category])
        else:
            return random.choice(self.reflection_categories['self_discovery'])

    def get_guided_session(self, session_type=None):
        """Get a guided reflection session"""
        
        if not session_type:
            # Choose based on time of day
            hour = datetime.now().hour
            if 5 <= hour < 12:
                session_type = 'morning_intention'
            elif 18 <= hour < 23:
                session_type = 'evening_reflection'
            else:
                session_type = random.choice(list(self.guided_sessions.keys()))
        
        if session_type in self.guided_sessions:
            return {
                'type': session_type,
                'prompts': self.guided_sessions[session_type],
                'description': self._get_session_description(session_type)
            }
        
        return None

    def get_reflection_technique(self, technique_name=None):
        """Get a specific reflection technique"""
        
        if not technique_name:
            technique_name = random.choice(list(self.techniques.keys()))
        
        if technique_name in self.techniques:
            return {
                'name': technique_name,
                'instruction': self.techniques[technique_name]
            }
        
        return None

    def _suggest_category_for_mood(self, mood_data):
        """Suggest reflection category based on detected mood"""
        
        if not mood_data:
            return 'self_discovery'
        
        sentiment = mood_data.get('sentiment', 'neutral')
        emotions = mood_data.get('emotions', [])
        intensity = mood_data.get('intensity', 5)
        
        # High intensity negative emotions
        if sentiment == 'negative' and intensity >= 7:
            if 'sadness' in emotions or 'loneliness' in emotions:
                return 'emotional_processing'
            elif 'stress' in emotions or 'anger' in emotions:
                return 'stress_processing'
            else:
                return 'emotional_processing'
        
        # Positive emotions
        elif sentiment == 'positive':
            if intensity >= 7:
                return 'gratitude'
            else:
                return 'future_focused'
        
        # Neutral or mixed emotions
        elif 'confusion' in emotions:
            return 'decision_making'
        elif intensity <= 4:  # Low energy
            return 'mindfulness'
        else:
            return 'self_discovery'

    def _get_session_description(self, session_type):
        """Get description for guided session types"""
        descriptions = {
            'morning_intention': "A gentle way to start your day with purpose and clarity.",
            'evening_reflection': "A peaceful way to process and integrate your day's experiences.",
            'weekly_review': "A deeper look at patterns and growth over the past week.",
            'stress_processing': "A supportive space to work through stress and find clarity.",
            'decision_making': "A structured approach to exploring choices and finding direction."
        }
        
        return descriptions.get(session_type, "A guided reflection to support your inner journey.")

    def create_custom_session(self, theme, prompts):
        """Create a custom reflection session"""
        return {
            'type': 'custom',
            'theme': theme,
            'prompts': prompts,
            'description': f"A personalized reflection session focused on {theme}."
        }

    def get_daily_reflection_schedule(self):
        """Get suggested reflection schedule for the day"""
        schedule = []
        
        current_hour = datetime.now().hour
        
        # Morning intention (6-10 AM)
        if 6 <= current_hour <= 10:
            schedule.append({
                'time': 'Morning',
                'type': 'morning_intention',
                'duration': '5-10 minutes',
                'description': 'Set intentions for the day'
            })
        
        # Midday check-in (12-2 PM)
        if 12 <= current_hour <= 14:
            schedule.append({
                'time': 'Midday',
                'type': 'mindfulness',
                'duration': '3-5 minutes',
                'description': 'Brief mindful pause'
            })
        
        # Evening reflection (6-9 PM)
        if 18 <= current_hour <= 21:
            schedule.append({
                'time': 'Evening',
                'type': 'evening_reflection',
                'duration': '10-15 minutes',
                'description': 'Process and integrate the day'
            })
        
        return schedule

    def get_reflection_history_prompt(self, previous_reflections):
        """Generate a prompt based on previous reflection history"""
        
        if not previous_reflections:
            return self.get_reflection_prompt()
        
        # Analyze patterns in previous reflections
        recent_themes = []
        for reflection in previous_reflections[-5:]:  # Last 5 reflections
            if 'theme' in reflection:
                recent_themes.append(reflection['theme'])
        
        # Avoid repeating recent themes
        available_categories = [cat for cat in self.reflection_categories.keys() 
                              if cat not in recent_themes]
        
        if available_categories:
            category = random.choice(available_categories)
        else:
            category = random.choice(list(self.reflection_categories.keys()))
        
        return self.get_reflection_prompt(category)

    def format_reflection_response(self, user_response, prompt):
        """Format and analyze a reflection response"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'response': user_response,
            'word_count': len(user_response.split()),
            'reflection_length': 'brief' if len(user_response.split()) < 20 else 'detailed',
            'themes_mentioned': self._extract_themes(user_response)
        }

    def _extract_themes(self, text):
        """Extract themes from reflection response"""
        
        theme_keywords = {
            'family': ['family', 'parents', 'children', 'siblings', 'relatives'],
            'work': ['work', 'job', 'career', 'colleagues', 'office'],
            'relationships': ['friend', 'partner', 'relationship', 'love', 'connection'],
            'health': ['health', 'exercise', 'sleep', 'energy', 'body'],
            'growth': ['learn', 'grow', 'change', 'improve', 'develop'],
            'creativity': ['create', 'art', 'music', 'write', 'express'],
            'spirituality': ['spiritual', 'meaning', 'purpose', 'faith', 'soul'],
            'nature': ['nature', 'outdoors', 'trees', 'sky', 'earth']
        }
        
        text_lower = text.lower()
        found_themes = []
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_themes.append(theme)
        
        return found_themes

# Example usage and testing
if __name__ == "__main__":
    reflection = ReflectionMode()
    
    print("Reflection Mode initialized!")
    print("=" * 50)
    
    # Test different types of prompts
    print("\n1. Random reflection prompt:")
    print(reflection.get_reflection_prompt())
    
    print("\n2. Gratitude-focused prompt:")
    print(reflection.get_reflection_prompt('gratitude'))
    
    print("\n3. Guided session:")
    session = reflection.get_guided_session()
    if session:
        print(f"Session: {session['type']}")
        print(f"Description: {session['description']}")
        print("Prompts:")
        for i, prompt in enumerate(session['prompts'], 1):
            print(f"  {i}. {prompt}")
    
    print("\n4. Reflection technique:")
    technique = reflection.get_reflection_technique()
    if technique:
        print(f"Technique: {technique['name']}")
        print(f"Instruction: {technique['instruction']}")
    
    print("\n5. Daily schedule:")
    schedule = reflection.get_daily_reflection_schedule()
    for item in schedule:
        print(f"{item['time']}: {item['description']} ({item['duration']})")
    
    print("\n6. Mood-based suggestion:")
    test_mood = {
        'sentiment': 'negative',
        'emotions': ['stress', 'anxiety'],
        'intensity': 8
    }
    mood_prompt = reflection.get_reflection_prompt(mood=test_mood)
    print(f"For stressed mood: {mood_prompt}")
