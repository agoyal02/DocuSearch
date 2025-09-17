from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
from document_parser import DocumentParser
from search_engine import SearchEngine
from job_manager import job_manager
from config import Config
from metrics_collector import metrics_collector
import tempfile
import shutil
import glob
import time

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import ClientError
except Exception:
    boto3 = None
    ClientError = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('parsed_documents', exist_ok=True)
os.makedirs('job_metadata', exist_ok=True)

# Initialize components
parser = DocumentParser()
search_engine = SearchEngine()

# Check GROBID availability
grobid_available = parser.is_grobid_available()
if grobid_available:
    print("✅ GROBID service is available - using enhanced PDF parsing")
else:
    print("⚠️  GROBID service not available - using fallback PDF parsing")
    print("   To enable GROBID, run: ./start_grobid.sh")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get metadata options
    metadata_options = request.form.get('metadata_options', '[]')
    try:
        metadata_options = json.loads(metadata_options)
    except:
        metadata_options = ['title', 'author', 'topic']  # Default options
    
    if file:
        # Save uploaded file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse the document with selected metadata options
            parsed_content = parser.parse_document(filepath, metadata_options)
            
            # Save parsed content
            parsed_filename = f"parsed_{filename}.json"
            parsed_filepath = os.path.join('parsed_documents', parsed_filename)
            with open(parsed_filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_content, f, indent=2, ensure_ascii=False)
            
            # Index for search
            search_engine.index_document(parsed_content, filename)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'parsed_content': parsed_content,
                'extracted_metadata': {key: parsed_content.get(key, 'Not found') for key in metadata_options},
                'message': 'Document uploaded and parsed successfully'
            })
            
        except Exception as e:
            return jsonify({'error': f'Error parsing document: {str(e)}'}), 500

@app.route('/search', methods=['GET'])
def search_documents():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    results = search_engine.search(query)
    return jsonify({
        'query': query,
        'results': results,
        'total': len(results)
    })

@app.route('/documents')
def list_documents():
    documents = []
    jobs = {}
    
    # Get all documents
    for filename in os.listdir('parsed_documents'):
        if filename.endswith('.json'):
            filepath = os.path.join('parsed_documents', filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
                # Extract job ID from filename or metadata
                job_id = content.get('job_id', 'unknown')
                
                document_info = {
                    'filename': filename,
                    'title': content.get('title', 'Untitled'),
                    'upload_date': content.get('upload_date', 'Unknown'),
                    'file_type': content.get('file_type', 'Unknown'),
                    'job_id': job_id,
                    'author': content.get('author', 'Not found'),
                    'topic': content.get('topic', 'Not found'),
                    'published_date': content.get('published_date', 'Not found'),
                    'parser': content.get('parser', 'Unknown')
                }
                
                documents.append(document_info)
                
                # Group by job ID
                if job_id not in jobs:
                    jobs[job_id] = {
                        'job_id': job_id,
                        'documents': [],
                        'total_documents': 0,
                        'successful_documents': 0,
                        'upload_date': content.get('upload_date', 'Unknown')
                    }
                
                jobs[job_id]['documents'].append(document_info)
                jobs[job_id]['total_documents'] += 1
                jobs[job_id]['successful_documents'] += 1
    
    # Get ALL jobs from job manager (including those without successful documents)
    all_jobs = job_manager.list_jobs()
    for job_summary in all_jobs:
        job_id = job_summary['job_id']
        
        # If job already exists from documents, update it
        if job_id in jobs:
            jobs[job_id].update({
                'status': job_summary.get('status', 'Unknown'),
                'processing_time': job_summary.get('processing_time', 0),
                'skipped_documents': job_summary.get('skipped_files', 0),
                'failed_documents': job_summary.get('failed_files', 0),
                'skipped_reasons': job_summary.get('skipped_reasons', {}),
                'corrupt_files': job_summary.get('corrupt_files', 0),
                'total_files': job_summary.get('total_files', 0),
                'processed_files': job_summary.get('processed_files', 0),
                'start_time': job_summary.get('start_time'),
                'end_time': job_summary.get('end_time'),
                'data_source': job_summary.get('data_source', 'Local')
            })
        else:
            # Create new job entry for jobs without successful documents
            jobs[job_id] = {
                'job_id': job_id,
                'documents': [],
                'total_documents': 0,
                'successful_documents': 0,
                'upload_date': job_summary.get('start_time', 'Unknown'),
                'status': job_summary.get('status', 'Unknown'),
                'processing_time': job_summary.get('processing_time', 0),
                'skipped_documents': job_summary.get('skipped_files', 0),
                'failed_documents': job_summary.get('failed_files', 0),
                'skipped_reasons': job_summary.get('skipped_reasons', {}),
                'corrupt_files': job_summary.get('corrupt_files', 0),
                'total_files': job_summary.get('total_files', 0),
                'processed_files': job_summary.get('processed_files', 0),
                'start_time': job_summary.get('start_time'),
                'end_time': job_summary.get('end_time'),
                'data_source': job_summary.get('data_source', 'Local')
            }
    
    return jsonify({
        'documents': documents,
        'jobs': list(jobs.values())
    })

@app.route('/document/<filename>')
def get_document(filename):
    filepath = os.path.join('parsed_documents', filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Document not found'}), 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    return jsonify(content)

@app.route('/bulk_upload', methods=['POST'])
def bulk_upload():
    """Handle bulk upload of multiple documents with job tracking"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    # Get metadata options
    metadata_options = request.form.get('metadata_options', '[]')
    try:
        metadata_options = json.loads(metadata_options)
    except:
        metadata_options = ['title', 'author', 'topic']  # Default options
    
    # Create job
    job_id = job_manager.create_job(len(files), metadata_options, 'Local')
    
    # Start metrics collection for this job
    metrics_collector.start_job(job_id, len(files))
    
    # Process files asynchronously (in a real app, this would be a background task)
    results = {
        'job_id': job_id,
        'success_count': 0,
        'error_count': 0,
        'skipped_count': 0,
        'successful_files': [],
        'failed_files': [],
        'skipped_files': [],
        'errors': []
    }
    
    for i, file in enumerate(files):
        if file.filename == '':
            continue
        
        # Extract just the filename from the path
        original_filename = os.path.basename(file.filename) if '/' in file.filename else file.filename
        
        # Update job progress
        job_manager.update_job_progress(job_id, original_filename, i + 1, results['success_count'], results['error_count'])
        
        # Start timing document processing
        doc_start_time = time.time()
        
        try:
            # Save uploaded file
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Validate file first
            is_valid, skip_reason, error_msg = parser.validate_file(filepath)
            
            if not is_valid:
                results['skipped_count'] += 1
                results['skipped_files'].append({
                    'filename': original_filename,
                    'reason': skip_reason,
                    'message': error_msg
                })
                job_manager.add_file_result(job_id, original_filename, False, error=error_msg, skip_reason=skip_reason)
                
                # Record document processing metrics
                doc_processing_time = time.time() - doc_start_time
                metrics_collector.record_document_processing(doc_processing_time, False)
                continue
            
            # Parse the document with selected metadata options
            parsed_content = parser.parse_document(filepath, metadata_options, job_id)
            
            # Save parsed content
            parsed_filename = f"parsed_{filename}.json"
            parsed_filepath = os.path.join('parsed_documents', parsed_filename)
            with open(parsed_filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_content, f, indent=2, ensure_ascii=False)
            
            # Index for search
            search_engine.index_document(parsed_content, filename)
            
            results['success_count'] += 1
            results['successful_files'].append({
                'filename': original_filename,
                'title': parsed_content.get('title', 'Untitled'),
                'extracted_metadata': {key: parsed_content.get(key, 'Not found') for key in metadata_options}
            })
            
            job_manager.add_file_result(job_id, original_filename, True, metadata=parsed_content)
            
            # Record successful document processing metrics
            doc_processing_time = time.time() - doc_start_time
            metrics_collector.record_document_processing(doc_processing_time, True)
            
        except Exception as e:
            results['error_count'] += 1
            results['failed_files'].append(original_filename)
            results['errors'].append(f"{original_filename}: {str(e)}")
            job_manager.add_file_result(job_id, original_filename, False, error=str(e))
            
            # Record failed document processing metrics
            doc_processing_time = time.time() - doc_start_time
            metrics_collector.record_document_processing(doc_processing_time, False)
    
    # Update metrics with final job progress
    metrics_collector.update_job_progress(job_id, results['success_count'], results['error_count'], results['skipped_count'])
    
    # Complete job
    job_manager.complete_job(job_id, success=True)
    
    # Complete metrics collection for this job
    metrics_collector.complete_job(job_id, success=True)
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': f'Bulk upload completed. {results["success_count"]} successful, {results["error_count"]} failed, {results["skipped_count"]} skipped.',
        'results': results
    })

@app.route('/job_status/<job_id>')
def get_job_status(job_id):
    """Get job status and progress"""
    job_status = job_manager.get_job_status(job_id)
    if not job_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job_status)

@app.route('/job_results/<job_id>')
def get_job_results(job_id):
    """Get job results as JSON"""
    job_results = job_manager.get_job_results(job_id)
    if not job_results:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job_results)

@app.route('/job_results/<job_id>/download')
def download_job_results(job_id):
    """Download job results as JSONL file"""
    job_status = job_manager.get_job_status(job_id)
    if not job_status:
        return jsonify({'error': 'Job not found'}), 404
    
    if job_status['status'] != 'Completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    jsonl_filename = f"job_{job_id}_results.jsonl"
    jsonl_path = os.path.join('job_results', jsonl_filename)
    
    if not os.path.exists(jsonl_path):
        return jsonify({'error': 'Job results file not found'}), 404
    
    return send_from_directory('job_results', jsonl_filename, as_attachment=True)

@app.route('/job_metadata/<filename>')
def serve_job_metadata(filename):
    """Serve job metadata JSON files"""
    try:
        return send_from_directory('job_metadata', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Job metadata file not found'}), 404

@app.route('/jobs')
def list_jobs():
    """List all jobs"""
    jobs = job_manager.list_jobs()
    return jsonify({'jobs': jobs})

@app.route('/grobid_status')
def grobid_status():
    """Check GROBID service status"""
    is_available = parser.is_grobid_available()
    return jsonify({
        'available': is_available,
        'url': parser.grobid_url,
        'message': 'GROBID service is available' if is_available else 'GROBID service is not available'
    })

@app.route('/metrics')
def get_metrics():
    """Get metrics in JSON format"""
    try:
        metrics = metrics_collector.get_metrics_summary()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': f'Failed to get metrics: {str(e)}'}), 500

@app.route('/metrics/prometheus')
def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    try:
        metrics = metrics_collector.get_prometheus_metrics()
        return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f'# Error getting metrics: {str(e)}', 500, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job and all related files (metadata, results, parsed documents)."""
    # Check if job exists
    job = job_manager.get_job_results(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    deleted = {
        'job_metadata': False,
        'job_results': False,
        'parsed_documents_deleted': 0,
        'metrics_reset': False
    }

    # Delete job metadata file
    metadata_path = os.path.join('job_metadata', f"{job_id}.json")
    if os.path.exists(metadata_path):
        try:
            os.remove(metadata_path)
            deleted['job_metadata'] = True
        except Exception:
            pass

    # Delete job results JSONL file
    results_path = os.path.join('job_results', f"job_{job_id}_results.jsonl")
    if os.path.exists(results_path):
        try:
            os.remove(results_path)
            deleted['job_results'] = True
        except Exception:
            pass

    # Delete parsed documents associated with this job
    for json_path in glob.glob(os.path.join('parsed_documents', '*.json')):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            if content.get('job_id') == job_id:
                try:
                    os.remove(json_path)
                    deleted['parsed_documents_deleted'] += 1
                except Exception:
                    pass
        except Exception:
            # Skip unreadable files
            continue

    # Remove from in-memory manager
    try:
        if job_id in job_manager.jobs:
            del job_manager.jobs[job_id]
    except Exception:
        pass

    # Check if this was the last job and reset metrics if so
    try:
        if len(job_manager.jobs) == 0:
            # No more jobs, reset metrics to clean state
            metrics_collector.reset_metrics()
            deleted['metrics_reset'] = True
    except Exception:
        pass

    return jsonify({'success': True, 'deleted': deleted})

@app.route('/jobs', methods=['DELETE'])
def clear_all_jobs():
    """Delete all job history and related local files (does not touch S3)."""
    summary = {
        'jobs_deleted': 0,
        'parsed_documents_deleted': 0,
        'job_metadata_deleted': 0,
        'job_results_deleted': 0,
        'uploads_deleted': 0,
        'metrics_reset': False
    }

    # Delete all job metadata files
    for path in glob.glob(os.path.join('job_metadata', '*.json')):
        try:
            os.remove(path)
            summary['job_metadata_deleted'] += 1
        except Exception:
            pass

    # Delete all job results files
    for path in glob.glob(os.path.join('job_results', 'job_*_results.jsonl')):
        try:
            os.remove(path)
            summary['job_results_deleted'] += 1
        except Exception:
            pass

    # Delete all parsed documents (they are derived artifacts)
    for path in glob.glob(os.path.join('parsed_documents', '*.json')):
        try:
            os.remove(path)
            summary['parsed_documents_deleted'] += 1
        except Exception:
            pass

    # Delete all uploaded files (local cache)
    for path in glob.glob(os.path.join(Config.UPLOAD_FOLDER, '*')):
        try:
            if os.path.isfile(path):
                os.remove(path)
                summary['uploads_deleted'] += 1
        except Exception:
            pass

    # Clear in-memory jobs
    try:
        summary['jobs_deleted'] = len(job_manager.jobs)
        job_manager.jobs.clear()
    except Exception:
        pass

    # Reset metrics data
    try:
        metrics_collector.reset_metrics()
        summary['metrics_reset'] = True
    except Exception as e:
        print(f"Error resetting metrics: {e}")

    return jsonify({'success': True, 'summary': summary})

def _is_supported_key(key: str) -> bool:
    key_lower = key.lower()
    return key_lower.endswith('.pdf') or key_lower.endswith('.docx') or key_lower.endswith('.txt') or key_lower.endswith('.html')

def _make_boto3_client(aws_access_key_id=None, aws_secret_access_key=None, aws_region=None):
    if boto3 is None:
        raise RuntimeError('boto3 is not installed. Please install boto3 to use S3 upload.')
    session_kwargs = {}
    
    # Use provided credentials or fall back to config
    access_key = aws_access_key_id or Config.AWS_ACCESS_KEY_ID
    secret_key = aws_secret_access_key or Config.AWS_SECRET_ACCESS_KEY
    region = aws_region or Config.AWS_REGION
    
    # Only add credentials if they are provided and not empty
    if access_key and secret_key and access_key.strip() and secret_key.strip():
        session_kwargs.update({
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
        })
        if Config.AWS_SESSION_TOKEN:
            session_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
    
    if region:
        session_kwargs['region_name'] = region
    
    # For public buckets, create client without credentials
    if session_kwargs:
        session = boto3.session.Session(**session_kwargs)
        return session.client('s3', config=BotoConfig(signature_version='s3v4'))
    else:
        # For public buckets, use default client without credentials
        return boto3.client('s3', region_name=region)

@app.route('/bulk_upload_s3', methods=['POST'])
def bulk_upload_s3():
    """Process documents from S3 bucket/prefix, delete local temp files after parsing."""
    try:
        data = request.get_json(silent=True) or {}
        bucket = data.get('bucket') or Config.DEFAULT_S3_BUCKET
        prefix = data.get('prefix') or Config.DEFAULT_S3_PREFIX
        metadata_options = data.get('metadata_options') or ['title', 'author', 'topic']
        aws_region = data.get('aws_region')
        aws_access_key_id = data.get('aws_access_key_id')
        aws_secret_access_key = data.get('aws_secret_access_key')
        is_public_bucket = data.get('is_public_bucket', False)

        if not bucket:
            return jsonify({'error': 'S3 bucket is required'}), 400
        if not aws_region:
            return jsonify({'error': 'AWS Region is required'}), 400
        
        # For private buckets, credentials are required
        if not is_public_bucket:
            if not aws_access_key_id:
                return jsonify({'error': 'AWS Access Key ID is required for private buckets'}), 400
            if not aws_secret_access_key:
                return jsonify({'error': 'AWS Secret Access Key is required for private buckets'}), 400

        # Create S3 client - for public buckets, credentials are optional
        s3 = _make_boto3_client(aws_access_key_id, aws_secret_access_key, aws_region)
    except Exception as e:
        return jsonify({'error': f'Failed to initialize S3 client: {str(e)}'}), 500

    # Collect keys recursively
    try:
        keys = []
        continuation_token = None
        while True:
            list_kwargs = {
                'Bucket': bucket,
                'Prefix': prefix or '',
                'MaxKeys': 1000,
            }
            if continuation_token:
                list_kwargs['ContinuationToken'] = continuation_token
            resp = s3.list_objects_v2(**list_kwargs)
            for obj in resp.get('Contents', []):
                key = obj['Key']
                if not key.endswith('/') and _is_supported_key(key):
                    keys.append(key)
            if resp.get('IsTruncated'):
                continuation_token = resp.get('NextContinuationToken')
            else:
                break

        if not keys:
            return jsonify({'error': 'No supported documents found in S3 location'}), 400
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidAccessKeyId':
            return jsonify({'error': 'Invalid AWS Access Key ID. Please check your credentials.'}), 401
        elif error_code == 'SignatureDoesNotMatch':
            return jsonify({'error': 'Invalid AWS Secret Access Key. Please check your credentials.'}), 401
        elif error_code == 'NoSuchBucket':
            return jsonify({'error': f'S3 bucket "{bucket}" does not exist or is not accessible.'}), 404
        else:
            return jsonify({'error': f'AWS S3 Error: {e.response["Error"]["Message"]}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to list S3 objects: {str(e)}'}), 500

    # Create job
    job_id = job_manager.create_job(len(keys), metadata_options, 'S3')
    
    # Start metrics collection for this job
    metrics_collector.start_job(job_id, len(keys))

    results = {
        'job_id': job_id,
        'success_count': 0,
        'error_count': 0,
        'skipped_count': 0,
        'successful_files': [],
        'failed_files': [],
        'skipped_files': [],
        'errors': []
    }

    temp_dir = tempfile.mkdtemp(prefix='s3_docs_')
    try:
        for idx, key in enumerate(keys, start=1):
            original_filename = os.path.basename(key)
            job_manager.update_job_progress(job_id, original_filename, idx, results['success_count'], results['error_count'])
            local_path = os.path.join(temp_dir, original_filename)
            
            # Start timing document processing
            doc_start_time = time.time()
            
            try:
                # Download to temp
                s3.download_file(bucket, key, local_path)

                # Validate
                is_valid, skip_reason, error_msg = parser.validate_file(local_path)
                if not is_valid:
                    results['skipped_count'] += 1
                    results['skipped_files'].append({'filename': original_filename, 'reason': skip_reason, 'message': error_msg})
                    job_manager.add_file_result(job_id, original_filename, False, error=error_msg, skip_reason=skip_reason)
                    
                    # Record document processing metrics
                    doc_processing_time = time.time() - doc_start_time
                    metrics_collector.record_document_processing(doc_processing_time, False)
                    continue

                # Parse
                parsed_content = parser.parse_document(local_path, metadata_options, job_id)

                # Save parsed JSON
                timestamped_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
                parsed_filename = f"parsed_{timestamped_name}.json"
                parsed_filepath = os.path.join('parsed_documents', parsed_filename)
                with open(parsed_filepath, 'w', encoding='utf-8') as f:
                    json.dump(parsed_content, f, indent=2, ensure_ascii=False)

                # Index
                search_engine.index_document(parsed_content, timestamped_name)

                results['success_count'] += 1
                results['successful_files'].append({
                    'filename': original_filename,
                    'title': parsed_content.get('title', 'Untitled'),
                    'extracted_metadata': {key: parsed_content.get(key, 'Not found') for key in metadata_options}
                })
                job_manager.add_file_result(job_id, original_filename, True, metadata=parsed_content)
                
                # Record successful document processing metrics
                doc_processing_time = time.time() - doc_start_time
                metrics_collector.record_document_processing(doc_processing_time, True)
                
            except Exception as e:
                results['error_count'] += 1
                results['failed_files'].append(original_filename)
                results['errors'].append(f"{original_filename}: {str(e)}")
                job_manager.add_file_result(job_id, original_filename, False, error=str(e))
                
                # Record failed document processing metrics
                doc_processing_time = time.time() - doc_start_time
                metrics_collector.record_document_processing(doc_processing_time, False)
                
            finally:
                # Per-file cleanup
                if os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except Exception:
                        pass
    finally:
        # Remove temp directory
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    # Update metrics with final job progress
    metrics_collector.update_job_progress(job_id, results['success_count'], results['error_count'], results['skipped_count'])
    
    job_manager.complete_job(job_id, success=True)
    
    # Complete metrics collection for this job
    metrics_collector.complete_job(job_id, success=True)

    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': f'S3 processing completed. {results["success_count"]} successful, {results["error_count"]} failed, {results["skipped_count"]} skipped.',
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
