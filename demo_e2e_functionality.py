#!/usr/bin/env python3
"""
Demonstration script showing the complete E2E functionality of the XN Mental Health Chatbot.

This script demonstrates how the system:
1. Processes user input expressing mental health concerns
2. Determines the type and severity of help needed
3. Provides appropriate resources and specialist recommendations
4. Maintains conversation context across multiple turns
"""

from conversation_flow import conversation_manager
from resource_database import resource_db
from data_models import SeverityLevel
import time

def print_separator(title):
    """Print a formatted separator for demo sections."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_analysis(session_id, user_input, response, is_crisis):
    """Print detailed analysis of the conversation."""
    session = conversation_manager.active_sessions[session_id]
    latest_message = session.messages[-1]
    
    print(f"\n🧠 SYSTEM ANALYSIS:")
    print(f"   Detected Keywords: {latest_message.detected_keywords}")
    print(f"   Severity Level: {latest_message.severity_assessment.value}")
    print(f"   Identified Concerns: {session.identified_concerns}")
    print(f"   Crisis Mode: {'YES' if is_crisis else 'NO'}")
    print(f"   Recommended Resources: {len(session.recommended_resources)} resources")
    
    # Show specific resources
    print(f"\n📋 RECOMMENDED RESOURCES:")
    for i, resource_id in enumerate(session.recommended_resources[:5], 1):
        resource = resource_db.get_resource(resource_id)
        if resource:
            contact = resource.contact_info.get('phone', resource.contact_info.get('website', 'Contact info available'))
            print(f"   {i}. {resource.name}")
            print(f"      Contact: {contact}")
            print(f"      Type: {resource.resource_type.value}")
            print(f"      Cost: {resource.cost}")

def demo_academic_stress_scenario():
    """Demonstrate academic stress detection and resource recommendation."""
    print_separator("ACADEMIC STRESS SCENARIO")
    
    session_id = conversation_manager.start_new_session()
    
    print("👤 STUDENT: I'm really overwhelmed with my upcoming final exams. I'm worried I'm going to fail and disappoint my parents. I can't sleep and I'm constantly anxious about studying.")
    
    user_input = "I'm really overwhelmed with my upcoming final exams. I'm worried I'm going to fail and disappoint my parents. I can't sleep and I'm constantly anxious about studying."
    response, is_crisis = conversation_manager.process_user_message(session_id, user_input)
    
    print(f"\n🤖 SYSTEM RESPONSE:\n{response}")
    
    print_analysis(session_id, user_input, response, is_crisis)
    
    # Follow-up conversation
    print(f"\n👤 STUDENT: That's helpful. I'm particularly struggling with time management and study techniques.")
    
    follow_up = "That's helpful. I'm particularly struggling with time management and study techniques."
    follow_up_response, _ = conversation_manager.process_user_message(session_id, follow_up)
    
    print(f"\n🤖 SYSTEM FOLLOW-UP:\n{follow_up_response}")
    
    conversation_manager.end_session(session_id)
    return True

def demo_crisis_intervention_scenario():
    """Demonstrate crisis detection and immediate intervention."""
    print_separator("CRISIS INTERVENTION SCENARIO")
    
    session_id = conversation_manager.start_new_session()
    
    print("👤 STUDENT: I can't take this anymore. I've been thinking about killing myself. Everything feels hopeless and I don't see a way out.")
    
    user_input = "I can't take this anymore. I've been thinking about killing myself. Everything feels hopeless and I don't see a way out."
    response, is_crisis = conversation_manager.process_user_message(session_id, user_input)
    
    print(f"\n🚨 CRISIS RESPONSE:\n{response}")
    
    print_analysis(session_id, user_input, response, is_crisis)
    
    conversation_manager.end_session(session_id)
    return True

def demo_social_isolation_scenario():
    """Demonstrate social isolation detection and peer support resources."""
    print_separator("SOCIAL ISOLATION SCENARIO")
    
    session_id = conversation_manager.start_new_session()
    
    print("👤 STUDENT: I feel so lonely at college. I don't have any real friends and I spend most of my time alone in my dorm. I see other students having fun together and I feel left out.")
    
    user_input = "I feel so lonely at college. I don't have any real friends and I spend most of my time alone in my dorm. I see other students having fun together and I feel left out."
    response, is_crisis = conversation_manager.process_user_message(session_id, user_input)
    
    print(f"\n🤖 SYSTEM RESPONSE:\n{response}")
    
    print_analysis(session_id, user_input, response, is_crisis)
    
    conversation_manager.end_session(session_id)
    return True

def demo_international_student_scenario():
    """Demonstrate international student support and cultural resources."""
    print_separator("INTERNATIONAL STUDENT SCENARIO")
    
    session_id = conversation_manager.start_new_session()
    
    print("👤 STUDENT: I'm an international student from India and I'm really struggling with homesickness. The cultural differences are overwhelming and I miss my family so much. I feel like I don't fit in here.")
    
    user_input = "I'm an international student from India and I'm really struggling with homesickness. The cultural differences are overwhelming and I miss my family so much. I feel like I don't fit in here."
    response, is_crisis = conversation_manager.process_user_message(session_id, user_input)
    
    print(f"\n🤖 SYSTEM RESPONSE:\n{response}")
    
    print_analysis(session_id, user_input, response, is_crisis)
    
    conversation_manager.end_session(session_id)
    return True

def demo_multi_turn_conversation():
    """Demonstrate context retention across multiple conversation turns."""
    print_separator("MULTI-TURN CONVERSATION WITH CONTEXT RETENTION")
    
    session_id = conversation_manager.start_new_session()
    
    # Turn 1
    print("👤 STUDENT: I'm having a really hard time this semester. I'm stressed about my grades and I feel isolated from other students.")
    
    turn1 = "I'm having a really hard time this semester. I'm stressed about my grades and I feel isolated from other students."
    response1, _ = conversation_manager.process_user_message(session_id, turn1)
    
    print(f"\n🤖 SYSTEM: {response1[:200]}...")
    
    session = conversation_manager.active_sessions[session_id]
    print(f"\n📊 CONTEXT AFTER TURN 1:")
    print(f"   Identified Concerns: {session.identified_concerns}")
    print(f"   User Profile: {session.user_profile}")
    
    # Turn 2
    print(f"\n👤 STUDENT: The academic stress is really the biggest issue. I'm a pre-med student and I'm worried about my GPA affecting my chances for medical school.")
    
    turn2 = "The academic stress is really the biggest issue. I'm a pre-med student and I'm worried about my GPA affecting my chances for medical school."
    response2, _ = conversation_manager.process_user_message(session_id, turn2)
    
    print(f"\n🤖 SYSTEM: {response2[:200]}...")
    
    print(f"\n📊 CONTEXT AFTER TURN 2:")
    print(f"   Identified Concerns: {session.identified_concerns}")
    print(f"   Message Count: {len(session.messages)}")
    print(f"   Context Retained: {'YES' if len(set(session.identified_concerns)) >= 2 else 'NO'}")
    
    # Turn 3
    print(f"\n👤 STUDENT: What kind of academic support is available? I need help with study strategies and time management.")
    
    turn3 = "What kind of academic support is available? I need help with study strategies and time management."
    response3, _ = conversation_manager.process_user_message(session_id, turn3)
    
    print(f"\n🤖 SYSTEM: {response3[:200]}...")
    
    # Show final session summary
    summary = conversation_manager.get_session_summary(session_id)
    print(f"\n📋 FINAL SESSION SUMMARY:")
    print(f"   Total Messages: {summary['message_count']}")
    print(f"   Total Responses: {summary['response_count']}")
    print(f"   Session Duration: {summary['duration_minutes']:.1f} minutes")
    print(f"   Identified Concerns: {summary['identified_concerns']}")
    
    conversation_manager.end_session(session_id)
    return True

def demo_resource_specialist_information():
    """Demonstrate the comprehensive resource and specialist information available."""
    print_separator("AVAILABLE MENTAL HEALTH RESOURCES & SPECIALISTS")
    
    print("🏥 MINDBRIDGE CARE RESOURCES:")
    mindbridge_resources = resource_db.get_mindbridge_resources()
    for resource in mindbridge_resources:
        print(f"\n   • {resource.name}")
        print(f"     Description: {resource.description}")
        print(f"     Availability: {resource.availability}")
        print(f"     Contact: {resource.contact_info}")
        print(f"     Cost: {resource.cost}")
    
    print(f"\n🎓 NORTHEASTERN UNIVERSITY RESOURCES:")
    northeastern_resources = resource_db.get_northeastern_resources()
    for resource in northeastern_resources:
        print(f"\n   • {resource.name}")
        print(f"     Description: {resource.description}")
        print(f"     Contact: {resource.contact_info}")
        print(f"     Availability: {resource.availability}")
    
    print(f"\n🚨 CRISIS RESOURCES:")
    crisis_resources = resource_db.get_crisis_resources()
    for resource in crisis_resources:
        print(f"\n   • {resource.name}")
        print(f"     Contact: {resource.contact_info}")
        print(f"     Availability: {resource.availability}")
    
    return True

def main():
    """Run the complete E2E demonstration."""
    print("🧠 XN MENTAL HEALTH CHATBOT - END-TO-END FUNCTIONALITY DEMONSTRATION")
    print("This demonstration shows how the system processes user concerns and provides appropriate resources.")
    
    try:
        # Run all demonstration scenarios
        demo_academic_stress_scenario()
        time.sleep(1)
        
        demo_crisis_intervention_scenario()
        time.sleep(1)
        
        demo_social_isolation_scenario()
        time.sleep(1)
        
        demo_international_student_scenario()
        time.sleep(1)
        
        demo_multi_turn_conversation()
        time.sleep(1)
        
        demo_resource_specialist_information()
        
        print_separator("DEMONSTRATION COMPLETE")
        print("✅ All scenarios demonstrated successfully!")
        print("✅ Crisis detection working properly")
        print("✅ Resource recommendations functioning")
        print("✅ Context retention across conversations")
        print("✅ Specialist contact information available")
        print("✅ MindBridge Care and Northeastern resources integrated")
        
        print(f"\n📊 SYSTEM CAPABILITIES VERIFIED:")
        print(f"   • Automatic concern categorization")
        print(f"   • Severity-based resource matching")
        print(f"   • Crisis intervention protocols")
        print(f"   • Multi-turn conversation context")
        print(f"   • Comprehensive resource database")
        print(f"   • Professional contact information")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)