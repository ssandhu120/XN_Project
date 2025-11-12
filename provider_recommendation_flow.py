"""Interactive conversation flow for personalized provider recommendations."""

from typing import Dict, List, Optional, Tuple
from data_models import UserPreferences, Location, ProviderMatch
from provider_database import provider_db

class ProviderRecommendationFlow:
    """Manages the conversation flow for gathering user preferences and providing provider recommendations."""
    
    def __init__(self):
        self.conversation_state = {}
        self.user_preferences = {}
    
    def start_provider_search(self, session_id: str) -> str:
        """Start the provider recommendation process."""
        self.conversation_state[session_id] = {
            "step": "initial_assessment",
            "preferences": UserPreferences(),
            "collected_info": {}
        }
        
        return """I'd be happy to help you find mental health providers that match your needs! 

To give you the best recommendations, I'll need to ask you a few questions about:
1. **Your location** (for in-person appointments)
2. **Your insurance coverage** 
3. **What type of care** you're looking for
4. **Any specific preferences** you have

Let's start: **What city or zip code are you located in?** (This helps me find providers near you)

*You can also say "telehealth only" if you prefer online appointments.*"""
    
    def process_location_response(self, session_id: str, user_input: str) -> str:
        """Process user's location input."""
        state = self.conversation_state.get(session_id, {})
        preferences = state.get("preferences", UserPreferences())
        
        user_input_lower = user_input.lower().strip()
        
        if "telehealth" in user_input_lower or "online" in user_input_lower:
            preferences.telehealth_preference = "required"
            state["collected_info"]["location"] = "telehealth_only"
            next_response = self._ask_insurance_question(session_id)
        else:
            # Parse location (simplified - in real implementation would use geocoding API)
            location = self._parse_location(user_input)
            preferences.location = location
            state["collected_info"]["location"] = user_input
            
            next_response = f"""Great! I'll look for providers in the **{user_input}** area.

**What insurance do you have?** This helps me find providers that accept your coverage.

Common options:
• Blue Cross Blue Shield
• Harvard Pilgrim 
• Aetna
• Cigna
• UnitedHealthcare
• **MindBridge Care** (if you have this through your school)
• No insurance / Self-pay
• Not sure

Just tell me your insurance name or say "not sure" if you need help figuring it out."""
        
        state["step"] = "insurance_collection"
        self.conversation_state[session_id] = state
        return next_response
    
    def process_insurance_response(self, session_id: str, user_input: str) -> str:
        """Process user's insurance input."""
        state = self.conversation_state.get(session_id, {})
        preferences = state.get("preferences", UserPreferences())
        
        user_input_lower = user_input.lower().strip()
        
        # Map common insurance variations
        insurance_mapping = {
            "blue cross": "Blue Cross Blue Shield",
            "bcbs": "Blue Cross Blue Shield", 
            "harvard pilgrim": "Harvard Pilgrim",
            "mindbridge": "MindBridge Care",
            "mind bridge": "MindBridge Care",
            "aetna": "Aetna",
            "cigna": "Cigna",
            "united": "UnitedHealthcare",
            "unitedhealthcare": "UnitedHealthcare"
        }
        
        insurance_plan = None
        for key, value in insurance_mapping.items():
            if key in user_input_lower:
                insurance_plan = value
                break
        
        if not insurance_plan and "no insurance" not in user_input_lower and "self-pay" not in user_input_lower:
            insurance_plan = user_input.strip()  # Use as-is if not recognized
        
        preferences.insurance_plan = insurance_plan
        state["collected_info"]["insurance"] = user_input
        state["step"] = "care_type_collection"
        
        next_response = f"""Perfect! I'll look for providers that accept **{insurance_plan or 'self-pay'}**.

**What type of mental health care are you looking for?**

• **Therapy/Counseling** - Talk therapy with a therapist or counselor
• **Psychiatry** - Medication evaluation and management with a psychiatrist  
• **Both** - Therapy and potential medication support
• **Not sure** - I can help you figure out what might be best

What sounds most helpful for your situation?"""
        
        self.conversation_state[session_id] = state
        return next_response
    
    def process_care_type_response(self, session_id: str, user_input: str) -> str:
        """Process user's care type preference."""
        state = self.conversation_state.get(session_id, {})
        preferences = state.get("preferences", UserPreferences())
        
        user_input_lower = user_input.lower().strip()
        
        if "therapy" in user_input_lower or "counseling" in user_input_lower:
            preferences.preferred_provider_type = ["therapist", "counselor", "LCSW", "LMHC"]
        elif "psychiatr" in user_input_lower:
            preferences.preferred_provider_type = ["psychiatrist", "MD"]
        elif "both" in user_input_lower:
            preferences.preferred_provider_type = ["therapist", "counselor", "psychiatrist", "LCSW", "LMHC", "MD"]
        else:
            # Default to therapy if not sure
            preferences.preferred_provider_type = ["therapist", "counselor", "LCSW", "LMHC"]
        
        state["collected_info"]["care_type"] = user_input
        state["step"] = "specialties_collection"
        
        next_response = """Great choice! 

**Are there any specific areas you'd like your provider to specialize in?** (Optional)

For example:
• Anxiety or panic attacks
• Depression 
• Academic stress or performance
• Social anxiety or isolation
• Relationship issues
• Cultural adjustment or international student support
• LGBTQ+ issues
• Trauma or PTSD

You can mention multiple areas, or say "no specific preference" if you're open to a general practitioner."""
        
        self.conversation_state[session_id] = state
        return next_response
    
    def process_specialties_response(self, session_id: str, user_input: str) -> str:
        """Process user's specialty preferences."""
        state = self.conversation_state.get(session_id, {})
        preferences = state.get("preferences", UserPreferences())
        
        user_input_lower = user_input.lower().strip()
        
        specialties = []
        specialty_keywords = {
            "anxiety": "Anxiety",
            "panic": "Anxiety", 
            "depression": "Depression",
            "academic": "Academic Stress",
            "stress": "Stress Management",
            "social": "Social Anxiety",
            "relationship": "Relationship Issues",
            "cultural": "Cultural Adjustment",
            "international": "International Students",
            "lgbtq": "LGBTQ+ Issues",
            "trauma": "Trauma",
            "ptsd": "PTSD"
        }
        
        for keyword, specialty in specialty_keywords.items():
            if keyword in user_input_lower:
                specialties.append(specialty)
        
        preferences.preferred_specialties = specialties
        state["collected_info"]["specialties"] = user_input
        state["step"] = "final_preferences"
        
        # Ask about final preferences
        next_response = """Perfect! Just a couple more quick questions:

**Do you have any preference for:**
• **Distance**: How far are you willing to travel? (e.g., "within 5 miles", "no preference")
• **Languages**: Do you need a provider who speaks a specific language?
• **Telehealth**: Do you prefer in-person, telehealth, or either?

You can answer all at once or say "no other preferences" to see your recommendations!"""
        
        self.conversation_state[session_id] = state
        return next_response
    
    def process_final_preferences(self, session_id: str, user_input: str) -> str:
        """Process final user preferences and generate recommendations."""
        state = self.conversation_state.get(session_id, {})
        preferences = state.get("preferences", UserPreferences())
        
        user_input_lower = user_input.lower().strip()
        
        # Parse distance preference
        if "mile" in user_input_lower:
            import re
            distance_match = re.search(r'(\d+)\s*mile', user_input_lower)
            if distance_match:
                preferences.max_distance_miles = int(distance_match.group(1))
        
        # Parse language preference
        languages = ["spanish", "mandarin", "chinese", "french", "arabic", "korean"]
        for lang in languages:
            if lang in user_input_lower:
                preferences.preferred_languages.append(lang.capitalize())
        
        # Parse telehealth preference
        if "telehealth" in user_input_lower or "online" in user_input_lower:
            if "prefer" in user_input_lower:
                preferences.telehealth_preference = "preferred"
            elif "only" in user_input_lower:
                preferences.telehealth_preference = "required"
        elif "in-person" in user_input_lower or "in person" in user_input_lower:
            preferences.telehealth_preference = "in_person_only"
        
        # Generate recommendations
        matches = provider_db.match_providers(preferences, max_results=5)
        
        if not matches:
            return self._generate_no_matches_response(preferences)
        
        return self._generate_recommendations_response(matches, preferences)
    
    def _parse_location(self, location_str: str) -> Location:
        """Parse location string into Location object (simplified)."""
        # In a real implementation, this would use a geocoding API
        location_str = location_str.strip()
        
        # Common Boston area locations with approximate coordinates
        location_mapping = {
            "boston": Location(city="Boston", state="MA", latitude=42.3601, longitude=-71.0589),
            "cambridge": Location(city="Cambridge", state="MA", latitude=42.3736, longitude=-71.1097),
            "somerville": Location(city="Somerville", state="MA", latitude=42.3876, longitude=-71.0995),
            "brookline": Location(city="Brookline", state="MA", latitude=42.3317, longitude=-71.1211),
            "02115": Location(city="Boston", state="MA", zip_code="02115", latitude=42.3398, longitude=-71.0892),
            "02116": Location(city="Boston", state="MA", zip_code="02116", latitude=42.3505, longitude=-71.0621),
            "02139": Location(city="Cambridge", state="MA", zip_code="02139", latitude=42.3656, longitude=-71.1040)
        }
        
        location_lower = location_str.lower()
        for key, location in location_mapping.items():
            if key in location_lower:
                return location
        
        # Default to Boston if not recognized
        return Location(city=location_str, state="MA", latitude=42.3601, longitude=-71.0589)
    
    def _ask_insurance_question(self, session_id: str) -> str:
        """Generate insurance question for telehealth-only users."""
        return """Perfect! Since you prefer telehealth, you'll have access to providers who offer online sessions.

**What insurance do you have?** This helps me find providers that accept your coverage.

Common options:
• **MindBridge Care** (if you have this through your school)
• Blue Cross Blue Shield
• Harvard Pilgrim 
• Aetna
• Cigna
• UnitedHealthcare
• No insurance / Self-pay
• Not sure

Just tell me your insurance name or say "not sure" if you need help figuring it out."""
    
    def _generate_recommendations_response(self, matches: List[ProviderMatch], preferences: UserPreferences) -> str:
        """Generate formatted response with provider recommendations."""
        response = f"""🎯 **Great! I found {len(matches)} mental health providers that match your preferences:**

"""
        
        for i, match in enumerate(matches, 1):
            provider = match.provider
            resource = match.resource
            
            response += f"""**{i}. {provider.name}, {provider.title}**
"""
            
            # Specialties
            if provider.specialties:
                response += f"   🎯 **Specializes in:** {', '.join(provider.specialties)}\n"
            
            # Location/Distance
            if match.distance_miles is not None:
                response += f"   📍 **Location:** {provider.location.address}, {provider.location.city} ({match.distance_miles:.1f} miles)\n"
            elif provider.location:
                response += f"   📍 **Location:** {provider.location.address}, {provider.location.city}\n"
            else:
                response += f"   💻 **Telehealth Only**\n"
            
            # Contact
            if provider.contact_info.get("phone"):
                response += f"   📞 **Phone:** {provider.contact_info['phone']}\n"
            
            # Insurance
            if preferences.insurance_plan and preferences.insurance_plan in provider.insurance_networks:
                response += f"   ✅ **Accepts your insurance:** {preferences.insurance_plan}\n"
            
            # Languages
            if len(provider.languages) > 1 or provider.languages[0] != "English":
                response += f"   🗣️ **Languages:** {', '.join(provider.languages)}\n"
            
            # Telehealth
            if provider.telehealth_available:
                response += f"   💻 **Telehealth available**\n"
            
            # Availability
            if provider.availability:
                response += f"   🕐 **Availability:** {provider.availability}\n"
            
            # Match reasons
            if match.match_reasons:
                response += f"   ⭐ **Why this is a good match:** {', '.join(match.match_reasons[:3])}\n"
            
            response += "\n"
        
        response += """**Next Steps:**
1. **Call the provider** that seems like the best fit
2. **Mention you're a student** (many offer student rates)
3. **Ask about availability** for new patients
4. **Confirm they accept your insurance** before your first appointment

**Need immediate support?** Remember these resources are always available:
• **MindBridge Care Crisis Line:** 1-800-CRISIS-MB
• **988 Suicide & Crisis Lifeline:** Call or text 988
• **Northeastern CAPS:** (617) 373-2772

Would you like me to help you with anything else, such as questions to ask when calling providers?"""
        
        return response
    
    def _generate_no_matches_response(self, preferences: UserPreferences) -> str:
        """Generate response when no providers match user preferences."""
        return f"""I wasn't able to find providers that exactly match all your preferences, but don't worry! Here are some options:

**🔄 Let's try expanding your search:**
• **Increase distance** if you specified a small radius
• **Consider telehealth** options for more flexibility  
• **Try different insurance** options or ask about sliding scale fees

**📞 Direct Resources:**
• **MindBridge Care Provider Line:** 1-800-MINDBRIDGE (they can help find in-network providers)
• **Your Insurance:** Call the number on your card for a provider directory
• **Psychology Today:** psychologytoday.com has a provider search tool

**🆘 Immediate Support:**
• **Northeastern CAPS:** (617) 373-2772 (free for students)
• **MindBridge Care Crisis Line:** 1-800-CRISIS-MB
• **988 Suicide & Crisis Lifeline:** Call or text 988

Would you like me to help you search again with different preferences?"""

# Global instance
provider_flow = ProviderRecommendationFlow()