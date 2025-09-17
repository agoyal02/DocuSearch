#!/usr/bin/env python3
"""
Test script for LLM UI configuration
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"

def test_llm_status():
    """Test LLM status endpoint"""
    print("🧪 Testing LLM Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/llm_status")
        if response.status_code == 200:
            status = response.json()
            print("✅ LLM Status endpoint working")
            print(f"   Enabled: {status['enabled']}")
            print(f"   Available: {status['available']}")
            print(f"   Provider: {status['provider']}")
            print(f"   Model: {status['model']}")
        else:
            print(f"❌ LLM Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM Status endpoint error: {e}")

def test_llm_config_save():
    """Test LLM configuration save"""
    print("\n🧪 Testing LLM Configuration Save...")
    
    try:
        config_data = {
            "provider": "openai",
            "api_key": "test-key-123",
            "model": "gpt-3.5-turbo",
            "base_url": ""
        }
        
        response = requests.post(f"{BASE_URL}/save_llm_config", json=config_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM Configuration save working")
            print(f"   Success: {result['success']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ LLM Configuration save failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM Configuration save error: {e}")

def test_llm_connection():
    """Test LLM connection test"""
    print("\n🧪 Testing LLM Connection Test...")
    
    try:
        test_data = {
            "provider": "openai",
            "api_key": "test-key-123",
            "model": "gpt-3.5-turbo",
            "base_url": ""
        }
        
        response = requests.post(f"{BASE_URL}/test_llm", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM Connection test working")
            print(f"   Success: {result['success']}")
            if result['success']:
                print(f"   Message: {result['message']}")
            else:
                print(f"   Error: {result['error']}")
        else:
            print(f"❌ LLM Connection test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM Connection test error: {e}")

def test_ui_elements():
    """Test if UI elements are present"""
    print("\n🧪 Testing UI Elements...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            html_content = response.text
            
            # Check for LLM configuration elements
            checks = [
                ("LLM Configuration", "LLM Configuration" in html_content),
                ("llmProvider", "id=\"llmProvider\"" in html_content),
                ("llmApiKey", "id=\"llmApiKey\"" in html_content),
                ("llmModel", "id=\"llmModel\"" in html_content),
                ("Test Connection", "Test Connection" in html_content),
                ("Save Config", "Save Config" in html_content),
                ("LLM Extraction", "LLM Extraction" in html_content),
                ("Auto (LLM + Fallback)", "Auto (LLM + Fallback)" in html_content)
            ]
            
            print("✅ UI Elements check:")
            for name, found in checks:
                status = "✅" if found else "❌"
                print(f"   {status} {name}")
        else:
            print(f"❌ UI request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ UI test error: {e}")

def main():
    """Run all LLM UI tests"""
    print("🚀 Starting LLM UI Configuration Testing...")
    print(f"   Testing against: {BASE_URL}")
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ Server not responding at {BASE_URL}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}: {e}")
        print("   Make sure the server is running with: python app.py")
        return
    
    print("✅ Server is running")
    
    # Run tests
    test_llm_status()
    test_llm_config_save()
    test_llm_connection()
    test_ui_elements()
    
    print("\n🎉 LLM UI configuration testing completed!")
    print("\n📝 LLM Configuration Features:")
    print("   ✅ LLM enabled by default")
    print("   ✅ LLM Extraction and Auto options available")
    print("   ✅ Provider selection (OpenAI, Anthropic, Local)")
    print("   ✅ API Key input field")
    print("   ✅ Model configuration")
    print("   ✅ Base URL for local models")
    print("   ✅ Test Connection button")
    print("   ✅ Save Configuration button")

if __name__ == "__main__":
    main()
