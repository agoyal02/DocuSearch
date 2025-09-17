#!/usr/bin/env python3
"""
Test script for LLM integration
"""

import requests
import json
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_FILES_DIR = "test_debug"

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

def test_parser_selection():
    """Test parser selection in upload"""
    print("\n🧪 Testing Parser Selection...")
    
    # Check if test files exist
    if not os.path.exists(TEST_FILES_DIR):
        print(f"❌ Test directory {TEST_FILES_DIR} not found")
        return
    
    test_files = [f for f in os.listdir(TEST_FILES_DIR) if f.endswith('.pdf')]
    if not test_files:
        print(f"❌ No PDF files found in {TEST_FILES_DIR}")
        return
    
    # Test with local parser
    print("   Testing Local Parser...")
    test_file = test_files[0]
    file_path = os.path.join(TEST_FILES_DIR, test_file)
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            data = {
                'metadata_options': json.dumps(['title', 'author', 'topic']),
                'parser_type': 'local'
            }
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Local parser working: {result['message']}")
            print(f"   Parser used: {result['parsed_content'].get('parser', 'unknown')}")
        else:
            print(f"❌ Local parser failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Local parser error: {e}")
    
    # Test with LLM parser (should fallback to local)
    print("   Testing LLM Parser (should fallback to local)...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            data = {
                'metadata_options': json.dumps(['title', 'author', 'topic']),
                'parser_type': 'llm'
            }
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM parser (fallback) working: {result['message']}")
            print(f"   Parser used: {result['parsed_content'].get('parser', 'unknown')}")
        else:
            print(f"❌ LLM parser failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ LLM parser error: {e}")

def test_metrics_with_parser():
    """Test metrics with parser information"""
    print("\n🧪 Testing Metrics with Parser Info...")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Metrics endpoint working")
            print(f"   Total Documents: {metrics['documents']['total_processed']}")
            print(f"   LLM Processed: {metrics['documents'].get('llm_processed', 0)}")
            print(f"   Local Processed: {metrics['documents'].get('local_processed', 0)}")
        else:
            print(f"❌ Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics error: {e}")

def test_prometheus_metrics():
    """Test Prometheus metrics with new naming"""
    print("\n🧪 Testing Prometheus Metrics...")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/prometheus")
        if response.status_code == 200:
            metrics_text = response.text
            print("✅ Prometheus metrics working")
            
            # Check for new metric names
            if "docuparse_" in metrics_text:
                print("✅ New metric naming (docuparse_) found")
            else:
                print("❌ Old metric naming found")
                
            # Show sample metrics
            lines = metrics_text.split('\n')[:10]
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    print(f"   {line}")
        else:
            print(f"❌ Prometheus metrics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prometheus metrics error: {e}")

def main():
    """Run all LLM integration tests"""
    print("🚀 Starting LLM Integration Testing...")
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
    test_parser_selection()
    test_metrics_with_parser()
    test_prometheus_metrics()
    
    print("\n🎉 LLM integration testing completed!")
    print("\n📝 To enable LLM functionality:")
    print("   1. Set environment variables:")
    print("      export LLM_ENABLED=true")
    print("      export LLM_API_KEY=your_api_key")
    print("      export LLM_PROVIDER=openai  # or anthropic")
    print("   2. Restart the application")

if __name__ == "__main__":
    main()
