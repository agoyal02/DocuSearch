# DocuSearch JSON Schemas

This directory contains JSON Schema definitions for all data models used in the DocuSearch application.

## Schema Files

### Core Data Models

1. **`job_information_schema.json`** - Complete job tracking information
   - Job status, progress, file counts
   - Skipped reasons and error tracking
   - Results array with file processing details

2. **`file_processing_result_schema.json`** - Individual file processing result
   - Success/failure status
   - Extracted metadata
   - Error messages and skip reasons

3. **`document_metadata_schema.json`** - Document metadata structure
   - File information (type, size, parser used)
   - Content metadata (title, author, abstract, etc.)
   - Structured sections and references

### Metrics Schemas

4. **`job_metrics_schema.json`** - Single job metrics
   - Processing times and file counts
   - Job status and timing information

5. **`document_metrics_schema.json`** - Aggregate document metrics
   - Total processed, successful, failed counts
   - Processing time statistics

6. **`system_metrics_schema.json`** - Complete system metrics
   - Job and document statistics
   - Latency percentiles (p50, p95)
   - System uptime information

### API Response Schemas

7. **`upload_response_schema.json`** - Single file upload response
   - Success status and parsed content
   - Extracted metadata based on options

8. **`bulk_upload_response_schema.json`** - Bulk upload response
   - Job ID for tracking
   - Processing statistics and results

9. **`search_response_schema.json`** - Document search response
   - Query and matching documents
   - Relevance scores and metadata

10. **`error_response_schema.json`** - Error response format
    - Error messages and additional details

## Usage

These schemas can be used for:

- **API Documentation** - Validate request/response formats
- **Data Validation** - Ensure data integrity in applications
- **Code Generation** - Generate type definitions and classes
- **Testing** - Validate test data against expected formats
- **Integration** - Ensure compatibility with external systems

## Schema Validation

You can validate JSON data against these schemas using:

- **Online validators** (json-schema-validator.herokuapp.com)
- **Command line tools** (ajv-cli, jsonschema)
- **Programming libraries** (jsonschema for Python, ajv for JavaScript)

## Example Usage

```bash
# Validate a job information JSON against its schema
ajv validate -s job_information_schema.json -d job_data.json

# Validate using Python
import jsonschema
with open('job_information_schema.json') as f:
    schema = json.load(f)
jsonschema.validate(job_data, schema)
```

## Schema Dependencies

Some schemas reference others:
- `upload_response_schema.json` references `document_metadata_schema.json`
- `job_information_schema.json` includes `file_processing_result_schema.json` as a definition

Make sure to have all referenced schemas available when validating.
