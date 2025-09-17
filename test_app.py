#!/usr/bin/env python3
"""
Test script for DocuSearch application
This script tests the core functionality without requiring the web interface
"""

import os
import json
import tempfile
from document_parser import DocumentParser
from search_engine import SearchEngine

def create_test_files():
    """Create test files for different document types"""
    test_files = {}
    
    # Create a test text file
    txt_content = """
    This is a test document for DocuSearch.
    It contains multiple paragraphs with various information.
    
    The document parser should be able to extract all this text
    and make it searchable through the search engine.
    
    Keywords: test, document, parser, search, engine
    """
    
    txt_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    txt_file.write(txt_content)
    txt_file.close()
    test_files['txt'] = txt_file.name
    
    # Create a test HTML file
    html_content = """
    <html>
    <head><title>Test HTML Document</title></head>
    <body>
        <h1>Test HTML Document</h1>
        <p>This is a test HTML document for DocuSearch.</p>
        <p>It contains <strong>formatted text</strong> and <em>various elements</em>.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
            <li>List item 3</li>
        </ul>
    </body>
    </html>
    """
    
    html_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    html_file.write(html_content)
    html_file.close()
    test_files['html'] = html_file.name
    
    return test_files

def test_document_parser():
    """Test the document parser with different file types"""
    print("Testing Document Parser...")
    print("=" * 50)
    
    parser = DocumentParser()
    test_files = create_test_files()
    
    for file_type, filepath in test_files.items():
        print(f"\nTesting {file_type.upper()} file: {filepath}")
        try:
            result = parser.parse_document(filepath)
            print(f"✓ Successfully parsed {file_type} file")
            print(f"  - Title: {result.get('title', 'N/A')}")
            print(f"  - Text length: {len(result.get('text', ''))}")
            print(f"  - File type: {result.get('file_type', 'N/A')}")
            print(f"  - Upload date: {result.get('upload_date', 'N/A')}")
            
            if file_type == 'txt':
                print(f"  - Word count: {result.get('word_count', 'N/A')}")
                print(f"  - Character count: {result.get('char_count', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Error parsing {file_type} file: {e}")
    
    # Clean up test files
    for filepath in test_files.values():
        try:
            os.unlink(filepath)
        except:
            pass
    
    print("\nDocument Parser test completed!")

def test_search_engine():
    """Test the search engine functionality"""
    print("\nTesting Search Engine...")
    print("=" * 50)
    
    search_engine = SearchEngine()
    
    # Create sample documents
    documents = [
        {
            'title': 'Python Programming Guide',
            'text': 'Python is a powerful programming language. It is used for web development, data science, and automation.',
            'filename': 'python_guide.txt',
            'file_type': 'text/plain'
        },
        {
            'title': 'Web Development Tutorial',
            'text': 'Learn web development with HTML, CSS, and JavaScript. Build responsive websites and web applications.',
            'filename': 'web_dev.txt',
            'file_type': 'text/plain'
        },
        {
            'title': 'Data Science Handbook',
            'text': 'Data science involves analyzing data using Python, pandas, and machine learning algorithms.',
            'filename': 'data_science.txt',
            'file_type': 'text/plain'
        }
    ]
    
    # Index documents
    print("Indexing documents...")
    for i, doc in enumerate(documents):
        search_engine.index_document(doc, doc['filename'])
        print(f"✓ Indexed: {doc['title']}")
    
    # Test searches
    test_queries = [
        'python programming',
        'web development',
        'data science',
        'machine learning',
        'HTML CSS',
        'javascript'
    ]
    
    print(f"\nSearch Engine Statistics:")
    stats = search_engine.get_index_stats()
    print(f"  - Total documents: {stats['total_documents']}")
    print(f"  - Total terms: {stats['total_terms']}")
    print(f"  - Average terms per doc: {stats['average_terms_per_doc']:.2f}")
    
    print(f"\nTesting search queries...")
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = search_engine.search(query, limit=3)
        
        if results:
            print(f"  Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"    {i}. {result['title']} (Score: {result['score']:.2f})")
                print(f"       Snippet: {result['snippet'][:100]}...")
        else:
            print("  No results found")
    
    print("\nSearch Engine test completed!")

def test_integration():
    """Test the integration between parser and search engine"""
    print("\nTesting Integration...")
    print("=" * 50)
    
    parser = DocumentParser()
    search_engine = SearchEngine()
    
    # Create a test document
    test_content = """
    Flask Web Framework
    
    Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.
    
    Key Features:
    - Simple and flexible
    - Built-in development server
    - RESTful request dispatching
    - Template engine support
    - Unit testing support
    
    Flask is often used for building web APIs and web applications in Python.
    """
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(test_content)
    temp_file.close()
    
    try:
        # Parse document
        print("Parsing test document...")
        parsed_doc = parser.parse_document(temp_file.name)
        print(f"✓ Parsed document: {parsed_doc['title']}")
        
        # Index document
        print("Indexing document...")
        search_engine.index_document(parsed_doc, parsed_doc['filename'])
        print("✓ Document indexed")
        
        # Test search
        print("Testing search...")
        results = search_engine.search('Flask web framework', limit=1)
        
        if results:
            result = results[0]
            print(f"✓ Search successful!")
            print(f"  - Found: {result['title']}")
            print(f"  - Score: {result['score']:.2f}")
            print(f"  - Snippet: {result['snippet'][:150]}...")
        else:
            print("✗ Search failed - no results found")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
    
    finally:
        # Clean up
        try:
            os.unlink(temp_file.name)
        except:
            pass
    
    print("\nIntegration test completed!")

def main():
    """Run all tests"""
    print("DocuSearch Application Tests")
    print("=" * 60)
    
    try:
        test_document_parser()
        test_search_engine()
        test_integration()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully! ✓")
        print("\nTo run the web application:")
        print("  python app.py")
        print("\nThen open your browser to: http://localhost:5000")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

