"""
Metrics collection system for DocuSearch application
Provides Prometheus-style metrics for observability
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
import statistics
import threading
from dataclasses import dataclass, asdict

@dataclass
class JobMetrics:
    """Metrics for a single job"""
    job_id: str
    start_time: float
    end_time: Optional[float] = None
    total_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    processing_time: float = 0.0
    status: str = "processing"

@dataclass
class DocumentMetrics:
    """Metrics for document processing"""
    total_processed: int = 0
    total_successful: int = 0
    total_failed: int = 0
    total_skipped: int = 0
    total_processing_time: float = 0.0
    llm_processed: int = 0
    llm_successful: int = 0
    llm_failed: int = 0
    local_processed: int = 0
    local_successful: int = 0
    local_failed: int = 0

class MetricsCollector:
    """Centralized metrics collection and storage"""
    
    def __init__(self, metrics_file: str = "metrics.json"):
        self.metrics_file = metrics_file
        self.lock = threading.Lock()
        
        # Job metrics
        self.jobs: Dict[str, JobMetrics] = {}
        self.completed_jobs: List[JobMetrics] = []
        
        # Document metrics
        self.document_metrics = DocumentMetrics()
        
        # Latency tracking (for p50/p95 calculations)
        self.job_latencies: deque = deque(maxlen=1000)  # Keep last 1000 job latencies
        self.document_latencies: deque = deque(maxlen=10000)  # Keep last 10k document latencies
        
        # Load existing metrics
        self._load_metrics()
    
    def start_job(self, job_id: str, total_files: int) -> None:
        """Record job start"""
        with self.lock:
            self.jobs[job_id] = JobMetrics(
                job_id=job_id,
                start_time=time.time(),
                total_files=total_files,
                status="processing"
            )
            self._save_metrics()
    
    def update_job_progress(self, job_id: str, successful: int, failed: int, skipped: int) -> None:
        """Update job progress metrics"""
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].successful_files = successful
                self.jobs[job_id].failed_files = failed
                self.jobs[job_id].skipped_files = skipped
                self._save_metrics()
    
    def complete_job(self, job_id: str, success: bool = True) -> None:
        """Record job completion"""
        with self.lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.end_time = time.time()
                job.processing_time = job.end_time - job.start_time
                job.status = "completed" if success else "failed"
                
                # Move to completed jobs
                self.completed_jobs.append(job)
                del self.jobs[job_id]
                
                # Add to latency tracking
                self.job_latencies.append(job.processing_time)
                
                # Update document metrics
                self.document_metrics.total_processed += job.total_files
                self.document_metrics.total_successful += job.successful_files
                self.document_metrics.total_failed += job.failed_files
                self.document_metrics.total_skipped += job.skipped_files
                self.document_metrics.total_processing_time += job.processing_time
                
                self._save_metrics()
    
    def record_document_processing(self, processing_time: float, success: bool, parser_type: str = 'local') -> None:
        """Record individual document processing metrics"""
        with self.lock:
            self.document_latencies.append(processing_time)
            
            # Track parser-specific metrics
            if parser_type in ['llm', 'llm_fallback', 'auto_local']:
                self.document_metrics.llm_processed += 1
                if success:
                    self.document_metrics.llm_successful += 1
                else:
                    self.document_metrics.llm_failed += 1
            else:
                self.document_metrics.local_processed += 1
                if success:
                    self.document_metrics.local_successful += 1
                else:
                    self.document_metrics.local_failed += 1
            
            self._save_metrics()
    
    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary"""
        with self.lock:
            # Calculate job statistics
            total_jobs = len(self.completed_jobs)
            successful_jobs = len([j for j in self.completed_jobs if j.status == "completed"])
            failed_jobs = len([j for j in self.completed_jobs if j.status == "failed"])
            
            # Calculate latency percentiles
            job_latencies = list(self.job_latencies)
            document_latencies = list(self.document_latencies)
            
            p50_job_latency = self._calculate_percentile(job_latencies, 50)
            p95_job_latency = self._calculate_percentile(job_latencies, 95)
            p50_document_latency = self._calculate_percentile(document_latencies, 50)
            p95_document_latency = self._calculate_percentile(document_latencies, 95)
            
            # Calculate average processing time
            avg_job_processing_time = statistics.mean(job_latencies) if job_latencies else 0
            avg_document_processing_time = statistics.mean(document_latencies) if document_latencies else 0
            
            return {
                "timestamp": datetime.now().isoformat(),
                "jobs": {
                    "total": total_jobs,
                    "successful": successful_jobs,
                    "failed": failed_jobs,
                    "currently_processing": len(self.jobs),
                    "p50_latency_seconds": p50_job_latency,
                    "p95_latency_seconds": p95_job_latency,
                    "avg_processing_time_seconds": avg_job_processing_time
                },
                "documents": {
                    "total_processed": self.document_metrics.total_processed,
                    "total_successful": self.document_metrics.total_successful,
                    "total_failed": self.document_metrics.total_failed,
                    "total_skipped": self.document_metrics.total_skipped,
                    "p50_processing_time_seconds": p50_document_latency,
                    "p95_processing_time_seconds": p95_document_latency,
                    "avg_processing_time_seconds": avg_document_processing_time,
                    "total_processing_time_seconds": self.document_metrics.total_processing_time
                },
                "system": {
                    "uptime_seconds": time.time() - self._get_start_time(),
                    "metrics_collection_start": self._get_start_time()
                }
            }
    
    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        summary = self.get_metrics_summary()
        
        metrics = []
        
        # Job metrics
        metrics.append(f"# HELP docuparse_jobs_total Total number of jobs")
        metrics.append(f"# TYPE docuparse_jobs_total counter")
        metrics.append(f"docuparse_jobs_total {summary['jobs']['total']}")
        
        metrics.append(f"# HELP docuparse_jobs_successful_total Total number of successful jobs")
        metrics.append(f"# TYPE docuparse_jobs_successful_total counter")
        metrics.append(f"docuparse_jobs_successful_total {summary['jobs']['successful']}")
        
        metrics.append(f"# HELP docuparse_jobs_failed_total Total number of failed jobs")
        metrics.append(f"# TYPE docuparse_jobs_failed_total counter")
        metrics.append(f"docuparse_jobs_failed_total {summary['jobs']['failed']}")
        
        metrics.append(f"# HELP docuparse_jobs_processing_current Current number of jobs being processed")
        metrics.append(f"# TYPE docuparse_jobs_processing_current gauge")
        metrics.append(f"docuparse_jobs_processing_current {summary['jobs']['currently_processing']}")
        
        metrics.append(f"# HELP docuparse_job_processing_time_seconds Job processing time in seconds")
        metrics.append(f"# TYPE docuparse_job_processing_time_seconds histogram")
        metrics.append(f"docuparse_job_processing_time_seconds_bucket{{le=\"0.1\"}} 0")
        metrics.append(f"docuparse_job_processing_time_seconds_bucket{{le=\"1\"}} 0")
        metrics.append(f"docuparse_job_processing_time_seconds_bucket{{le=\"10\"}} 0")
        metrics.append(f"docuparse_job_processing_time_seconds_bucket{{le=\"60\"}} 0")
        metrics.append(f"docuparse_job_processing_time_seconds_bucket{{le=\"300\"}} 0")
        metrics.append(f"docuparse_job_processing_time_seconds_bucket{{le=\"+Inf\"}} {summary['jobs']['total']}")
        metrics.append(f"docuparse_job_processing_time_seconds_sum {summary['jobs']['avg_processing_time_seconds'] * summary['jobs']['total']}")
        metrics.append(f"docuparse_job_processing_time_seconds_count {summary['jobs']['total']}")
        
        # Document metrics
        metrics.append(f"# HELP docuparse_documents_processed_total Total number of documents processed")
        metrics.append(f"# TYPE docuparse_documents_processed_total counter")
        metrics.append(f"docuparse_documents_processed_total {summary['documents']['total_processed']}")
        
        metrics.append(f"# HELP docuparse_documents_successful_total Total number of successfully processed documents")
        metrics.append(f"# TYPE docuparse_documents_successful_total counter")
        metrics.append(f"docuparse_documents_successful_total {summary['documents']['total_successful']}")
        
        metrics.append(f"# HELP docuparse_documents_failed_total Total number of failed document processing")
        metrics.append(f"# TYPE docuparse_documents_failed_total counter")
        metrics.append(f"docuparse_documents_failed_total {summary['documents']['total_failed']}")
        
        metrics.append(f"# HELP docuparse_documents_skipped_total Total number of skipped documents")
        metrics.append(f"# TYPE docuparse_documents_skipped_total counter")
        metrics.append(f"docuparse_documents_skipped_total {summary['documents']['total_skipped']}")
        
        metrics.append(f"# HELP docuparse_document_processing_time_seconds Document processing time in seconds")
        metrics.append(f"# TYPE docuparse_document_processing_time_seconds histogram")
        metrics.append(f"docuparse_document_processing_time_seconds_bucket{{le=\"0.1\"}} 0")
        metrics.append(f"docuparse_document_processing_time_seconds_bucket{{le=\"1\"}} 0")
        metrics.append(f"docuparse_document_processing_time_seconds_bucket{{le=\"5\"}} 0")
        metrics.append(f"docuparse_document_processing_time_seconds_bucket{{le=\"10\"}} 0")
        metrics.append(f"docuparse_document_processing_time_seconds_bucket{{le=\"30\"}} 0")
        metrics.append(f"docuparse_document_processing_time_seconds_bucket{{le=\"+Inf\"}} {summary['documents']['total_processed']}")
        metrics.append(f"docuparse_document_processing_time_seconds_sum {summary['documents']['total_processing_time_seconds']}")
        metrics.append(f"docuparse_document_processing_time_seconds_count {summary['documents']['total_processed']}")
        
        # System metrics
        metrics.append(f"# HELP docuparse_system_uptime_seconds System uptime in seconds")
        metrics.append(f"# TYPE docuparse_system_uptime_seconds gauge")
        metrics.append(f"docuparse_system_uptime_seconds {summary['system']['uptime_seconds']}")
        
        return "\n".join(metrics)
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]
    
    def _get_start_time(self) -> float:
        """Get system start time (first job or current time)"""
        if self.completed_jobs:
            return min(job.start_time for job in self.completed_jobs)
        return time.time()
    
    def _save_metrics(self) -> None:
        """Save metrics to file"""
        try:
            data = {
                "completed_jobs": [asdict(job) for job in self.completed_jobs],
                "document_metrics": asdict(self.document_metrics),
                "job_latencies": list(self.job_latencies),
                "document_latencies": list(self.document_latencies),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def _load_metrics(self) -> None:
        """Load metrics from file"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                
                # Load completed jobs
                self.completed_jobs = [
                    JobMetrics(**job_data) for job_data in data.get("completed_jobs", [])
                ]
                
                # Load document metrics
                doc_metrics = data.get("document_metrics", {})
                self.document_metrics = DocumentMetrics(**doc_metrics)
                
                # Load latencies
                self.job_latencies = deque(data.get("job_latencies", []), maxlen=1000)
                self.document_latencies = deque(data.get("document_latencies", []), maxlen=10000)
                
        except Exception as e:
            print(f"Error loading metrics: {e}")
    
    def reset_metrics(self) -> None:
        """Reset all metrics data to initial state"""
        with self.lock:
            # Clear all in-memory data
            self.jobs.clear()
            self.completed_jobs.clear()
            self.document_metrics = DocumentMetrics()
            self.job_latencies.clear()
            self.document_latencies.clear()
            
            # Delete metrics file
            try:
                if os.path.exists(self.metrics_file):
                    os.remove(self.metrics_file)
            except Exception as e:
                print(f"Error deleting metrics file: {e}")
            
            print("Metrics data has been reset")

# Global metrics collector instance
metrics_collector = MetricsCollector()
