#!/usr/bin/env python3
"""
Web-based Interactive Demo for XN Mental Health Chatbot

This creates a simple web interface for testing the chatbot with Gemini API integration.
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, session
import uuid
import time
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_flow import conversation_manager
from resource_database import resource_db
from config import config
from llm_client import llm_client

app = Flask(__name__)
app.secret_key = 'demo-secret-key-change-in-production'

# Store active demo sessions
demo_sessions = {}

@app.route('/')
def index():
    """Main demo page."""
    return render_template('demo.html')

@app.route('/api/setup', methods=['POST'])
def setup_api():
    """Set up Gemini API key."""
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    
    if api_key:
        # Validate API key format
        if len(api_key) < 10:
            return jsonify({
                'success': False, 
                'message': 'API key appears to be too short. Please check your key.',
                'llm_enabled': False
            })
        
        # Set the API key in environment and config
        os.environ["GEMINI_API_KEY"] = api_key
        config.GEMINI_API_KEY = api_key
        config.ENABLE_LLM = True
        
        # Reinitialize the LLM client
        try:
            # Clear any previous client
            llm_client.client = None
            llm_client._initialize_client()
            
            # Give it a moment and check again
            import time
            time.sleep(0.5)
            
            # Check if client was created successfully
            if llm_client.client is not None:
                session['api_key_set'] = True
                return jsonify({
                    'success': True, 
                    'message': 'Gemini API key validated successfully! LLM responses enabled.',
                    'llm_enabled': True
                })
            else:
                # Client creation failed, but let's try a direct test
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    
                    # Try to create any working model
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
                    
                    working_model = None
                    for model_name in model_names:
                        try:
                            test_model = genai.GenerativeModel(model_name)
                            # If we can create the model, the API key is valid
                            working_model = model_name
                            break
                        except Exception as model_err:
                            continue
                    
                    if working_model:
                        # API key is valid, manually set up the client
                        llm_client.client = genai.GenerativeModel(working_model)
                        session['api_key_set'] = True
                        return jsonify({
                            'success': True, 
                            'message': f'Gemini API key validated successfully! Using model: {working_model}',
                            'llm_enabled': True
                        })
                    else:
                        session['api_key_set'] = False
                        return jsonify({
                            'success': False, 
                            'message': 'No available Gemini models found for your API key. Using fallback responses.',
                            'llm_enabled': False
                        })
                        
                except Exception as direct_error:
                    session['api_key_set'] = False
                    error_msg = str(direct_error)
                    if "API_KEY" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                        return jsonify({
                            'success': False, 
                            'message': 'API key authentication failed. Please check your key. Using fallback responses.',
                            'llm_enabled': False
                        })
                    else:
                        return jsonify({
                            'success': False, 
                            'message': f'API setup issue: {error_msg}. Using fallback responses.',
                            'llm_enabled': False
                        })
                        
        except Exception as e:
            session['api_key_set'] = False
            return jsonify({
                'success': False, 
                'message': f'Error setting up API: {str(e)}. Using fallback responses.',
                'llm_enabled': False
            })
    else:
        session['api_key_set'] = False
        return jsonify({
            'success': True, 
            'message': 'No API key provided. Using rule-based fallback responses.',
            'llm_enabled': False
        })

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Start a new conversation session."""
    session_id = conversation_manager.start_new_session()
    session['conversation_id'] = session_id
    
    welcome = conversation_manager.get_welcome_message()
    
    return jsonify({
        'session_id': session_id,
        'welcome_message': welcome,
        'llm_enabled': session.get('api_key_set', False)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat message."""
    data = request.get_json()
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({'error': 'Empty message'}), 400
    
    conversation_id = session.get('conversation_id')
    if not conversation_id:
        return jsonify({'error': 'No active session'}), 400
    
    try:
        start_time = time.time()
        response, is_crisis = conversation_manager.process_user_message(conversation_id, user_input)
        processing_time = time.time() - start_time
        
        # Get session analysis
        conv_session = conversation_manager.active_sessions[conversation_id]
        latest_message = conv_session.messages[-1]
        
        # Get recommended resources
        resources = []
        for resource_id in conv_session.recommended_resources[:5]:  # Top 5
            resource = resource_db.get_resource(resource_id)
            if resource:
                contact = resource.contact_info.get('phone', 
                         resource.contact_info.get('website', 
                         resource.contact_info.get('email', 'Contact available')))
                resources.append({
                    'name': resource.name,
                    'contact': contact,
                    'type': resource.resource_type.value,
                    'cost': resource.cost,
                    'description': resource.description
                })
        
        return jsonify({
            'response': response,
            'is_crisis': is_crisis,
            'analysis': {
                'processing_time': round(processing_time, 2),
                'llm_used': session.get('api_key_set', False) and llm_client.is_available(),
                'severity': latest_message.severity_assessment.value,
                'keywords': latest_message.detected_keywords,
                'concerns': conv_session.identified_concerns,
                'resources_count': len(conv_session.recommended_resources)
            },
            'resources': resources,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session_info', methods=['GET'])
def session_info():
    """Get current session information."""
    conversation_id = session.get('conversation_id')
    if not conversation_id or conversation_id not in conversation_manager.active_sessions:
        return jsonify({'error': 'No active session'}), 400
    
    summary = conversation_manager.get_session_summary(conversation_id)
    conv_session = conversation_manager.active_sessions[conversation_id]
    
    return jsonify({
        'session_id': conversation_id[:8] + '...',
        'message_count': summary['message_count'],
        'duration_minutes': round(summary['duration_minutes'], 1),
        'identified_concerns': summary['identified_concerns'],
        'crisis_flags': len(conv_session.crisis_flags),
        'total_resources': len(conv_session.recommended_resources),
        'user_profile': conv_session.user_profile
    })

@app.route('/api/resources', methods=['GET'])
def get_resources():
    """Get all available resources."""
    crisis_resources = []
    for resource in resource_db.get_crisis_resources():
        contact = resource.contact_info.get('phone', 'Contact available')
        crisis_resources.append({'name': resource.name, 'contact': contact})
    
    northeastern_resources = []
    for resource in resource_db.get_northeastern_resources():
        contact = resource.contact_info.get('phone', 
                 resource.contact_info.get('email', 'Contact available'))
        northeastern_resources.append({'name': resource.name, 'contact': contact})
    
    mindbridge_resources = []
    for resource in resource_db.get_mindbridge_resources():
        contact = resource.contact_info.get('phone', 
                 resource.contact_info.get('website', 'Contact available'))
        mindbridge_resources.append({'name': resource.name, 'contact': contact})
    
    return jsonify({
        'crisis': crisis_resources,
        'northeastern': northeastern_resources,
        'mindbridge': mindbridge_resources
    })

@app.route('/api/demo_scenarios', methods=['GET'])
def demo_scenarios():
    """Get predefined demo scenarios."""
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
        },
        {
            "name": "Find Mental Health Provider",
            "input": "I think I need to find a therapist to help me with my anxiety. Can you help me find someone in my area?",
            "description": "Tests personalized provider search with location and insurance matching"
        }
    ]
    return jsonify(scenarios)

if __name__ == '__main__':
    # Create templates directory and HTML file
    os.makedirs('templates', exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XN Mental Health Chatbot - Interactive Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .main-content {
            display: flex;
            height: 600px;
        }
        .chat-section {
            flex: 2;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #eee;
        }
        .sidebar {
            flex: 1;
            background: #f8f9fa;
            padding: 20px;
            overflow-y: auto;
        }
        .setup-section {
            background: #fff3cd;
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .setup-section.success {
            background: #d4edda;
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #fafafa;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 10px;
            max-width: 80%;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
        }
        .bot-message {
            background: white;
            border: 1px solid #ddd;
        }
        .crisis-message {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        .chat-input {
            padding: 20px;
            border-top: 1px solid #eee;
            background: white;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        .input-group input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background: #0056b3;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-warning {
            background: #ffc107;
            color: #212529;
        }
        .analysis-panel {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        .resource-item {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #28a745;
        }
        .scenario-btn {
            width: 100%;
            margin: 5px 0;
            text-align: left;
            background: #e9ecef;
            border: 1px solid #ced4da;
        }
        .scenario-btn:hover {
            background: #dee2e6;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-enabled {
            background: #28a745;
        }
        .status-disabled {
            background: #dc3545;
        }
        .small-text {
            font-size: 0.85em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 XN Mental Health Chatbot</h1>
            <p>Interactive Demo with Live Gemini API Integration</p>
        </div>
        
        <div id="setup-section" class="setup-section">
            <h3>🔑 API Setup</h3>
            <p>Enter your Gemini API key to enable live LLM responses, or continue with fallback responses.</p>
            <div class="input-group">
                <input type="password" id="api-key" placeholder="Enter Gemini API key (optional)">
                <button class="btn btn-primary" onclick="setupAPI()">Setup</button>
            </div>
            <p class="small-text">Get a free API key at: <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a></p>
        </div>
        
        <div class="main-content">
            <div class="chat-section">
                <div id="chat-messages" class="chat-messages">
                    <div class="message bot-message">
                        <strong>🤖 Chatbot:</strong> Welcome! Please set up your API key above, then click "Start Session" to begin.
                    </div>
                </div>
                <div class="chat-input">
                    <div class="input-group">
                        <input type="text" id="message-input" placeholder="Type your message..." disabled>
                        <button class="btn btn-primary" id="send-btn" onclick="sendMessage()" disabled>Send</button>
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="analysis-panel">
                    <h4>📊 System Status</h4>
                    <p><span id="llm-status" class="status-indicator status-disabled"></span>LLM: <span id="llm-text">Disabled</span></p>
                    <p><span id="session-status" class="status-indicator status-disabled"></span>Session: <span id="session-text">Not Started</span></p>
                </div>
                
                <div class="analysis-panel">
                    <h4>🎭 Demo Scenarios</h4>
                    <div id="scenarios-container">
                        <button class="btn scenario-btn" onclick="startSession()">Start Session First</button>
                    </div>
                </div>
                
                <div id="analysis-container" class="analysis-panel" style="display: none;">
                    <h4>🔍 Last Response Analysis</h4>
                    <div id="analysis-content"></div>
                </div>
                
                <div id="resources-container" class="analysis-panel" style="display: none;">
                    <h4>📋 Recommended Resources</h4>
                    <div id="resources-content"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let sessionStarted = false;
        let llmEnabled = false;

        async function setupAPI() {
            const apiKey = document.getElementById('api-key').value;
            const setupSection = document.getElementById('setup-section');
            
            try {
                const response = await fetch('/api/setup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: apiKey})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    setupSection.className = 'setup-section success';
                    setupSection.innerHTML = `
                        <h3>✅ Setup Complete</h3>
                        <p>${data.message}</p>
                        <button class="btn btn-success" onclick="startSession()">Start Conversation</button>
                    `;
                    
                    llmEnabled = data.llm_enabled;
                    updateStatus();
                    loadScenarios();
                } else {
                    alert('Setup failed: ' + data.message);
                }
            } catch (error) {
                alert('Setup error: ' + error.message);
            }
        }

        async function startSession() {
            try {
                const response = await fetch('/api/start_session', {method: 'POST'});
                const data = await response.json();
                
                addMessage('bot', data.welcome_message);
                
                document.getElementById('message-input').disabled = false;
                document.getElementById('send-btn').disabled = false;
                
                sessionStarted = true;
                updateStatus();
                
            } catch (error) {
                alert('Failed to start session: ' + error.message);
            }
        }

        async function runScenario(message) {
            // Ensure session is started first
            if (!sessionStarted) {
                await startSession();
            }
            
            // Small delay to ensure session is ready
            setTimeout(() => {
                sendMessage(message);
            }, 500);
        }

        async function sendMessage(message = null) {
            const input = document.getElementById('message-input');
            const userMessage = message || input.value.trim();
            
            if (!userMessage) return;
            
            addMessage('user', userMessage);
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: userMessage})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage('bot', 'Error: ' + data.error, true);
                    return;
                }
                
                addMessage('bot', data.response, data.is_crisis);
                showAnalysis(data.analysis);
                showResources(data.resources);
                
            } catch (error) {
                addMessage('bot', 'Error: ' + error.message, true);
            }
        }

        function addMessage(sender, content, isCrisis = false) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            
            let className = 'message ';
            if (sender === 'user') {
                className += 'user-message';
            } else if (isCrisis) {
                className += 'crisis-message';
            } else {
                className += 'bot-message';
            }
            
            messageDiv.className = className;
            messageDiv.innerHTML = `<strong>${sender === 'user' ? '👤 You' : '🤖 Chatbot'}:</strong> ${content.replace(/\\n/g, '<br>')}`;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function showAnalysis(analysis) {
            const container = document.getElementById('analysis-container');
            const content = document.getElementById('analysis-content');
            
            content.innerHTML = `
                <p><strong>Response Time:</strong> ${analysis.processing_time}s</p>
                <p><strong>LLM Used:</strong> ${analysis.llm_used ? 'Yes (Gemini)' : 'No (Fallback)'}</p>
                <p><strong>Severity:</strong> ${analysis.severity.toUpperCase()}</p>
                <p><strong>Keywords:</strong> ${analysis.keywords.join(', ')}</p>
                <p><strong>Concerns:</strong> ${analysis.concerns.join(', ')}</p>
                <p><strong>Resources:</strong> ${analysis.resources_count}</p>
            `;
            
            container.style.display = 'block';
        }

        function showResources(resources) {
            const container = document.getElementById('resources-container');
            const content = document.getElementById('resources-content');
            
            if (resources.length === 0) {
                container.style.display = 'none';
                return;
            }
            
            content.innerHTML = resources.map(resource => `
                <div class="resource-item">
                    <strong>${resource.name}</strong><br>
                    <small>Contact: ${resource.contact}</small><br>
                    <small>Type: ${resource.type} | Cost: ${resource.cost}</small>
                </div>
            `).join('');
            
            container.style.display = 'block';
        }

        async function loadScenarios() {
            try {
                const response = await fetch('/api/demo_scenarios');
                const scenarios = await response.json();
                
                const container = document.getElementById('scenarios-container');
                container.innerHTML = scenarios.map((scenario, index) => `
                    <button class="btn scenario-btn" data-scenario-input="${scenario.input.replace(/"/g, '&quot;')}" data-scenario-index="${index}">
                        <strong>${scenario.name}</strong><br>
                        <small>${scenario.description}</small>
                    </button>
                `).join('');
                
                // Add event listeners to scenario buttons
                document.querySelectorAll('.scenario-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const input = this.getAttribute('data-scenario-input');
                        runScenario(input);
                    });
                });
                
            } catch (error) {
                console.error('Failed to load scenarios:', error);
            }
        }

        function updateStatus() {
            const llmStatus = document.getElementById('llm-status');
            const llmText = document.getElementById('llm-text');
            const sessionStatus = document.getElementById('session-status');
            const sessionText = document.getElementById('session-text');
            
            if (llmEnabled) {
                llmStatus.className = 'status-indicator status-enabled';
                llmText.textContent = 'Enabled (Gemini)';
            } else {
                llmStatus.className = 'status-indicator status-disabled';
                llmText.textContent = 'Disabled (Fallback)';
            }
            
            if (sessionStarted) {
                sessionStatus.className = 'status-indicator status-enabled';
                sessionText.textContent = 'Active';
            } else {
                sessionStatus.className = 'status-indicator status-disabled';
                sessionText.textContent = 'Not Started';
            }
        }

        // Enter key support
        document.getElementById('message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Load scenarios when page loads
        window.addEventListener('load', function() {
            loadScenarios();
            updateStatus();
        });
    </script>
</body>
</html>'''
    
    with open('templates/demo.html', 'w') as f:
        f.write(html_content)
    
    print("🌐 Starting web demo server...")
    print("📱 Access the demo at: http://localhost:12000")
    print("🌐 External access: https://work-1-fnrhzfupamkpdhxp.prod-runtime.all-hands.dev")
    print("🔑 You can enter your Gemini API key in the web interface")
    print("⚡ The demo will show both LLM and fallback responses")
    print()
    
    app.run(host='0.0.0.0', port=12000, debug=False)