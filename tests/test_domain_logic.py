"""Tests for domain logic and mental health matching."""

import pytest
from data_models import SeverityLevel
from domain_logic import mental_health_matcher
from scenario_data import scenario_db
from resource_database import resource_db

class TestMentalHealthMatcher:
    """Test cases for the mental health matcher."""
    
    def test_analyze_user_input_academic_stress(self):
        """Test analysis of academic stress input."""
        user_input = "I'm really stressed about my upcoming exams and worried about failing"
        analysis = mental_health_matcher.analyze_user_input(user_input)
        
        assert 'academic_stress' in analysis['categories']
        assert analysis['severity'] in [SeverityLevel.MODERATE, SeverityLevel.LOW]
        assert len(analysis['keywords']) > 0
        assert 'exam' in analysis['keywords'] or 'stressed' in analysis['keywords']
        assert len(analysis['recommendations']) > 0
    
    def test_analyze_user_input_crisis(self):
        """Test analysis of crisis-level input."""
        user_input = "I want to kill myself, I can't take it anymore"
        analysis = mental_health_matcher.analyze_user_input(user_input)
        
        assert analysis['severity'] == SeverityLevel.CRISIS
        assert analysis['requires_immediate_attention'] is True
        assert analysis['crisis_assessment'].requires_immediate_intervention is True
        assert len(analysis['crisis_assessment'].detected_indicators) > 0
    
    def test_analyze_user_input_loneliness(self):
        """Test analysis of loneliness/social isolation input."""
        user_input = "I feel so lonely at college, I don't have any friends"
        analysis = mental_health_matcher.analyze_user_input(user_input)
        
        assert 'social_isolation' in analysis['categories']
        assert 'lonely' in analysis['keywords']
        assert len(analysis['matching_scenarios']) > 0
        
        # Check that appropriate resources are recommended
        resource_names = [r.resource_name for r in analysis['recommendations']]
        assert any('peer' in name.lower() or 'social' in name.lower() 
                  for name in resource_names)
    
    def test_analyze_user_input_international_student(self):
        """Test analysis of international student concerns."""
        user_input = "I'm an international student feeling homesick and struggling with cultural differences"
        analysis = mental_health_matcher.analyze_user_input(user_input)
        
        assert 'cultural_adjustment' in analysis['categories']
        assert any(keyword in analysis['keywords'] 
                  for keyword in ['international', 'homesick', 'culture'])
        
        # Should recommend international student services
        resource_ids = [r.resource_id for r in analysis['recommendations']]
        assert any('international' in rid for rid in resource_ids)
    
    def test_scenario_matching(self):
        """Test scenario matching functionality."""
        keywords = ['exam', 'anxiety', 'academic']
        scenarios = mental_health_matcher._find_matching_scenarios(
            keywords, ['academic_stress'], SeverityLevel.MODERATE
        )
        
        assert len(scenarios) > 0
        assert any('academic' in scenario.id for scenario in scenarios)
    
    def test_recommendation_generation(self):
        """Test resource recommendation generation."""
        # Mock analysis data
        scenarios = [scenario_db.get_scenario('academic_exam_anxiety')]
        keywords = ['exam', 'anxiety']
        categories = ['academic_stress']
        severity = SeverityLevel.MODERATE
        
        from crisis_handler import crisis_handler
        crisis_assessment = crisis_handler.assess_crisis_risk("I'm anxious about exams")
        
        recommendations = mental_health_matcher._generate_recommendations(
            scenarios, keywords, categories, severity, crisis_assessment
        )
        
        assert len(recommendations) > 0
        assert all(rec.relevance_score > 0 for rec in recommendations)
        assert all(rec.priority > 0 for rec in recommendations)
    
    def test_conversation_context_generation(self):
        """Test conversation context generation for LLM."""
        analysis = {
            'severity': SeverityLevel.MODERATE,
            'categories': ['academic_stress'],
            'matching_scenarios': [scenario_db.get_scenario('academic_exam_anxiety')],
            'recommendations': [],
            'emotions': ['anxious'],
            'requires_immediate_attention': False
        }
        
        context = mental_health_matcher.get_conversation_context(analysis)
        
        assert context['severity'] == 'moderate'
        assert 'academic_stress' in context['categories']
        assert 'anxious' in context['emotions']
        assert context['crisis_detected'] is False

class TestScenarioDatabase:
    """Test cases for scenario database."""
    
    def test_get_scenario(self):
        """Test retrieving specific scenario."""
        scenario = scenario_db.get_scenario('academic_exam_anxiety')
        assert scenario is not None
        assert scenario.id == 'academic_exam_anxiety'
        assert scenario.severity == SeverityLevel.MODERATE
    
    def test_find_matching_scenarios(self):
        """Test finding scenarios by keywords."""
        keywords = ['exam', 'anxiety']
        scenarios = scenario_db.find_matching_scenarios(keywords)
        
        assert len(scenarios) > 0
        assert any('academic' in scenario.id for scenario in scenarios)
    
    def test_get_scenarios_by_category(self):
        """Test retrieving scenarios by category."""
        academic_scenarios = scenario_db.get_scenarios_by_category('academic_stress')
        assert len(academic_scenarios) > 0
        assert all(scenario.category == 'academic_stress' for scenario in academic_scenarios)
    
    def test_get_crisis_scenarios(self):
        """Test retrieving crisis scenarios."""
        crisis_scenarios = scenario_db.get_crisis_scenarios()
        assert len(crisis_scenarios) > 0
        assert all(scenario.severity == SeverityLevel.CRISIS for scenario in crisis_scenarios)

class TestResourceDatabase:
    """Test cases for resource database."""
    
    def test_get_resource(self):
        """Test retrieving specific resource."""
        resource = resource_db.get_resource('northeastern_counseling')
        assert resource is not None
        assert resource.id == 'northeastern_counseling'
        assert 'northeastern' in resource.name.lower()
    
    def test_get_crisis_resources(self):
        """Test retrieving crisis resources."""
        crisis_resources = resource_db.get_crisis_resources()
        assert len(crisis_resources) > 0
        assert all(resource.is_crisis_resource for resource in crisis_resources)
    
    def test_get_mindbridge_resources(self):
        """Test retrieving MindBridge Care resources."""
        mindbridge_resources = resource_db.get_mindbridge_resources()
        assert len(mindbridge_resources) > 0
        assert all('mindbridge' in resource.id.lower() for resource in mindbridge_resources)
    
    def test_search_resources(self):
        """Test resource search functionality."""
        keywords = ['counseling', 'therapy']
        resources = resource_db.search_resources(keywords)
        
        assert len(resources) > 0
        # Should find counseling-related resources
        assert any('counseling' in resource.name.lower() or 
                  'counseling' in resource.description.lower() 
                  for resource in resources)
    
    def test_get_recommended_resources_for_scenario(self):
        """Test getting recommended resources for specific scenarios."""
        resources = resource_db.get_recommended_resources_for_scenario('academic_exam_anxiety')
        assert len(resources) > 0
        
        # Should include academic support resources
        resource_names = [r.name.lower() for r in resources]
        assert any('academic' in name or 'counseling' in name for name in resource_names)

if __name__ == '__main__':
    pytest.main([__file__])