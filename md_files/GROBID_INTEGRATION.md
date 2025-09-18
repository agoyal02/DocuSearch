# GROBID Integration for DocuSearch

This document explains how to use GROBID (GeneRation Of BIbliographic Data) for enhanced document parsing in the DocuSearch application.

## What is GROBID?

[GROBID](https://github.com/kermitt2/grobid/) is a machine learning-based tool specifically designed for extracting structured information from scholarly documents. It provides significantly better PDF parsing compared to traditional libraries like PyPDF2.

## Benefits of GROBID Integration

- **Enhanced PDF Parsing**: Uses machine learning models for more accurate text extraction
- **Structured Metadata**: Automatically extracts titles, authors, abstracts, references, and sections
- **Academic Document Optimization**: Specifically designed for scholarly documents
- **Better Layout Understanding**: Preserves document structure and formatting
- **Fallback Support**: Automatically falls back to PyPDF2 if GROBID is unavailable

## Setup Instructions

### 1. Start GROBID Service

```bash
# Start GROBID using Docker Compose
./start_grobid.sh

# Or manually with Docker Compose
docker-compose up -d grobid
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify GROBID is Running

```bash
# Check GROBID status
curl http://localhost:8070/api/isalive

# Or use the test script
python test_grobid_integration.py
```

### 4. Start DocuSearch Application

```bash
python app.py
```

## API Endpoints

### Check GROBID Status
```bash
GET /grobid_status
```

Returns:
```json
{
  "available": true,
  "url": "http://localhost:8070",
  "message": "GROBID service is available"
}
```

## Document Parsing Features

### PDF Documents (with GROBID)
- **Title extraction** from document metadata
- **Author extraction** with proper name parsing
- **Abstract extraction** from document content
- **Section parsing** with hierarchical structure
- **Reference extraction** from bibliography
- **Keyword extraction** from document metadata
- **Full text extraction** with preserved formatting

### Fallback Parsing
If GROBID is unavailable, the system automatically falls back to:
- **PyPDF2** for PDF documents
- **python-docx** for DOCX documents
- **BeautifulSoup** for HTML documents
- **Built-in parsing** for TXT documents

## Configuration

### GROBID Service URL
The GROBID service URL can be configured in the `DocumentParser` class:

```python
parser = DocumentParser(grobid_url="http://localhost:8070")
```

### Docker Configuration
The GROBID service is configured in `docker-compose.yml`:

```yaml
services:
  grobid:
    image: lfoppiano/grobid:0.8.2
    ports:
      - "8070:8070"
      - "8071:8071"
    environment:
      - JAVA_OPTS=-Xmx4g
```

## Performance Considerations

### GROBID Performance
- **First request**: May take 30-60 seconds due to model loading
- **Subsequent requests**: Typically 2-5 seconds per document
- **Memory usage**: Requires 4GB RAM (configurable)
- **CPU usage**: Benefits from multi-core systems

### Fallback Performance
- **PyPDF2**: Very fast (1-2 seconds per document)
- **python-docx**: Fast (1-3 seconds per document)
- **Memory usage**: Minimal (100-200MB)

## Troubleshooting

### GROBID Not Starting
```bash
# Check Docker logs
docker-compose logs grobid

# Check if port 8070 is available
netstat -an | grep 8070

# Restart GROBID
docker-compose restart grobid
```

### Memory Issues
If you encounter memory issues, reduce the Java heap size in `docker-compose.yml`:

```yaml
environment:
  - JAVA_OPTS=-Xmx2g  # Reduce from 4g to 2g
```

### Slow Performance
- Ensure GROBID has enough memory allocated
- Check if the system has sufficient CPU cores
- Consider using GROBID's Deep Learning models for better accuracy

## Testing

### Run Integration Tests
```bash
python test_grobid_integration.py
```

### Test with Sample Documents
1. Upload a PDF document through the web interface
2. Check the parsed content in the `/documents` endpoint
3. Verify that GROBID parsing was used (check the `parser` field)

## Monitoring

### Check GROBID Health
```bash
curl http://localhost:8070/api/isalive
```

### Monitor GROBID Logs
```bash
docker-compose logs -f grobid
```

### Check DocuSearch Logs
The application will log GROBID availability status on startup:
- ✅ GROBID service is available - using enhanced PDF parsing
- ⚠️ GROBID service not available - using fallback PDF parsing

## Advanced Configuration

### Using Deep Learning Models
To enable GROBID's Deep Learning models for better accuracy:

1. Edit the GROBID configuration file
2. Enable the desired models
3. Restart the GROBID service

### Custom GROBID Settings
You can modify the GROBID processing parameters in the `_parse_pdf_with_grobid` method:

```python
result = self.grobid_client.process_pdf(
    filepath, 
    "processFulltextDocument", 
    generateIDs=True, 
    consolidate_citations=True,
    include_raw_citations=True,
    include_raw_affiliations=True,
    tei_coordinates=True
)
```

## Support

For issues related to:
- **GROBID**: Check the [GROBID documentation](https://grobid.readthedocs.io/)
- **DocuSearch integration**: Check the application logs and test script output
- **Docker issues**: Check Docker logs and system resources
