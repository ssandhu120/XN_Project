"""Text processing utilities for natural language understanding."""

import re
from typing import List, Dict, Set, Tuple
from data_models import SeverityLevel

class TextProcessor:
    """Handles text analysis and pattern matching for mental health conversations."""
    
    def __init__(self):
        self.crisis_keywords = {
            'suicide', 'kill myself', 'killing myself', 'end it all', 'not worth living', 'better off dead',
            'suicide', 'suicidal', 'harm myself', 'hurt myself', 'end my life',
            'want to die', 'wish I was dead', 'no point in living', 'take my life'
        }
        
        self.high_severity_keywords = {
            'panic attack', 'can\'t breathe', 'overwhelming', 'breakdown', 'crisis',
            'emergency', 'desperate', 'hopeless', 'trapped', 'unbearable'
        }
        
        self.moderate_severity_keywords = {
            'anxious', 'worried', 'stressed', 'depressed', 'sad', 'lonely',
            'overwhelmed', 'struggling', 'difficult', 'hard time', 'upset'
        }
        
        self.academic_keywords = {
            'exam', 'test', 'grade', 'study', 'homework', 'assignment', 'class',
            'professor', 'academic', 'school', 'college', 'university', 'semester'
        }
        
        self.social_keywords = {
            'friends', 'lonely', 'isolated', 'social', 'relationship', 'dating',
            'roommate', 'family', 'homesick', 'miss home', 'alone'
        }
        
        self.international_keywords = {
            'international', 'foreign', 'homesick', 'culture', 'language',
            'visa', 'home country', 'cultural', 'adjustment', 'different culture'
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from user input."""
        text_lower = text.lower()
        keywords = []
        
        # Check all keyword categories
        all_keywords = (
            self.crisis_keywords | self.high_severity_keywords | 
            self.moderate_severity_keywords | self.academic_keywords |
            self.social_keywords | self.international_keywords
        )
        
        for keyword in all_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords
    
    def assess_severity(self, text: str, keywords: List[str] = None) -> SeverityLevel:
        """Assess the severity level of user's mental health concern."""
        if keywords is None:
            keywords = self.extract_keywords(text)
        
        text_lower = text.lower()
        
        # Crisis level detection
        for crisis_word in self.crisis_keywords:
            if crisis_word in text_lower:
                return SeverityLevel.CRISIS
        
        # High severity detection
        high_severity_count = sum(1 for word in self.high_severity_keywords 
                                 if word in text_lower)
        if high_severity_count >= 2:
            return SeverityLevel.HIGH
        
        # Moderate severity detection
        moderate_severity_count = sum(1 for word in self.moderate_severity_keywords 
                                    if word in text_lower)
        if moderate_severity_count >= 2 or high_severity_count >= 1:
            return SeverityLevel.MODERATE
        
        # Check for any mental health indicators
        if keywords:
            return SeverityLevel.LOW
        
        return SeverityLevel.LOW
    
    def categorize_concern(self, text: str, keywords: List[str] = None) -> List[str]:
        """Categorize the type of mental health concern."""
        if keywords is None:
            keywords = self.extract_keywords(text)
        
        text_lower = text.lower()
        categories = []
        
        # Academic stress
        if any(word in text_lower for word in self.academic_keywords):
            categories.append("academic_stress")
        
        # Social/relationship issues
        if any(word in text_lower for word in self.social_keywords):
            categories.append("social_isolation")
        
        # International student concerns
        if any(word in text_lower for word in self.international_keywords):
            categories.append("cultural_adjustment")
        
        # Self-esteem issues
        self_esteem_indicators = ['confidence', 'self-worth', 'inadequate', 'failure', 'imposter']
        if any(word in text_lower for word in self_esteem_indicators):
            categories.append("self_esteem")
        
        # General mental health
        if not categories:
            categories.append("general_mental_health")
        
        return categories
    
    def detect_crisis_indicators(self, text: str) -> Tuple[bool, List[str]]:
        """Detect specific crisis indicators in text."""
        text_lower = text.lower()
        detected_indicators = []
        
        crisis_patterns = [
            (r'\b(want to|going to|plan to) (die|kill myself|end it)\b', 'suicidal_ideation'),
            (r'\b(hurt|harm) myself\b', 'self_harm'),
            (r'\b(no point|not worth) (living|it)\b', 'hopelessness'),
            (r'\b(can\'t|cannot) (go on|continue|take it)\b', 'desperation'),
            (r'\b(emergency|crisis|help me)\b', 'immediate_help_needed')
        ]
        
        for pattern, indicator in crisis_patterns:
            if re.search(pattern, text_lower):
                detected_indicators.append(indicator)
        
        return len(detected_indicators) > 0, detected_indicators
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text input."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\?\!\,\-\']', '', text)
        
        return text
    
    def extract_emotions(self, text: str) -> List[str]:
        """Extract emotional indicators from text."""
        emotion_keywords = {
            'sad': ['sad', 'sadness', 'down', 'blue', 'melancholy'],
            'anxious': ['anxious', 'anxiety', 'nervous', 'worried', 'tense'],
            'angry': ['angry', 'mad', 'furious', 'irritated', 'frustrated'],
            'lonely': ['lonely', 'alone', 'isolated', 'disconnected'],
            'overwhelmed': ['overwhelmed', 'swamped', 'too much', 'can\'t handle'],
            'hopeless': ['hopeless', 'helpless', 'stuck', 'trapped', 'no way out']
        }
        
        text_lower = text.lower()
        detected_emotions = []
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions

# Global text processor instance
text_processor = TextProcessor()