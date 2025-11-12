"""LLM client with fallback to rule-based responses for mental health conversations."""

import os
from typing import Optional, Dict, Any, List
from config import config
from utils.logger import logger

class LLMClient:
    """Client for interacting with LLM APIs with graceful fallback."""
    
    def __init__(self):
        self.provider = config.get_available_llm_provider()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if not config.ENABLE_LLM or not self.provider:
            logger.info("LLM disabled or no API key available, using fallback responses")
            return
        
        try:
            if self.provider == "openai":
                self._initialize_openai()
            elif self.provider == "gemini":
                self._initialize_gemini()
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            self.client = None
    
    def _initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.warning("OpenAI library not available")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
    
    def _initialize_gemini(self):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai
            
            # Validate API key
            if not config.GEMINI_API_KEY or len(config.GEMINI_API_KEY.strip()) < 10:
                logger.warning("Invalid or missing Gemini API key")
                return
            
            # Configure and test the client
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # First, try to discover available models
            available_models = []
            try:
                models = genai.list_models()
                for model in models:
                    if hasattr(model, 'supported_generation_methods') and 'generateContent' in model.supported_generation_methods:
                        available_models.append(model.name)
                logger.info(f"Found {len(available_models)} available models: {available_models[:3]}")
            except Exception as list_error:
                logger.warning(f"Could not list models: {list_error}")
                # Fallback to common model names, prioritizing 2.0 series
                available_models = [
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
                    'models/gemini-pro',
                    'gemini-pro'
                ]
            
            # Try each available model
            for model_name in available_models:
                try:
                    self.client = genai.GenerativeModel(model_name)
                    logger.info(f"Successfully using Gemini model: {model_name}")
                    break
                except Exception as model_error:
                    logger.warning(f"Model {model_name} not available: {model_error}")
                    continue
            
            if not self.client:
                raise Exception(f"No working Gemini models found. Available: {available_models[:5]}")
            
            # If we got here, the client was created successfully
            logger.info(f"Gemini client initialized successfully with model")
            
            # Optional test - don't fail if this doesn't work
            try:
                test_response = self.client.generate_content(
                    "Hello", 
                    generation_config={
                        'max_output_tokens': 10,
                        'temperature': 0.1
                    }
                )
                
                if test_response and hasattr(test_response, 'text'):
                    try:
                        response_text = test_response.text
                        if response_text:
                            logger.info(f"Test successful: {response_text[:30]}")
                        else:
                            logger.info("Test completed (empty response, likely safety filters)")
                    except:
                        logger.info("Test completed (text access blocked, likely safety filters)")
                else:
                    logger.info("Test completed (no response object)")
                    
            except Exception as test_error:
                logger.info(f"Test request failed but client is still valid: {test_error}")
                # Don't fail - the client creation succeeded, so API key is good
                
        except ImportError:
            logger.warning("Google Generative AI library not available")
        except Exception as e:
            logger.error(f"Gemini initialization failed: {e}")
            self.client = None
    
    def generate_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Generate response using LLM or fallback to rule-based response."""
        if self.client and config.ENABLE_LLM:
            try:
                return self._generate_llm_response(user_input, context)
            except Exception as e:
                logger.error(f"LLM response generation failed: {e}")
                logger.log_llm_usage(self.provider, False, True)
                return self._generate_fallback_response(user_input, context)
        else:
            return self._generate_fallback_response(user_input, context)
    
    def _generate_llm_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Generate response using LLM API."""
        system_prompt = self._build_system_prompt(context)
        user_prompt = self._build_user_prompt(user_input, context)
        
        if self.provider == "openai":
            response = self._call_openai(system_prompt, user_prompt)
        elif self.provider == "gemini":
            response = self._call_gemini(system_prompt + "\n\n" + user_prompt)
        else:
            raise Exception("No valid LLM provider available")
        
        logger.log_llm_usage(self.provider, True, False)
        return response
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=config.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE
        )
        return response.choices[0].message.content.strip()
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        response = self.client.generate_content(
            prompt,
            generation_config={
                'max_output_tokens': config.MAX_TOKENS,
                'temperature': config.TEMPERATURE
            }
        )
        return response.text.strip()
    
    def _build_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Build system prompt for mental health conversations."""
        base_prompt = """You are a supportive mental health chatbot for college students, working with MindBridge Care and Northeastern University services. 

IMPORTANT GUIDELINES:
- Be empathetic, supportive, and non-judgmental
- NEVER provide medical diagnoses or replace professional help
- For crisis situations, immediately direct to professional resources
- Focus on connecting students to appropriate resources and support
- Be culturally sensitive, especially for international students
- Keep responses concise but caring (2-3 sentences typically)
- Always validate feelings while encouraging professional support when needed

CRISIS PROTOCOL:
- If user mentions suicide, self-harm, or crisis: Immediately provide crisis resources
- Crisis contacts: 988 (Crisis Lifeline), (617) 373-3333 (Northeastern Emergency)
- Never minimize crisis situations

AVAILABLE RESOURCES:
- Northeastern CAPS: (617) 373-2772
- MindBridge Care: 1-800-MINDBRIDGE  
- International Student Support: (617) 373-2310
- Academic Support: (617) 373-4430"""
        
        if context:
            if context.get('severity') == 'crisis':
                base_prompt += "\n\nCRISIS DETECTED: Prioritize immediate safety and professional intervention."
            elif context.get('categories'):
                categories = ', '.join(context['categories'])
                base_prompt += f"\n\nUser concerns appear related to: {categories}"
        
        return base_prompt
    
    def _build_user_prompt(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Build user prompt with context."""
        prompt_parts = [f"Student says: \"{user_input}\""]
        
        if context:
            if context.get('matched_scenarios'):
                scenarios = ', '.join(context['matched_scenarios'])
                prompt_parts.append(f"Relevant scenarios: {scenarios}")
            
            if context.get('recommended_resources'):
                resources = ', '.join(context['recommended_resources'])
                prompt_parts.append(f"Recommended resources: {resources}")
        
        prompt_parts.append("Provide a supportive response and suggest appropriate next steps.")
        
        return "\n".join(prompt_parts)
    
    def _generate_fallback_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Generate rule-based fallback response."""
        user_input_lower = user_input.lower()
        
        # Crisis responses
        crisis_keywords = ['suicide', 'kill myself', 'want to die', 'end it all', 'harm myself']
        if any(keyword in user_input_lower for keyword in crisis_keywords):
            return self._get_crisis_fallback_response()
        
        # Academic stress responses
        academic_keywords = ['exam', 'test', 'grade', 'study', 'academic', 'homework']
        if any(keyword in user_input_lower for keyword in academic_keywords):
            return self._get_academic_fallback_response()
        
        # Social/loneliness responses
        social_keywords = ['lonely', 'alone', 'friends', 'social', 'isolated']
        if any(keyword in user_input_lower for keyword in social_keywords):
            return self._get_social_fallback_response()
        
        # International student responses
        international_keywords = ['homesick', 'home', 'international', 'culture', 'family']
        if any(keyword in user_input_lower for keyword in international_keywords):
            return self._get_international_fallback_response()
        
        # Anxiety/stress responses
        anxiety_keywords = ['anxious', 'anxiety', 'worried', 'stressed', 'panic', 'overwhelmed']
        if any(keyword in user_input_lower for keyword in anxiety_keywords):
            return self._get_anxiety_fallback_response()
        
        # General supportive response
        return self._get_general_fallback_response()
    
    def _get_crisis_fallback_response(self) -> str:
        return """🚨 I'm very concerned about what you're sharing. Your safety is the most important thing right now.

**Please contact immediately:**
• **988** - Suicide & Crisis Lifeline (24/7)
• **911** - If in immediate danger
• **(617) 373-3333** - Northeastern Emergency

You are not alone, and there are people who want to help you through this."""
    
    def _get_academic_fallback_response(self) -> str:
        return """Academic stress is really common among college students - you're not alone in feeling this way. It sounds like you're dealing with a lot of pressure right now.

**Resources that can help:**
• **Northeastern CAPS:** (617) 373-2772 for counseling support
• **Academic Success Center:** (617) 373-4430 for study strategies
• **MindBridge Care:** 1-800-MINDBRIDGE for academic coaching

Would you like help connecting with any of these resources?"""
    
    def _get_social_fallback_response(self) -> str:
        return """Feeling lonely or isolated in college is more common than you might think. Many students struggle with making connections, especially in a new environment.

**Support options:**
• **Northeastern CAPS:** (617) 373-2772 for counseling
• **Peer Support Programs:** peersupport@northeastern.edu
• **MindBridge Care Peer Network:** Connect through their app

Building friendships takes time. What kind of social connections are you hoping to make?"""
    
    def _get_international_fallback_response(self) -> str:
        return """Homesickness and cultural adjustment are natural parts of the international student experience. It's completely normal to miss home and feel overwhelmed by cultural differences.

**Specialized support:**
• **International Student Services:** (617) 373-2310
• **Northeastern CAPS:** (617) 373-2772 (culturally sensitive counseling)
• **MindBridge Care:** 1-800-MINDBRIDGE

Many international students find it helpful to connect with others who understand their experience. Would you like information about cultural groups or international student communities?"""
    
    def _get_anxiety_fallback_response(self) -> str:
        return """Anxiety can feel overwhelming, but it's very treatable with the right support. What you're experiencing is valid, and there are effective ways to manage these feelings.

**Immediate support:**
• **Northeastern CAPS:** (617) 373-2772
• **MindBridge Care:** 1-800-MINDBRIDGE
• **Crisis Lifeline:** 988 (if anxiety becomes overwhelming)

In the meantime, try some grounding techniques like deep breathing or the 5-4-3-2-1 method (name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste)."""
    
    def _get_general_fallback_response(self) -> str:
        return """Thank you for sharing what's on your mind. It takes courage to reach out when you're struggling. Whatever you're going through, you don't have to face it alone.

**Available support:**
• **Northeastern CAPS:** (617) 373-2772
• **MindBridge Care:** 1-800-MINDBRIDGE  
• **Crisis support:** 988 (available 24/7)

Would you like to tell me more about what's been bothering you? I'm here to listen and help connect you with the right resources."""
    
    def is_available(self) -> bool:
        """Check if LLM client is available."""
        return self.client is not None and config.ENABLE_LLM

# Global LLM client instance
llm_client = LLMClient()