"""Database of mental health resources including MindBridge Care and Northeastern services."""

from typing import Dict, List
from data_models import Resource, ResourceType

class ResourceDatabase:
    """Database of mental health resources and services."""
    
    def __init__(self):
        self.resources = self._initialize_resources()
    
    def _initialize_resources(self) -> Dict[str, Resource]:
        """Initialize the database with available resources."""
        resources = {}
        
        # Crisis Resources
        resources["crisis_hotline"] = Resource(
            id="crisis_hotline",
            name="988 Suicide & Crisis Lifeline",
            description="24/7 free and confidential support for people in distress",
            resource_type=ResourceType.CRISIS_SUPPORT,
            contact_info={"phone": "988", "text": "Text HOME to 741741"},
            availability="24/7",
            cost="Free",
            is_crisis_resource=True
        )
        
        resources["northeastern_emergency"] = Resource(
            id="northeastern_emergency",
            name="Northeastern Emergency Mental Health",
            description="24/7 emergency mental health support for Northeastern students",
            resource_type=ResourceType.CRISIS_SUPPORT,
            contact_info={"phone": "(617) 373-3333", "location": "Northeastern University Police"},
            availability="24/7",
            cost="Free",
            eligibility=["Northeastern students"],
            is_crisis_resource=True
        )
        
        # Northeastern Counseling Services
        resources["northeastern_counseling"] = Resource(
            id="northeastern_counseling",
            name="Northeastern University Counseling and Psychological Services (CAPS)",
            description="Professional counseling services for Northeastern students",
            resource_type=ResourceType.COUNSELING,
            contact_info={
                "phone": "(617) 373-2772",
                "location": "346 Huntington Avenue, Suite 506",
                "email": "counseling@northeastern.edu"
            },
            availability="Monday-Friday 8:30 AM - 5:00 PM",
            cost="Free",
            eligibility=["Northeastern students"],
            website="https://www.northeastern.edu/uhcs/caps/"
        )
        
        resources["northeastern_group_therapy"] = Resource(
            id="northeastern_group_therapy",
            name="CAPS Group Therapy Programs",
            description="Various group therapy options including anxiety, depression, and social skills groups",
            resource_type=ResourceType.COUNSELING,
            contact_info={"phone": "(617) 373-2772"},
            availability="Various times throughout semester",
            cost="Free",
            eligibility=["Northeastern students"]
        )
        
        # Academic Support
        resources["northeastern_academic_support"] = Resource(
            id="northeastern_academic_support",
            name="Academic Success Coaching",
            description="Support for academic challenges, study skills, and time management",
            resource_type=ResourceType.ACADEMIC_SUPPORT,
            contact_info={"phone": "(617) 373-4430", "location": "Academic Success Center"},
            availability="Monday-Friday 9:00 AM - 5:00 PM",
            cost="Free",
            eligibility=["Northeastern students"]
        )
        
        resources["northeastern_disability_services"] = Resource(
            id="northeastern_disability_services",
            name="Disability Resource Center",
            description="Academic accommodations and support for students with disabilities",
            resource_type=ResourceType.ACADEMIC_SUPPORT,
            contact_info={"phone": "(617) 373-2675", "email": "drc@northeastern.edu"},
            availability="Monday-Friday 8:30 AM - 5:00 PM",
            cost="Free",
            eligibility=["Northeastern students with documented disabilities"]
        )
        
        # International Student Support
        resources["northeastern_international"] = Resource(
            id="northeastern_international",
            name="International Student & Scholar Institute (ISSI)",
            description="Support services specifically for international students",
            resource_type=ResourceType.PEER_SUPPORT,
            contact_info={
                "phone": "(617) 373-2310",
                "location": "Steast Hall, Suite 200",
                "email": "issi@northeastern.edu"
            },
            availability="Monday-Friday 8:30 AM - 5:00 PM",
            cost="Free",
            eligibility=["International students"]
        )
        
        # MindBridge Care Benefits
        resources["mindbridge_counseling"] = Resource(
            id="mindbridge_counseling",
            name="MindBridge Care Counseling Network",
            description="Access to licensed therapists and counselors through MindBridge Care",
            resource_type=ResourceType.MINDBRIDGE_BENEFIT,
            contact_info={"website": "mindbridge.care", "phone": "1-800-MINDBRIDGE"},
            availability="Flexible scheduling, including evenings and weekends",
            cost="Covered by MindBridge Care benefits",
            eligibility=["Students with MindBridge Care coverage"]
        )
        
        resources["mindbridge_crisis_support"] = Resource(
            id="mindbridge_crisis_support",
            name="MindBridge Care Crisis Intervention",
            description="24/7 crisis support and intervention services",
            resource_type=ResourceType.MINDBRIDGE_BENEFIT,
            contact_info={"phone": "1-800-CRISIS-MB", "text": "Text CRISIS to 555-MIND"},
            availability="24/7",
            cost="Covered by MindBridge Care benefits",
            eligibility=["Students with MindBridge Care coverage"],
            is_crisis_resource=True
        )
        
        resources["mindbridge_academic_coaching"] = Resource(
            id="mindbridge_academic_coaching",
            name="MindBridge Care Academic Success Coaching",
            description="Personalized academic coaching and study skills development",
            resource_type=ResourceType.MINDBRIDGE_BENEFIT,
            contact_info={"website": "mindbridge.care/academic", "phone": "1-800-MINDBRIDGE"},
            availability="Flexible scheduling",
            cost="Covered by MindBridge Care benefits",
            eligibility=["Students with MindBridge Care coverage"]
        )
        
        resources["mindbridge_peer_support"] = Resource(
            id="mindbridge_peer_support",
            name="MindBridge Care Peer Support Network",
            description="Connect with trained peer supporters who understand college challenges",
            resource_type=ResourceType.MINDBRIDGE_BENEFIT,
            contact_info={"website": "mindbridge.care/peers", "app": "MindBridge Connect"},
            availability="24/7 through app, scheduled sessions available",
            cost="Covered by MindBridge Care benefits",
            eligibility=["Students with MindBridge Care coverage"]
        )
        
        resources["mindbridge_wellness_programs"] = Resource(
            id="mindbridge_wellness_programs",
            name="MindBridge Care Wellness Programs",
            description="Stress management, mindfulness, and wellness workshops",
            resource_type=ResourceType.MINDBRIDGE_BENEFIT,
            contact_info={"website": "mindbridge.care/wellness"},
            availability="Various times, online and in-person options",
            cost="Covered by MindBridge Care benefits",
            eligibility=["Students with MindBridge Care coverage"]
        )
        
        # Peer Support and Community Resources
        resources["northeastern_peer_support"] = Resource(
            id="northeastern_peer_support",
            name="Northeastern Peer Support Programs",
            description="Student-led support groups and peer mentoring programs",
            resource_type=ResourceType.PEER_SUPPORT,
            contact_info={"email": "peersupport@northeastern.edu"},
            availability="Various times throughout week",
            cost="Free",
            eligibility=["Northeastern students"]
        )
        
        resources["northeastern_wellness_center"] = Resource(
            id="northeastern_wellness_center",
            name="Northeastern Wellness Center",
            description="Holistic wellness programs including fitness, nutrition, and stress management",
            resource_type=ResourceType.WELLNESS,
            contact_info={"phone": "(617) 373-2772", "location": "Marino Center"},
            availability="Monday-Friday 6:00 AM - 11:00 PM",
            cost="Free for students",
            eligibility=["Northeastern students"]
        )
        
        # External Community Resources
        resources["boston_area_crisis"] = Resource(
            id="boston_area_crisis",
            name="Boston Area Crisis Services",
            description="Local crisis intervention and mental health emergency services",
            resource_type=ResourceType.CRISIS_SUPPORT,
            contact_info={"phone": "(617) 626-9300"},
            availability="24/7",
            cost="Varies by insurance",
            is_crisis_resource=True
        )
        
        resources["massachusetts_mental_health"] = Resource(
            id="massachusetts_mental_health",
            name="Massachusetts Mental Health Resources",
            description="State-provided mental health services and resources",
            resource_type=ResourceType.COUNSELING,
            contact_info={"website": "mass.gov/mental-health", "phone": "211"},
            availability="Varies by provider",
            cost="Varies by insurance and income"
        )
        
        return resources
    
    def get_resource(self, resource_id: str) -> Resource:
        """Get a specific resource by ID."""
        return self.resources.get(resource_id)
    
    def get_crisis_resources(self) -> List[Resource]:
        """Get all crisis-level resources."""
        return [r for r in self.resources.values() if r.is_crisis_resource]
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """Get all resources of a specific type."""
        return [r for r in self.resources.values() if r.resource_type == resource_type]
    
    def get_mindbridge_resources(self) -> List[Resource]:
        """Get all MindBridge Care resources."""
        return [r for r in self.resources.values() 
                if r.resource_type == ResourceType.MINDBRIDGE_BENEFIT]
    
    def get_northeastern_resources(self) -> List[Resource]:
        """Get all Northeastern University resources."""
        return [r for r in self.resources.values() 
                if "northeastern" in r.id.lower()]
    
    def search_resources(self, keywords: List[str], include_crisis: bool = True) -> List[Resource]:
        """Search resources based on keywords."""
        matching_resources = []
        
        for resource in self.resources.values():
            # Skip crisis resources if not requested
            if resource.is_crisis_resource and not include_crisis:
                continue
            
            # Check if any keywords match resource name or description
            text_to_search = f"{resource.name} {resource.description}".lower()
            keyword_matches = any(keyword.lower() in text_to_search for keyword in keywords)
            
            if keyword_matches:
                matching_resources.append(resource)
        
        # Sort by resource type priority (crisis first, then counseling, etc.)
        type_priority = {
            ResourceType.CRISIS_SUPPORT: 0,
            ResourceType.COUNSELING: 1,
            ResourceType.MINDBRIDGE_BENEFIT: 2,
            ResourceType.ACADEMIC_SUPPORT: 3,
            ResourceType.PEER_SUPPORT: 4,
            ResourceType.WELLNESS: 5
        }
        
        matching_resources.sort(key=lambda r: type_priority.get(r.resource_type, 6))
        return matching_resources
    
    def get_recommended_resources_for_scenario(self, scenario_id: str) -> List[Resource]:
        """Get recommended resources for a specific scenario."""
        # This would typically be configured based on scenario analysis
        # For now, providing general mappings
        
        scenario_resource_mapping = {
            "academic_exam_anxiety": ["northeastern_counseling", "mindbridge_academic_coaching", "northeastern_academic_support"],
            "academic_failure_fear": ["northeastern_counseling", "mindbridge_counseling", "northeastern_academic_support"],
            "loneliness_isolation": ["northeastern_peer_support", "mindbridge_peer_support", "northeastern_counseling"],
            "homesickness_cultural": ["northeastern_international", "mindbridge_counseling", "northeastern_counseling"],
            "low_self_esteem": ["northeastern_counseling", "mindbridge_counseling", "northeastern_peer_support"],
            "suicidal_ideation": ["crisis_hotline", "northeastern_emergency", "mindbridge_crisis_support"],
            "panic_attacks": ["northeastern_counseling", "mindbridge_crisis_support", "northeastern_emergency"],
            "financial_stress": ["northeastern_academic_support", "mindbridge_wellness_programs"]
        }
        
        resource_ids = scenario_resource_mapping.get(scenario_id, ["northeastern_counseling", "mindbridge_counseling"])
        return [self.resources[rid] for rid in resource_ids if rid in self.resources]

# Global resource database instance
resource_db = ResourceDatabase()