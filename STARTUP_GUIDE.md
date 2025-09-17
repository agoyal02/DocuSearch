# 🚀 DocuSearch Service Startup Guide

This guide provides multiple ways to start all DocuSearch services with a single command.

## 📋 Prerequisites

Before running any startup script, ensure you have:

- **Python 3.7+** installed
- **Docker** and **Docker Compose** installed
- **Git** (for cloning the repository)

**Note:** The startup scripts will automatically check for and install **pip** if it's missing.

### Installation Links:
- [Python](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Git](https://git-scm.com/downloads)

### Automatic Pip Installation

The startup scripts include automatic pip installation:

- **Linux/macOS**: Downloads and installs pip using `get-pip.py`
- **Windows**: Downloads and installs pip using PowerShell
- **Fallback**: Provides manual installation instructions if automatic installation fails

## 🎯 Quick Start Options

### Option 1: Full-Featured Script (Recommended)

**Linux/macOS:**
```bash
./start_all_services.sh
```

**Windows:**
```cmd
start_all_services.bat
```

**Features:**
- ✅ Comprehensive error checking
- ✅ Service health monitoring
- ✅ Automatic dependency installation
- ✅ Service management commands
- ✅ Colored output and status reporting

### Option 2: Simple Quick Start

**Linux/macOS:**
```bash
./quick_start.sh
```

**Features:**
- ✅ Minimal output
- ✅ Fast startup
- ✅ Basic error handling

### Option 3: Standalone Pip Installation

If you need to install pip separately before running the startup scripts:

**Linux/macOS:**
```bash
./install_pip.sh
```

**Windows:**
```cmd
install_pip.bat
```

**Features:**
- ✅ Multiple installation methods (ensurepip, get-pip.py, package managers)
- ✅ Automatic fallback if one method fails
- ✅ User installation (no sudo required)
- ✅ Automatic pip upgrade after installation

## 🛠️ Service Management Commands

The full-featured script supports multiple commands:

```bash
# Start all services (default)
./start_all_services.sh start

# Stop all services
./start_all_services.sh stop

# Restart all services
./start_all_services.sh restart

# Check service status
./start_all_services.sh status

# View application logs
./start_all_services.sh logs

# Clean up logs and temporary files
./start_all_services.sh clean

# Show help
./start_all_services.sh help
```

## 🔧 What the Scripts Do

### 1. **Environment Setup**
- Creates necessary directories (`uploads`, `parsed_documents`, `job_results`, etc.)
- Sets up Python virtual environment
- Installs required dependencies from `requirements.txt`

### 2. **GROBID Service**
- Starts GROBID using Docker Compose
- Waits for GROBID to be healthy and ready
- Verifies service availability at `http://localhost:8070`

### 3. **DocuSearch Application**
- Starts the Flask application
- Runs on `http://localhost:5000`
- Logs output to `app.log`

## 🌐 Service URLs

Once started, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Web Interface** | http://localhost:5000 | Main DocuSearch UI |
| **Metrics** | http://localhost:5000/metrics | System metrics |
| **Search API** | http://localhost:5000/search?q=query | Document search |
| **Upload API** | http://localhost:5000/upload | Single file upload |
| **Bulk Upload** | http://localhost:5000/bulk_upload | Multiple file upload |
| **S3 Upload** | http://localhost:5000/bulk_upload_s3 | S3 bulk upload |
| **GROBID** | http://localhost:8070 | PDF parsing service |

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Port Already in Use**
```bash
# Check what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

#### 2. **Docker Not Running**
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

#### 3. **GROBID Not Starting**
```bash
# Check GROBID logs
docker-compose logs grobid

# Restart GROBID
docker-compose restart grobid
```

#### 4. **Python Dependencies Issues**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Manual Service Management:

#### Start Services Individually:
```bash
# 1. Start GROBID
docker-compose up -d grobid

# 2. Wait for GROBID (30 seconds)
sleep 30

# 3. Start DocuSearch
source venv/bin/activate
python3 app.py
```

#### Stop Services:
```bash
# Stop DocuSearch
pkill -f "python.*app.py"

# Stop GROBID
docker-compose down
```

## 📊 Monitoring Services

### Check Service Status:
```bash
# Using the script
./start_all_services.sh status

# Manual checks
curl http://localhost:8070/api/isalive  # GROBID
curl http://localhost:5000              # DocuSearch
```

### View Logs:
```bash
# Application logs
tail -f app.log

# GROBID logs
docker-compose logs -f grobid

# All Docker logs
docker-compose logs -f
```

## 🔄 Development Mode

For development with auto-reload:

```bash
# Start GROBID
docker-compose up -d grobid

# Start app in development mode
source venv/bin/activate
export FLASK_ENV=development
python3 app.py
```

## 🧹 Cleanup

To completely clean up:

```bash
# Stop all services
./start_all_services.sh stop

# Clean up Docker
docker-compose down -v
docker system prune -f

# Remove virtual environment
rm -rf venv

# Remove logs
rm -f app.log
```

## 📝 Notes

- **First Run**: The first startup may take longer due to Docker image downloads
- **Memory**: GROBID requires at least 4GB RAM (configured in docker-compose.yml)
- **Ports**: Ensure ports 5000 and 8070 are available
- **Logs**: Application logs are saved to `app.log`
- **Data**: Uploaded files are stored in the `uploads/` directory
- **Parsed Documents**: Processed documents are stored in `parsed_documents/`

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs: `./start_all_services.sh logs`
3. Check service status: `./start_all_services.sh status`
4. Restart services: `./start_all_services.sh restart`

For additional help, refer to the main [README.md](README.md) file.
