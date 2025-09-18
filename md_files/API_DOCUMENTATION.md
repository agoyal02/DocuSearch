# 📚 DocuSearch API Documentation

Complete API reference for the DocuSearch document parsing, extraction, and search application.

## 🌐 Base URL

```
http://localhost:5000
```

## 📋 API Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface |
| `POST` | `/upload` | Single file upload |
| `GET` | `/search` | Search documents |
| `GET` | `/documents` | List all documents |
| `GET` | `/document/<filename>` | Get specific document |
| `POST` | `/bulk_upload` | Bulk file upload |
| `POST` | `/bulk_upload_s3` | S3 bulk upload |
| `GET` | `/jobs` | List all jobs |
| `GET` | `/job_status/<job_id>` | Get job status |
| `GET` | `/job_results/<job_id>` | Get job results |
| `GET` | `/job_results/<job_id>/download` | Download job results |
| `DELETE` | `/jobs/<job_id>` | Delete specific job |
| `DELETE` | `/jobs` | Delete all jobs |
| `GET` | `/grobid_status` | Check GROBID service |
| `GET` | `/metrics` | Get system metrics |
| `GET` | `/metrics/prometheus` | Get Prometheus metrics |

---

## 🏠 Web Interface

### `GET /`
**Description**: Serves the main web interface

**Response**: HTML page with the DocuSearch web interface

---

## 📄 Document Upload & Processing

### `POST /upload`
**Description**: Upload and parse a single document

**Content-Type**: `multipart/form-data`

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Document file to upload |
| `metadata_options` | String | No | JSON array of metadata fields to extract (default: `["title", "author", "topic"]`) |

**Supported File Types**:
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Plain Text (`.txt`)
- HTML (`.html`)

**Response**:
```json
{
  "success": true,
  "filename": "20241217_143022_document.pdf",
  "parsed_content": {
    "file_type": "PDF",
    "file_size": 1024000,
    "upload_date": "2024-12-17T14:30:22.123456",
    "job_id": null,
    "parser": "GROBID",
    "title": "Document Title",
    "author": "Author Name",
    "topic": "Document Topic",
    "published_date": "2024-01-01",
    "abstract": "Document abstract...",
    "keywords": ["keyword1", "keyword2"],
    "references": ["Reference 1", "Reference 2"],
    "sections": [
      {
        "title": "Section 1",
        "content": "Section content..."
      }
    ],
    "full_text": "Complete document text..."
  },
  "extracted_metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "topic": "Document Topic"
  },
  "message": "Document uploaded and parsed successfully"
}
```

**Error Response**:
```json
{
  "error": "Error parsing document: [error message]"
}
```

---

## 🔍 Document Search

### `GET /search`
**Description**: Search through processed documents

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | String | Yes | Search query |

**Example**: `GET /search?q=artificial intelligence`

**Response**:
```json
{
  "query": "artificial intelligence",
  "results": [
    {
      "filename": "parsed_20241217_143022_document.pdf.json",
      "title": "AI in Healthcare",
      "author": "Dr. Smith",
      "topic": "Artificial Intelligence, Healthcare",
      "upload_date": "2024-12-17T14:30:22.123456",
      "relevance_score": 0.95
    }
  ],
  "total": 1
}
```

**Error Response**:
```json
{
  "error": "No search query provided"
}
```

---

## 📚 Document Management

### `GET /documents`
**Description**: List all processed documents

**Response**:
```json
{
  "documents": [
    {
      "filename": "parsed_20241217_143022_document.pdf.json",
      "title": "Document Title",
      "upload_date": "2024-12-17T14:30:22.123456",
      "file_type": "PDF",
      "job_id": "abc12345",
      "author": "Author Name",
      "topic": "Document Topic",
      "published_date": "2024-01-01",
      "parser": "GROBID"
    }
  ],
  "jobs": [
    {
      "job_id": "abc12345",
      "documents": [...],
      "total_documents": 5,
      "successful_documents": 4,
      "upload_date": "2024-12-17T14:30:22.123456"
    }
  ]
}
```

### `GET /document/<filename>`
**Description**: Get specific document content

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | String | Yes | Document filename |

**Response**: Complete document JSON object

**Error Response**:
```json
{
  "error": "Document not found"
}
```

---

## 📦 Bulk Operations

### `POST /bulk_upload`
**Description**: Upload and process multiple documents

**Content-Type**: `multipart/form-data`

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | File[] | Yes | Array of document files |
| `metadata_options` | String | No | JSON array of metadata fields to extract |

**Response**:
```json
{
  "success": true,
  "job_id": "abc12345",
  "message": "Bulk upload completed. 4 successful, 1 failed, 0 skipped.",
  "results": {
    "success_count": 4,
    "error_count": 1,
    "skipped_count": 0,
    "total_files": 5,
    "processing_time": 45.67,
    "successful_files": [
      {
        "filename": "document1.pdf",
        "title": "Document 1",
        "extracted_metadata": {...}
      }
    ],
    "failed_files": [
      {
        "filename": "corrupt.pdf",
        "error": "File is corrupted"
      }
    ],
    "skipped_files": []
  }
}
```

### `POST /bulk_upload_s3`
**Description**: Process documents from S3 bucket

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "bucket": "my-documents-bucket",
  "prefix": "documents/",
  "metadata_options": ["title", "author", "topic"],
  "aws_region": "us-east-1",
  "aws_access_key_id": "AKIA...",
  "aws_secret_access_key": "...",
  "is_public_bucket": false
}
```

**Response**: Same as bulk upload with S3-specific details

---

## 📊 Job Management

### `GET /jobs`
**Description**: List all processing jobs

**Response**:
```json
{
  "jobs": [
    {
      "job_id": "abc12345",
      "status": "Completed",
      "total_files": 5,
      "successful_files": 4,
      "failed_files": 1,
      "skipped_files": 0,
      "start_time": "2024-12-17T14:30:22.123456",
      "end_time": "2024-12-17T14:31:07.789012",
      "processing_time": 45.67,
      "data_source": "Local"
    }
  ]
}
```

### `GET /job_status/<job_id>`
**Description**: Get specific job status and progress

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | String | Yes | Job identifier |

**Response**:
```json
{
  "job_id": "abc12345",
  "status": "Completed",
  "progress_percentage": 100,
  "current_file": null,
  "total_files": 5,
  "processed_files": 5,
  "successful_files": 4,
  "failed_files": 1,
  "skipped_files": 0,
  "skipped_reasons": {
    "unknown_format": 0,
    "file_size_limit": 0,
    "page_limit": 0
  },
  "corrupt_files": 0,
  "processing_time": 45.67,
  "start_time": "2024-12-17T14:30:22.123456",
  "end_time": "2024-12-17T14:31:07.789012",
  "data_source": "Local"
}
```

### `GET /job_results/<job_id>`
**Description**: Get detailed job results

**Response**:
```json
{
  "job_id": "abc12345",
  "status": "Completed",
  "total_files": 5,
  "successful_files": 4,
  "failed_files": 1,
  "skipped_files": 0,
  "start_time": "2024-12-17T14:30:22.123456",
  "end_time": "2024-12-17T14:31:07.789012",
  "processing_time_seconds": 45.67,
  "metadata_options": ["title", "author", "topic"],
  "results": [
    {
      "filename": "document1.pdf",
      "success": true,
      "timestamp": "2024-12-17T14:30:25.123456",
      "metadata": {...},
      "error": null,
      "skip_reason": null
    }
  ]
}
```

### `GET /job_results/<job_id>/download`
**Description**: Download job results as JSONL file

**Response**: File download (JSONL format)

---

## 🗑️ Job Deletion

### `DELETE /jobs/<job_id>`
**Description**: Delete specific job and all related files

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | String | Yes | Job identifier |

**Response**:
```json
{
  "success": true,
  "deleted": {
    "job_metadata": true,
    "job_results": true,
    "parsed_documents_deleted": 4,
    "metrics_reset": false
  }
}
```

### `DELETE /jobs`
**Description**: Delete all jobs and reset system

**Response**:
```json
{
  "success": true,
  "summary": {
    "jobs_deleted": 5,
    "documents_deleted": 20,
    "files_deleted": 25,
    "metrics_reset": true
  }
}
```

---

## 🔧 System Status & Monitoring

### `GET /grobid_status`
**Description**: Check GROBID service availability

**Response**:
```json
{
  "available": true,
  "url": "http://localhost:8070",
  "message": "GROBID service is available"
}
```

### `GET /metrics`
**Description**: Get system metrics in JSON format

**Response**:
```json
{
  "timestamp": "2024-12-17T14:31:07.789012",
  "jobs": {
    "total": 25,
    "successful": 23,
    "failed": 2,
    "currently_processing": 0,
    "p50_latency_seconds": 42.1,
    "p95_latency_seconds": 78.3,
    "avg_processing_time_seconds": 45.67
  },
  "documents": {
    "total_processed": 150,
    "total_successful": 142,
    "total_failed": 8,
    "total_skipped": 0,
    "p50_processing_time_seconds": 6.2,
    "p95_processing_time_seconds": 15.8,
    "avg_processing_time_seconds": 8.34,
    "total_processing_time_seconds": 1250.45
  },
  "system": {
    "uptime_seconds": 3600.45,
    "metrics_collection_start": 1702822207.789012
  }
}
```

### `GET /metrics/prometheus`
**Description**: Get metrics in Prometheus format

**Response**: Plain text Prometheus metrics format

---

## 📝 Metadata Options

Available metadata fields for extraction:

| Field | Description |
|-------|-------------|
| `title` | Document title |
| `author` | Author(s) information |
| `published_date` | Publication date |
| `topic` | Document topic/subject |
| `abstract` | Document abstract |
| `keywords` | Document keywords |
| `references` | Bibliography references |
| `sections` | Document sections with titles and content |
| `full_text` | Complete document text |

---

## 🚨 Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid parameters |
| `404` | Not Found - Resource not found |
| `500` | Internal Server Error - Server error |

---

## 📋 Request/Response Examples

### Upload a PDF Document
```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@document.pdf" \
  -F "metadata_options=[\"title\", \"author\", \"topic\"]"
```

### Search Documents
```bash
curl "http://localhost:5000/search?q=artificial intelligence"
```

### Get Job Status
```bash
curl http://localhost:5000/job_status/abc12345
```

### Bulk Upload Files
```bash
curl -X POST http://localhost:5000/bulk_upload \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx" \
  -F "metadata_options=[\"title\", \"author\", \"abstract\"]"
```

### S3 Bulk Upload
```bash
curl -X POST http://localhost:5000/bulk_upload_s3 \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "my-documents",
    "prefix": "research/",
    "aws_region": "us-east-1",
    "aws_access_key_id": "AKIA...",
    "aws_secret_access_key": "...",
    "metadata_options": ["title", "author", "topic"]
  }'
```

---

## 🔗 Related Documentation

- [JSON Schemas](schemas/) - Data model schemas
- [Startup Guide](STARTUP_GUIDE.md) - Service startup instructions
- [README](README.md) - Main project documentation
