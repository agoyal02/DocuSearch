# 📁 DocuSearch Repository Structure

Complete directory and file structure of the DocuSearch document parsing, extraction, and search application.

## 🌳 Repository Overview

```
DocuSearch/
├── 📁 Core Application Files
├── 📁 Configuration & Setup
├── 📁 Documentation
├── 📁 Schemas & Data Models
├── 📁 Templates & UI
├── 📁 Scripts & Automation
├── 📁 Testing & Development
├── 📁 Data Directories
└── 📁 Generated Files (gitignored)
```

---

## 📂 Detailed Directory Structure

### 🏠 **Root Directory**
```
DocuSearch/
├── 📄 app.py                          # Main Flask application
├── 📄 config.py                       # Application configuration
├── 📄 document_parser.py              # Document parsing logic
├── 📄 job_manager.py                  # Job management system
├── 📄 metrics_collector.py            # Metrics collection system
├── 📄 search_engine.py                # Document search functionality
├── 📄 requirements.txt                # Python dependencies
├── 📄 docker-compose.yml              # Docker services configuration
├── 📄 .gitignore                      # Git ignore rules
└── 📄 README.md                       # Main project documentation
```

### 📁 **Core Application Files**
```
├── app.py                             # Flask web server & API endpoints
├── config.py                          # Environment variables & settings
├── document_parser.py                 # PDF/DOCX parsing with GROBID
├── job_manager.py                     # Job tracking & management
├── metrics_collector.py               # Prometheus-style metrics
└── search_engine.py                   # Full-text search engine
```

### 📁 **Configuration & Setup**
```
├── docker-compose.yml                 # GROBID & application services
├── docusearch.service                 # Systemd service file
├── get-pip.py                         # Pip installation script
├── start_grobid.sh                    # GROBID startup script
└── .gitignore                         # Git exclusions
```

### 📁 **Documentation** (`/docs/`)
```
docs/
├── 📄 docker-compose.yml              # Additional Docker config
└── 📁 Sample Documents/
    ├── AI Financial Sector.pdf
    ├── Artificial Intelligence Chatbot.pdf
    ├── Factual Predictions.pdf
    └── Teaching Artificial Intelligence.pdf
```

### 📁 **API & Data Schemas** (`/schemas/`)
```
schemas/
├── 📄 README.md                       # Schema documentation
├── 📄 job_information_schema.json     # Job data structure
├── 📄 file_processing_result_schema.json
├── 📄 document_metadata_schema.json   # Document metadata structure
├── 📄 job_metrics_schema.json         # Job metrics structure
├── 📄 document_metrics_schema.json    # Document metrics structure
├── 📄 system_metrics_schema.json      # System metrics structure
├── 📄 upload_response_schema.json     # Upload API response
├── 📄 bulk_upload_response_schema.json
├── 📄 search_response_schema.json     # Search API response
└── 📄 error_response_schema.json      # Error response structure
```

### 📁 **Web Templates** (`/templates/`)
```
templates/
└── 📄 index.html                      # Main web interface
```

### 📁 **Scripts & Automation**
```
├── 📄 start_all_services.sh           # Complete startup script (Linux/macOS)
├── 📄 quick_start.sh                  # Quick startup script (Linux/macOS)
├── 📄 install_pip.sh                  # Pip installation script (Linux/macOS)
├── 📄 install_docker.sh               # Docker installation script (Linux/macOS)
└── 📄 Makefile                        # Make commands for service management
```

### 📁 **Testing & Development**
```
├── 📄 test_app.py                     # Main application tests
├── 📄 test_bulk_upload.py             # Bulk upload tests
├── 📄 test_collapsible_jobs.py        # UI collapsible tests
├── 📄 test_directory_display.html     # Directory display tests
├── 📄 test_directory_filtering.html   # Directory filtering tests
├── 📄 test_file_limits.py             # File limit tests
├── 📄 test_grobid_integration.py      # GROBID integration tests
├── 📄 test_job_system.py              # Job system tests
├── 📄 test_metadata.py                # Metadata extraction tests
├── 📄 test_metrics.py                 # Metrics system tests
└── 📁 test_debug/                     # Debug test files
    ├── file1.pdf
    ├── file2.pdf
    └── file3.pdf
```

### 📁 **Data Directories** (Runtime Generated)
```
├── 📁 uploads/                        # Uploaded files (gitignored)
├── 📁 parsed_documents/               # Processed documents (gitignored)
├── 📁 job_metadata/                   # Job metadata files (gitignored)
├── 📁 job_results/                    # Job result files (gitignored)
└── 📁 architecture_images/            # Architecture diagrams (gitignored)
```

### 📁 **Documentation Files**
```
├── 📄 README.md                       # Main project documentation
├── 📄 API_DOCUMENTATION.md            # Complete API reference
├── 📄 REPOSITORY_STRUCTURE.md         # This file
├── 📄 STARTUP_GUIDE.md                # Detailed startup instructions
├── 📄 SERVICE_SCRIPTS_README.md       # Service scripts reference
├── 📄 DECISIONS.md                    # Architecture decisions log
├── 📄 AUTHOR_ARRAY_UPDATE.md          # Feature update notes
├── 📄 DIRECTORY_COUNT_FIX.md          # Bug fix documentation
├── 📄 DIRECTORY_UPLOAD_UPDATE.md      # Feature update notes
├── 📄 ENHANCED_DIRECTORY_DISPLAY.md   # UI enhancement notes
├── 📄 GROBID_INTEGRATION.md           # GROBID integration notes
├── 📄 IMPROVED_DIRECTORY_FILTERING.md # Filtering enhancement notes
├── 📄 INTEGRATION_SUMMARY.md          # Integration summary
├── 📄 PERFORMANCE_OPTIMIZATION.md     # Performance notes
├── 📄 PERSISTENT_JOB_STORAGE.md       # Job storage documentation
├── 📄 PIP_INSTALLATION_UPDATE.md      # Pip installation features
├── 📄 DOCKER_INSTALLATION_UPDATE.md   # Docker installation features
└── 📄 SYSTEM_STATUS_REPORT.md         # System status documentation
```

---

## 🏗️ **Architecture Overview**

### **Core Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │  Document       │    │   Search        │
│   (app.py)      │◄──►│  Parser         │◄──►│   Engine        │
│                 │    │  (GROBID)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Job Manager   │    │   Metrics       │    │   Templates     │
│                 │    │   Collector     │    │   (HTML/JS)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Flow**
```
Upload → Job Manager → Document Parser → Search Engine
   ↓           ↓              ↓              ↓
Metrics ← Job Results ← Parsed Content ← Indexed Content
```

---

## 📋 **File Categories**

### **🐍 Python Files**
- **Core Logic**: `app.py`, `config.py`, `document_parser.py`
- **Management**: `job_manager.py`, `metrics_collector.py`
- **Search**: `search_engine.py`
- **Tests**: `test_*.py`

### **🌐 Web Files**
- **Templates**: `templates/index.html`
- **Static Assets**: CSS/JS embedded in HTML

### **🐳 Docker Files**
- **Services**: `docker-compose.yml`
- **Scripts**: `start_grobid.sh`

### **📊 Data Files**
- **Schemas**: `schemas/*.json`
- **Config**: `requirements.txt`, `.gitignore`
- **Service**: `docusearch.service`

### **📚 Documentation**
- **Main**: `README.md`, `API_DOCUMENTATION.md`
- **Guides**: `STARTUP_GUIDE.md`, `SERVICE_SCRIPTS_README.md`
- **Updates**: `*_UPDATE.md`, `*_FIX.md`

### **🔧 Scripts**
- **Startup**: `start_all_services.sh`, `quick_start.sh`
- **Installation**: `install_*.sh`
- **Build**: `Makefile`

---

## 🚀 **Quick Navigation**

### **Start Here**
- `README.md` - Project overview and quick start
- `start_all_services.sh` - One-command setup
- `API_DOCUMENTATION.md` - Complete API reference

### **Development**
- `app.py` - Main application code
- `test_*.py` - Test files
- `schemas/` - Data model definitions

### **Configuration**
- `config.py` - Environment settings
- `docker-compose.yml` - Service configuration
- `requirements.txt` - Dependencies

### **Documentation**
- `STARTUP_GUIDE.md` - Detailed setup instructions
- `DECISIONS.md` - Architecture decisions
- `schemas/README.md` - Schema documentation

---

## 📦 **Dependencies**

### **Python Packages** (`requirements.txt`)
```
Flask==2.3.3
PyPDF2==3.0.1
python-docx==0.8.11
beautifulsoup4==4.12.2
python-magic==0.4.27
requests==2.31.0
grobid-client-python==0.0.7
openai==1.35.0
anthropic==0.18.0
httpx==0.24.1
boto3==1.34.0
```

### **External Services**
- **GROBID** - PDF parsing service
- **Docker** - Containerization
- **S3** - Cloud storage (optional)

---

## 🔒 **Security & Git**

### **Git Ignored Files** (`.gitignore`)
```
# Python
__pycache__/, *.pyc, venv/, .venv/

# Application Data
uploads/, parsed_documents/, job_metadata/, job_results/
metrics.json, *.log, temp/

# Docker
docker-data/, grobid_data/

# IDE & OS
.vscode/, .idea/, .DS_Store, Thumbs.db

# Security
.env*, *.key, *.pem, secrets.json, credentials.json
```

---

## 📈 **Repository Statistics**

- **Total Files**: ~60+ files
- **Python Files**: 8 core + 8 test files
- **Documentation**: 20+ markdown files
- **Schemas**: 10 JSON schema files
- **Scripts**: 5 automation scripts
- **Templates**: 1 HTML template
- **Configuration**: 4 config files

---

## 🎯 **Key Directories**

| Directory | Purpose | Files |
|-----------|---------|-------|
| `/` | Core application | `app.py`, `config.py`, etc. |
| `/schemas/` | Data models | JSON schemas |
| `/templates/` | Web UI | HTML templates |
| `/docs/` | Sample files | PDF documents |
| `/uploads/` | Runtime data | Uploaded files |
| `/parsed_documents/` | Runtime data | Processed documents |
| `/job_metadata/` | Runtime data | Job tracking |
| `/job_results/` | Runtime data | Job results |

This structure provides a clean, organized, and maintainable codebase for the DocuSearch application! 🚀
