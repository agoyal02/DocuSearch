# DocuSearch - Document Parser & Search Application

A powerful document parsing and search application built with Flask that supports multiple document formats and provides intelligent search capabilities.

## Features

- **Multi-format Support**: Parse PDF, DOCX, TXT, and HTML documents
- **Intelligent Search**: Full-text search with relevance scoring
- **Web Interface**: Modern, responsive web UI for easy document management
- **REST API**: Complete API endpoints for integration
- **Metadata Extraction**: Extract document metadata and structure
- **Real-time Processing**: Upload and parse documents instantly

## Supported Document Types

- **PDF**: Extract text, metadata, and page information
- **DOCX**: Parse paragraphs, tables, and document properties
- **TXT**: Plain text processing with word/character counts
- **HTML**: Extract text content from HTML documents

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DocuSearch
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## Usage

### Web Interface

1. **Upload Documents**: Use the upload section to select and upload documents
2. **Search Documents**: Use the search bar to find content across all uploaded documents
3. **View Documents**: Browse all uploaded documents in the documents list

### API Endpoints

- `POST /upload` - Upload and parse a document
- `GET /search?q=query` - Search documents
- `GET /documents` - List all documents
- `GET /document/<filename>` - Get specific document content

### Example API Usage

**Upload a document**:
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/upload
```

**Search documents**:
```bash
curl "http://localhost:5000/search?q=your search query"
```

**List all documents**:
```bash
curl http://localhost:5000/documents
```

## Project Structure

```
DocuSearch/
├── app.py                 # Main Flask application
├── document_parser.py     # Document parsing logic
├── search_engine.py       # Search and indexing functionality
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Uploaded files (created automatically)
├── parsed_documents/     # Parsed document data (created automatically)
└── README.md            # This file
```

## Dependencies

- **Flask**: Web framework
- **python-docx**: DOCX document parsing
- **PyPDF2**: PDF document parsing
- **python-magic**: File type detection
- **Werkzeug**: WSGI utilities

## Configuration

The application can be configured by modifying the following settings in `app.py`:

- `UPLOAD_FOLDER`: Directory for uploaded files
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 16MB)
- `HOST` and `PORT`: Server configuration

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

## Development

To extend the application:

1. **Add new document types**: Extend the `DocumentParser` class
2. **Improve search**: Enhance the `SearchEngine` with better algorithms
3. **Add features**: Extend the Flask routes and templates
4. **Database integration**: Add persistent storage for documents and indexes

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

