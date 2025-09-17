#!/usr/bin/env python3
"""
Test script for collapsible job interface
"""

import tempfile
import os
import requests
import json

def create_test_documents_for_jobs():
    """Create test documents for multiple jobs"""
    jobs_data = []
    
    # Job 1: Normal documents
    job1_docs = [
        "Title: Document 1\nAuthor: Author A\nTopic: Topic A\nThis is document 1.",
        "Title: Document 2\nAuthor: Author B\nTopic: Topic B\nThis is document 2."
    ]
    
    # Job 2: Mixed results
    job2_docs = [
        "Title: Document 3\nAuthor: Author C\nTopic: Topic C\nThis is document 3.",
        "Title: Large Document\n" + "Content " * 10000  # Large file
    ]
    
    # Job 3: Single document
    job3_docs = [
        "Title: Document 4\nAuthor: Author D\nTopic: Topic D\nThis is document 4."
    ]
    
    all_docs = job1_docs + job2_docs + job3_docs
    
    # Create temporary files
    test_files = []
    for i, content in enumerate(all_docs):
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_job_test_{i}.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        test_files.append(temp_file.name)
    
    return test_files

def test_collapsible_jobs():
    """Test the collapsible job interface"""
    print("Testing Collapsible Job Interface...")
    print("=" * 50)
    
    # Create test documents
    test_files = create_test_documents_for_jobs()
    
    try:
        # Test multiple job uploads
        job_ids = []
        
        # Upload first batch (2 documents)
        print("Uploading first batch (2 documents)...")
        files1 = []
        for file_path in test_files[:2]:
            files1.append(('files', (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')))
        
        data1 = {'metadata_options': json.dumps(['title', 'author', 'topic'])}
        response1 = requests.post('http://localhost:5000/bulk_upload', files=files1, data=data1)
        
        if response1.status_code == 200:
            result1 = response1.json()
            job_ids.append(result1['job_id'])
            print(f"✓ Job 1 created: {result1['job_id']}")
        else:
            print(f"✗ Job 1 failed: {response1.status_code}")
        
        # Upload second batch (2 documents - one will be skipped due to size)
        print("Uploading second batch (2 documents)...")
        files2 = []
        for file_path in test_files[2:4]:
            files2.append(('files', (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')))
        
        data2 = {'metadata_options': json.dumps(['title', 'author', 'topic'])}
        response2 = requests.post('http://localhost:5000/bulk_upload', files=files2, data=data2)
        
        if response2.status_code == 200:
            result2 = response2.json()
            job_ids.append(result2['job_id'])
            print(f"✓ Job 2 created: {result2['job_id']}")
        else:
            print(f"✗ Job 2 failed: {response2.status_code}")
        
        # Upload third batch (1 document)
        print("Uploading third batch (1 document)...")
        files3 = []
        files3.append(('files', (os.path.basename(test_files[4]), open(test_files[4], 'rb'), 'text/plain')))
        
        data3 = {'metadata_options': json.dumps(['title', 'author', 'topic'])}
        response3 = requests.post('http://localhost:5000/bulk_upload', files=files3, data=data3)
        
        if response3.status_code == 200:
            result3 = response3.json()
            job_ids.append(result3['job_id'])
            print(f"✓ Job 3 created: {result3['job_id']}")
        else:
            print(f"✗ Job 3 failed: {response3.status_code}")
        
        # Test documents endpoint
        print("\nTesting documents endpoint...")
        docs_response = requests.get('http://localhost:5000/documents')
        
        if docs_response.status_code == 200:
            result = docs_response.json()
            print("✓ Documents endpoint working!")
            print(f"  - Total jobs: {len(result['jobs'])}")
            print(f"  - Total documents: {len(result['documents'])}")
            
            # Show job details
            for job in result['jobs']:
                print(f"\nJob {job['job_id']}:")
                print(f"  - Status: {job['status']}")
                print(f"  - Total documents: {job['total_documents']}")
                print(f"  - Successful: {job['successful_documents']}")
                print(f"  - Skipped: {job.get('skipped_documents', 0)}")
                print(f"  - Failed: {job.get('failed_documents', 0)}")
                print(f"  - Processing time: {job.get('processing_time', 0):.2f}s")
                
                if job.get('skipped_reasons'):
                    print("  - Skip reasons:")
                    for reason, count in job['skipped_reasons'].items():
                        if count > 0:
                            print(f"    • {reason}: {count}")
                
                if job.get('documents'):
                    print(f"  - Documents in job:")
                    for doc in job['documents']:
                        print(f"    • {doc['title']} ({doc['file_type']})")
        else:
            print(f"✗ Documents endpoint failed: {docs_response.status_code}")
        
        # Test individual job status
        print("\nTesting individual job status...")
        for job_id in job_ids:
            status_response = requests.get(f'http://localhost:5000/job_status/{job_id}')
            if status_response.status_code == 200:
                job_status = status_response.json()
                print(f"✓ Job {job_id}: {job_status['status']} - {job_status['successful_files']}/{job_status['total_files']} files")
            else:
                print(f"✗ Job {job_id} status failed: {status_response.status_code}")
        
    except Exception as e:
        print(f"✗ Error testing collapsible jobs: {e}")
    
    finally:
        # Clean up test files
        for file_path in test_files:
            try:
                os.unlink(file_path)
            except:
                pass

if __name__ == '__main__':
    print("Collapsible Job Interface Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000')
        if response.status_code == 200:
            print("✓ Server is running")
            test_collapsible_jobs()
        else:
            print("✗ Server is not responding properly")
    except:
        print("✗ Server is not running. Please start the application with: python3 app.py")
    
    print("\n" + "=" * 60)
    print("Collapsible job interface tests completed!")

