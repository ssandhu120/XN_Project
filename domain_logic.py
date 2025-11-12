"""Core domain logic for matching user situations to mental health resources."""

from typing import List, Dict, Tuple, Optional
from data_models import (
    MentalHealthScenario, Resource, Recommendation, UserMessage, 
    SeverityLevel, CrisisAssessment
)
from scenario_data import scenario_db
from resource_database import resource_db
from crisis_handler import crisis_handler
from utils.text_processing import text_processor
from utils.logger import logger

class MentalHealthMatcher:
    """Core logic for matching user needs to appropriate resources and scenarios."""
    
    def __init__(self):
        self.scenario_weights = {
            SeverityLevel.CRISIS: 1.0,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.MODERATE: 0.6,
            SeverityLevel.LOW: 0.4
        }
    
    def analyze_user_input(self, user_input: str, conversation_history: List[str] = None) -> Dict:
        """Comprehensive analysis of user input to determine appropriate response."""
        # Clean and process text
        cleaned_input = text_processor.clean_text(user_input)
        keywords = text_processor.extract_keywords(cleaned_input)
        severity = text_processor.assess_severity(cleaned_input, keywords)
        categories = text_processor.categorize_concern(cleaned_input, keywords)
        emotions = text_processor.extract_emotions(cleaned_input)
        
        # Crisis assessment
        crisis_assessment = crisis_handler.assess_crisis_risk(cleaned_input, conversation_history)
        
        # Find matching scenarios
        matching_scenarios = self._find_matching_scenarios(keywords, categories, severity)
        
        # Generate resource recommendations
        recommendations = self._generate_recommendations(
            matching_scenarios, keywords, categories, severity, crisis_assessment
        )
        
        analysis = {
            'original_input': user_input,
            'cleaned_input': cleaned_input,
            'keywords': keywords,
            'severity': severity,
            'categories': categories,
            'emotions': emotions,
            'crisis_assessment': crisis_assessment,
            'matching_scenarios': matching_scenarios,
            'recommendations': recommendations,
            'requires_immediate_attention': crisis_assessment.requires_immediate_intervention
        }
        
        # Log the interaction
        logger.log_user_interaction(
            session_id="current", 
            interaction_type="analysis",
            severity=severity.value
        )
        
        return analysis
    
    def _find_matching_scenarios(self, keywords: List[str], categories: List[str], 
                                severity: SeverityLevel) -> List[MentalHealthScenario]:
        """Find scenarios that match user input."""
        matching_scenarios = []
        
        # First, try to match by keywords
        for category in categories:
            category_scenarios = scenario_db.get_scenarios_by_category(category)
            for scenario in category_scenarios:
                relevance_score = self._calculate_scenario_relevance(scenario, keywords, severity)
                if relevance_score > 0.3:  # Threshold for relevance
                    matching_scenarios.append((scenario, relevance_score))
        
        # If no category matches, search all scenarios by keywords
        if not matching_scenarios:
            all_matching = scenario_db.find_matching_scenarios(keywords)
            for scenario in all_matching[:3]:  # Top 3 matches
                relevance_score = self._calculate_scenario_relevance(scenario, keywords, severity)
                matching_scenarios.append((scenario, relevance_score))
        
        # Sort by relevance score and return scenarios
        matching_scenarios.sort(key=lambda x: x[1], reverse=True)
        return [scenario for scenario, _ in matching_scenarios[:5]]  # Top 5 scenarios
    
    def _calculate_scenario_relevance(self, scenario: MentalHealthScenario, 
                                    keywords: List[str], severity: SeverityLevel) -> float:
        """Calculate how relevant a scenario is to the user input."""
        relevance_score = 0.0
        
        # Keyword matching (40% of score)
        keyword_matches = sum(1 for keyword in keywords 
                            if any(k.lower() in keyword.lower() or keyword.lower() in k.lower() 
                                  for k in scenario.keywords))
        keyword_score = min(keyword_matches / len(scenario.keywords), 1.0) * 0.4
        relevance_score += keyword_score
        
        # Severity matching (30% of score)
        severity_weight = self.scenario_weights.get(scenario.severity, 0.5)
        user_severity_weight = self.scenario_weights.get(severity, 0.5)
        severity_score = (1.0 - abs(severity_weight - user_severity_weight)) * 0.3
        relevance_score += severity_score
        
        # Category bonus (30% of score)
        # This would be calculated based on category matching in the calling function
        relevance_score += 0.3  # Base category score if we got here
        
        return relevance_score
    
    def _generate_recommendations(self, scenarios: List[MentalHealthScenario], 
                                keywords: List[str], categories: List[str],
                                severity: SeverityLevel, 
                                crisis_assessment: CrisisAssessment) -> List[Recommendation]:
        """Generate personalized resource recommendations."""
        recommendations = []
        
        # Crisis resources always come first
        if crisis_assessment.requires_immediate_intervention:
            crisis_resources = resource_db.get_crisis_resources()
            for i, resource in enumerate(crisis_resources[:3]):
                recommendations.append(Recommendation(
                    resource_id=resource.id,
                    resource_name=resource.name,
                    relevance_score=1.0,
                    reasoning="Immediate crisis support needed",
                    priority=i + 1,
                    is_immediate=True,
                    follow_up_actions=["Contact immediately", "Ensure safety"]
                ))
        
        # Scenario-based recommendations
        for scenario in scenarios[:2]:  # Top 2 scenarios
            scenario_resources = resource_db.get_recommended_resources_for_scenario(scenario.id)
            for resource in scenario_resources:
                if not any(r.resource_id == resource.id for r in recommendations):
                    relevance_score = self._calculate_resource_relevance(
                        resource, keywords, categories, severity
                    )
                    recommendations.append(Recommendation(
                        resource_id=resource.id,
                        resource_name=resource.name,
                        relevance_score=relevance_score,
                        reasoning=f"Recommended for {scenario.title.lower()}",
                        priority=len(recommendations) + 1,
                        follow_up_actions=self._get_follow_up_actions(resource, severity)
                    ))
        
        # Category-based recommendations
        category_resources = self._get_category_resources(categories, severity)
        for resource in category_resources:
            if not any(r.resource_id == resource.id for r in recommendations):
                relevance_score = self._calculate_resource_relevance(
                    resource, keywords, categories, severity
                )
                recommendations.append(Recommendation(
                    resource_id=resource.id,
                    resource_name=resource.name,
                    relevance_score=relevance_score,
                    reasoning=f"Relevant for {', '.join(categories)}",
                    priority=len(recommendations) + 1,
                    follow_up_actions=self._get_follow_up_actions(resource, severity)
                ))
        
        # Always include general counseling if not already present
        general_counseling = ["northeastern_counseling", "mindbridge_counseling"]
        for resource_id in general_counseling:
            if not any(r.resource_id == resource_id for r in recommendations):
                resource = resource_db.get_resource(resource_id)
                if resource:
                    recommendations.append(Recommendation(
                        resource_id=resource.id,
                        resource_name=resource.name,
                        relevance_score=0.7,
                        reasoning="General mental health support",
                        priority=len(recommendations) + 1,
                        follow_up_actions=["Schedule appointment", "Discuss concerns"]
                    ))
        
        # Sort by priority and relevance
        recommendations.sort(key=lambda r: (r.priority, -r.relevance_score))
        
        logger.log_resource_recommendation("current", len(recommendations))
        return recommendations[:6]  # Top 6 recommendations
    
    def _calculate_resource_relevance(self, resource: Resource, keywords: List[str],
                                    categories: List[str], severity: SeverityLevel) -> float:
        """Calculate how relevant a resource is to the user's needs."""
        relevance_score = 0.5  # Base score
        
        # Crisis resources get highest priority for high severity
        if resource.is_crisis_resource and severity in [SeverityLevel.HIGH, SeverityLevel.CRISIS]:
            relevance_score += 0.4
        
        # MindBridge resources get bonus for comprehensive care
        if "mindbridge" in resource.id.lower():
            relevance_score += 0.2
        
        # Northeastern resources get bonus for accessibility
        if "northeastern" in resource.id.lower():
            relevance_score += 0.1
        
        # Keyword matching in resource description
        resource_text = f"{resource.name} {resource.description}".lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in resource_text)
        relevance_score += min(keyword_matches * 0.1, 0.3)
        
        return min(relevance_score, 1.0)
    
    def _get_category_resources(self, categories: List[str], severity: SeverityLevel) -> List[Resource]:
        """Get resources relevant to specific categories."""
        category_resource_mapping = {
            'academic_stress': ['northeastern_academic_support', 'mindbridge_academic_coaching'],
            'social_isolation': ['northeastern_peer_support', 'mindbridge_peer_support'],
            'cultural_adjustment': ['northeastern_international', 'mindbridge_counseling'],
            'self_esteem': ['northeastern_counseling', 'mindbridge_counseling'],
            'crisis': ['crisis_hotline', 'northeastern_emergency', 'mindbridge_crisis_support'],
            'anxiety': ['northeastern_counseling', 'mindbridge_counseling'],
            'family_relationships': ['northeastern_counseling', 'mindbridge_counseling'],
            'financial_stress': ['northeastern_academic_support', 'mindbridge_wellness_programs']
        }
        
        resources = []
        for category in categories:
            resource_ids = category_resource_mapping.get(category, [])
            for resource_id in resource_ids:
                resource = resource_db.get_resource(resource_id)
                if resource and resource not in resources:
                    resources.append(resource)
        
        return resources
    
    def _get_follow_up_actions(self, resource: Resource, severity: SeverityLevel) -> List[str]:
        """Get appropriate follow-up actions for a resource."""
        if resource.is_crisis_resource:
            return ["Contact immediately", "Prioritize safety", "Follow crisis protocol"]
        elif severity == SeverityLevel.HIGH:
            return ["Contact within 24 hours", "Schedule urgent appointment", "Monitor symptoms"]
        elif severity == SeverityLevel.MODERATE:
            return ["Schedule appointment this week", "Prepare questions to ask", "Consider ongoing support"]
        else:
            return ["Contact when ready", "Explore available services", "Consider preventive support"]
    
    def get_conversation_context(self, analysis: Dict) -> Dict:
        """Extract context for LLM conversation generation."""
        return {
            'severity': analysis['severity'].value,
            'categories': analysis['categories'],
            'matched_scenarios': [s.id for s in analysis['matching_scenarios']],
            'recommended_resources': [r.resource_name for r in analysis['recommendations'][:3]],
            'emotions': analysis['emotions'],
            'crisis_detected': analysis['requires_immediate_attention']
        }
    
    def format_recommendations_for_display(self, recommendations: List[Recommendation]) -> str:
        """Format recommendations for user display."""
        if not recommendations:
            return "I'd recommend reaching out to Northeastern CAPS at (617) 373-2772 or MindBridge Care at 1-800-MINDBRIDGE for personalized support."
        
        formatted_parts = ["**Recommended Resources:**\n"]
        
        for i, rec in enumerate(recommendations[:4], 1):  # Top 4 for display
            resource = resource_db.get_resource(rec.resource_id)
            if resource:
                priority_indicator = "🚨" if rec.is_immediate else f"{i}."
                formatted_parts.append(f"{priority_indicator} **{resource.name}**")
                
                if resource.contact_info.get('phone'):
                    formatted_parts.append(f"   📞 {resource.contact_info['phone']}")
                if resource.contact_info.get('website'):
                    formatted_parts.append(f"   🌐 {resource.contact_info['website']}")
                
                formatted_parts.append(f"   *{rec.reasoning}*")
                formatted_parts.append("")
        
        return "\n".join(formatted_parts)

# Global matcher instance
mental_health_matcher = MentalHealthMatcher()