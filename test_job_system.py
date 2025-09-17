#!/usr/bin/env python3
"""
Test script for job status system
"""

import tempfile
import os
import requests
import json
import time

def create_test_documents_with_limits():
    """Create test documents with various characteristics to test limits"""
    documents = []
    
    # Document 1: Normal document
    doc1_content = """
    Title: Normal Document
    Author: Test Author
    Published: 2025-09-16
    Topic: Testing
    
    This is a normal document that should process successfully.
    """
    
    # Document 2: Large document (simulate by creating a large file)
    doc2_content = "Large Document\n" * 10000  # Create a large file
    
    # Document 3: Document with unsupported format
    doc3_content = "This is a .xyz file which should be skipped"
    
    # Create temporary files
    files_to_create = [
        (doc1_content, '_normal.txt'),
        (doc2_content, '_large.txt'),
        (doc3_content, '_unsupported.xyz')
    ]
    
    for content, suffix in files_to_create:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        documents.append(temp_file.name)
    
    return documents

def test_job_system():
    """Test the job status system"""
    print("Testing Job Status System...")
    print("=" * 50)
    
    # Create test documents
    test_files = create_test_documents_with_limits()
    
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
        
        print("Uploading files for job processing...")
        
        # Make request to bulk upload endpoint
        response = requests.post('http://localhost:5000/bulk_upload', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Job created successfully!")
            print(f"  - Job ID: {result['job_id']}")
            print(f"  - Success count: {result['results']['success_count']}")
            print(f"  - Error count: {result['results']['error_count']}")
            print(f"  - Skipped count: {result['results']['skipped_count']}")
            
            # Test job status endpoint
            print("\nTesting job status endpoint...")
            status_response = requests.get(f"http://localhost:5000/job_status/{result['job_id']}")
            
            if status_response.status_code == 200:
                job_status = status_response.json()
                print("✓ Job status retrieved successfully!")
                print(f"  - Status: {job_status['status']}")
                print(f"  - Progress: {job_status['progress_percentage']}%")
                print(f"  - Total files: {job_status['total_files']}")
                print(f"  - Processed: {job_status['processed_files']}")
                print(f"  - Successful: {job_status['successful_files']}")
                print(f"  - Failed: {job_status['failed_files']}")
                print(f"  - Skipped: {job_status['skipped_files']}")
                
                if job_status['skipped_reasons']:
                    print("  - Skip reasons:")
                    for reason, count in job_status['skipped_reasons'].items():
                        print(f"    • {reason}: {count}")
                
                if job_status['corrupt_files'] > 0:
                    print(f"  - Corrupt files: {job_status['corrupt_files']}")
                
                if job_status['processing_time'] > 0:
                    print(f"  - Processing time: {job_status['processing_time']:.2f} seconds")
            else:
                print(f"✗ Failed to get job status: {status_response.status_code}")
            
            # Test job results download
            print("\nTesting job results download...")
            results_response = requests.get(f"http://localhost:5000/job_results/{result['job_id']}")
            
            if results_response.status_code == 200:
                print("✓ Job results downloaded successfully!")
                print(f"  - Content type: {results_response.headers.get('content-type', 'Unknown')}")
                print(f"  - Content length: {len(results_response.content)} bytes")
                
                # Parse JSONL content
                jsonl_lines = results_response.text.strip().split('\n')
                print(f"  - JSONL lines: {len(jsonl_lines)}")
                
                # Show first line (job summary)
                if jsonl_lines:
                    summary = json.loads(jsonl_lines[0])
                    print(f"  - Job summary: {summary['status']} - {summary['successful_files']} successful, {summary['failed_files']} failed, {summary['skipped_files']} skipped")
            else:
                print(f"✗ Failed to download job results: {results_response.status_code}")
            
            # Test jobs list endpoint
            print("\nTesting jobs list endpoint...")
            jobs_response = requests.get("http://localhost:5000/jobs")
            
            if jobs_response.status_code == 200:
                jobs = jobs_response.json()
                print("✓ Jobs list retrieved successfully!")
                print(f"  - Total jobs: {len(jobs['jobs'])}")
                
                for job in jobs['jobs']:
                    print(f"    • Job {job['job_id']}: {job['status']} - {job['successful_files']}/{job['total_files']} files")
            else:
                print(f"✗ Failed to get jobs list: {jobs_response.status_code}")
                
        else:
            print(f"✗ Job creation failed: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except Exception as e:
        print(f"✗ Error testing job system: {e}")
    
    finally:
        # Clean up test files
        for file_path in test_files:
            try:
                os.unlink(file_path)
            except:
                pass

if __name__ == '__main__':
    print("Job Status System Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000')
        if response.status_code == 200:
            print("✓ Server is running")
            test_job_system()
        else:
            print("✗ Server is not responding properly")
    except:
        print("✗ Server is not running. Please start the application with: python3 app.py")
    
    print("\n" + "=" * 60)
    print("Job status system tests completed!")

