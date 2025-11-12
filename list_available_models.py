#!/usr/bin/env python3
"""
List available Gemini models for your API key
"""

def list_models(api_key):
    """List all available models for the given API key."""
    print(f"🔍 Checking available models for API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        print("📋 Available models:")
        models = genai.list_models()
        
        for model in models:
            print(f"   • {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                methods = model.supported_generation_methods
                if 'generateContent' in methods:
                    print(f"     ✅ Supports generateContent")
                else:
                    print(f"     ❌ Does not support generateContent")
            print()
            
        # Test the most common ones
        test_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']
        
        print("🧪 Testing common model names:")
        for model_name in test_models:
            try:
                test_model = genai.GenerativeModel(model_name)
                response = test_model.generate_content("Hello", generation_config={'max_output_tokens': 5})
                print(f"   ✅ {model_name}: WORKS")
            except Exception as e:
                print(f"   ❌ {model_name}: {str(e)[:100]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        list_models(api_key)
    else:
        print("Usage: python list_available_models.py YOUR_API_KEY")