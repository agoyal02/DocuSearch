#!/usr/bin/env python3
"""
Test script for metrics functionality
"""

import requests
import json
import time
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_FILES_DIR = "test_debug"

def test_metrics_endpoints():
    """Test the metrics endpoints"""
    print("🧪 Testing Metrics Endpoints...")
    
    # Test JSON metrics endpoint
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        if response.status_code == 200:
            metrics = response.json()
            print("✅ JSON Metrics endpoint working")
            print(f"   Total Jobs: {metrics['jobs']['total']}")
            print(f"   Successful Jobs: {metrics['jobs']['successful']}")
            print(f"   Failed Jobs: {metrics['jobs']['failed']}")
            print(f"   Documents Processed: {metrics['documents']['total_processed']}")
            print(f"   P50 Job Latency: {metrics['jobs']['p50_latency_seconds']:.2f}s")
            print(f"   P95 Job Latency: {metrics['jobs']['p95_latency_seconds']:.2f}s")
        else:
            print(f"❌ JSON Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ JSON Metrics endpoint error: {e}")
    
    # Test Prometheus metrics endpoint
    try:
        response = requests.get(f"{BASE_URL}/metrics/prometheus")
        if response.status_code == 200:
            print("✅ Prometheus Metrics endpoint working")
            print("   Sample metrics:")
            lines = response.text.split('\n')[:10]  # Show first 10 lines
            for line in lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Prometheus Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prometheus Metrics endpoint error: {e}")

def test_bulk_upload_with_metrics():
    """Test bulk upload and verify metrics are updated"""
    print("\n🧪 Testing Bulk Upload with Metrics...")
    
    # Check if test files exist
    if not os.path.exists(TEST_FILES_DIR):
        print(f"❌ Test directory {TEST_FILES_DIR} not found")
        return
    
    test_files = [f for f in os.listdir(TEST_FILES_DIR) if f.endswith('.pdf')]
    if not test_files:
        print(f"❌ No PDF files found in {TEST_FILES_DIR}")
        return
    
    print(f"   Found {len(test_files)} test files")
    
    # Get initial metrics
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        initial_metrics = response.json() if response.status_code == 200 else None
        if initial_metrics:
            initial_jobs = initial_metrics['jobs']['total']
            initial_docs = initial_metrics['documents']['total_processed']
            print(f"   Initial Jobs: {initial_jobs}, Documents: {initial_docs}")
    except:
        initial_metrics = None
    
    # Prepare files for upload
    files = []
    for test_file in test_files[:3]:  # Test with first 3 files
        file_path = os.path.join(TEST_FILES_DIR, test_file)
        files.append(('files', (test_file, open(file_path, 'rb'), 'application/pdf')))
    
    # Upload files
    try:
        print("   Uploading test files...")
        response = requests.post(f"{BASE_URL}/bulk_upload", files=files)
        
        # Close file handles
        for _, (_, file_handle, _) in files:
            file_handle.close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful: {result['message']}")
            print(f"   Job ID: {result['job_id']}")
            
            # Wait a moment for metrics to update
            time.sleep(2)
            
            # Check updated metrics
            response = requests.get(f"{BASE_URL}/metrics")
            if response.status_code == 200:
                updated_metrics = response.json()
                new_jobs = updated_metrics['jobs']['total']
                new_docs = updated_metrics['documents']['total_processed']
                print(f"   Updated Jobs: {new_jobs}, Documents: {new_docs}")
                
                if initial_metrics:
                    job_increase = new_jobs - initial_jobs
                    doc_increase = new_docs - initial_docs
                    print(f"   Jobs increased by: {job_increase}")
                    print(f"   Documents increased by: {doc_increase}")
            else:
                print("❌ Failed to get updated metrics")
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Upload error: {e}")
        # Close file handles in case of error
        for _, (_, file_handle, _) in files:
            try:
                file_handle.close()
            except:
                pass

def test_individual_upload_with_metrics():
    """Test individual file upload and verify metrics"""
    print("\n🧪 Testing Individual Upload with Metrics...")
    
    # Check if test files exist
    if not os.path.exists(TEST_FILES_DIR):
        print(f"❌ Test directory {TEST_FILES_DIR} not found")
        return
    
    test_files = [f for f in os.listdir(TEST_FILES_DIR) if f.endswith('.pdf')]
    if not test_files:
        print(f"❌ No PDF files found in {TEST_FILES_DIR}")
        return
    
    # Test with first file
    test_file = test_files[0]
    file_path = os.path.join(TEST_FILES_DIR, test_file)
    
    try:
        print(f"   Uploading {test_file}...")
        with open(file_path, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Individual upload successful: {result['message']}")
        else:
            print(f"❌ Individual upload failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Individual upload error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Metrics Testing...")
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
    test_metrics_endpoints()
    test_individual_upload_with_metrics()
    test_bulk_upload_with_metrics()
    
    print("\n🎉 Metrics testing completed!")

if __name__ == "__main__":
    main()
