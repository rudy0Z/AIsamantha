import nltk
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from datetime import datetime
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class EmotionDetector:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Emotion keywords dictionary
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'cheerful', 'elated', 
                   'joyful', 'glad', 'pleased', 'content', 'blissful', 'euphoric'],
            'sadness': ['sad', 'depressed', 'down', 'upset', 'disappointed', 'heartbroken', 
                       'miserable', 'gloomy', 'melancholy', 'sorrowful', 'dejected'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 
                     'outraged', 'livid', 'enraged', 'hostile', 'resentful'],
            'fear': ['scared', 'afraid', 'terrified', 'anxious', 'worried', 'nervous', 
                    'frightened', 'panicked', 'apprehensive', 'uneasy'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 
                        'bewildered', 'startled', 'astounded'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'appalled', 
                       'nauseated', 'repelled'],
            'love': ['love', 'adore', 'cherish', 'treasure', 'devoted', 'affectionate', 
                    'passionate', 'romantic', 'caring'],
            'hope': ['hopeful', 'optimistic', 'confident', 'positive', 'encouraged', 
                    'inspired', 'motivated', 'determined'],
            'loneliness': ['lonely', 'isolated', 'alone', 'abandoned', 'disconnected', 
                          'solitary', 'forsaken'],
            'stress': ['stressed', 'overwhelmed', 'pressured', 'tense', 'strained', 
                      'burned out', 'exhausted', 'frazzled'],
            'gratitude': ['grateful', 'thankful', 'appreciative', 'blessed', 'fortunate'],
            'confusion': ['confused', 'puzzled', 'perplexed', 'bewildered', 'lost', 'uncertain']
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 1.8, 'really': 1.3,
            'quite': 1.2, 'somewhat': 0.8, 'slightly': 0.6, 'a bit': 0.7,
            'totally': 1.8, 'completely': 1.9, 'absolutely': 2.0
        }
    
    def analyze_emotion(self, text):
        """Comprehensive emotion analysis"""
        if not text or not text.strip():
            return self._default_emotion()
        
        text_lower = text.lower()
        
        # VADER sentiment analysis
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment
        
        # Detect specific emotions
        detected_emotions = self._detect_emotions(text_lower)
        
        # Calculate overall sentiment
        sentiment = self._calculate_sentiment(vader_scores, textblob_sentiment)
        
        # Calculate intensity
        intensity = self._calculate_intensity(text_lower, vader_scores, detected_emotions)
        
        # Contextual adjustments
        intensity = self._apply_contextual_adjustments(text_lower, intensity)
        
        return {
            'sentiment': sentiment,
            'emotions': detected_emotions,
            'intensity': min(max(round(intensity, 1), 1), 10),
            'vader_scores': vader_scores,
            'confidence': self._calculate_confidence(detected_emotions, vader_scores),
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_emotions(self, text):
        """Detect specific emotions from text"""
        detected = []
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected.append(emotion)
                    break
        
        return list(set(detected))  # Remove duplicates
    
    def _calculate_sentiment(self, vader_scores, textblob_sentiment):
        """Calculate overall sentiment"""
        # Combine VADER and TextBlob
        vader_compound = vader_scores['compound']
        textblob_polarity = textblob_sentiment.polarity
        
        # Weighted average (VADER is generally more accurate for social media text)
        combined_score = (vader_compound * 0.7) + (textblob_polarity * 0.3)
        
        if combined_score >= 0.1:
            return 'positive'
        elif combined_score <= -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_intensity(self, text, vader_scores, emotions):
        """Calculate emotional intensity"""
        base_intensity = 5.0  # Neutral baseline
        
        # VADER compound score influence
        vader_intensity = abs(vader_scores['compound']) * 5
        
        # Number of emotions detected
        emotion_count_bonus = len(emotions) * 0.5
        
        # Intensity modifiers in text
        modifier_bonus = 0
        for modifier, multiplier in self.intensity_modifiers.items():
            if modifier in text:
                modifier_bonus += (multiplier - 1) * 2
        
        # Exclamation marks and caps
        exclamation_bonus = text.count('!') * 0.5
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        caps_bonus = caps_ratio * 3
        
        # Question marks (often indicate uncertainty, lower intensity)
        question_penalty = text.count('?') * 0.3
        
        total_intensity = (base_intensity + vader_intensity + emotion_count_bonus + 
                          modifier_bonus + exclamation_bonus + caps_bonus - question_penalty)
        
        return total_intensity
    
    def _apply_contextual_adjustments(self, text, intensity):
        """Apply contextual adjustments based on patterns"""
        
        # Time-related context
        time_patterns = {
            'morning': ['morning', 'wake up', 'woke up', 'breakfast'],
            'night': ['night', 'evening', 'tired', 'sleepy', 'bed'],
            'work': ['work', 'job', 'office', 'meeting', 'deadline', 'boss'],
            'weekend': ['weekend', 'saturday', 'sunday', 'relax']
        }
        
        # Adjust intensity based on context
        for context, patterns in time_patterns.items():
            if any(pattern in text for pattern in patterns):
                if context == 'night' and intensity > 7:
                    intensity *= 0.9  # Slightly reduce intensity for night emotions
                elif context == 'work' and 'stress' in text:
                    intensity *= 1.1  # Increase work-related stress
        
        return intensity
    
    def _calculate_confidence(self, emotions, vader_scores):
        """Calculate confidence in emotion detection"""
        base_confidence = 0.5
        
        # More emotions detected = higher confidence
        emotion_confidence = min(len(emotions) * 0.15, 0.3)
        
        # Strong VADER scores = higher confidence
        vader_confidence = abs(vader_scores['compound']) * 0.4
        
        total_confidence = base_confidence + emotion_confidence + vader_confidence
        return min(total_confidence, 1.0)
    
    def _default_emotion(self):
        """Return default emotion state"""
        return {
            'sentiment': 'neutral',
            'emotions': [],
            'intensity': 5.0,
            'vader_scores': {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0},
            'confidence': 0.5,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_emotion_trend(self, emotion_history):
        """Analyze emotion trends over time"""
        if len(emotion_history) < 2:
            return "insufficient_data"
        
        recent_intensities = [e['intensity'] for e in emotion_history[-5:]]
        avg_recent = np.mean(recent_intensities)
        
        if len(emotion_history) >= 10:
            older_intensities = [e['intensity'] for e in emotion_history[-10:-5]]
            avg_older = np.mean(older_intensities)
            
            if avg_recent > avg_older + 1:
                return "improving"
            elif avg_recent < avg_older - 1:
                return "declining"
        
        return "stable"

# Example usage and testing
if __name__ == "__main__":
    detector = EmotionDetector()
    
    # Test cases
    test_texts = [
        "I'm feeling really excited about my new job!",
        "I'm so sad and lonely tonight...",
        "This is absolutely frustrating! I can't take it anymore!",
        "I'm a bit worried about the presentation tomorrow",
        "What a beautiful day! I feel grateful for everything",
        "I don't know what to do anymore. I'm confused and lost."
    ]
    
    print("Emotion Detection Test Results:")
    print("=" * 50)
    
    for text in test_texts:
        result = detector.analyze_emotion(text)
        print(f"\nText: '{text}'")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Emotions: {result['emotions']}")
        print(f"Intensity: {result['intensity']}/10")
        print(f"Confidence: {result['confidence']:.2f}")
