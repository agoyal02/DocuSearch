from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
from document_parser import DocumentParser
from search_engine import SearchEngine
from job_manager import job_manager
from config import Config

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
                'end_time': job_summary.get('end_time')
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
                'end_time': job_summary.get('end_time')
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
    job_id = job_manager.create_job(len(files), metadata_options)
    
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
            
        except Exception as e:
            results['error_count'] += 1
            results['failed_files'].append(original_filename)
            results['errors'].append(f"{original_filename}: {str(e)}")
            job_manager.add_file_result(job_id, original_filename, False, error=str(e))
    
    # Complete job
    job_manager.complete_job(job_id, success=True)
    
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
