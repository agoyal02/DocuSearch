#!/usr/bin/env python3
"""
Test script for file size and page limits
"""

import tempfile
import os
import requests
import json

def create_large_file(size_mb=60):
    """Create a large file to test size limits"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    
    # Write enough content to exceed the limit
    content = "This is a test line for file size limit testing. " * 1000
    target_size = size_mb * 1024 * 1024  # Convert MB to bytes
    
    while os.path.getsize(temp_file.name) < target_size:
        temp_file.write(content)
        temp_file.flush()
    
    temp_file.close()
    return temp_file.name

def test_file_limits():
    """Test file size and page limits"""
    print("Testing File Size and Page Limits...")
    print("=" * 50)
    
    # Create test files
    test_files = []
    
    # Normal file
    normal_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    normal_file.write("Title: Normal Document\nAuthor: Test Author\nThis is a normal document.")
    normal_file.close()
    test_files.append(normal_file.name)
    
    # Large file (exceeds 50MB limit)
    print("Creating large file to test size limit...")
    large_file = create_large_file(55)  # 55MB file (exceeds 50MB limit)
    test_files.append(large_file)
    
    # Unsupported format
    unsupported_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False)
    unsupported_file.write("This is an unsupported file format.")
    unsupported_file.close()
    test_files.append(unsupported_file.name)
    
    try:
        # Prepare files for upload
        files = []
        for file_path in test_files:
            files.append(('files', (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')))
        
        # Metadata options
        metadata_options = ['title', 'author']
        
        # Prepare form data
        data = {
            'metadata_options': json.dumps(metadata_options)
        }
        
        print("Uploading files to test limits...")
        
        # Make request to bulk upload endpoint
        response = requests.post('http://localhost:5000/bulk_upload', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Job completed!")
            print(f"  - Job ID: {result['job_id']}")
            print(f"  - Success count: {result['results']['success_count']}")
            print(f"  - Error count: {result['results']['error_count']}")
            print(f"  - Skipped count: {result['results']['skipped_count']}")
            
            if result['results']['skipped_files']:
                print("\nSkipped files:")
                for file in result['results']['skipped_files']:
                    print(f"  • {file['filename']}: {file['reason']} - {file['message']}")
            
            if result['results']['failed_files']:
                print("\nFailed files:")
                for file in result['results']['failed_files']:
                    print(f"  • {file}")
            
            if result['results']['successful_files']:
                print("\nSuccessful files:")
                for file in result['results']['successful_files']:
                    print(f"  • {file['title']} ({file['filename']})")
            
            # Test job status for detailed breakdown
            print("\nDetailed job status:")
            status_response = requests.get(f"http://localhost:5000/job_status/{result['job_id']}")
            
            if status_response.status_code == 200:
                job_status = status_response.json()
                print(f"  - Total files: {job_status['total_files']}")
                print(f"  - Processed: {job_status['processed_files']}")
                print(f"  - Successful: {job_status['successful_files']}")
                print(f"  - Failed: {job_status['failed_files']}")
                print(f"  - Skipped: {job_status['skipped_files']}")
                
                if job_status['skipped_reasons']:
                    print("  - Skip reasons breakdown:")
                    for reason, count in job_status['skipped_reasons'].items():
                        print(f"    • {reason}: {count}")
                
                if job_status['corrupt_files'] > 0:
                    print(f"  - Corrupt files: {job_status['corrupt_files']}")
                
                print(f"  - Processing time: {job_status['processing_time']:.2f} seconds")
            
        else:
            print(f"✗ Job failed: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except Exception as e:
        print(f"✗ Error testing file limits: {e}")
    
    finally:
        # Clean up test files
        for file_path in test_files:
            try:
                os.unlink(file_path)
            except:
                pass

if __name__ == '__main__':
    print("File Limits Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000')
        if response.status_code == 200:
            print("✓ Server is running")
            test_file_limits()
        else:
            print("✗ Server is not responding properly")
    except:
        print("✗ Server is not running. Please start the application with: python3 app.py")
    
    print("\n" + "=" * 60)
    print("File limits tests completed!")
