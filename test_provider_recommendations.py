#!/usr/bin/env python3
"""Test script for provider recommendation functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_flow import conversation_manager
from provider_recommendation_flow import provider_flow
from data_models import UserPreferences, Location
from provider_database import provider_db

def test_provider_matching():
    """Test the provider matching algorithm."""
    print("🧪 Testing Provider Matching Algorithm")
    print("=" * 50)
    
    # Test case 1: Boston student with MindBridge Care insurance
    print("\n📍 Test Case 1: Boston student with MindBridge Care")
    preferences = UserPreferences(
        location=Location(city="Boston", state="MA", latitude=42.3601, longitude=-71.0589),
        insurance_plan="MindBridge Care",
        preferred_provider_type=["therapist", "counselor"],
        preferred_specialties=["Anxiety", "Academic Stress"],
        max_distance_miles=10
    )
    
    matches = provider_db.match_providers(preferences, max_results=3)
    print(f"Found {len(matches)} matches:")
    
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match.provider.name} ({match.provider.title})")
        print(f"   Score: {match.match_score:.1f}")
        print(f"   Specialties: {', '.join(match.provider.specialties)}")
        print(f"   Distance: {match.distance_miles:.1f} miles" if match.distance_miles else "   Telehealth only")
        print(f"   Match reasons: {', '.join(match.match_reasons)}")
    
    # Test case 2: International student needing cultural support
    print("\n\n📍 Test Case 2: International student needing cultural support")
    preferences = UserPreferences(
        location=Location(city="Cambridge", state="MA", latitude=42.3736, longitude=-71.1097),
        insurance_plan="Harvard Pilgrim",
        preferred_specialties=["Cultural Adjustment", "International Students"],
        preferred_languages=["English", "French"],
        max_distance_miles=15
    )
    
    matches = provider_db.match_providers(preferences, max_results=3)
    print(f"Found {len(matches)} matches:")
    
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match.provider.name} ({match.provider.title})")
        print(f"   Score: {match.match_score:.1f}")
        print(f"   Specialties: {', '.join(match.provider.specialties)}")
        print(f"   Languages: {', '.join(match.provider.languages)}")
        print(f"   Distance: {match.distance_miles:.1f} miles" if match.distance_miles else "   Telehealth only")
        print(f"   Match reasons: {', '.join(match.match_reasons)}")

def test_conversation_flow():
    """Test the integrated conversation flow with provider recommendations."""
    print("\n\n🗣️ Testing Integrated Conversation Flow")
    print("=" * 50)
    
    # Start a new session
    session_id = conversation_manager.start_new_session()
    print(f"Started session: {session_id}")
    
    # Simulate conversation leading to provider search
    test_messages = [
        "I'm really stressed about my finals and can't sleep",
        "It's been going on for about 2 weeks now",
        "I think I need to find a therapist to help me"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"User: {message}")
        
        response, is_crisis = conversation_manager.process_user_message(session_id, message)
        print(f"Bot: {response[:200]}..." if len(response) > 200 else f"Bot: {response}")
        
        if is_crisis:
            print("⚠️ Crisis detected!")

def test_provider_search_flow():
    """Test the step-by-step provider search flow."""
    print("\n\n🔍 Testing Provider Search Flow")
    print("=" * 50)
    
    session_id = "test_provider_search"
    
    # Step 1: Start provider search
    print("\n--- Starting Provider Search ---")
    response = provider_flow.start_provider_search(session_id)
    print(f"Bot: {response}")
    
    # Step 2: Location
    print("\n--- User provides location ---")
    user_input = "Boston, MA"
    print(f"User: {user_input}")
    response = provider_flow.process_location_response(session_id, user_input)
    print(f"Bot: {response}")
    
    # Step 3: Insurance
    print("\n--- User provides insurance ---")
    user_input = "MindBridge Care"
    print(f"User: {user_input}")
    response = provider_flow.process_insurance_response(session_id, user_input)
    print(f"Bot: {response}")
    
    # Step 4: Care type
    print("\n--- User specifies care type ---")
    user_input = "therapy"
    print(f"User: {user_input}")
    response = provider_flow.process_care_type_response(session_id, user_input)
    print(f"Bot: {response}")
    
    # Step 5: Specialties
    print("\n--- User specifies specialties ---")
    user_input = "anxiety and academic stress"
    print(f"User: {user_input}")
    response = provider_flow.process_specialties_response(session_id, user_input)
    print(f"Bot: {response}")
    
    # Step 6: Final preferences
    print("\n--- User provides final preferences ---")
    user_input = "within 5 miles, telehealth preferred"
    print(f"User: {user_input}")
    response = provider_flow.process_final_preferences(session_id, user_input)
    print(f"Bot: {response[:500]}..." if len(response) > 500 else f"Bot: {response}")

def main():
    """Run all tests."""
    print("🚀 Testing Provider Recommendation System")
    print("=" * 60)
    
    try:
        test_provider_matching()
        test_provider_search_flow()
        test_conversation_flow()
        
        print("\n\n✅ All tests completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("• Location-based provider matching")
        print("• Insurance network filtering")
        print("• Specialty-based recommendations")
        print("• Distance calculations")
        print("• Multi-language support")
        print("• Telehealth options")
        print("• Integrated conversation flow")
        print("• Step-by-step preference collection")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()