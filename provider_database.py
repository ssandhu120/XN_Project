"""Enhanced provider database with location and insurance-based matching."""

from typing import Dict, List, Optional
import math
from data_models import Resource, Provider, Location, ResourceType, UserPreferences, ProviderMatch

class ProviderDatabase:
    """Database of mental health providers with location and insurance matching."""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.resources = self._initialize_enhanced_resources()
    
    def _initialize_providers(self) -> Dict[str, Provider]:
        """Initialize database with sample mental health providers."""
        providers = {}
        
        # Boston Area Therapists
        providers["dr_sarah_chen"] = Provider(
            id="dr_sarah_chen",
            name="Dr. Sarah Chen",
            title="Licensed Clinical Social Worker (LCSW)",
            specialties=["Anxiety", "Depression", "Academic Stress", "Young Adults"],
            insurance_networks=["Blue Cross Blue Shield", "Aetna", "Harvard Pilgrim", "MindBridge Care"],
            location=Location(
                address="123 Boylston Street, Suite 400",
                city="Boston",
                state="MA",
                zip_code="02116",
                latitude=42.3505,
                longitude=-71.0621
            ),
            contact_info={
                "phone": "(617) 555-0123",
                "email": "schen@bostontherapy.com"
            },
            availability="Monday-Friday 9 AM - 6 PM, some evening appointments",
            languages=["English", "Mandarin"],
            telehealth_available=True,
            accepting_new_patients=True
        )
        
        providers["dr_michael_rodriguez"] = Provider(
            id="dr_michael_rodriguez",
            name="Dr. Michael Rodriguez",
            title="Psychiatrist (MD)",
            specialties=["Depression", "Anxiety", "ADHD", "Medication Management"],
            insurance_networks=["Blue Cross Blue Shield", "Cigna", "UnitedHealthcare", "MindBridge Care"],
            location=Location(
                address="456 Commonwealth Avenue",
                city="Boston",
                state="MA",
                zip_code="02215",
                latitude=42.3505,
                longitude=-71.0956
            ),
            contact_info={
                "phone": "(617) 555-0456",
                "email": "mrodriguez@bostonpsych.com"
            },
            availability="Tuesday-Thursday 10 AM - 4 PM",
            languages=["English", "Spanish"],
            telehealth_available=True,
            accepting_new_patients=True
        )
        
        providers["lisa_thompson"] = Provider(
            id="lisa_thompson",
            name="Lisa Thompson",
            title="Licensed Mental Health Counselor (LMHC)",
            specialties=["Social Anxiety", "Relationship Issues", "International Students", "Cultural Adjustment"],
            insurance_networks=["Harvard Pilgrim", "Tufts Health Plan", "MindBridge Care"],
            location=Location(
                address="789 Huntington Avenue, Suite 200",
                city="Boston",
                state="MA",
                zip_code="02115",
                latitude=42.3398,
                longitude=-71.0892
            ),
            contact_info={
                "phone": "(617) 555-0789",
                "email": "lthompson@culturalcounseling.com"
            },
            availability="Monday, Wednesday, Friday 11 AM - 7 PM",
            languages=["English", "French", "Arabic"],
            telehealth_available=True,
            accepting_new_patients=True
        )
        
        providers["dr_james_kim"] = Provider(
            id="dr_james_kim",
            name="Dr. James Kim",
            title="Clinical Psychologist (PhD)",
            specialties=["Academic Performance", "Test Anxiety", "Perfectionism", "Stress Management"],
            insurance_networks=["Blue Cross Blue Shield", "Aetna", "MindBridge Care"],
            location=Location(
                address="321 Newbury Street, Floor 3",
                city="Boston",
                state="MA",
                zip_code="02115",
                latitude=42.3505,
                longitude=-71.0821
            ),
            contact_info={
                "phone": "(617) 555-0321",
                "email": "jkim@academicwellness.com"
            },
            availability="Monday-Friday 8 AM - 5 PM",
            languages=["English", "Korean"],
            telehealth_available=False,  # In-person only
            accepting_new_patients=True
        )
        
        # Cambridge Area Providers
        providers["dr_emily_watson"] = Provider(
            id="dr_emily_watson",
            name="Dr. Emily Watson",
            title="Licensed Clinical Social Worker (LCSW)",
            specialties=["Depression", "Trauma", "LGBTQ+ Issues", "Young Adults"],
            insurance_networks=["Harvard Pilgrim", "Blue Cross Blue Shield", "MindBridge Care"],
            location=Location(
                address="567 Massachusetts Avenue",
                city="Cambridge",
                state="MA",
                zip_code="02139",
                latitude=42.3656,
                longitude=-71.1040
            ),
            contact_info={
                "phone": "(617) 555-0567",
                "email": "ewatson@cambridgecounseling.com"
            },
            availability="Tuesday-Saturday 10 AM - 8 PM",
            languages=["English"],
            telehealth_available=True,
            accepting_new_patients=True
        )
        
        # Telehealth-Only Providers
        providers["dr_maria_gonzalez"] = Provider(
            id="dr_maria_gonzalez",
            name="Dr. Maria Gonzalez",
            title="Licensed Professional Counselor (LPC)",
            specialties=["Anxiety", "Depression", "Bilingual Therapy", "Family Issues"],
            insurance_networks=["MindBridge Care", "Aetna", "Cigna"],
            location=None,  # Telehealth only
            contact_info={
                "phone": "(800) 555-TELE",
                "email": "mgonzalez@teletherapy.com",
                "website": "teletherapy.com/maria-gonzalez"
            },
            availability="Monday-Friday 7 AM - 9 PM, Saturday 9 AM - 5 PM",
            languages=["English", "Spanish"],
            telehealth_available=True,
            accepting_new_patients=True
        )
        
        return providers
    
    def _initialize_enhanced_resources(self) -> Dict[str, Resource]:
        """Initialize enhanced resources with provider information."""
        resources = {}
        
        # MindBridge Care Provider Network
        resources["mindbridge_provider_network"] = Resource(
            id="mindbridge_provider_network",
            name="MindBridge Care Provider Network",
            description="Network of licensed mental health professionals covered by MindBridge Care",
            resource_type=ResourceType.MINDBRIDGE_BENEFIT,
            contact_info={
                "phone": "1-800-MINDBRIDGE",
                "website": "mindbridge.care/find-provider"
            },
            availability="Flexible scheduling, including evenings and weekends",
            cost="Covered by MindBridge Care benefits",
            eligibility=["Students with MindBridge Care coverage"],
            service_area=["Boston", "Cambridge", "Somerville", "Brookline", "Newton"],
            telehealth_available=True,
            insurance_networks=["MindBridge Care"],
            providers=list(self.providers.values())
        )
        
        # Boston Area Mental Health Consortium
        resources["boston_mental_health_consortium"] = Resource(
            id="boston_mental_health_consortium",
            name="Boston Area Mental Health Consortium",
            description="Collaborative network of mental health providers in the Boston area",
            resource_type=ResourceType.COUNSELING,
            contact_info={
                "phone": "(617) 555-BMHC",
                "website": "bostonmentalhealth.org"
            },
            availability="Varies by provider",
            cost="Varies by insurance",
            service_area=["Boston", "Cambridge", "Somerville", "Brookline"],
            telehealth_available=True,
            insurance_networks=["Blue Cross Blue Shield", "Harvard Pilgrim", "Aetna", "Cigna"],
            providers=[p for p in self.providers.values() if p.id != "dr_maria_gonzalez"]  # Exclude telehealth-only for this network
        )
        
        return resources
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate distance between two locations in miles using Haversine formula."""
        if not loc1 or not loc2 or not all([loc1.latitude, loc1.longitude, loc2.latitude, loc2.longitude]):
            return float('inf')
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [loc1.latitude, loc1.longitude, loc2.latitude, loc2.longitude])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in miles
        r = 3956
        return c * r
    
    def match_providers(self, preferences: UserPreferences, max_results: int = 10) -> List[ProviderMatch]:
        """Find providers matching user preferences."""
        matches = []
        
        for resource in self.resources.values():
            for provider in resource.providers:
                match_score = 0.0
                match_reasons = []
                distance = None
                
                # Insurance matching (high priority)
                if preferences.insurance_plan:
                    if preferences.insurance_plan in provider.insurance_networks:
                        match_score += 30
                        match_reasons.append(f"Accepts {preferences.insurance_plan}")
                    else:
                        # Skip providers that don't accept user's insurance
                        continue
                
                # Location/distance matching
                if preferences.location and provider.location:
                    distance = self.calculate_distance(preferences.location, provider.location)
                    if preferences.max_distance_miles:
                        if distance <= preferences.max_distance_miles:
                            match_score += 25 - (distance / preferences.max_distance_miles * 10)
                            match_reasons.append(f"{distance:.1f} miles away")
                        else:
                            # Skip providers too far away
                            continue
                    else:
                        # No distance preference, but closer is better
                        match_score += max(0, 15 - distance * 0.5)
                        match_reasons.append(f"{distance:.1f} miles away")
                
                # Telehealth preference matching
                if preferences.telehealth_preference == "required" and not provider.telehealth_available:
                    continue
                elif preferences.telehealth_preference == "in_person_only" and not provider.location:
                    continue
                elif preferences.telehealth_preference == "preferred" and provider.telehealth_available:
                    match_score += 10
                    match_reasons.append("Offers telehealth")
                
                # Specialty matching
                if preferences.preferred_specialties:
                    specialty_matches = set(preferences.preferred_specialties) & set(provider.specialties)
                    if specialty_matches:
                        match_score += len(specialty_matches) * 15
                        match_reasons.append(f"Specializes in: {', '.join(specialty_matches)}")
                
                # Language matching
                if preferences.preferred_languages:
                    language_matches = set(preferences.preferred_languages) & set(provider.languages)
                    if language_matches:
                        match_score += len(language_matches) * 10
                        match_reasons.append(f"Speaks: {', '.join(language_matches)}")
                
                # Provider type matching
                if preferences.preferred_provider_type:
                    for pref_type in preferences.preferred_provider_type:
                        if pref_type.lower() in provider.title.lower():
                            match_score += 15
                            match_reasons.append(f"Matches preferred type: {pref_type}")
                
                # Accepting new patients
                if provider.accepting_new_patients:
                    match_score += 5
                    match_reasons.append("Accepting new patients")
                
                # Only include providers with reasonable match scores
                if match_score > 10:
                    matches.append(ProviderMatch(
                        provider=provider,
                        resource=resource,
                        match_score=match_score,
                        match_reasons=match_reasons,
                        distance_miles=distance
                    ))
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:max_results]
    
    def get_provider_by_id(self, provider_id: str) -> Optional[Provider]:
        """Get a specific provider by ID."""
        return self.providers.get(provider_id)
    
    def get_providers_by_specialty(self, specialty: str) -> List[Provider]:
        """Get providers with a specific specialty."""
        return [p for p in self.providers.values() if specialty.lower() in [s.lower() for s in p.specialties]]
    
    def get_providers_by_insurance(self, insurance: str) -> List[Provider]:
        """Get providers that accept a specific insurance."""
        return [p for p in self.providers.values() if insurance in p.insurance_networks]
    
    def get_telehealth_providers(self) -> List[Provider]:
        """Get all providers that offer telehealth."""
        return [p for p in self.providers.values() if p.telehealth_available]

# Global provider database instance
provider_db = ProviderDatabase()