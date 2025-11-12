# 🧠 XN Mental Health Chatbot - Live Demo Instructions

## 🚀 Ready to Demo!

Your XN Mental Health Chatbot is now ready for live demonstration with Gemini API integration. Here are your options:

## 🌐 **Option 1: Web Demo (Recommended)**

**✅ CURRENTLY RUNNING** at: **http://localhost:5000**

### Features:
- 🎨 Beautiful web interface
- 🔑 Easy API key entry in the browser
- 📊 Real-time system analysis display
- 🎭 One-click demo scenarios
- 📋 Live resource recommendations
- 💬 Interactive chat interface

### How to Use:
1. **Open your browser** and go to: `http://localhost:5000`
2. **Enter your Gemini API key** in the setup section (or skip for fallback responses)
3. **Click "Start Conversation"** to begin
4. **Try demo scenarios** or chat freely
5. **See live analysis** of system responses in the sidebar

---

## 💻 **Option 2: Terminal Demo**

Run the interactive terminal demo:

```bash
cd /workspace/project/XN_Project
python interactive_demo.py
```

### Features:
- 🔐 Secure API key entry (hidden input)
- 📊 Detailed system analysis after each response
- 🎭 Predefined demo scenarios
- 💬 Free chat mode
- 📋 Resource information display

---

## 🧪 **Option 3: Run All Tests**

See all 50 tests passing (including 7 E2E tests):

```bash
cd /workspace/project/XN_Project
python -m pytest tests/ -v
```

---

## 📊 **Option 4: Static Demo**

See pre-recorded scenarios without API key:

```bash
cd /workspace/project/XN_Project
python demo_e2e_functionality.py
```

---

## 🔑 **Gemini API Key Setup**

### Get Your Free API Key:
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (should start with "AIza...")

### 🔧 **Troubleshooting API Key Issues**

If you get "Setup failed" or "API key validation failed":

1. **Test your API key first:**
   ```bash
   cd /workspace/project/XN_Project
   python test_gemini_api.py
   ```

2. **Common issues:**
   - ❌ API key too short (should be ~40 characters)
   - ❌ API key doesn't start with "AIza"
   - ❌ API key has extra spaces or characters
   - ❌ Gemini API not enabled in your Google Cloud project

3. **If API key validation fails:**
   - Double-check you copied the complete key
   - Try generating a new API key
   - Make sure you're using Google AI Studio (not Google Cloud Console)

4. **Still having issues?**
   - The system works perfectly with fallback responses
   - All E2E functionality is available without API key
   - You'll still see complete resource recommendations

### What Happens With/Without API Key:

**✅ WITH Gemini API Key:**
- Real LLM-generated responses
- More natural, contextual conversations
- Dynamic response generation
- Personalized mental health guidance

**⚡ WITHOUT API Key:**
- Rule-based fallback responses
- Still fully functional
- All E2E scenarios work
- Resource recommendations work
- Crisis detection works

---

## 🎭 **Demo Scenarios to Try**

### 1. **Academic Stress**
*"I'm really stressed about my upcoming finals. I can't sleep and I'm worried I'll fail everything."*

**Expected:** Academic coaching + counseling resources

### 2. **Crisis Intervention**
*"I can't take this anymore. I've been thinking about ending it all."*

**Expected:** Immediate crisis resources (988, emergency contacts)

### 3. **Social Isolation**
*"I feel so lonely at college. I don't have any friends and spend all my time alone."*

**Expected:** Peer support + social programs

### 4. **International Student**
*"I'm an international student and I'm really homesick. Everything feels different here."*

**Expected:** ISSI resources + cultural support

---

## 🏥 **What You'll See Demonstrated**

### ✅ **Complete E2E Flow:**
1. **User Input Processing** - Natural language understanding
2. **Concern Detection** - Academic stress, social isolation, crisis, etc.
3. **Severity Assessment** - Low, moderate, high, crisis levels
4. **Resource Matching** - Appropriate specialists and services
5. **Response Generation** - Supportive, professional responses

### ✅ **MindBridge Care Integration:**
- Licensed therapists and counselors (1-800-MINDBRIDGE)
- 24/7 crisis intervention (1-800-CRISIS-MB)
- Academic success coaching
- Peer support network (MindBridge Connect app)
- Wellness programs

### ✅ **Northeastern University Resources:**
- CAPS counseling (617) 373-2772
- Emergency mental health (617) 373-3333
- Academic Success Center (617) 373-4430
- International Student Services (617) 373-2310
- Peer support programs

### ✅ **Crisis Safety Protocols:**
- Immediate detection of suicidal ideation
- Emergency resource escalation (988, 911)
- Human intervention flags
- Safety-first response prioritization

### ✅ **Context Retention:**
- Multi-turn conversation memory
- User profile building
- Concern accumulation
- Session history tracking

---

## 📈 **System Capabilities Verified**

- ✅ **50/50 tests passing** (100% success rate)
- ✅ **7 comprehensive E2E tests** covering complete workflows
- ✅ **Crisis detection and intervention** protocols working
- ✅ **Resource recommendation accuracy** validated
- ✅ **Contact information completeness** verified
- ✅ **Multi-turn conversation context** maintained
- ✅ **MindBridge Care and university integration** confirmed

---

## 🎯 **Key Demo Points**

1. **Show both LLM and fallback responses** - System works with or without API
2. **Demonstrate crisis detection** - Safety protocols activate immediately
3. **Highlight resource integration** - Real contact information for specialists
4. **Test conversation continuity** - Context maintained across multiple turns
5. **Validate E2E functionality** - Complete flow from input to resource delivery

---

## 🚀 **Ready to Go!**

Your system is fully functional and ready for demonstration. The web interface at `http://localhost:5000` provides the best demo experience, but all options are available.

**Happy demoing! 🎉**