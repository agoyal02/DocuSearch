#!/usr/bin/env python3
"""
Test script for LLM configuration visibility
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"

def test_llm_visibility():
    """Test LLM configuration visibility behavior"""
    print("🧪 Testing LLM Configuration Visibility...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            html_content = response.text
            
            # Check if LLM config is hidden by default
            if 'id="llmConfigGroup" style="display: none;"' in html_content:
                print("✅ LLM Configuration is hidden by default")
            else:
                print("❌ LLM Configuration is not hidden by default")
            
            # Check if JavaScript functions are present
            checks = [
                ("updateLLMConfigVisibility", "updateLLMConfigVisibility" in html_content),
                ("parser type event listeners", "input[name=\"parserType\"]" in html_content),
                ("LLM Extraction option", "LLM Extraction" in html_content),
                ("Auto option", "Auto (LLM + Fallback)" in html_content),
                ("Local Parser option", "Local Parser" in html_content)
            ]
            
            print("✅ JavaScript functionality check:")
            for name, found in checks:
                status = "✅" if found else "❌"
                print(f"   {status} {name}")
                
        else:
            print(f"❌ UI request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ UI test error: {e}")

def test_llm_status():
    """Test LLM status"""
    print("\n🧪 Testing LLM Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/llm_status")
        if response.status_code == 200:
            status = response.json()
            print("✅ LLM Status endpoint working")
            print(f"   Enabled: {status['enabled']}")
            print(f"   Available: {status['available']}")
        else:
            print(f"❌ LLM Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM Status endpoint error: {e}")

def main():
    """Run LLM visibility tests"""
    print("🚀 Starting LLM Configuration Visibility Testing...")
    print(f"   Testing against: {BASE_URL}")
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ Server not responding at {BASE_URL}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}: {e}")
        return
    
    print("✅ Server is running")
    
    # Run tests
    test_llm_visibility()
    test_llm_status()
    
    print("\n🎉 LLM Configuration Visibility Testing Completed!")
    print("\n📝 Expected Behavior:")
    print("   ✅ LLM Configuration hidden by default")
    print("   ✅ Shows when 'LLM Extraction' is selected")
    print("   ✅ Shows when 'Auto (LLM + Fallback)' is selected")
    print("   ✅ Hides when 'Local Parser' is selected")
    print("   ✅ JavaScript handles visibility changes dynamically")

if __name__ == "__main__":
    main()
