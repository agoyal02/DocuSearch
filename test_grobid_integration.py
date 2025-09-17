#!/usr/bin/env python3
"""
Test script for GROBID integration
"""

import os
import sys
import json
from document_parser import DocumentParser

def test_grobid_availability():
    """Test if GROBID service is available"""
    print("Testing GROBID availability...")
    parser = DocumentParser()
    
    if parser.is_grobid_available():
        print("✅ GROBID service is available")
        return True
    else:
        print("❌ GROBID service is not available")
        print("   Start GROBID with: ./start_grobid.sh")
        return False

def test_document_parsing():
    """Test document parsing with GROBID"""
    print("\nTesting document parsing...")
    parser = DocumentParser()
    
    # Test with existing PDF files
    test_files = []
    for filename in os.listdir('uploads'):
        if filename.endswith('.pdf'):
            test_files.append(os.path.join('uploads', filename))
            break  # Test with just one file
    
    if not test_files:
        print("❌ No PDF files found in uploads directory")
        return False
    
    test_file = test_files[0]
    print(f"Testing with file: {test_file}")
    
    try:
        # Validate file
        is_valid, skip_reason, error_msg = parser.validate_file(test_file)
        if not is_valid:
            print(f"❌ File validation failed: {error_msg}")
            return False
        
        print("✅ File validation passed")
        
        # Parse document
        metadata_options = ['title', 'author', 'abstract', 'topic']
        result = parser.parse_document(test_file, metadata_options)
        
        print("✅ Document parsing completed")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Author: {result.get('author', 'N/A')}")
        print(f"   Parser: {result.get('parser', 'N/A')}")
        print(f"   Text length: {len(result.get('text', ''))}")
        
        if result.get('parser') == 'GROBID':
            print("✅ GROBID parsing was used")
            if result.get('abstract'):
                print(f"   Abstract: {result['abstract'][:100]}...")
            if result.get('references'):
                print(f"   References found: {len(result['references'])}")
        else:
            print("⚠️  Fallback parsing was used")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during parsing: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    try:
        import requests
        
        # Test GROBID status endpoint
        response = requests.get('http://localhost:5000/grobid_status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GROBID status endpoint: {data['message']}")
        else:
            print(f"❌ GROBID status endpoint failed: {response.status_code}")
        
        # Test documents endpoint
        response = requests.get('http://localhost:5000/documents', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documents endpoint: {len(data.get('documents', []))} documents found")
        else:
            print(f"❌ Documents endpoint failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("GROBID Integration Test Suite")
    print("=" * 40)
    
    # Test GROBID availability
    grobid_available = test_grobid_availability()
    
    # Test document parsing
    parsing_success = test_document_parsing()
    
    # Test API endpoints (only if app is running)
    api_success = test_api_endpoints()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"GROBID Available: {'✅' if grobid_available else '❌'}")
    print(f"Document Parsing: {'✅' if parsing_success else '❌'}")
    print(f"API Endpoints: {'✅' if api_success else '❌'}")
    
    if grobid_available and parsing_success:
        print("\n🎉 GROBID integration is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == '__main__':
    main()
