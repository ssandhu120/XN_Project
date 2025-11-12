#!/usr/bin/env python3
"""
Demo Launcher for XN Mental Health Chatbot

Choose between terminal-based or web-based demo.
"""

import sys
import subprocess

def main():
    print("🧠 XN MENTAL HEALTH CHATBOT - DEMO LAUNCHER")
    print("=" * 50)
    print("Choose your demo experience:")
    print()
    print("1. 💻 Terminal Demo - Interactive command-line interface")
    print("2. 🌐 Web Demo - Browser-based interface (recommended)")
    print("3. 🧪 Run E2E Tests - See all tests passing")
    print("4. 📊 Static Demo - Pre-recorded scenarios")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting Terminal Demo...")
                subprocess.run([sys.executable, "interactive_demo.py"])
                break
                
            elif choice == "2":
                print("\n🚀 Starting Web Demo...")
                print("📱 The web interface will open at http://localhost:5000")
                print("🔑 You can enter your Gemini API key in the web interface")
                subprocess.run([sys.executable, "web_demo.py"])
                break
                
            elif choice == "3":
                print("\n🧪 Running E2E Tests...")
                subprocess.run([sys.executable, "-m", "pytest", "tests/test_e2e_conversation_flows.py", "-v"])
                break
                
            elif choice == "4":
                print("\n📊 Running Static Demo...")
                subprocess.run([sys.executable, "demo_e2e_functionality.py"])
                break
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo cancelled. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    main()