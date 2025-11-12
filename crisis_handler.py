"""Crisis detection and intervention handling for mental health emergencies."""

from typing import List, Tuple, Dict
from data_models import CrisisAssessment, SeverityLevel, Resource
from resource_database import resource_db
from utils.text_processing import text_processor
from utils.logger import logger

class CrisisHandler:
    """Handles crisis detection and appropriate intervention responses."""
    
    def __init__(self):
        self.crisis_keywords = {
            'immediate_danger': [
                'kill myself', 'killing myself', 'end my life', 'suicide', 'want to die', 
                'better off dead', 'not worth living', 'end it all', 'take my life'
            ],
            'self_harm': [
                'hurt myself', 'harm myself', 'cut myself', 'self-harm',
                'hurting myself', 'harming myself'
            ],
            'hopelessness': [
                'no point', 'hopeless', 'helpless', 'trapped', 'no way out',
                'can\'t go on', 'give up', 'nothing matters'
            ],
            'emergency_requests': [
                'emergency', 'crisis', 'help me', 'need help now', 'urgent'
            ]
        }
        
        self.crisis_responses = {
            'immediate_safety': [
                "I'm very concerned about what you're sharing with me. Your safety is the most important thing right now.",
                "What you're feeling is serious, and I want to make sure you get the help you need immediately.",
                "I hear that you're in a lot of pain right now. There are people who can help you through this crisis."
            ],
            'professional_help': [
                "This sounds like a situation where professional help is needed right away.",
                "I strongly encourage you to reach out to a crisis counselor who can provide immediate support.",
                "A trained crisis counselor can help you work through these feelings safely."
            ],
            'not_alone': [
                "You are not alone in this. Many people have felt this way and found help.",
                "These feelings can be overwhelming, but they are temporary and treatable.",
                "Your life has value, and there are people who want to help you."
            ]
        }
    
    def assess_crisis_risk(self, user_input: str, conversation_history: List[str] = None) -> CrisisAssessment:
        """Assess the crisis risk level based on user input and conversation history."""
        user_input_lower = user_input.lower()
        detected_indicators = []
        risk_level = SeverityLevel.LOW
        
        # Check for immediate danger indicators
        for category, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    detected_indicators.append(f"{category}: {keyword}")
                    if category == 'immediate_danger':
                        risk_level = SeverityLevel.CRISIS
                    elif category == 'self_harm' and risk_level != SeverityLevel.CRISIS:
                        risk_level = SeverityLevel.HIGH
                    elif risk_level == SeverityLevel.LOW:
                        risk_level = SeverityLevel.MODERATE
        
        # Use text processor for additional analysis
        is_crisis, crisis_indicators = text_processor.detect_crisis_indicators(user_input)
        if is_crisis:
            detected_indicators.extend(crisis_indicators)
            if risk_level == SeverityLevel.LOW:
                risk_level = SeverityLevel.HIGH
        
        # Check conversation history for escalating patterns
        if conversation_history:
            history_text = ' '.join(conversation_history[-3:])  # Last 3 messages
            history_severity = text_processor.assess_severity(history_text)
            if history_severity == SeverityLevel.CRISIS:
                risk_level = SeverityLevel.CRISIS
        
        # Determine immediate actions needed
        immediate_actions = self._get_immediate_actions(risk_level, detected_indicators)
        recommended_contacts = self._get_recommended_contacts(risk_level)
        
        assessment = CrisisAssessment(
            risk_level=risk_level,
            detected_indicators=detected_indicators,
            immediate_actions=immediate_actions,
            recommended_contacts=recommended_contacts,
            requires_immediate_intervention=(risk_level == SeverityLevel.CRISIS)
        )
        
        # Log crisis detection
        if risk_level in [SeverityLevel.HIGH, SeverityLevel.CRISIS]:
            logger.log_crisis_detection("current_session", risk_level.value)
        
        return assessment
    
    def _get_immediate_actions(self, risk_level: SeverityLevel, indicators: List[str]) -> List[str]:
        """Get immediate actions based on risk level."""
        if risk_level == SeverityLevel.CRISIS:
            return [
                "Contact crisis hotline immediately (988)",
                "If in immediate danger, call 911",
                "Reach out to Northeastern emergency services: (617) 373-3333",
                "Contact MindBridge Care crisis support: 1-800-CRISIS-MB",
                "Stay with someone you trust or go to emergency room"
            ]
        elif risk_level == SeverityLevel.HIGH:
            return [
                "Contact Northeastern CAPS: (617) 373-2772",
                "Call 988 if thoughts become more intense",
                "Reach out to MindBridge Care counseling",
                "Talk to a trusted friend, family member, or advisor",
                "Consider visiting CAPS for same-day consultation"
            ]
        elif risk_level == SeverityLevel.MODERATE:
            return [
                "Schedule appointment with Northeastern CAPS",
                "Contact MindBridge Care for counseling support",
                "Reach out to peer support resources",
                "Practice self-care and stress management techniques"
            ]
        else:
            return [
                "Consider talking to a counselor about your concerns",
                "Contact MindBridge Care wellness programs",
                "Connect with peer support groups"
            ]
    
    def _get_recommended_contacts(self, risk_level: SeverityLevel) -> List[str]:
        """Get recommended contacts based on risk level."""
        if risk_level == SeverityLevel.CRISIS:
            return [
                "988 - Suicide & Crisis Lifeline (24/7)",
                "911 - Emergency Services",
                "(617) 373-3333 - Northeastern Emergency",
                "1-800-CRISIS-MB - MindBridge Crisis Support"
            ]
        elif risk_level == SeverityLevel.HIGH:
            return [
                "988 - Suicide & Crisis Lifeline (24/7)",
                "(617) 373-2772 - Northeastern CAPS",
                "1-800-MINDBRIDGE - MindBridge Care",
                "(617) 373-3333 - Northeastern Emergency (if needed)"
            ]
        else:
            return [
                "(617) 373-2772 - Northeastern CAPS",
                "1-800-MINDBRIDGE - MindBridge Care",
                "988 - Crisis Lifeline (if needed)"
            ]
    
    def generate_crisis_response(self, assessment: CrisisAssessment) -> str:
        """Generate appropriate crisis response based on assessment."""
        if assessment.risk_level == SeverityLevel.CRISIS:
            response = self._build_crisis_response(assessment)
        elif assessment.risk_level == SeverityLevel.HIGH:
            response = self._build_high_risk_response(assessment)
        else:
            response = self._build_moderate_risk_response(assessment)
        
        return response
    
    def _build_crisis_response(self, assessment: CrisisAssessment) -> str:
        """Build response for crisis-level situations."""
        response_parts = [
            "🚨 **CRISIS SUPPORT NEEDED** 🚨",
            "",
            self.crisis_responses['immediate_safety'][0],
            "",
            "**IMMEDIATE ACTIONS:**",
            "• **Call 988** (Suicide & Crisis Lifeline) - Available 24/7",
            "• **If in immediate danger, call 911**",
            "• **Northeastern Emergency:** (617) 373-3333",
            "• **MindBridge Crisis Support:** 1-800-CRISIS-MB",
            "",
            self.crisis_responses['not_alone'][0],
            "",
            "**Please reach out to one of these resources RIGHT NOW. Your safety is the priority.**"
        ]
        
        return "\n".join(response_parts)
    
    def _build_high_risk_response(self, assessment: CrisisAssessment) -> str:
        """Build response for high-risk situations."""
        response_parts = [
            "⚠️ **URGENT SUPPORT RECOMMENDED** ⚠️",
            "",
            "I'm concerned about what you're sharing. This sounds like you need professional support soon.",
            "",
            "**RECOMMENDED ACTIONS:**",
            "• **Call Northeastern CAPS:** (617) 373-2772",
            "• **Crisis Lifeline (if needed):** 988",
            "• **MindBridge Care:** 1-800-MINDBRIDGE",
            "",
            "**Same-day support may be available through CAPS.**",
            "",
            self.crisis_responses['not_alone'][1]
        ]
        
        return "\n".join(response_parts)
    
    def _build_moderate_risk_response(self, assessment: CrisisAssessment) -> str:
        """Build response for moderate-risk situations."""
        response_parts = [
            "I hear that you're going through a difficult time. It's important to get support.",
            "",
            "**RECOMMENDED RESOURCES:**",
            "• **Northeastern CAPS:** (617) 373-2772",
            "• **MindBridge Care:** 1-800-MINDBRIDGE",
            "• **Crisis Lifeline (24/7):** 988",
            "",
            "Would you like help connecting with any of these resources?"
        ]
        
        return "\n".join(response_parts)
    
    def get_crisis_resources(self) -> List[Resource]:
        """Get all available crisis resources."""
        return resource_db.get_crisis_resources()
    
    def should_escalate_immediately(self, assessment: CrisisAssessment) -> bool:
        """Determine if immediate escalation is required."""
        return assessment.requires_immediate_intervention
    
    def get_safety_plan_suggestions(self) -> List[str]:
        """Get safety plan suggestions for users."""
        return [
            "Identify warning signs when you're starting to feel worse",
            "List people you can contact when you need support",
            "Remove or secure items that could be used for self-harm",
            "Identify safe places you can go during difficult times",
            "List activities that help you feel better or distract you",
            "Write down professional contacts and crisis numbers",
            "Practice grounding techniques (5-4-3-2-1 sensory method)",
            "Keep a list of reasons for living and future goals"
        ]

# Global crisis handler instance
crisis_handler = CrisisHandler()