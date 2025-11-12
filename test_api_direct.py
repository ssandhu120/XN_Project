#!/usr/bin/env python3
"""
Direct API key tester - bypasses our client logic
"""

def test_api_key_direct(api_key):
    """Test API key directly with minimal setup."""
    print(f"🔍 Testing API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI library available")
        
        # Configure API
        genai.configure(api_key=api_key)
        print("✅ API key configured")
        
        # Create model - try latest model names first, prioritizing 2.0 series
        model_names = [
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash',
            'models/gemini-2.0-flash-exp', 
            'models/gemini-2.0-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'models/gemini-1.5-flash-latest',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'gemini-pro'
        ]
        model = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"✅ Model created: {model_name}")
                break
            except Exception as model_error:
                print(f"⚠️  Model {model_name} not available: {model_error}")
                continue
        
        if not model:
            print("❌ No available models found")
            return False
        
        # Test with multiple prompts to handle safety filters
        test_prompts = [
            "Hello",
            "Say hi",
            "What is 2+2?",
            "Respond with the word 'test'"
        ]
        
        for i, prompt in enumerate(test_prompts):
            try:
                print(f"🧪 Testing prompt {i+1}: '{prompt}'")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'max_output_tokens': 20,
                        'temperature': 0.1
                    }
                )
                
                if response:
                    try:
                        text = response.text
                        if text and text.strip():
                            print(f"✅ SUCCESS! Response: '{text.strip()}'")
                            return True
                        else:
                            print(f"⚠️  Empty response for prompt {i+1}")
                    except Exception as text_error:
                        print(f"⚠️  Text access error for prompt {i+1}: {text_error}")
                        # This might be safety filters, but API key could still be valid
                        continue
                else:
                    print(f"⚠️  No response object for prompt {i+1}")
                    
            except Exception as prompt_error:
                print(f"⚠️  Error with prompt {i+1}: {prompt_error}")
                continue
        
        # If we get here, we tried all prompts
        print("⚠️  All test prompts had issues, but API key might still be valid")
        print("🤔 This could be due to safety filters or regional restrictions")
        return "partial"  # API key might work, just having issues with test prompts
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error: {error_str}")
        
        if any(keyword in error_str.lower() for keyword in ['api_key', 'authentication', 'invalid', 'unauthorized']):
            print("🔑 This appears to be an API key authentication issue")
            return False
        else:
            print("🤔 This might not be an API key issue")
            return "unknown"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        result = test_api_key_direct(api_key)
        print(f"\n📊 Result: {result}")
    else:
        print("Usage: python test_api_direct.py YOUR_API_KEY")