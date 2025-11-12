"""Tests for crisis detection and handling."""

import pytest
from data_models import SeverityLevel
from crisis_handler import crisis_handler

class TestCrisisHandler:
    """Test cases for crisis detection and handling."""
    
    def test_assess_crisis_risk_high(self):
        """Test crisis risk assessment for high-risk input."""
        user_input = "I want to kill myself, I can't take this anymore"
        assessment = crisis_handler.assess_crisis_risk(user_input)
        
        assert assessment.risk_level == SeverityLevel.CRISIS
        assert assessment.requires_immediate_intervention is True
        assert len(assessment.detected_indicators) > 0
        assert len(assessment.immediate_actions) > 0
        assert len(assessment.recommended_contacts) > 0
        
        # Should contain crisis-specific indicators
        indicators_text = ' '.join(assessment.detected_indicators)
        assert 'kill myself' in indicators_text or 'suicide' in indicators_text.lower()
    
    def test_assess_crisis_risk_moderate(self):
        """Test crisis risk assessment for moderate-risk input."""
        user_input = "I'm feeling really hopeless and don't know what to do"
        assessment = crisis_handler.assess_crisis_risk(user_input)
        
        assert assessment.risk_level in [SeverityLevel.MODERATE, SeverityLevel.HIGH]
        assert len(assessment.immediate_actions) > 0
        assert len(assessment.recommended_contacts) > 0
    
    def test_assess_crisis_risk_low(self):
        """Test crisis risk assessment for low-risk input."""
        user_input = "I'm feeling a bit stressed about my exams"
        assessment = crisis_handler.assess_crisis_risk(user_input)
        
        assert assessment.risk_level in [SeverityLevel.LOW, SeverityLevel.MODERATE]
        assert assessment.requires_immediate_intervention is False
    
    def test_assess_crisis_risk_self_harm(self):
        """Test crisis risk assessment for self-harm indicators."""
        user_input = "I've been thinking about hurting myself"
        assessment = crisis_handler.assess_crisis_risk(user_input)
        
        assert assessment.risk_level in [SeverityLevel.HIGH, SeverityLevel.CRISIS]
        assert len(assessment.detected_indicators) > 0
        
        # Should detect self-harm indicators
        indicators_text = ' '.join(assessment.detected_indicators)
        assert 'self_harm' in indicators_text or 'hurt myself' in indicators_text
    
    def test_assess_crisis_risk_with_history(self):
        """Test crisis risk assessment with conversation history."""
        user_input = "I can't go on like this"
        history = [
            "I've been feeling really depressed lately",
            "Nothing seems to matter anymore",
            "I feel like giving up"
        ]
        
        assessment = crisis_handler.assess_crisis_risk(user_input, history)
        
        # History should influence risk assessment
        assert assessment.risk_level in [SeverityLevel.MODERATE, SeverityLevel.HIGH, SeverityLevel.CRISIS]
    
    def test_generate_crisis_response_crisis_level(self):
        """Test crisis response generation for crisis-level situations."""
        assessment = crisis_handler.assess_crisis_risk("I want to kill myself")
        response = crisis_handler.generate_crisis_response(assessment)
        
        assert response is not None
        assert len(response) > 0
        assert '988' in response  # Crisis hotline
        assert '911' in response  # Emergency services
        assert 'CRISIS' in response.upper()
        
        # Should contain immediate action instructions
        assert 'immediate' in response.lower() or 'now' in response.lower()
    
    def test_generate_crisis_response_high_risk(self):
        """Test crisis response generation for high-risk situations."""
        assessment = crisis_handler.assess_crisis_risk("I'm thinking about hurting myself")
        response = crisis_handler.generate_crisis_response(assessment)
        
        assert response is not None
        assert len(response) > 0
        assert '988' in response or '617' in response  # Crisis or counseling numbers
        assert 'URGENT' in response.upper() or 'support' in response.lower()
    
    def test_generate_crisis_response_moderate_risk(self):
        """Test crisis response generation for moderate-risk situations."""
        assessment = crisis_handler.assess_crisis_risk("I'm feeling hopeless")
        response = crisis_handler.generate_crisis_response(assessment)
        
        assert response is not None
        assert len(response) > 0
        assert '617' in response or '988' in response  # Should include contact numbers
    
    def test_get_crisis_resources(self):
        """Test getting crisis resources."""
        crisis_resources = crisis_handler.get_crisis_resources()
        
        assert len(crisis_resources) > 0
        assert all(resource.is_crisis_resource for resource in crisis_resources)
        
        # Should include key crisis resources
        resource_names = [r.name.lower() for r in crisis_resources]
        assert any('988' in name or 'crisis' in name or 'suicide' in name 
                  for name in resource_names)
    
    def test_should_escalate_immediately(self):
        """Test immediate escalation determination."""
        crisis_assessment = crisis_handler.assess_crisis_risk("I want to kill myself")
        moderate_assessment = crisis_handler.assess_crisis_risk("I'm feeling sad")
        
        assert crisis_handler.should_escalate_immediately(crisis_assessment) is True
        assert crisis_handler.should_escalate_immediately(moderate_assessment) is False
    
    def test_get_safety_plan_suggestions(self):
        """Test safety plan suggestions."""
        suggestions = crisis_handler.get_safety_plan_suggestions()
        
        assert len(suggestions) > 0
        assert all(isinstance(suggestion, str) for suggestion in suggestions)
        assert all(len(suggestion) > 0 for suggestion in suggestions)
        
        # Should include key safety planning elements
        suggestions_text = ' '.join(suggestions).lower()
        assert 'warning signs' in suggestions_text
        assert 'contact' in suggestions_text
        assert 'safe' in suggestions_text
    
    def test_crisis_keyword_detection(self):
        """Test detection of various crisis keywords."""
        crisis_phrases = [
            "I want to die",
            "kill myself",
            "end it all",
            "not worth living",
            "better off dead",
            "suicide",
            "harm myself"
        ]
        
        for phrase in crisis_phrases:
            assessment = crisis_handler.assess_crisis_risk(f"I feel like I should {phrase}")
            assert assessment.risk_level in [SeverityLevel.HIGH, SeverityLevel.CRISIS], \
                f"Failed to detect crisis in: {phrase}"
    
    def test_emergency_request_detection(self):
        """Test detection of emergency requests."""
        emergency_phrases = [
            "This is an emergency",
            "I need help now",
            "Crisis situation",
            "Help me please"
        ]
        
        for phrase in emergency_phrases:
            assessment = crisis_handler.assess_crisis_risk(phrase)
            assert assessment.risk_level in [SeverityLevel.MODERATE, SeverityLevel.HIGH, SeverityLevel.CRISIS], \
                f"Failed to detect urgency in: {phrase}"
    
    def test_immediate_actions_appropriateness(self):
        """Test that immediate actions are appropriate for risk level."""
        crisis_assessment = crisis_handler.assess_crisis_risk("I want to kill myself")
        moderate_assessment = crisis_handler.assess_crisis_risk("I'm feeling stressed")
        
        crisis_actions = crisis_assessment.immediate_actions
        moderate_actions = moderate_assessment.immediate_actions
        
        # Crisis actions should include emergency contacts
        crisis_text = ' '.join(crisis_actions).lower()
        assert '988' in crisis_text or '911' in crisis_text
        
        # Moderate actions should be less urgent
        moderate_text = ' '.join(moderate_actions).lower()
        assert 'schedule' in moderate_text or 'contact' in moderate_text
    
    def test_recommended_contacts_appropriateness(self):
        """Test that recommended contacts match risk level."""
        crisis_assessment = crisis_handler.assess_crisis_risk("I want to end my life")
        low_assessment = crisis_handler.assess_crisis_risk("I'm a bit worried")
        
        crisis_contacts = crisis_assessment.recommended_contacts
        low_contacts = low_assessment.recommended_contacts
        
        # Crisis contacts should include emergency numbers
        crisis_text = ' '.join(crisis_contacts)
        assert '988' in crisis_text and '911' in crisis_text
        
        # Low-risk contacts should be less urgent
        low_text = ' '.join(low_contacts)
        assert '617' in low_text  # Northeastern CAPS number

if __name__ == '__main__':
    pytest.main([__file__])