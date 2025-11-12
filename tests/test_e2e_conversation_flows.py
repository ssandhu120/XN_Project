"""End-to-End tests for complete conversation flows demonstrating full system functionality."""

import pytest
from datetime import datetime
from typing import List, Dict, Any

from conversation_flow import conversation_manager
from domain_logic import mental_health_matcher
from resource_database import resource_db
from crisis_handler import crisis_handler
from data_models import SeverityLevel, ResourceType


class TestE2EConversationFlows:
    """End-to-End tests demonstrating complete conversation flows from user input to resource recommendations."""
    
    def setup_method(self):
        """Set up fresh session for each test."""
        self.session_id = conversation_manager.start_new_session()
    
    def teardown_method(self):
        """Clean up session after each test."""
        if self.session_id in conversation_manager.active_sessions:
            conversation_manager.end_session(self.session_id)
    
    def test_e2e_academic_stress_complete_flow(self):
        """
        E2E Test: Student with academic stress gets appropriate resources and specialist recommendations.
        
        Flow: User expresses exam anxiety → System detects academic stress → 
              Provides academic coaching + counseling resources → Offers follow-up support
        """
        # Step 1: User expresses academic stress
        user_input = "I'm really overwhelmed with my upcoming final exams. I'm worried I'm going to fail and disappoint my parents. I can't sleep and I'm constantly anxious about studying."
        
        response, is_crisis = conversation_manager.process_user_message(self.session_id, user_input)
        
        # Validate crisis detection
        assert is_crisis is False, "Academic stress should not trigger crisis mode"
        
        # Validate response contains supportive content
        assert len(response) > 100, "Response should be comprehensive"
        assert any(word in response.lower() for word in ['understand', 'help', 'support', 'resources'])
        
        # Step 2: Validate session analysis
        session = conversation_manager.active_sessions[self.session_id]
        assert len(session.messages) == 1
        assert len(session.responses) == 1
        
        # Check that academic stress was identified
        assert 'academic_stress' in session.identified_concerns
        assert session.messages[0].severity_assessment in [SeverityLevel.MODERATE, SeverityLevel.LOW]
        
        # Step 3: Validate specific resource recommendations
        recommended_resource_ids = session.recommended_resources
        assert len(recommended_resource_ids) > 0
        
        # Should include academic support resources
        academic_resources = [rid for rid in recommended_resource_ids 
                            if 'academic' in rid or 'mindbridge_academic' in rid]
        assert len(academic_resources) > 0, "Should recommend academic support resources"
        
        # Should include counseling resources
        counseling_resources = [rid for rid in recommended_resource_ids 
                              if 'counseling' in rid]
        assert len(counseling_resources) > 0, "Should recommend counseling resources"
        
        # Step 4: Validate specific MindBridge Care and Northeastern resources are included
        mindbridge_resources = [rid for rid in recommended_resource_ids 
                              if 'mindbridge' in rid]
        northeastern_resources = [rid for rid in recommended_resource_ids 
                                if 'northeastern' in rid]
        
        assert len(mindbridge_resources) > 0, "Should include MindBridge Care resources"
        assert len(northeastern_resources) > 0, "Should include Northeastern resources"
        
        # Step 5: Validate contact information is available
        for resource_id in recommended_resource_ids[:3]:  # Check top 3 recommendations
            resource = resource_db.get_resource(resource_id)
            assert resource is not None
            assert len(resource.contact_info) > 0, f"Resource {resource_id} should have contact information"
            
            # Validate specific contact methods
            has_contact = any(key in resource.contact_info for key in ['phone', 'email', 'website'])
            assert has_contact, f"Resource {resource_id} should have phone, email, or website contact"
        
        # Step 6: Test follow-up conversation
        follow_up_input = "That's helpful. I'm particularly struggling with time management and study techniques."
        
        follow_up_response, _ = conversation_manager.process_user_message(self.session_id, follow_up_input)
        
        # Validate conversation continuity
        updated_session = conversation_manager.active_sessions[self.session_id]
        assert len(updated_session.messages) == 2
        assert len(updated_session.responses) == 2
        
        # Should maintain academic stress context
        assert 'academic_stress' in updated_session.identified_concerns
        
        # Should provide more specific academic resources
        assert any(word in follow_up_response.lower() 
                  for word in ['study', 'time management', 'academic', 'coaching'])
    
    def test_e2e_crisis_intervention_complete_flow(self):
        """
        E2E Test: Crisis situation triggers immediate intervention with emergency resources.
        
        Flow: User expresses suicidal ideation → System detects crisis → 
              Provides immediate crisis resources → Escalates to human intervention
        """
        # Step 1: User expresses crisis-level distress
        user_input = "I can't take this anymore. I've been thinking about killing myself. Everything feels hopeless and I don't see a way out."
        
        response, is_crisis = conversation_manager.process_user_message(self.session_id, user_input)
        
        # Validate crisis detection
        assert is_crisis is True, "Suicidal ideation should trigger crisis mode"
        
        # Validate immediate crisis response
        assert '988' in response, "Should include 988 crisis hotline"
        assert '911' in response, "Should include 911 emergency number"
        assert any(word in response.upper() for word in ['CRISIS', 'EMERGENCY', 'IMMEDIATE'])
        
        # Step 2: Validate session crisis handling
        session = conversation_manager.active_sessions[self.session_id]
        assert len(session.crisis_flags) > 0, "Should have crisis flags set"
        assert session.responses[0].requires_human_intervention is True
        assert session.messages[0].severity_assessment == SeverityLevel.CRISIS
        
        # Step 3: Validate crisis resource recommendations
        crisis_resources = resource_db.get_crisis_resources()
        crisis_resource_ids = [r.id for r in crisis_resources]
        
        # Should recommend crisis-specific resources
        recommended_crisis = [rid for rid in session.recommended_resources 
                            if rid in crisis_resource_ids]
        assert len(recommended_crisis) > 0, "Should recommend crisis resources"
        
        # Step 4: Validate emergency contact information
        for crisis_resource in crisis_resources[:3]:  # Check top 3 crisis resources
            assert crisis_resource.is_crisis_resource is True
            assert len(crisis_resource.contact_info) > 0
            
            # Crisis resources should have immediate contact methods
            has_immediate_contact = any(key in crisis_resource.contact_info 
                                     for key in ['phone', 'text'])
            assert has_immediate_contact, f"Crisis resource {crisis_resource.id} should have phone or text contact"
        
        # Step 5: Validate MindBridge Care crisis support is included
        mindbridge_crisis = resource_db.get_resource('mindbridge_crisis_support')
        assert mindbridge_crisis is not None
        assert mindbridge_crisis.is_crisis_resource is True
        assert '24/7' in mindbridge_crisis.availability
        
        # Step 6: Validate response includes safety planning
        assert any(word in response.lower() 
                  for word in ['safe', 'safety', 'plan', 'support'])
    
    def test_e2e_social_isolation_complete_flow(self):
        """
        E2E Test: Student with social isolation gets peer support and social resources.
        
        Flow: User expresses loneliness → System detects social isolation → 
              Provides peer support + social programs → Offers connection opportunities
        """
        # Step 1: User expresses social isolation
        user_input = "I feel so lonely at college. I don't have any real friends and I spend most of my time alone in my dorm. I see other students having fun together and I feel left out."
        
        response, is_crisis = conversation_manager.process_user_message(self.session_id, user_input)
        
        # Validate not crisis but supportive response
        assert is_crisis is False
        assert any(word in response.lower() for word in ['understand', 'common', 'connect', 'support'])
        
        # Step 2: Validate social isolation detection
        session = conversation_manager.active_sessions[self.session_id]
        assert 'social_isolation' in session.identified_concerns
        assert session.messages[0].severity_assessment in [SeverityLevel.MODERATE, SeverityLevel.LOW]
        
        # Step 3: Validate peer support resource recommendations
        peer_support_resources = resource_db.get_resources_by_type(ResourceType.PEER_SUPPORT)
        mindbridge_resources = resource_db.get_mindbridge_resources()
        
        # Include both peer support and MindBridge peer resources
        peer_resource_ids = [r.id for r in peer_support_resources]
        mindbridge_peer_ids = [r.id for r in mindbridge_resources if 'peer' in r.id]
        all_peer_ids = peer_resource_ids + mindbridge_peer_ids
        
        recommended_peer_support = [rid for rid in session.recommended_resources 
                                  if rid in all_peer_ids]
        assert len(recommended_peer_support) > 0, "Should recommend peer support resources"
        
        # Step 4: Validate specific social connection resources
        # Should include MindBridge peer support
        mindbridge_peer = resource_db.get_resource('mindbridge_peer_support')
        assert mindbridge_peer is not None
        assert 'peer' in mindbridge_peer.name.lower()
        assert 'app' in mindbridge_peer.contact_info or 'website' in mindbridge_peer.contact_info
        
        # Should include Northeastern peer support
        northeastern_peer = resource_db.get_resource('northeastern_peer_support')
        assert northeastern_peer is not None
        assert 'peer' in northeastern_peer.name.lower()
        
        # Step 5: Test follow-up for specific social activities
        follow_up_input = "I'm interested in joining some activities but I'm nervous about meeting new people."
        
        follow_up_response, _ = conversation_manager.process_user_message(self.session_id, follow_up_input)
        
        # Should provide supportive response and resources
        assert any(word in follow_up_response.lower() 
                  for word in ['support', 'help', 'resources', 'counseling', 'connect'])
        
        # Should maintain social isolation context
        updated_session = conversation_manager.active_sessions[self.session_id]
        assert 'social_isolation' in updated_session.identified_concerns
    
    def test_e2e_international_student_complete_flow(self):
        """
        E2E Test: International student gets cultural adjustment and specialized support.
        
        Flow: User expresses cultural challenges → System detects international student needs → 
              Provides ISSI resources + cultural support → Offers community connections
        """
        # Step 1: User expresses international student challenges
        user_input = "I'm an international student from India and I'm really struggling with homesickness. The cultural differences are overwhelming and I miss my family so much. I feel like I don't fit in here."
        
        response, is_crisis = conversation_manager.process_user_message(self.session_id, user_input)
        
        # Validate supportive response for cultural adjustment
        assert is_crisis is False
        assert any(word in response.lower() 
                  for word in ['international', 'cultural', 'adjustment', 'understand'])
        
        # Step 2: Validate international student detection
        session = conversation_manager.active_sessions[self.session_id]
        assert 'cultural_adjustment' in session.identified_concerns
        assert session.user_profile.get('is_international') is True
        
        # Step 3: Validate international student resource recommendations
        # Should include ISSI (International Student & Scholar Institute)
        issi_resource = resource_db.get_resource('northeastern_international')
        assert issi_resource is not None
        assert 'international' in issi_resource.name.lower()
        assert any('international students' in eligibility.lower() for eligibility in issi_resource.eligibility)
        
        # Should be in recommended resources
        assert 'northeastern_international' in session.recommended_resources
        
        # Step 4: Validate cultural support resources
        # Should include MindBridge counseling for cultural issues
        mindbridge_counseling = resource_db.get_resource('mindbridge_counseling')
        assert mindbridge_counseling is not None
        
        # Should include general counseling
        northeastern_counseling = resource_db.get_resource('northeastern_counseling')
        assert northeastern_counseling is not None
        
        # Step 5: Validate contact information for international services
        assert len(issi_resource.contact_info) > 0
        assert 'phone' in issi_resource.contact_info
        assert 'email' in issi_resource.contact_info
        assert 'location' in issi_resource.contact_info
        
        # Step 6: Test follow-up for specific cultural concerns
        follow_up_input = "I'm also having trouble with the academic system here. The teaching style is so different from what I'm used to."
        
        follow_up_response, _ = conversation_manager.process_user_message(self.session_id, follow_up_input)
        
        # Should address both cultural and academic aspects
        assert any(word in follow_up_response.lower() 
                  for word in ['academic', 'cultural', 'adjustment', 'support'])
        
        # Should maintain international student context
        updated_session = conversation_manager.active_sessions[self.session_id]
        assert updated_session.user_profile.get('is_international') is True
        assert 'cultural_adjustment' in updated_session.identified_concerns
    
    def test_e2e_multi_turn_conversation_context_retention(self):
        """
        E2E Test: Multi-turn conversation maintains context and builds understanding.
        
        Flow: Initial concern → Follow-up questions → Deeper exploration → 
              Refined recommendations → Ongoing support planning
        """
        # Turn 1: Initial expression of multiple concerns
        turn1_input = "I'm having a really hard time this semester. I'm stressed about my grades and I feel isolated from other students."
        
        response1, _ = conversation_manager.process_user_message(self.session_id, turn1_input)
        
        session = conversation_manager.active_sessions[self.session_id]
        initial_concerns = set(session.identified_concerns)
        initial_resources = set(session.recommended_resources)
        
        # Should identify multiple concern categories
        assert len(initial_concerns) >= 2
        assert 'academic_stress' in initial_concerns
        assert 'social_isolation' in initial_concerns
        
        # Turn 2: User provides more specific information
        turn2_input = "The academic stress is really the biggest issue. I'm a pre-med student and I'm worried about my GPA affecting my chances for medical school."
        
        response2, _ = conversation_manager.process_user_message(self.session_id, turn2_input)
        
        # Should maintain context and refine understanding
        updated_session = conversation_manager.active_sessions[self.session_id]
        assert len(updated_session.messages) == 2
        assert len(updated_session.responses) == 2
        
        # Should still remember both concerns but focus on academic
        current_concerns = set(updated_session.identified_concerns)
        assert initial_concerns.issubset(current_concerns)  # Should retain previous concerns
        
        # Should provide more specific academic guidance
        assert any(word in response2.lower() 
                  for word in ['academic', 'gpa', 'pre-med', 'medical school'])
        
        # Turn 3: User asks about specific resources
        turn3_input = "What kind of academic support is available? I need help with study strategies and time management."
        
        response3, _ = conversation_manager.process_user_message(self.session_id, turn3_input)
        
        # Should provide specific resource information
        final_session = conversation_manager.active_sessions[self.session_id]
        assert len(final_session.messages) == 3
        
        # Should include specific academic resources in response
        assert any(word in response3.lower() 
                  for word in ['academic success', 'study', 'time management', 'coaching'])
        
        # Should have accumulated comprehensive resource recommendations
        final_resources = set(final_session.recommended_resources)
        assert len(final_resources) >= len(initial_resources)  # Should have same or more resources
        
        # Should include both MindBridge and Northeastern academic resources
        academic_resources = [rid for rid in final_resources 
                            if 'academic' in rid]
        assert len(academic_resources) > 0
        
        # Validate session summary captures the full conversation
        session_summary = conversation_manager.get_session_summary(self.session_id)
        assert session_summary['message_count'] == 3
        assert session_summary['response_count'] == 3
        assert len(session_summary['identified_concerns']) >= 2
    
    def test_e2e_resource_contact_information_completeness(self):
        """
        E2E Test: Validates that recommended resources include complete contact information for specialists.
        
        Ensures users can actually reach the mental health professionals and services recommended.
        """
        # Test with general mental health concern
        user_input = "I think I need to talk to someone about my mental health. I'm not sure where to start."
        
        response, _ = conversation_manager.process_user_message(self.session_id, user_input)
        
        session = conversation_manager.active_sessions[self.session_id]
        recommended_resources = session.recommended_resources
        
        # Should have resource recommendations
        assert len(recommended_resources) >= 2
        
        # Validate each recommended resource has complete contact information
        for resource_id in recommended_resources:
            resource = resource_db.get_resource(resource_id)
            assert resource is not None, f"Resource {resource_id} should exist in database"
            
            # Each resource should have contact information
            assert len(resource.contact_info) > 0, f"Resource {resource.name} should have contact info"
            
            # Validate specific contact methods based on resource type
            if resource.resource_type == ResourceType.CRISIS_SUPPORT:
                # Crisis resources must have phone contact
                assert 'phone' in resource.contact_info, f"Crisis resource {resource.name} must have phone"
                
            elif resource.resource_type == ResourceType.COUNSELING:
                # Counseling resources should have phone and/or email
                has_direct_contact = any(key in resource.contact_info 
                                       for key in ['phone', 'email'])
                assert has_direct_contact, f"Counseling resource {resource.name} should have phone or email"
                
            elif resource.resource_type == ResourceType.MINDBRIDGE_BENEFIT:
                # MindBridge resources should have website or phone
                has_mindbridge_contact = any(key in resource.contact_info 
                                           for key in ['website', 'phone', 'app'])
                assert has_mindbridge_contact, f"MindBridge resource {resource.name} should have website, phone, or app"
            
            # Validate availability information
            assert len(resource.availability) > 0, f"Resource {resource.name} should have availability info"
            
            # Validate cost information
            assert len(resource.cost) > 0, f"Resource {resource.name} should have cost info"
        
        # Validate response includes contact information
        assert any(contact in response for contact in ['617', '988', '1-800', 'phone', 'email'])
        
        # Validate specific key resources are included
        key_resources = ['northeastern_counseling', 'mindbridge_counseling']
        included_key_resources = [rid for rid in recommended_resources if rid in key_resources]
        assert len(included_key_resources) > 0, "Should include key counseling resources"
        
        # Validate MindBridge Care specialist access
        mindbridge_resources = resource_db.get_mindbridge_resources()
        mindbridge_counseling = next((r for r in mindbridge_resources if 'counseling' in r.id), None)
        
        assert mindbridge_counseling is not None
        assert 'therapists' in mindbridge_counseling.description.lower() or 'counselors' in mindbridge_counseling.description.lower()
        assert 'licensed' in mindbridge_counseling.description.lower()
    
    def test_e2e_severity_escalation_and_resource_matching(self):
        """
        E2E Test: Validates that resource recommendations match severity levels appropriately.
        
        Tests that higher severity situations get more intensive resources and faster access.
        """
        # Test progression from low to high severity
        
        # Low severity: General stress
        low_severity_input = "I'm feeling a bit stressed about college life in general."
        response1, _ = conversation_manager.process_user_message(self.session_id, low_severity_input)
        
        session = conversation_manager.active_sessions[self.session_id]
        assert session.messages[0].severity_assessment == SeverityLevel.LOW
        
        # Should get general support resources
        low_severity_resources = session.recommended_resources
        assert len(low_severity_resources) > 0
        
        # Start new session for moderate severity test
        moderate_session_id = conversation_manager.start_new_session()
        
        # Moderate severity: Specific academic anxiety
        moderate_input = "I'm having panic attacks before exams and can't sleep. I'm really worried about failing."
        response2, _ = conversation_manager.process_user_message(moderate_session_id, moderate_input)
        
        moderate_session = conversation_manager.active_sessions[moderate_session_id]
        assert moderate_session.messages[0].severity_assessment in [SeverityLevel.MODERATE, SeverityLevel.HIGH]
        
        # Should get more specific and intensive resources
        moderate_resources = moderate_session.recommended_resources
        assert len(moderate_resources) >= len(low_severity_resources)
        
        # Should include counseling resources for moderate severity
        counseling_resources = [rid for rid in moderate_resources if 'counseling' in rid]
        assert len(counseling_resources) > 0
        
        # Start new session for high severity test
        high_session_id = conversation_manager.start_new_session()
        
        # High severity: Self-harm thoughts (but not suicidal)
        high_input = "I've been having thoughts about hurting myself when I get overwhelmed. I don't want to die, but I don't know how to cope."
        response3, is_crisis = conversation_manager.process_user_message(high_session_id, high_input)
        
        high_session = conversation_manager.active_sessions[high_session_id]
        assert high_session.messages[0].severity_assessment in [SeverityLevel.HIGH, SeverityLevel.CRISIS]
        
        # Should get immediate and comprehensive resources
        high_resources = high_session.recommended_resources
        
        # Should include crisis resources even if not full crisis
        if not is_crisis:
            # Should still include urgent support resources
            assert len(high_resources) > 0
            assert any('counseling' in rid for rid in high_resources)
        
        # Validate escalation in resource intensity
        # Higher severity should include more immediate contact options
        for resource_id in high_resources[:3]:  # Check top 3
            resource = resource_db.get_resource(resource_id)
            if resource and resource.resource_type in [ResourceType.COUNSELING, ResourceType.CRISIS_SUPPORT]:
                # Should have immediate contact methods
                has_immediate_contact = 'phone' in resource.contact_info
                assert has_immediate_contact, f"High severity resource {resource.name} should have phone contact"
        
        # Clean up additional sessions
        conversation_manager.end_session(moderate_session_id)
        conversation_manager.end_session(high_session_id)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])