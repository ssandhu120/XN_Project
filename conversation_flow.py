"""Conversation flow management for the mental health chatbot."""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from data_models import (
    ConversationSession, UserMessage, BotResponse, SeverityLevel
)
from domain_logic import mental_health_matcher
from crisis_handler import crisis_handler
from llm_client import llm_client
from utils.logger import logger
from config import config

class ConversationManager:
    """Manages conversation flow and session state."""
    
    def __init__(self):
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.welcome_messages = [
            "Hello! I'm here to help you navigate mental health resources and support. How are you feeling today?",
            "Hi there! I'm a mental health support assistant connected to MindBridge Care and Northeastern services. What's on your mind?",
            "Welcome! I'm here to listen and help connect you with the right mental health resources. How can I support you today?"
        ]
        
        self.follow_up_questions = {
            'academic_stress': [
                "What specific academic challenges are you facing?",
                "How long have you been feeling this academic pressure?",
                "Have you been able to talk to any professors or advisors about this?"
            ],
            'social_isolation': [
                "How long have you been feeling lonely?",
                "What kinds of social connections are you hoping to make?",
                "Have you tried joining any clubs or activities on campus?"
            ],
            'cultural_adjustment': [
                "What aspects of cultural adjustment are most challenging?",
                "How long have you been away from home?",
                "Have you connected with other international students?"
            ],
            'self_esteem': [
                "What situations tend to trigger these feelings?",
                "How do these feelings affect your daily life?",
                "What usually helps you feel more confident?"
            ]
        }
    
    def start_new_session(self) -> str:
        """Start a new conversation session."""
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        self.active_sessions[session_id] = session
        
        logger.log_user_interaction(session_id, "session_started")
        return session_id
    
    def get_welcome_message(self) -> str:
        """Get a welcome message for new users."""
        import random
        return random.choice(self.welcome_messages)
    
    def process_user_message(self, session_id: str, user_input: str) -> Tuple[str, bool]:
        """Process user message and generate appropriate response."""
        session = self.active_sessions.get(session_id)
        if not session:
            session_id = self.start_new_session()
            session = self.active_sessions[session_id]
        
        # Create user message
        user_message = UserMessage(content=user_input)
        
        # Analyze user input
        conversation_history = [msg.content for msg in session.messages[-5:]]  # Last 5 messages
        analysis = mental_health_matcher.analyze_user_input(user_input, conversation_history)
        
        # Update user message with analysis
        user_message.detected_keywords = analysis['keywords']
        user_message.severity_assessment = analysis['severity']
        user_message.matched_scenarios = [s.id for s in analysis['matching_scenarios']]
        
        # Add to session
        session.messages.append(user_message)
        session.identified_concerns.extend(analysis['categories'])
        session.recommended_resources.extend([r.resource_id for r in analysis['recommendations']])
        
        # Handle crisis situations immediately
        if analysis['requires_immediate_attention']:
            session.crisis_flags.extend(analysis['crisis_assessment'].detected_indicators)
            crisis_response = crisis_handler.generate_crisis_response(analysis['crisis_assessment'])
            
            bot_response = BotResponse(
                content=crisis_response,
                response_type="crisis",
                requires_human_intervention=True
            )
            session.responses.append(bot_response)
            
            logger.log_crisis_detection(session_id, analysis['severity'].value)
            return crisis_response, True  # True indicates crisis situation
        
        # Generate regular response
        response_content = self._generate_response(session, analysis)
        
        # Create bot response
        bot_response = BotResponse(
            content=response_content,
            response_type=self._determine_response_type(analysis),
            recommended_resources=[r.resource_id for r in analysis['recommendations'][:3]],
            follow_up_questions=self._get_follow_up_questions(analysis['categories'])
        )
        
        session.responses.append(bot_response)
        
        # Update session metadata
        self._update_session_metadata(session, analysis)
        
        return response_content, False  # False indicates normal conversation
    
    def _generate_response(self, session: ConversationSession, analysis: Dict) -> str:
        """Generate appropriate response based on analysis."""
        # Prepare context for LLM
        context = mental_health_matcher.get_conversation_context(analysis)
        
        # Try to generate LLM response
        llm_response = llm_client.generate_response(analysis['original_input'], context)
        
        # Add resource recommendations
        recommendations_text = mental_health_matcher.format_recommendations_for_display(
            analysis['recommendations']
        )
        
        # Combine LLM response with recommendations
        if recommendations_text and not analysis['requires_immediate_attention']:
            full_response = f"{llm_response}\n\n{recommendations_text}"
        else:
            full_response = llm_response
        
        # Add follow-up questions if appropriate
        follow_ups = self._get_follow_up_questions(analysis['categories'])
        if follow_ups and len(session.messages) < 3:  # Only for early conversation
            import random
            follow_up = random.choice(follow_ups)
            full_response += f"\n\n{follow_up}"
        
        return full_response
    
    def _determine_response_type(self, analysis: Dict) -> str:
        """Determine the type of response based on analysis."""
        if analysis['requires_immediate_attention']:
            return "crisis"
        elif analysis['severity'] == SeverityLevel.HIGH:
            return "urgent_support"
        elif analysis['recommendations']:
            return "resource_recommendation"
        else:
            return "general_support"
    
    def _get_follow_up_questions(self, categories: List[str]) -> List[str]:
        """Get appropriate follow-up questions based on categories."""
        questions = []
        for category in categories:
            if category in self.follow_up_questions:
                questions.extend(self.follow_up_questions[category])
        
        # Add general follow-up questions
        general_questions = [
            "Would you like to talk more about what's been bothering you?",
            "How long have you been feeling this way?",
            "What kind of support do you think would be most helpful?",
            "Have you been able to talk to anyone else about this?"
        ]
        
        if not questions:
            questions = general_questions
        
        return questions[:2]  # Return max 2 questions
    
    def _update_session_metadata(self, session: ConversationSession, analysis: Dict):
        """Update session metadata based on analysis."""
        # Update user profile
        if 'cultural_adjustment' in analysis['categories']:
            session.user_profile['is_international'] = True
        
        if analysis['severity'] in [SeverityLevel.HIGH, SeverityLevel.CRISIS]:
            session.user_profile['high_risk'] = True
        
        # Track conversation themes
        session.user_profile['primary_concerns'] = list(set(
            session.user_profile.get('primary_concerns', []) + analysis['categories']
        ))
        
        # Update session activity
        session.user_profile['last_activity'] = datetime.now().isoformat()
        session.user_profile['message_count'] = len(session.messages)
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get a summary of the conversation session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        # Analyze conversation patterns
        severity_levels = [msg.severity_assessment for msg in session.messages 
                          if msg.severity_assessment]
        
        # Find highest severity using enum ordering
        severity_order = {
            SeverityLevel.LOW: 0,
            SeverityLevel.MODERATE: 1,
            SeverityLevel.HIGH: 2,
            SeverityLevel.CRISIS: 3
        }
        
        if severity_levels:
            highest_severity = max(severity_levels, key=lambda s: severity_order[s])
        else:
            highest_severity = SeverityLevel.LOW
        
        # Get unique concerns and resources
        unique_concerns = list(set(session.identified_concerns))
        unique_resources = list(set(session.recommended_resources))
        
        return {
            'session_id': session_id,
            'start_time': session.start_time.isoformat(),
            'duration_minutes': (datetime.now() - session.start_time).total_seconds() / 60,
            'message_count': len(session.messages),
            'response_count': len(session.responses),
            'highest_severity': highest_severity.value,
            'identified_concerns': unique_concerns,
            'recommended_resources': unique_resources,
            'crisis_flags': session.crisis_flags,
            'user_profile': session.user_profile
        }
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Clean up sessions older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        expired_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.start_time < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id[:8]}...")
        
        return len(expired_sessions)
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for display."""
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        
        history = []
        
        # Interleave messages and responses
        for i in range(min(len(session.messages), len(session.responses), limit)):
            history.append({
                'type': 'user',
                'content': session.messages[i].content,
                'timestamp': session.messages[i].timestamp.isoformat(),
                'severity': session.messages[i].severity_assessment.value if session.messages[i].severity_assessment else None
            })
            
            history.append({
                'type': 'bot',
                'content': session.responses[i].content,
                'timestamp': session.responses[i].timestamp.isoformat(),
                'response_type': session.responses[i].response_type
            })
        
        return history[-limit:]  # Return most recent entries
    
    def end_session(self, session_id: str) -> bool:
        """End a conversation session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.is_active = False
            
            # Log session end
            logger.log_user_interaction(session_id, "session_ended")
            
            # Keep session for a while for potential reference
            # In production, you might want to save to database
            return True
        
        return False
    
    def get_active_session_count(self) -> int:
        """Get count of active sessions."""
        return len([s for s in self.active_sessions.values() if s.is_active])

# Global conversation manager instance
conversation_manager = ConversationManager()