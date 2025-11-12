# XN Mental Health Chatbot

A comprehensive mental health support chatbot designed for college students, integrating MindBridge Care services with Northeastern University resources.

## 🎯 Project Overview

This Experiential Network (XN) project provides personalized mental health guidance and resource navigation for college students. The system handles diverse scenarios including academic stress, social isolation, cultural adjustment challenges, and crisis situations with appropriate escalation protocols.

## ✨ Key Features

- **Intelligent Conversation Flow**: Natural language processing with crisis detection
- **Comprehensive Resource Database**: Integration of MindBridge Care and Northeastern services
- **Crisis Intervention**: Immediate safety protocols with professional escalation
- **Scenario-Based Matching**: 75+ mental health scenarios with personalized recommendations
- **Multi-Modal Support**: Academic, social, cultural, and wellness assistance
- **Privacy-First Design**: No storage of personal mental health information
- **LLM Integration**: Optional AI enhancement with rule-based fallback

## 🏗️ Architecture

### Core Components

- **Streamlit Web Interface** (`main.py`): Interactive chat interface with resource browser
- **Conversation Manager** (`conversation_flow.py`): Session management and dialogue flow
- **Domain Logic** (`domain_logic.py`): Mental health scenario matching and resource recommendation
- **Crisis Handler** (`crisis_handler.py`): Safety-first crisis detection and intervention
- **Resource Database** (`resource_database.py`): Comprehensive service catalog
- **Scenario Database** (`scenario_data.py`): 75+ college mental health scenarios
- **LLM Client** (`llm_client.py`): AI integration with offline fallback

### Data Models

- **Mental Health Scenarios**: Structured representation of student challenges
- **Resources**: MindBridge Care and Northeastern services with contact information
- **Conversation Sessions**: Privacy-conscious session management
- **Crisis Assessments**: Risk evaluation and intervention protocols

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd XN_Project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Configure LLM API keys** (system works without them):
   ```bash
   # Create .env file (optional)
   echo "OPENAI_API_KEY=your_openai_key_here" > .env
   echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
   ```

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

5. **Access the application:**
   - Open your browser to `http://localhost:12000`
   - Or use the provided URL in the terminal

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_domain_logic.py
pytest tests/test_conversation_flow.py
pytest tests/test_crisis_handler.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## 📊 Usage Examples

### Academic Stress Support
```
User: "I'm overwhelmed with upcoming exams and worried about failing"
System: Provides academic support resources, study strategies, and counseling options
```

### Crisis Intervention
```
User: "I'm thinking about hurting myself"
System: Immediately activates crisis protocols with emergency contacts and safety resources
```

### International Student Support
```
User: "I'm homesick and struggling with cultural differences"
System: Connects to international student services and cultural adjustment resources
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key (optional)
- `GEMINI_API_KEY`: Google Gemini API key (optional)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ENABLE_LLM`: Enable/disable LLM features (default: true)
- `DEBUG_MODE`: Enable debug logging (default: false)

### Key Contacts

- **Crisis Hotline**: 988 (Suicide & Crisis Lifeline)
- **Emergency**: 911
- **Northeastern CAPS**: (617) 373-2772
- **MindBridge Care**: 1-800-MINDBRIDGE

## 🛡️ Privacy & Ethics

### Privacy Protections
- No storage of personal mental health information
- Session data is temporary and anonymized
- Conversation history is not persisted beyond session

### Ethical Guidelines
- Clear boundaries about system capabilities vs. professional help
- Immediate escalation for crisis situations
- Cultural sensitivity for diverse student populations
- Transparency about AI vs. rule-based responses

### Crisis Safety Protocols
- Automatic detection of suicidal ideation and self-harm indicators
- Immediate connection to professional crisis resources
- Clear escalation pathways to human intervention
- 24/7 crisis contact information prominently displayed

## 📚 Resource Integration

### MindBridge Care Services
- Counseling network access
- Crisis intervention support
- Academic success coaching
- Peer support network
- Wellness programs

### Northeastern University Resources
- Counseling and Psychological Services (CAPS)
- International Student & Scholar Institute (ISSI)
- Academic Success Center
- Disability Resource Center
- Peer support programs

## 🔄 System Workflow

1. **User Input Processing**: Natural language analysis and keyword extraction
2. **Scenario Matching**: Map concerns to relevant mental health scenarios
3. **Crisis Assessment**: Evaluate risk level and safety concerns
4. **Resource Recommendation**: Generate personalized resource suggestions
5. **Response Generation**: Combine AI/rule-based responses with resource information
6. **Follow-up Planning**: Provide next steps and continued support options

## 🧠 Mental Health Scenarios Covered

- **Academic Stress**: Exam anxiety, performance pressure, failure fears
- **Social Isolation**: Loneliness, difficulty making friends, social anxiety
- **Cultural Adjustment**: Homesickness, international student challenges
- **Self-Esteem Issues**: Confidence problems, imposter syndrome
- **Crisis Situations**: Suicidal ideation, self-harm, emergency support
- **Relationship Problems**: Family pressure, romantic relationships, conflicts
- **Financial Stress**: Money worries, tuition concerns, work-life balance

## 🤝 Contributing

This project is designed for educational and research purposes. Key areas for enhancement:

- Additional mental health scenarios
- Enhanced cultural sensitivity features
- Integration with additional university systems
- Improved natural language processing
- Mobile application development

## 📄 License

This project is developed for educational purposes as part of the Experiential Network (XN) program.

## 🆘 Emergency Resources

**If you or someone you know is in immediate danger:**

- **Call 911** for emergency services
- **Call 988** for Suicide & Crisis Lifeline (24/7)
- **Text HOME to 741741** for Crisis Text Line
- **Call (617) 373-3333** for Northeastern Emergency Services

**Remember**: This chatbot is a support tool and not a replacement for professional mental health care.

---

*Developed in partnership with MindBridge Care and Northeastern University*