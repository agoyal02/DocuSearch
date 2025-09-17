# DocuParse - Document Parser, Extractor & Search Application

A powerful document parsing, extraction and search application built with Flask that supports multiple document formats, provides intelligent search capabilities, and includes comprehensive observability features.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd DocuParse
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the application
python app.py

# Open browser to http://localhost:5000
```

**That's it!** The application will automatically create necessary directories and start running.

## Features

- **Multi-format Support**: Parse PDF, DOCX, TXT, and HTML documents
- **Intelligent Search**: Full-text search with relevance scoring
- **Web Interface**: Modern, responsive web UI with collapsible sections
- **REST API**: Complete API endpoints for integration
- **Metadata Extraction**: Extract document metadata, structure, and content
- **Real-time Processing**: Upload, parse, and extract documents instantly
- **Bulk Upload**: Process multiple documents with job tracking
- **S3 Integration**: Process documents directly from S3 buckets
- **GROBID Integration**: Enhanced PDF parsing with GROBID service
- **LLM Integration**: AI-powered metadata extraction using OpenAI/Anthropic
- **Observability**: Comprehensive metrics and monitoring
- **Job Management**: Track processing jobs with detailed status

## Supported Document Types

- **PDF**: Extract text, metadata, and page information
- **DOCX**: Parse paragraphs, tables, and document properties
- **TXT**: Plain text processing with word/character counts
- **HTML**: Extract text content from HTML documents

## Quick Start

### Prerequisites

- **Python 3.7+** (recommended: Python 3.8 or higher)
- **pip** (Python package installer)
- **Git** (for cloning the repository)

### Local Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DocuSearch
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up GROBID (optional but recommended for enhanced PDF parsing)**:
   ```bash
   # Download and start GROBID service
   ./start_grobid.sh
   
   # Verify GROBID is running
   curl http://localhost:8070/api/isalive
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and go to `http://localhost:5000`

### First Run Setup

The application will automatically create the following directories on first run:
- `uploads/` - For uploaded files
- `parsed_documents/` - For processed document data
- `job_metadata/` - For job tracking data
- `job_results/` - For job result files
- `metrics.json` - For metrics data

### Environment Variables (Optional)

Create a `.env` file for custom configuration:

```bash
# File processing limits
MAX_FILE_SIZE_MB=50
MAX_PAGES_PER_DOCUMENT=500

# AWS S3 Configuration (for S3 integration)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DOCUSEARCH_S3_BUCKET=your-bucket-name
DOCUSEARCH_S3_PREFIX=documents/

# GROBID Configuration
GROBID_URL=http://localhost:8070

# LLM Configuration (for AI-powered metadata extraction)
LLM_ENABLED=true  # Default: enabled
LLM_PROVIDER=openai  # openai, anthropic, or local
LLM_API_KEY=your_api_key_here  # Optional: can be set via UI
LLM_MODEL=gpt-3.5-turbo
LLM_BASE_URL=http://localhost:11434  # For local models like Ollama
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.1
```

## Usage

### Web Interface

1. **Upload Documents**: 
   - **Single File**: Use the file input to upload individual documents
   - **Bulk Upload**: Select multiple files or entire directories for batch processing
   - **S3 Integration**: Process documents directly from S3 buckets
   - **Parser Selection**: Choose between Local Parser, LLM Extraction, or Auto mode
   - **LLM Configuration**: Enter your API key and configure LLM settings directly in the UI

2. **Search Documents**: Use the search bar to find content across all uploaded documents

3. **View Job History**: 
   - Click on "📋 Job History" to expand and view all processing jobs
   - See detailed job status, processing times, and results
   - Download job results and metadata
   - Clear all history (also resets metrics to zero)

4. **Monitor System Metrics**:
   - Click on "📊 System Metrics" to view performance metrics
   - Monitor job success rates, processing times, and system health
   - View P50/P95 latency percentiles

### API Endpoints

#### Document Processing
- `POST /upload` - Upload and parse a single document
- `POST /bulk_upload` - Upload and parse multiple documents
- `POST /bulk_upload_s3` - Process documents from S3 bucket

#### Search & Retrieval
- `GET /search?q=query` - Search documents
- `GET /documents` - List all documents and jobs
- `GET /document/<filename>` - Get specific document content

#### Job Management
- `GET /jobs` - List all jobs
- `GET /job_status/<job_id>` - Get job status and progress
- `GET /job_results/<job_id>` - Get job results as JSON
- `GET /job_results/<job_id>/download` - Download job results as JSONL
- `DELETE /jobs/<job_id>` - Delete specific job (resets metrics if last job)
- `DELETE /jobs` - Clear all job history and reset metrics

#### System & Monitoring
- `GET /metrics` - Get system metrics in JSON format
- `GET /metrics/prometheus` - Get metrics in Prometheus format
- `GET /grobid_status` - Check GROBID service status
- `GET /llm_status` - Check LLM service status

### Example API Usage

**Upload a single document with LLM extraction**:
```bash
curl -X POST -F "file=@document.pdf" -F "parser_type=llm" -F "metadata_options=[\"title\",\"author\",\"topic\"]" http://localhost:5000/upload
```

**Bulk upload multiple documents**:
```bash
curl -X POST -F "files=@doc1.pdf" -F "files=@doc2.docx" -F "files=@doc3.txt" http://localhost:5000/bulk_upload
```

**Process documents from S3**:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"bucket": "my-bucket", "prefix": "documents/", "aws_region": "us-east-1"}' \
  http://localhost:5000/bulk_upload_s3
```

**Search documents**:
```bash
curl "http://localhost:5000/search?q=your search query"
```

**Get system metrics**:
```bash
# JSON format
curl http://localhost:5000/metrics

# Prometheus format
curl http://localhost:5000/metrics/prometheus
```

**List all jobs**:
```bash
curl http://localhost:5000/jobs
```

**Get job status**:
```bash
curl http://localhost:5000/job_status/abc12345
```

**Check LLM status**:
```bash
curl http://localhost:5000/llm_status
```

**Test LLM connection**:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"provider":"openai","api_key":"your_key","model":"gpt-3.5-turbo"}' \
  http://localhost:5000/test_llm
```

**Save LLM configuration**:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"provider":"openai","api_key":"your_key","model":"gpt-3.5-turbo"}' \
  http://localhost:5000/save_llm_config
```

## Project Structure

```
DocuParse/
├── app.py                    # Main Flask application
├── document_parser.py        # Document parsing logic
├── search_engine.py          # Search and indexing functionality
├── job_manager.py            # Job tracking and management
├── metrics_collector.py      # Metrics collection and storage
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── start_grobid.sh          # GROBID service startup script
├── test_metrics.py          # Metrics testing script
├── templates/
│   └── index.html           # Web interface with collapsible sections
├── uploads/                 # Uploaded files (created automatically)
├── parsed_documents/        # Parsed document data (created automatically)
├── job_metadata/            # Job tracking data (created automatically)
├── job_results/             # Job result files (created automatically)
├── metrics.json             # Metrics data (created automatically)
├── test_debug/              # Test files for development
├── DECISIONS.md             # Architectural decision log
└── README.md               # This file
```

## Dependencies

### Core Dependencies
- **Flask**: Web framework
- **python-docx**: DOCX document parsing
- **PyPDF2**: PDF document parsing
- **python-magic**: File type detection
- **Werkzeug**: WSGI utilities

### Optional Dependencies
- **boto3**: AWS S3 integration (for S3 uploads)
- **requests**: HTTP client for GROBID integration
- **statistics**: Built-in Python module for metrics calculations

### External Services
- **GROBID**: Enhanced PDF parsing service (optional)
- **AWS S3**: Cloud storage integration (optional)

## Configuration

### File-based Configuration (`config.py`)

The application uses `config.py` for centralized configuration:

- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 50MB)
- `MAX_PAGES_PER_DOCUMENT`: Maximum pages per document (default: 500)
- `UPLOAD_FOLDER`: Directory for uploaded files
- `SEARCH_RESULTS_LIMIT`: Maximum search results (default: 50)
- `SUPPORTED_FILE_TYPES`: Supported MIME types
- `AVAILABLE_METADATA_OPTIONS`: Metadata extraction options

### Environment Variables

Override configuration using environment variables:

```bash
export MAX_FILE_SIZE_MB=100
export MAX_PAGES_PER_DOCUMENT=1000
export AWS_REGION=us-west-2
export DOCUSEARCH_S3_BUCKET=my-documents
```

### Server Configuration

Modify `app.py` for server settings:

- `HOST`: Server host (default: '0.0.0.0')
- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: True)

## Features in Detail

### Document Parser

The `DocumentParser` class handles multiple document formats:

- **PDF**: Extracts text, metadata, and page information using PyPDF2
- **DOCX**: Parses paragraphs, tables, and core properties using python-docx
- **TXT**: Simple text processing with statistics
- **HTML**: Basic HTML parsing with tag removal

### Search Engine

The `SearchEngine` class provides:

- **Tokenization**: Simple word-based tokenization
- **Indexing**: Inverted index for fast searching
- **Scoring**: Relevance scoring based on term frequency and position
- **Snippets**: Context-aware text snippets for search results

### Web Interface

- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Feedback**: Loading states and error handling
- **Modern UI**: Clean, professional interface with smooth animations
- **File Upload**: Drag-and-drop file upload with validation

## Troubleshooting

### Common Issues

**Application won't start**:
```bash
# Check Python version
python3 --version

# Verify dependencies
pip install -r requirements.txt

# Check for port conflicts
lsof -i :5000
```

**GROBID service not working**:
```bash
# Check if GROBID is running
curl http://localhost:8070/api/isalive

# Start GROBID manually
./start_grobid.sh

# Check GROBID logs
tail -f grobid.log
```

**File upload errors**:
- Check file size limits in `config.py`
- Verify file format is supported
- Ensure sufficient disk space

**S3 integration issues**:
- Verify AWS credentials are set
- Check S3 bucket permissions
- Ensure correct region configuration

**Metrics not updating**:
- Check `metrics.json` file permissions
- Verify metrics collection is enabled
- Restart application to reset metrics

### Testing

**Run the test suite**:
```bash
# Test metrics functionality
python3 test_metrics.py

# Test individual components
python3 -c "from metrics_collector import metrics_collector; print('Metrics OK')"
python3 -c "from job_manager import job_manager; print('Job Manager OK')"
```

**Check application health**:
```bash
# Basic health check
curl http://localhost:5000/

# Metrics endpoint
curl http://localhost:5000/metrics

# GROBID status
curl http://localhost:5000/grobid_status
```

## Development

### Extending the Application

1. **Add new document types**: Extend the `DocumentParser` class
2. **Improve search**: Enhance the `SearchEngine` with better algorithms
3. **Add features**: Extend the Flask routes and templates
4. **Database integration**: Add persistent storage for documents and indexes
5. **Custom metrics**: Extend `MetricsCollector` for additional metrics
6. **New job types**: Add job types in `JobManager`

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make changes and test**: `python3 test_metrics.py`
4. **Commit changes**: `git commit -m "Add new feature"`
5. **Push and create PR**: `git push origin feature/new-feature`

### Code Structure

- **`app.py`**: Main Flask application and routes
- **`document_parser.py`**: Document parsing logic
- **`search_engine.py`**: Search and indexing
- **`job_manager.py`**: Job tracking and management
- **`metrics_collector.py`**: Metrics collection and storage
- **`config.py`**: Configuration management
- **`templates/index.html`**: Web interface

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

