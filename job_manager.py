import uuid
import json
import os
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

class JobStatus(Enum):
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

class JobManager:
    def __init__(self):
        self.jobs = {}  # job_id -> job_info
        self.job_results_dir = "job_results"
        self.jobs_metadata_dir = "job_metadata"
        os.makedirs(self.job_results_dir, exist_ok=True)
        os.makedirs(self.jobs_metadata_dir, exist_ok=True)
        
        # Load existing jobs from metadata files
        self._load_existing_jobs()
    
    def create_job(self, total_files: int, metadata_options: List[str], data_source: str = 'Local') -> str:
        """Create a new job and return job ID"""
        job_id = str(uuid.uuid4())[:8]  # Short job ID
        
        job_info = {
            'job_id': job_id,
            'status': JobStatus.PROCESSING.value,
            'total_files': total_files,
            'processed_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'skipped_reasons': {
                'unknown_format': 0,
                'file_size_limit': 0,
                'page_limit': 0
            },
            'corrupt_files': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'current_file': None,
            'progress_percentage': 0,
            'metadata_options': metadata_options,
            'data_source': data_source,
            'results': []
        }
        
        self.jobs[job_id] = job_info
        self._save_job_metadata(job_id)
        return job_id
    
    def update_job_progress(self, job_id: str, current_file: str, processed: int, successful: int, failed: int):
        """Update job progress"""
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        job['processed_files'] = processed
        job['successful_files'] = successful
        job['failed_files'] = failed
        job['current_file'] = current_file
        job['progress_percentage'] = int((processed / job['total_files']) * 100) if job['total_files'] > 0 else 0
        
        # Save updated job metadata
        self._save_job_metadata(job_id)
    
    def add_file_result(self, job_id: str, filename: str, success: bool, metadata: Dict = None, error: str = None, skip_reason: str = None):
        """Add a file processing result to the job"""
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        
        result = {
            'filename': filename,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'error': error,
            'skip_reason': skip_reason
        }
        
        job['results'].append(result)
        
        if success:
            job['successful_files'] += 1
        elif skip_reason:
            job['skipped_files'] += 1
            if skip_reason in job['skipped_reasons']:
                job['skipped_reasons'][skip_reason] += 1
        else:
            job['failed_files'] += 1
            if error and ('corrupt' in error.lower() or 'not readable' in error.lower() or 'not parsable' in error.lower()):
                job['corrupt_files'] += 1
        
        # Save updated job metadata
        self._save_job_metadata(job_id)
    
    def complete_job(self, job_id: str, success: bool = True):
        """Mark job as completed or failed"""
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        job['status'] = JobStatus.COMPLETED.value if success else JobStatus.FAILED.value
        job['end_time'] = datetime.now().isoformat()
        job['progress_percentage'] = 100
        
        # Save job results to JSONL file
        self._save_job_results(job_id)
        
        # Save final job metadata
        self._save_job_metadata(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get current job status"""
        job = self.jobs.get(job_id)
        if job:
            # Add processing time to the response
            job['processing_time'] = self._calculate_processing_time(job)
        return job
    
    def get_job_results(self, job_id: str) -> Optional[Dict]:
        """Get job results including individual file results"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        # Try to load results from JSONL file if not in memory
        if not job.get('results') or len(job['results']) == 0:
            self._load_job_results_from_file(job_id)
        
        return job
    
    def _save_job_results(self, job_id: str):
        """Save job results to JSONL file"""
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        jsonl_filename = f"job_{job_id}_results.jsonl"
        jsonl_path = os.path.join(self.job_results_dir, jsonl_filename)
        
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            # Write job summary first
            summary = {
                'job_id': job['job_id'],
                'status': job['status'],
                'total_files': job['total_files'],
                'successful_files': job['successful_files'],
                'failed_files': job['failed_files'],
                'skipped_files': job['skipped_files'],
                'skipped_reasons': job['skipped_reasons'],
                'corrupt_files': job['corrupt_files'],
                'start_time': job['start_time'],
                'end_time': job['end_time'],
                'processing_time_seconds': self._calculate_processing_time(job),
                'metadata_options': job['metadata_options']
            }
            f.write(json.dumps(summary, ensure_ascii=False) + '\n')
            
            # Write individual file results
            for result in job['results']:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    def _calculate_processing_time(self, job: Dict) -> float:
        """Calculate total processing time in seconds"""
        if not job['start_time'] or not job['end_time']:
            return 0
        
        start = datetime.fromisoformat(job['start_time'])
        end = datetime.fromisoformat(job['end_time'])
        return (end - start).total_seconds()
    
    def get_job_summary(self, job_id: str) -> Optional[Dict]:
        """Get job summary for display"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        
        return {
            'job_id': job.get('job_id', job_id),
            'status': job.get('status', 'Unknown'),
            'progress_percentage': job.get('progress_percentage', 0),
            'current_file': job.get('current_file'),
            'total_files': job.get('total_files', 0),
            'processed_files': job.get('processed_files', 0),
            'successful_files': job.get('successful_files', 0),
            'failed_files': job.get('failed_files', 0),
            'skipped_files': job.get('skipped_files', 0),
            'skipped_reasons': job.get('skipped_reasons', {}),
            'corrupt_files': job.get('corrupt_files', 0),
            'processing_time': self._calculate_processing_time(job),
            'start_time': job.get('start_time'),
            'end_time': job.get('end_time'),
            'data_source': job.get('data_source', 'Local')
        }
    
    def list_jobs(self) -> List[Dict]:
        """List all jobs with basic info"""
        return [self.get_job_summary(job_id) for job_id in self.jobs.keys()]
    
    def _load_existing_jobs(self):
        """Load existing jobs from metadata files and job results files"""
        # Load from metadata files first
        if os.path.exists(self.jobs_metadata_dir):
            for filename in os.listdir(self.jobs_metadata_dir):
                if filename.endswith('.json'):
                    job_id = filename.replace('.json', '')
                    metadata_path = os.path.join(self.jobs_metadata_dir, filename)
                    
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            job_data = json.load(f)
                            self.jobs[job_id] = job_data
                    except Exception as e:
                        print(f"Error loading job metadata for {job_id}: {str(e)}")
        
        # Load from job results files for jobs not already loaded
        if os.path.exists(self.job_results_dir):
            for filename in os.listdir(self.job_results_dir):
                if filename.startswith('job_') and filename.endswith('_results.jsonl'):
                    job_id = filename.replace('job_', '').replace('_results.jsonl', '')
                    
                    # Skip if already loaded from metadata
                    if job_id in self.jobs:
                        continue
                    
                    try:
                        self._load_job_results_from_file(job_id)
                    except Exception as e:
                        print(f"Error loading job results for {job_id}: {str(e)}")
    
    def _save_job_metadata(self, job_id: str):
        """Save job metadata to JSON file"""
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        metadata_path = os.path.join(self.jobs_metadata_dir, f"{job_id}.json")
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(job, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving job metadata for {job_id}: {str(e)}")
    
    def _load_job_results_from_file(self, job_id: str):
        """Load job results from JSONL file"""
        jsonl_filename = f"job_{job_id}_results.jsonl"
        jsonl_path = os.path.join(self.job_results_dir, jsonl_filename)
        
        if not os.path.exists(jsonl_path):
            return
        
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    # First line is the summary
                    summary = json.loads(lines[0])
                    
                    # Create job entry if it doesn't exist
                    if job_id not in self.jobs:
                        self.jobs[job_id] = {}
                    
                    # Update job with summary data
                    self.jobs[job_id].update(summary)
                    
                    # Load individual file results
                    results = []
                    for line in lines[1:]:
                        if line.strip():
                            result = json.loads(line)
                            results.append(result)
                    
                    self.jobs[job_id]['results'] = results
        except Exception as e:
            print(f"Error loading job results for {job_id}: {str(e)}")

# Global job manager instance
job_manager = JobManager()
