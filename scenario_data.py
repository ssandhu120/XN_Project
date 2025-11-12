"""Mental health scenarios database based on college student needs."""

from typing import Dict, List
from data_models import MentalHealthScenario, SeverityLevel

class ScenarioDatabase:
    """Database of mental health scenarios for college students."""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> Dict[str, MentalHealthScenario]:
        """Initialize the database with predefined scenarios."""
        scenarios = {}
        
        # Academic Stress Scenarios
        scenarios["academic_exam_anxiety"] = MentalHealthScenario(
            id="academic_exam_anxiety",
            title="Exam Anxiety and Academic Pressure",
            description="Student experiencing severe anxiety about upcoming exams and academic performance",
            keywords=["exam", "test", "anxiety", "academic", "pressure", "grade", "study"],
            severity=SeverityLevel.MODERATE,
            category="academic_stress",
            common_triggers=["upcoming exams", "poor grades", "time pressure", "competition"],
            recommended_resources=["academic_support", "counseling", "study_skills"],
            response_templates=[
                "I understand exam anxiety can feel overwhelming. Let's explore some strategies to help you manage this stress.",
                "Academic pressure is common among college students. There are effective ways to cope with exam anxiety."
            ]
        )
        
        scenarios["academic_failure_fear"] = MentalHealthScenario(
            id="academic_failure_fear",
            title="Fear of Academic Failure",
            description="Student worried about failing classes or not meeting academic expectations",
            keywords=["failing", "failure", "academic", "disappointed", "expectations", "parents"],
            severity=SeverityLevel.MODERATE,
            category="academic_stress",
            common_triggers=["poor performance", "family expectations", "scholarship concerns"],
            recommended_resources=["academic_advisor", "counseling", "mindbridge_academic_support"],
            response_templates=[
                "Fear of failure can be paralyzing, but remember that setbacks are part of learning.",
                "Let's talk about realistic expectations and strategies to improve your academic situation."
            ]
        )
        
        # Social Isolation Scenarios
        scenarios["loneliness_isolation"] = MentalHealthScenario(
            id="loneliness_isolation",
            title="Loneliness and Social Isolation",
            description="Student feeling lonely and having difficulty making connections",
            keywords=["lonely", "alone", "isolated", "friends", "social", "connection"],
            severity=SeverityLevel.MODERATE,
            category="social_isolation",
            common_triggers=["new environment", "social anxiety", "introversion", "rejection"],
            recommended_resources=["peer_support", "social_activities", "counseling"],
            response_templates=[
                "Feeling lonely in college is more common than you might think. Many students struggle with this.",
                "Building connections takes time. Let's explore some ways to help you meet like-minded people."
            ]
        )
        
        scenarios["roommate_conflict"] = MentalHealthScenario(
            id="roommate_conflict",
            title="Roommate and Living Situation Conflicts",
            description="Student experiencing stress from roommate conflicts or living arrangements",
            keywords=["roommate", "living", "conflict", "dorm", "apartment", "housing"],
            severity=SeverityLevel.LOW,
            category="social_isolation",
            common_triggers=["personality differences", "lifestyle conflicts", "boundaries"],
            recommended_resources=["residential_life", "mediation", "counseling"],
            response_templates=[
                "Roommate conflicts can significantly impact your well-being. Let's discuss some resolution strategies.",
                "Living with others requires compromise and communication. I can help you navigate this situation."
            ]
        )
        
        # International Student Scenarios
        scenarios["homesickness_cultural"] = MentalHealthScenario(
            id="homesickness_cultural",
            title="Homesickness and Cultural Adjustment",
            description="International student struggling with homesickness and cultural adaptation",
            keywords=["homesick", "home", "culture", "international", "family", "country", "adjustment"],
            severity=SeverityLevel.MODERATE,
            category="cultural_adjustment",
            common_triggers=["distance from family", "cultural differences", "language barriers"],
            recommended_resources=["international_student_services", "cultural_groups", "counseling"],
            response_templates=[
                "Homesickness is a natural response to being far from home. Many international students experience this.",
                "Cultural adjustment takes time. Let's explore resources specifically designed for international students."
            ]
        )
        
        scenarios["language_academic_barrier"] = MentalHealthScenario(
            id="language_academic_barrier",
            title="Language Barriers in Academic Settings",
            description="Student struggling with language barriers affecting academic performance",
            keywords=["language", "english", "communication", "academic", "understanding", "barrier"],
            severity=SeverityLevel.MODERATE,
            category="cultural_adjustment",
            common_triggers=["complex academic language", "participation anxiety", "comprehension issues"],
            recommended_resources=["language_support", "academic_support", "tutoring"],
            response_templates=[
                "Language barriers in academic settings can be challenging. There are specific resources to help you succeed.",
                "Many international students face similar challenges. Let's find the right support for your language needs."
            ]
        )
        
        # Self-Esteem and Confidence Scenarios
        scenarios["low_self_esteem"] = MentalHealthScenario(
            id="low_self_esteem",
            title="Low Self-Esteem and Confidence Issues",
            description="Student struggling with self-worth and confidence",
            keywords=["confidence", "self-esteem", "worth", "inadequate", "failure", "imposter"],
            severity=SeverityLevel.MODERATE,
            category="self_esteem",
            common_triggers=["comparison with others", "past failures", "perfectionism"],
            recommended_resources=["counseling", "self_help_groups", "mindbridge_confidence_building"],
            response_templates=[
                "Self-esteem issues are common among college students. You're not alone in feeling this way.",
                "Building confidence is a process. Let's explore strategies to help you recognize your strengths."
            ]
        )
        
        scenarios["imposter_syndrome"] = MentalHealthScenario(
            id="imposter_syndrome",
            title="Imposter Syndrome",
            description="Student feeling like they don't belong or deserve their achievements",
            keywords=["imposter", "don't belong", "fraud", "deserve", "luck", "fake"],
            severity=SeverityLevel.MODERATE,
            category="self_esteem",
            common_triggers=["academic success", "competitive environment", "high expectations"],
            recommended_resources=["counseling", "peer_support", "mindbridge_success_coaching"],
            response_templates=[
                "Imposter syndrome affects many high-achieving students. Your feelings are valid and addressable.",
                "You've earned your place here. Let's work on recognizing your legitimate accomplishments."
            ]
        )
        
        # Crisis Scenarios
        scenarios["suicidal_ideation"] = MentalHealthScenario(
            id="suicidal_ideation",
            title="Suicidal Thoughts and Crisis",
            description="Student expressing suicidal thoughts or in mental health crisis",
            keywords=["suicide", "kill myself", "end it all", "not worth living", "die", "harm myself"],
            severity=SeverityLevel.CRISIS,
            category="crisis",
            common_triggers=["overwhelming stress", "hopelessness", "isolation", "trauma"],
            recommended_resources=["crisis_hotline", "emergency_services", "immediate_counseling"],
            response_templates=[
                "I'm very concerned about what you're sharing. Your life has value and there is help available.",
                "This sounds like a crisis situation. Let me connect you with immediate professional support."
            ]
        )
        
        scenarios["panic_attacks"] = MentalHealthScenario(
            id="panic_attacks",
            title="Panic Attacks and Severe Anxiety",
            description="Student experiencing panic attacks or severe anxiety episodes",
            keywords=["panic", "attack", "can't breathe", "heart racing", "overwhelming", "anxiety"],
            severity=SeverityLevel.HIGH,
            category="anxiety",
            common_triggers=["stress", "academic pressure", "social situations", "health anxiety"],
            recommended_resources=["counseling", "anxiety_management", "mindbridge_crisis_support"],
            response_templates=[
                "Panic attacks can be frightening, but they are treatable. Let's get you connected with appropriate support.",
                "You're experiencing something very real and manageable with the right help."
            ]
        )
        
        # Relationship and Family Scenarios
        scenarios["family_pressure"] = MentalHealthScenario(
            id="family_pressure",
            title="Family Pressure and Expectations",
            description="Student struggling with family expectations and pressure",
            keywords=["family", "parents", "pressure", "expectations", "disappointed", "career"],
            severity=SeverityLevel.MODERATE,
            category="family_relationships",
            common_triggers=["career choices", "academic performance", "cultural expectations"],
            recommended_resources=["counseling", "family_therapy", "mindbridge_family_support"],
            response_templates=[
                "Family pressure can be intense, especially when it conflicts with your own goals.",
                "Balancing family expectations with personal autonomy is challenging but manageable."
            ]
        )
        
        scenarios["relationship_breakup"] = MentalHealthScenario(
            id="relationship_breakup",
            title="Relationship Issues and Breakups",
            description="Student dealing with relationship problems or recent breakup",
            keywords=["relationship", "breakup", "boyfriend", "girlfriend", "dating", "heartbreak"],
            severity=SeverityLevel.MODERATE,
            category="relationships",
            common_triggers=["breakup", "conflict", "long-distance", "trust issues"],
            recommended_resources=["counseling", "peer_support", "mindbridge_relationship_support"],
            response_templates=[
                "Relationship difficulties can significantly impact your emotional well-being.",
                "Breakups are painful, but they're also opportunities for growth and self-discovery."
            ]
        )
        
        # Financial Stress Scenarios
        scenarios["financial_stress"] = MentalHealthScenario(
            id="financial_stress",
            title="Financial Stress and Money Worries",
            description="Student experiencing stress related to financial concerns",
            keywords=["money", "financial", "debt", "tuition", "job", "work", "afford"],
            severity=SeverityLevel.MODERATE,
            category="financial_stress",
            common_triggers=["tuition costs", "living expenses", "job loss", "family financial issues"],
            recommended_resources=["financial_aid", "career_services", "mindbridge_financial_wellness"],
            response_templates=[
                "Financial stress is a major concern for many college students. There are resources to help.",
                "Money worries can affect your mental health and academic performance. Let's explore your options."
            ]
        )
        
        # Provider Search Scenario
        scenarios["provider_search_request"] = MentalHealthScenario(
            id="provider_search_request",
            title="Finding Mental Health Providers",
            description="Student requesting help finding mental health providers in their area",
            keywords=["find provider", "find therapist", "need help finding", "therapy near me", "mental health provider"],
            severity=SeverityLevel.MODERATE,
            category="provider_search",
            common_triggers=["need ongoing support", "want professional help", "insurance coverage"],
            recommended_resources=["provider_search", "mindbridge_provider_network"],
            response_templates=[
                "I'd be happy to help you find mental health providers that match your needs and insurance.",
                "Let me help you find qualified therapists and counselors in your area."
            ]
        )
        
        return scenarios
    
    def get_scenario(self, scenario_id: str) -> MentalHealthScenario:
        """Get a specific scenario by ID."""
        return self.scenarios.get(scenario_id)
    
    def find_matching_scenarios(self, keywords: List[str], category: str = None) -> List[MentalHealthScenario]:
        """Find scenarios that match given keywords and optional category."""
        matching_scenarios = []
        
        for scenario in self.scenarios.values():
            if category and scenario.category != category:
                continue
            
            # Check if any keywords match
            keyword_matches = any(
                keyword.lower() in [k.lower() for k in scenario.keywords]
                for keyword in keywords
            )
            
            if keyword_matches:
                matching_scenarios.append(scenario)
        
        # Sort by severity (crisis first, then high, moderate, low)
        severity_order = {
            SeverityLevel.CRISIS: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MODERATE: 2,
            SeverityLevel.LOW: 3
        }
        
        matching_scenarios.sort(key=lambda s: severity_order[s.severity])
        return matching_scenarios
    
    def get_scenarios_by_category(self, category: str) -> List[MentalHealthScenario]:
        """Get all scenarios in a specific category."""
        return [s for s in self.scenarios.values() if s.category == category]
    
    def get_crisis_scenarios(self) -> List[MentalHealthScenario]:
        """Get all crisis-level scenarios."""
        return [s for s in self.scenarios.values() if s.severity == SeverityLevel.CRISIS]

# Global scenario database instance
scenario_db = ScenarioDatabase()