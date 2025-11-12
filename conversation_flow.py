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
from provider_recommendation_flow import provider_flow

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
        
        # Check if user is asking for provider recommendations
        provider_keywords = ["find provider", "find therapist", "find psychiatrist", "find counselor", 
                           "help finding", "looking for", "recommend provider", "therapy near me",
                           "therapist near me", "mental health provider", "where can i find",
                           "help me find", "find a therapist", "find a provider", "find a counselor"]
        
        user_input_lower = user_input.lower()
        wants_provider_search = any(keyword in user_input_lower for keyword in provider_keywords)
        
        # Also trigger provider search for moderate/high severity after initial assessment
        should_offer_providers = (
            analysis['severity'] in [SeverityLevel.MODERATE, SeverityLevel.HIGH] and 
            len(session.messages) >= 2 and  # After some conversation
            not analysis['requires_immediate_attention']
        )
        
        if wants_provider_search:
            # Start provider recommendation flow
            response_content = provider_flow.start_provider_search(session_id)
            session.user_profile['provider_search_active'] = True
            session.user_profile['provider_search_step'] = 'location_collection'
        elif session.user_profile.get('provider_search_active'):
            # Continue provider recommendation flow
            response_content = self._handle_provider_search_flow(session_id, user_input, session)
        else:
            # Generate regular response
            response_content = self._generate_response(session, analysis)
            
            # Offer provider search for appropriate cases
            if should_offer_providers and not session.user_profile.get('provider_search_offered'):
                response_content += "\n\n💡 **Would you like help finding a mental health provider?** I can help you find therapists or counselors in your area that accept your insurance. Just say \"help me find a provider\" if you're interested!"
                session.user_profile['provider_search_offered'] = True
        
        # Create bot response
        # Use conversation context for follow-up questions instead of re-analyzing
        conversation_categories = self._get_conversation_context(session, analysis)
        bot_response = BotResponse(
            content=response_content,
            response_type=self._determine_response_type(analysis),
            recommended_resources=[r.resource_id for r in analysis['recommendations'][:3]],
            follow_up_questions=self._get_follow_up_questions(conversation_categories)
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
        
        # Add resource recommendations based on conversation context
        conversation_categories = self._get_conversation_context(session, analysis)
        contextual_recommendations = mental_health_matcher.get_contextual_recommendations(
            conversation_categories, analysis['severity']
        )
        recommendations_text = mental_health_matcher.format_recommendations_for_display(
            contextual_recommendations
        )
        
        # Combine LLM response with recommendations
        if recommendations_text and not analysis['requires_immediate_attention']:
            full_response = f"{llm_response}\n\n{recommendations_text}"
        else:
            full_response = llm_response
        
        # Add follow-up questions if appropriate
        # Use established conversation context instead of re-analyzing
        conversation_categories = self._get_conversation_context(session, analysis)
        follow_ups = self._get_contextual_follow_up_questions(session, conversation_categories, analysis)
        if follow_ups and len(session.messages) < 4:  # Allow more conversation turns
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
        
        # Prioritize categories - more specific concerns first
        category_priority = ['social_isolation', 'cultural_adjustment', 'self_esteem', 'academic_stress']
        
        # Sort categories by priority
        prioritized_categories = []
        for priority_cat in category_priority:
            if priority_cat in categories:
                prioritized_categories.append(priority_cat)
        
        # Add any remaining categories
        for cat in categories:
            if cat not in prioritized_categories:
                prioritized_categories.append(cat)
        
        # Get questions from the highest priority category only
        if prioritized_categories and prioritized_categories[0] in self.follow_up_questions:
            questions = self.follow_up_questions[prioritized_categories[0]]
        
        # Add general follow-up questions if no specific ones found
        general_questions = [
            "Would you like to talk more about what's been bothering you?",
            "How long have you been feeling this way?",
            "What kind of support do you think would be most helpful?",
            "Have you been able to talk to anyone else about this?"
        ]
        
        if not questions:
            questions = general_questions
        
        return questions[:2]  # Return max 2 questions
    
    def _get_contextual_follow_up_questions(self, session: ConversationSession, categories: List[str], analysis: Dict) -> List[str]:
        """Get contextual follow-up questions that avoid repetition and build on the conversation."""
        # Track what questions we've already asked
        asked_questions = session.user_profile.get('asked_questions', set())
        
        # Get base questions for the category
        base_questions = self._get_follow_up_questions(categories)
        
        # Add contextual questions based on conversation progress
        contextual_questions = []
        
        # For social isolation conversations
        if 'social_isolation' in categories:
            if len(session.messages) == 2:  # First follow-up
                contextual_questions.extend([
                    "What kinds of social connections are you hoping to make?",
                    "Have you tried joining any clubs or activities on campus?",
                    "What's been the hardest part about making friends?"
                ])
            elif len(session.messages) >= 3:  # Later in conversation
                contextual_questions.extend([
                    "What do you think would help you feel more connected?",
                    "Are there any activities or interests you'd like to explore with others?",
                    "Would you be interested in connecting with peer support groups?"
                ])
        
        # For academic stress conversations  
        elif 'academic_stress' in categories:
            if len(session.messages) == 2:
                contextual_questions.extend([
                    "What specific academic challenges are you facing?",
                    "How is this affecting your daily routine?",
                    "Have you been able to talk to any professors or advisors about this?"
                ])
            elif len(session.messages) >= 3:
                contextual_questions.extend([
                    "What study strategies have you tried so far?",
                    "Would you be interested in academic coaching or tutoring resources?",
                    "How are you taking care of yourself during stressful times?"
                ])
        
        # Combine and filter out already asked questions
        all_questions = base_questions + contextual_questions
        available_questions = [q for q in all_questions if q not in asked_questions]
        
        # If we've asked everything, use general questions
        if not available_questions:
            general_questions = [
                "How are you feeling about the resources I've shared?",
                "What kind of support do you think would be most helpful right now?",
                "Is there anything else you'd like to talk about?"
            ]
            available_questions = [q for q in general_questions if q not in asked_questions]
        
        # Track the question we're about to ask
        if available_questions:
            selected_question = available_questions[0]  # Will be randomly selected later
            if 'asked_questions' not in session.user_profile:
                session.user_profile['asked_questions'] = set()
            session.user_profile['asked_questions'].add(selected_question)
        
        return available_questions[:3]  # Return up to 3 options
    
    def _get_conversation_context(self, session: ConversationSession, current_analysis: Dict) -> List[str]:
        """Get conversation context, prioritizing established themes over new analysis."""
        # If this is the first message, establish primary concern based on priority
        if len(session.messages) <= 1:
            # Use our priority system to determine the main concern
            category_priority = ['social_isolation', 'cultural_adjustment', 'self_esteem', 'academic_stress']
            primary_concern = None
            
            for priority_cat in category_priority:
                if priority_cat in current_analysis['categories']:
                    primary_concern = priority_cat
                    break
            
            if primary_concern:
                session.user_profile['primary_concerns'] = [primary_concern]
                return [primary_concern]
            else:
                session.user_profile['primary_concerns'] = current_analysis['categories']
                return current_analysis['categories']
        
        # For subsequent messages, maintain the established context
        established_concerns = session.user_profile.get('primary_concerns', [])
        
        # Only allow context switching if:
        # 1. No established concerns yet, OR
        # 2. Current message has crisis-level severity, OR  
        # 3. User explicitly mentions a completely different major concern
        should_switch_context = (
            not established_concerns or
            current_analysis['severity'] in [SeverityLevel.HIGH, SeverityLevel.CRISIS] or
            self._is_major_context_shift(established_concerns, current_analysis['categories'])
        )
        
        if should_switch_context:
            session.user_profile['primary_concerns'] = current_analysis['categories']
            return current_analysis['categories']
        else:
            # Maintain established conversation context
            return established_concerns
    
    def _is_major_context_shift(self, established: List[str], current: List[str]) -> bool:
        """Determine if current analysis represents a major shift in conversation context."""
        # Define major concern categories that warrant context switching
        major_concerns = ['crisis', 'self_harm', 'suicidal_ideation']
        
        # Check if current analysis contains major concerns not in established
        for concern in current:
            if concern in major_concerns and concern not in established:
                return True
        
        # Otherwise, maintain established context
        return False
    
    def _handle_provider_search_flow(self, session_id: str, user_input: str, session: ConversationSession) -> str:
        """Handle the provider search conversation flow."""
        current_step = session.user_profile.get('provider_search_step', 'location_collection')
        
        if current_step == 'location_collection':
            response = provider_flow.process_location_response(session_id, user_input)
            session.user_profile['provider_search_step'] = 'insurance_collection'
        elif current_step == 'insurance_collection':
            response = provider_flow.process_insurance_response(session_id, user_input)
            session.user_profile['provider_search_step'] = 'care_type_collection'
        elif current_step == 'care_type_collection':
            response = provider_flow.process_care_type_response(session_id, user_input)
            session.user_profile['provider_search_step'] = 'specialties_collection'
        elif current_step == 'specialties_collection':
            response = provider_flow.process_specialties_response(session_id, user_input)
            session.user_profile['provider_search_step'] = 'final_preferences'
        elif current_step == 'final_preferences':
            response = provider_flow.process_final_preferences(session_id, user_input)
            # Provider search is complete
            session.user_profile['provider_search_active'] = False
            session.user_profile['provider_search_completed'] = True
        else:
            # Fallback - restart the flow
            response = provider_flow.start_provider_search(session_id)
            session.user_profile['provider_search_step'] = 'location_collection'
        
        return response
    
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