#!/usr/bin/env python3
"""
Quick API test - paste your API key here to test
"""

# PASTE YOUR API KEY HERE (replace the placeholder)
API_KEY = "PASTE_YOUR_API_KEY_HERE"

def test_api():
    if API_KEY == "PASTE_YOUR_API_KEY_HERE":
        print("❌ Please paste your actual API key in the script")
        return
    
    print(f"🔍 Testing API key: {API_KEY[:10]}...{API_KEY[-4:]}")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content("Say 'Hello World' in exactly those two words")
        
        if response and response.text:
            print(f"✅ SUCCESS! Response: {response.text}")
            print("🎉 Your API key works perfectly!")
            
            # Test with chatbot system
            import os
            import sys
            sys.path.insert(0, '.')
            
            os.environ["GEMINI_API_KEY"] = API_KEY
            from config import config
            from llm_client import llm_client
            
            config.GEMINI_API_KEY = API_KEY
            config.ENABLE_LLM = True
            
            llm_client._initialize_client()
            
            if llm_client.is_available():
                print("✅ Chatbot integration also works!")
            else:
                print("⚠️  API works but chatbot integration needs debugging")
                
        else:
            print(f"❌ No response: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()