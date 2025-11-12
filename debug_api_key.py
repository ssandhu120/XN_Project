#!/usr/bin/env python3
"""
Debug script to test Gemini API key functionality
"""

import os
import sys
sys.path.insert(0, '.')

def test_api_key_direct(api_key):
    """Test API key directly with Gemini."""
    print(f"🔍 Testing API key: {api_key[:10]}...{api_key[-4:]}")
    print(f"📏 Key length: {len(api_key)} characters")
    
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
            "Say hello in exactly 2 words",
            generation_config={'max_output_tokens': 10}
        )
        
        if response and response.text:
            print(f"✅ API test successful!")
            print(f"📝 Response: '{response.text.strip()}'")
            return True
        else:
            print("❌ No response from API")
            print(f"Response object: {response}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_with_chatbot_system(api_key):
    """Test with the actual chatbot system."""
    print("\n🤖 TESTING WITH CHATBOT SYSTEM")
    print("=" * 50)
    
    # Set environment
    os.environ["GEMINI_API_KEY"] = api_key
    
    # Import and configure
    from config import config
    from llm_client import llm_client
    
    config.GEMINI_API_KEY = api_key
    config.ENABLE_LLM = True
    
    print("🔄 Initializing LLM client...")
    llm_client._initialize_client()
    
    print(f"🔍 Client available: {llm_client.is_available()}")
    print(f"🔍 Client object: {llm_client.client}")
    
    if llm_client.is_available():
        print("✅ LLM client working!")
        
        # Test generation
        test_response = llm_client.generate_response("Hello, how are you?")
        print(f"📝 Test response: {test_response[:100]}...")
        return True
    else:
        print("❌ LLM client not available")
        return False

def main():
    """Main debug function."""
    print("🔑 GEMINI API KEY DEBUGGER")
    print("=" * 40)
    
    # Check environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print(f"✅ Found API key in environment: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ No API key found in environment")
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    # Test direct API
    print("\n1️⃣ DIRECT API TEST")
    print("=" * 30)
    direct_success = test_api_key_direct(api_key)
    
    # Test with chatbot
    print("\n2️⃣ CHATBOT INTEGRATION TEST")
    print("=" * 30)
    chatbot_success = test_with_chatbot_system(api_key)
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 20)
    print(f"Direct API Test: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"Chatbot Integration: {'✅ PASS' if chatbot_success else '❌ FAIL'}")
    
    if direct_success and chatbot_success:
        print("\n🎉 Your API key should work perfectly!")
    elif direct_success and not chatbot_success:
        print("\n⚠️  API key works, but chatbot integration has issues")
    else:
        print("\n❌ API key validation failed")

if __name__ == "__main__":
    main()