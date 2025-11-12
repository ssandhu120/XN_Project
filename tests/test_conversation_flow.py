"""Tests for conversation flow management."""

import pytest
from datetime import datetime, timedelta
from conversation_flow import conversation_manager
from data_models import SeverityLevel

class TestConversationManager:
    """Test cases for conversation management."""
    
    def test_start_new_session(self):
        """Test starting a new conversation session."""
        session_id = conversation_manager.start_new_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        assert session_id in conversation_manager.active_sessions
        
        session = conversation_manager.active_sessions[session_id]
        assert session.is_active is True
        assert len(session.messages) == 0
        assert len(session.responses) == 0
    
    def test_get_welcome_message(self):
        """Test getting welcome message."""
        welcome_msg = conversation_manager.get_welcome_message()
        
        assert welcome_msg is not None
        assert len(welcome_msg) > 0
        assert any(word in welcome_msg.lower() 
                  for word in ['hello', 'hi', 'welcome', 'help'])
    
    def test_process_user_message_normal(self):
        """Test processing normal user message."""
        session_id = conversation_manager.start_new_session()
        user_input = "I'm feeling stressed about my upcoming exams"
        
        response, is_crisis = conversation_manager.process_user_message(session_id, user_input)
        
        assert response is not None
        assert len(response) > 0
        assert is_crisis is False
        
        # Check session was updated
        session = conversation_manager.active_sessions[session_id]
        assert len(session.messages) == 1
        assert len(session.responses) == 1
        assert session.messages[0].content == user_input
    
    def test_process_user_message_crisis(self):
        """Test processing crisis-level user message."""
        session_id = conversation_manager.start_new_session()
        user_input = "I want to kill myself, I can't take it anymore"
        
        response, is_crisis = conversation_manager.process_user_message(session_id, user_input)
        
        assert response is not None
        assert len(response) > 0
        assert is_crisis is True
        
        # Crisis response should contain emergency contacts
        assert '988' in response or '911' in response
        
        # Check session was updated with crisis flags
        session = conversation_manager.active_sessions[session_id]
        assert len(session.crisis_flags) > 0
        assert session.responses[0].requires_human_intervention is True
    
    def test_session_metadata_updates(self):
        """Test that session metadata is properly updated."""
        session_id = conversation_manager.start_new_session()
        
        # Process international student message
        conversation_manager.process_user_message(
            session_id, "I'm an international student feeling homesick"
        )
        
        session = conversation_manager.active_sessions[session_id]
        assert session.user_profile.get('is_international') is True
        assert 'cultural_adjustment' in session.identified_concerns
        assert session.user_profile.get('message_count') == 1
    
    def test_get_session_summary(self):
        """Test getting session summary."""
        session_id = conversation_manager.start_new_session()
        
        # Add some messages
        conversation_manager.process_user_message(session_id, "I'm feeling anxious")
        conversation_manager.process_user_message(session_id, "I'm worried about exams")
        
        summary = conversation_manager.get_session_summary(session_id)
        
        assert summary is not None
        assert summary['session_id'] == session_id
        assert summary['message_count'] == 2
        assert summary['response_count'] == 2
        assert 'start_time' in summary
        assert 'duration_minutes' in summary
        assert isinstance(summary['identified_concerns'], list)
    
    def test_get_conversation_history(self):
        """Test getting conversation history."""
        session_id = conversation_manager.start_new_session()
        
        # Add messages
        conversation_manager.process_user_message(session_id, "Hello")
        conversation_manager.process_user_message(session_id, "I need help")
        
        history = conversation_manager.get_conversation_history(session_id)
        
        assert len(history) == 4  # 2 user messages + 2 bot responses
        assert history[0]['type'] == 'user'
        assert history[1]['type'] == 'bot'
        assert history[0]['content'] == "Hello"
    
    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions."""
        # Create a session and manually set old timestamp
        session_id = conversation_manager.start_new_session()
        session = conversation_manager.active_sessions[session_id]
        session.start_time = datetime.now() - timedelta(hours=25)  # 25 hours ago
        
        # Create a recent session
        recent_session_id = conversation_manager.start_new_session()
        
        # Cleanup sessions older than 24 hours
        cleaned_count = conversation_manager.cleanup_old_sessions(hours=24)
        
        assert cleaned_count == 1
        assert session_id not in conversation_manager.active_sessions
        assert recent_session_id in conversation_manager.active_sessions
    
    def test_end_session(self):
        """Test ending a session."""
        session_id = conversation_manager.start_new_session()
        
        result = conversation_manager.end_session(session_id)
        
        assert result is True
        session = conversation_manager.active_sessions[session_id]
        assert session.is_active is False
    
    def test_get_active_session_count(self):
        """Test getting active session count."""
        initial_count = conversation_manager.get_active_session_count()
        
        # Start new sessions
        session1 = conversation_manager.start_new_session()
        session2 = conversation_manager.start_new_session()
        
        assert conversation_manager.get_active_session_count() == initial_count + 2
        
        # End one session
        conversation_manager.end_session(session1)
        
        assert conversation_manager.get_active_session_count() == initial_count + 1
    
    def test_follow_up_questions(self):
        """Test follow-up question generation."""
        categories = ['academic_stress']
        questions = conversation_manager._get_follow_up_questions(categories)
        
        assert len(questions) > 0
        assert len(questions) <= 2  # Should return max 2 questions
        assert all(isinstance(q, str) for q in questions)
        assert all(len(q) > 0 for q in questions)
    
    def test_response_type_determination(self):
        """Test response type determination."""
        # Mock analysis for different scenarios
        crisis_analysis = {
            'requires_immediate_attention': True,
            'severity': SeverityLevel.CRISIS,
            'recommendations': []
        }
        
        high_risk_analysis = {
            'requires_immediate_attention': False,
            'severity': SeverityLevel.HIGH,
            'recommendations': []
        }
        
        normal_analysis = {
            'requires_immediate_attention': False,
            'severity': SeverityLevel.MODERATE,
            'recommendations': [{'resource_id': 'test'}]
        }
        
        assert conversation_manager._determine_response_type(crisis_analysis) == "crisis"
        assert conversation_manager._determine_response_type(high_risk_analysis) == "urgent_support"
        assert conversation_manager._determine_response_type(normal_analysis) == "resource_recommendation"

if __name__ == '__main__':
    pytest.main([__file__])