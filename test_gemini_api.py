#!/usr/bin/env python3
"""
Test script to validate Gemini API key functionality
"""

import os
import sys
import getpass

def test_gemini_api():
    """Test Gemini API key functionality."""
    print("🔑 GEMINI API KEY TESTER")
    print("=" * 40)
    
    # Get API key
    api_key = getpass.getpass("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    if len(api_key) < 10:
        print("❌ API key appears too short")
        return False
    
    print("🔍 Testing API key...")
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI library available")
        
        # Configure API
        genai.configure(api_key=api_key)
        print("✅ API key configured")
        
        # Create model
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Model created")
        
        # Test generation
        print("🧪 Testing content generation...")
        response = model.generate_content(
            "Say hello in exactly 3 words",
            generation_config={'max_output_tokens': 10}
        )
        
        if response and response.text:
            print(f"✅ API test successful!")
            print(f"📝 Response: {response.text.strip()}")
            return True
        else:
            print("❌ No response from API")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_with_chatbot():
    """Test the API key with the actual chatbot system."""
    print("\n🤖 TESTING WITH CHATBOT SYSTEM")
    print("=" * 40)
    
    api_key = getpass.getpass("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    # Set up environment
    os.environ["GEMINI_API_KEY"] = api_key
    
    # Import chatbot components
    sys.path.insert(0, '.')
    from config import config
    from llm_client import llm_client
    from conversation_flow import conversation_manager
    
    # Update config
    config.GEMINI_API_KEY = api_key
    config.ENABLE_LLM = True
    
    # Initialize client
    print("🔄 Initializing LLM client...")
    llm_client._initialize_client()
    
    if llm_client.is_available():
        print("✅ LLM client initialized successfully!")
        
        # Test with chatbot
        print("🧪 Testing with chatbot conversation...")
        session_id = conversation_manager.start_new_session()
        
        test_input = "I'm feeling stressed about my exams."
        response, is_crisis = conversation_manager.process_user_message(session_id, test_input)
        
        print(f"📝 User: {test_input}")
        print(f"🤖 Bot: {response[:100]}...")
        print(f"🔍 LLM Used: {llm_client.is_available()}")
        
        conversation_manager.end_session(session_id)
        return True
    else:
        print("❌ LLM client initialization failed")
        return False

def main():
    """Main test function."""
    print("🧠 XN MENTAL HEALTH CHATBOT - API KEY TESTER")
    print("This script helps you test your Gemini API key")
    print()
    
    print("Choose test type:")
    print("1. Basic API test")
    print("2. Full chatbot integration test")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        success = test_gemini_api()
    elif choice == "2":
        success = test_with_chatbot()
    else:
        print("Invalid choice")
        return
    
    if success:
        print("\n🎉 All tests passed! Your API key should work with the demo.")
    else:
        print("\n❌ Tests failed. Please check your API key.")
        print("💡 Get a free API key at: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    main()