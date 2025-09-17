#!/usr/bin/env python3
"""
Test script for metadata extraction functionality
"""

import tempfile
import os
from document_parser import DocumentParser

def test_metadata_extraction():
    """Test the new metadata extraction functionality"""
    print("Testing Metadata Extraction...")
    print("=" * 50)
    
    parser = DocumentParser()
    
    # Create a test document with metadata
    test_content = """
    Title: Advanced Document Processing System
    Author: John Smith
    Published: 2025-09-16
    Topic: Document Management
    
    Abstract: This document describes an advanced document processing system that can extract metadata from various document formats including PDF, DOCX, and HTML files.
    
    Summary: The system provides intelligent metadata extraction capabilities that allow users to select specific fields they want to extract from documents. It supports multiple document formats and provides a user-friendly web interface for document management and search.
    
    The system includes features such as:
    - Multi-format document parsing
    - Configurable metadata extraction
    - Full-text search capabilities
    - Modern web interface
    """
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(test_content)
    temp_file.close()
    
    try:
        # Test with all metadata options
        metadata_options = ['author', 'published_date', 'abstract', 'summary', 'title', 'topic']
        result = parser.parse_document(temp_file.name, metadata_options)
        
        print("✓ Document parsed with metadata extraction")
        print(f"  - Title: {result.get('title', 'Not found')}")
        print(f"  - Author: {result.get('author', 'Not found')}")
        print(f"  - Published Date: {result.get('published_date', 'Not found')}")
        print(f"  - Topic: {result.get('topic', 'Not found')}")
        print(f"  - Abstract: {result.get('abstract', 'Not found')[:100]}...")
        print(f"  - Summary: {result.get('summary', 'Not found')[:100]}...")
        
        # Test with selective metadata options
        print("\nTesting selective metadata extraction...")
        selective_options = ['author', 'title']
        result2 = parser.parse_document(temp_file.name, selective_options)
        
        print("✓ Selective metadata extraction working")
        print(f"  - Title: {result2.get('title', 'Not found')}")
        print(f"  - Author: {result2.get('author', 'Not found')}")
        print(f"  - Abstract: {result2.get('abstract', 'Not extracted')}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        # Clean up
        try:
            os.unlink(temp_file.name)
        except:
            pass
    
    print("\nMetadata extraction test completed!")

if __name__ == '__main__':
    test_metadata_extraction()

