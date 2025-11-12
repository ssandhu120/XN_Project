#!/usr/bin/env python3
"""
Interactive Demo for XN Mental Health Chatbot with Live Gemini API Integration

This script allows you to:
1. Enter your Gemini API key
2. Test the chatbot with real LLM responses
3. See the complete E2E functionality in action
4. Compare LLM responses vs fallback responses
"""

import os
import sys
import getpass
from typing import Optional
import time

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_flow import conversation_manager
from resource_database import resource_db
from config import config
from llm_client import llm_client
from utils.logger import logger

class InteractiveDemo:
    """Interactive demonstration of the XN Mental Health Chatbot."""
    
    def __init__(self):
        self.session_id = None
        self.api_key_set = False
        
    def setup_api_key(self):
        """Set up Gemini API key for the demo."""
        print("🔑 GEMINI API KEY SETUP")
        print("=" * 50)
        print("To use the live LLM functionality, please enter your Gemini API key.")
        print("You can get a free API key at: https://makersuite.google.com/app/apikey")
        print("(The key will only be used for this demo session)")
        print()
        
        api_key = getpass.getpass("Enter your Gemini API key (or press Enter to use fallback responses): ").strip()
        
        if api_key:
            # Set the API key in environment and config
            os.environ["GEMINI_API_KEY"] = api_key
            config.GEMINI_API_KEY = api_key
            config.ENABLE_LLM = True
            
            # Reinitialize the LLM client
            llm_client._initialize_client()
            
            if llm_client.is_available():
                print("✅ Gemini API key set successfully! LLM responses enabled.")
                self.api_key_set = True
            else:
                print("❌ Failed to initialize Gemini client. Using fallback responses.")
                self.api_key_set = False
        else:
            print("ℹ️  No API key provided. Using rule-based fallback responses.")
            self.api_key_set = False
        
        print()
        
    def print_header(self):
        """Print the demo header."""
        print("\n" + "=" * 80)
        print("🧠 XN MENTAL HEALTH CHATBOT - INTERACTIVE DEMO")
        print("=" * 80)
        print("This demo shows the complete E2E functionality with real conversation flows.")
        print(f"LLM Status: {'✅ ENABLED (Gemini)' if self.api_key_set else '❌ DISABLED (Fallback responses)'}")
        print("=" * 80)
        
    def start_conversation(self):
        """Start a new conversation session."""
        self.session_id = conversation_manager.start_new_session()
        welcome = conversation_manager.get_welcome_message()
        
        print("\n🤖 CHATBOT:")
        print(welcome)
        print()
        
    def process_user_input(self, user_input: str):
        """Process user input and show detailed analysis."""
        print(f"👤 YOU: {user_input}")
        print("\n⏳ Processing...")
        
        start_time = time.time()
        response, is_crisis = conversation_manager.process_user_message(self.session_id, user_input)
        processing_time = time.time() - start_time
        
        print(f"\n🤖 CHATBOT RESPONSE:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # Show system analysis
        self.show_analysis(user_input, is_crisis, processing_time)
        
    def show_analysis(self, user_input: str, is_crisis: bool, processing_time: float):
        """Show detailed system analysis."""
        session = conversation_manager.active_sessions[self.session_id]
        latest_message = session.messages[-1]
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"   Response Time: {processing_time:.2f} seconds")
        print(f"   LLM Used: {'Yes (Gemini)' if self.api_key_set and llm_client.is_available() else 'No (Fallback)'}")
        print(f"   Crisis Detected: {'🚨 YES' if is_crisis else '✅ No'}")
        print(f"   Severity Level: {latest_message.severity_assessment.value.upper()}")
        print(f"   Detected Keywords: {latest_message.detected_keywords}")
        print(f"   Identified Concerns: {session.identified_concerns}")
        print(f"   Resources Recommended: {len(session.recommended_resources)}")
        
        # Show top 3 recommended resources
        if session.recommended_resources:
            print(f"\n📋 TOP RECOMMENDED RESOURCES:")
            for i, resource_id in enumerate(session.recommended_resources[:3], 1):
                resource = resource_db.get_resource(resource_id)
                if resource:
                    contact = resource.contact_info.get('phone', 
                             resource.contact_info.get('website', 
                             resource.contact_info.get('email', 'Contact available')))
                    print(f"   {i}. {resource.name}")
                    print(f"      Contact: {contact}")
                    print(f"      Type: {resource.resource_type.value}")
        
        print()
        
    def run_demo_scenarios(self):
        """Run predefined demo scenarios."""
        scenarios = [
            {
                "name": "Academic Stress",
                "input": "I'm really stressed about my upcoming finals. I can't sleep and I'm worried I'll fail everything.",
                "description": "Tests academic stress detection and resource recommendations"
            },
            {
                "name": "Social Isolation", 
                "input": "I feel so lonely at college. I don't have any friends and spend all my time alone in my room.",
                "description": "Tests social isolation detection and peer support resources"
            },
            {
                "name": "International Student",
                "input": "I'm an international student and I'm really homesick. Everything feels so different here and I miss my family.",
                "description": "Tests international student support and cultural resources"
            },
            {
                "name": "Crisis Situation",
                "input": "I can't take this anymore. I've been thinking about ending it all. Nothing seems worth it.",
                "description": "Tests crisis detection and immediate intervention protocols"
            }
        ]
        
        print("\n🎭 DEMO SCENARIOS")
        print("=" * 50)
        print("Let's test some common scenarios to see how the system responds:")
        print()
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['name']}: {scenario['description']}")
        
        print("\nWhich scenario would you like to test? (1-4, or 0 for free chat): ", end="")
        
        try:
            choice = int(input().strip())
            if 1 <= choice <= len(scenarios):
                scenario = scenarios[choice - 1]
                print(f"\n🎬 TESTING SCENARIO: {scenario['name']}")
                print("=" * 50)
                self.process_user_input(scenario['input'])
                return True
            elif choice == 0:
                return False  # User wants free chat
            else:
                print("Invalid choice. Starting free chat mode.")
                return False
        except ValueError:
            print("Invalid input. Starting free chat mode.")
            return False
    
    def run_free_chat(self):
        """Run free chat mode."""
        print("\n💬 FREE CHAT MODE")
        print("=" * 50)
        print("Type your message to chat with the bot. Type 'quit', 'exit', or 'bye' to end.")
        print("Type 'help' to see available commands.")
        print("Type 'analysis' to see detailed session analysis.")
        print()
        
        while True:
            try:
                user_input = input("👤 YOU: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n👋 Thank you for using the XN Mental Health Chatbot demo!")
                    break
                    
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                    
                elif user_input.lower() == 'analysis':
                    self.show_session_analysis()
                    continue
                    
                elif user_input.lower() == 'resources':
                    self.show_all_resources()
                    continue
                
                self.process_user_input(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'quit' to exit.")
    
    def show_help(self):
        """Show help information."""
        print("\n📖 AVAILABLE COMMANDS:")
        print("   help      - Show this help message")
        print("   analysis  - Show detailed session analysis")
        print("   resources - Show all available resources")
        print("   quit/exit - End the demo")
        print()
    
    def show_session_analysis(self):
        """Show detailed session analysis."""
        if not self.session_id or self.session_id not in conversation_manager.active_sessions:
            print("No active session found.")
            return
            
        summary = conversation_manager.get_session_summary(self.session_id)
        session = conversation_manager.active_sessions[self.session_id]
        
        print(f"\n📊 SESSION ANALYSIS:")
        print(f"   Session ID: {self.session_id[:8]}...")
        print(f"   Messages Exchanged: {summary['message_count']}")
        print(f"   Session Duration: {summary['duration_minutes']:.1f} minutes")
        print(f"   Identified Concerns: {summary['identified_concerns']}")
        print(f"   Crisis Flags: {len(session.crisis_flags)}")
        print(f"   Total Resources Recommended: {len(session.recommended_resources)}")
        print(f"   User Profile: {session.user_profile}")
        print()
    
    def show_all_resources(self):
        """Show all available resources."""
        print(f"\n🏥 AVAILABLE MENTAL HEALTH RESOURCES:")
        print("=" * 50)
        
        print("🔴 CRISIS RESOURCES:")
        crisis_resources = resource_db.get_crisis_resources()
        for resource in crisis_resources:
            contact = resource.contact_info.get('phone', 'Contact available')
            print(f"   • {resource.name}: {contact}")
        
        print(f"\n🎓 NORTHEASTERN UNIVERSITY RESOURCES:")
        northeastern_resources = resource_db.get_northeastern_resources()
        for resource in northeastern_resources:
            contact = resource.contact_info.get('phone', 
                     resource.contact_info.get('email', 'Contact available'))
            print(f"   • {resource.name}: {contact}")
        
        print(f"\n🏥 MINDBRIDGE CARE RESOURCES:")
        mindbridge_resources = resource_db.get_mindbridge_resources()
        for resource in mindbridge_resources:
            contact = resource.contact_info.get('phone', 
                     resource.contact_info.get('website', 'Contact available'))
            print(f"   • {resource.name}: {contact}")
        print()
    
    def cleanup(self):
        """Clean up the demo session."""
        if self.session_id:
            conversation_manager.end_session(self.session_id)
    
    def run(self):
        """Run the complete interactive demo."""
        try:
            self.setup_api_key()
            self.print_header()
            self.start_conversation()
            
            # Ask user if they want to run demo scenarios or free chat
            if self.run_demo_scenarios():
                # After scenario, offer free chat
                print("\n" + "=" * 50)
                print("Would you like to continue with free chat? (y/n): ", end="")
                if input().strip().lower() in ['y', 'yes']:
                    self.run_free_chat()
            else:
                # Go directly to free chat
                self.run_free_chat()
                
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        finally:
            self.cleanup()

def main():
    """Main entry point for the interactive demo."""
    print("🧠 XN MENTAL HEALTH CHATBOT - INTERACTIVE DEMO")
    print("Welcome to the live demonstration of the mental health chatbot system!")
    print()
    
    demo = InteractiveDemo()
    demo.run()

if __name__ == "__main__":
    main()