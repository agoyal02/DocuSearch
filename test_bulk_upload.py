#!/usr/bin/env python3
"""
Test script for bulk upload functionality
"""

import tempfile
import os
import requests
import json

def create_test_documents():
    """Create multiple test documents for bulk upload testing"""
    documents = []
    
    # Document 1: PDF-like content
    doc1_content = """
    Title: Advanced Document Processing
    Author: Dr. Jane Smith
    Published: 2025-09-16
    Topic: Document Management
    
    Abstract: This document describes advanced techniques for document processing and metadata extraction.
    
    This is a comprehensive guide to document processing systems that can handle multiple file formats and extract meaningful metadata from various document types.
    """
    
    # Document 2: Technical content
    doc2_content = """
    Title: Machine Learning for Text Analysis
    Author: Prof. John Doe
    Published: 2025-09-15
    Topic: Artificial Intelligence
    
    Abstract: This paper presents novel approaches to text analysis using machine learning techniques.
    
    The research focuses on natural language processing and automated text understanding for document classification and metadata extraction.
    """
    
    # Document 3: Business content
    doc3_content = """
    Title: Digital Transformation in Business
    Author: Sarah Johnson
    Published: 2025-09-14
    Topic: Business Strategy
    
    Abstract: This report examines the impact of digital transformation on modern business practices.
    
    Digital transformation has revolutionized how organizations handle documents, process information, and manage knowledge assets.
    """
    
    # Create temporary files
    for i, content in enumerate([doc1_content, doc2_content, doc3_content], 1):
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_doc{i}.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        documents.append(temp_file.name)
    
    return documents

def test_bulk_upload_api():
    """Test the bulk upload API endpoint"""
    print("Testing Bulk Upload API...")
    print("=" * 50)
    
    # Create test documents
    test_files = create_test_documents()
    
    try:
        # Prepare files for upload
        files = []
        for file_path in test_files:
            files.append(('files', (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')))
        
        # Metadata options
        metadata_options = ['author', 'published_date', 'abstract', 'summary', 'title', 'topic']
        
        # Prepare form data
        data = {
            'metadata_options': json.dumps(metadata_options)
        }
        
        # Make request to bulk upload endpoint
        response = requests.post('http://localhost:5000/bulk_upload', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Bulk upload successful!")
            print(f"  - Success count: {result['results']['success_count']}")
            print(f"  - Error count: {result['results']['error_count']}")
            
            if result['results']['successful_files']:
                print("\nSuccessfully processed files:")
                for file_info in result['results']['successful_files']:
                    print(f"  • {file_info['title']} ({file_info['filename']})")
                    print(f"    Metadata: {file_info['extracted_metadata']}")
            
            if result['results']['errors']:
                print("\nErrors:")
                for error in result['results']['errors']:
                    print(f"  • {error}")
        else:
            print(f"✗ Bulk upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except Exception as e:
        print(f"✗ Error testing bulk upload: {e}")
    
    finally:
        # Clean up test files
        for file_path in test_files:
            try:
                os.unlink(file_path)
            except:
                pass

def test_single_vs_bulk():
    """Test both single and bulk upload modes"""
    print("\nTesting Single vs Bulk Upload Modes...")
    print("=" * 50)
    
    # Test single file upload
    print("Testing single file upload...")
    test_content = "Title: Single Document Test\nAuthor: Test Author\nThis is a test document for single upload."
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(test_content)
    temp_file.close()
    
    try:
        with open(temp_file.name, 'rb') as f:
            files = [('file', (os.path.basename(temp_file.name), f, 'text/plain'))]
            data = {'metadata_options': json.dumps(['title', 'author'])}
            
            response = requests.post('http://localhost:5000/upload', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Single upload successful!")
                print(f"  - Title: {result['parsed_content'].get('title', 'Not found')}")
                print(f"  - Author: {result['parsed_content'].get('author', 'Not found')}")
            else:
                print(f"✗ Single upload failed: {response.status_code}")
    
    except Exception as e:
        print(f"✗ Error testing single upload: {e}")
    
    finally:
        try:
            os.unlink(temp_file.name)
        except:
            pass

if __name__ == '__main__':
    print("Bulk Upload Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000')
        if response.status_code == 200:
            print("✓ Server is running")
            test_bulk_upload_api()
            test_single_vs_bulk()
        else:
            print("✗ Server is not responding properly")
    except:
        print("✗ Server is not running. Please start the application with: python3 app.py")
    
    print("\n" + "=" * 60)
    print("Bulk upload tests completed!")

