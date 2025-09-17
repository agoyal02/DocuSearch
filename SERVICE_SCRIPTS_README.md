# 🚀 DocuSearch Service Startup Scripts

This directory contains multiple ways to start all DocuSearch services with a single command.

## 📁 Available Scripts

### 1. **Full-Featured Scripts** (Recommended)

| Script | Platform | Description |
|--------|----------|-------------|
| `start_all_services.sh` | Linux/macOS | Complete service manager with health checks |
| `start_all_services.bat` | Windows | Windows equivalent with full features |

**Features:**
- ✅ Comprehensive error checking and validation
- ✅ Service health monitoring and status reporting
- ✅ Automatic dependency installation
- ✅ Multiple management commands (start/stop/restart/status/logs/clean)
- ✅ Colored output and progress indicators
- ✅ Port conflict detection and resolution

### 2. **Quick Start Scripts**

| Script | Platform | Description |
|--------|----------|-------------|
| `quick_start.sh` | Linux/macOS | Simple, fast startup with minimal output |

**Features:**
- ✅ Minimal output for quick startup
- ✅ Basic error handling
- ✅ Fast execution

### 3. **Makefile Commands**

| Command | Description |
|---------|-------------|
| `make start` | Start all services |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make status` | Show service status |
| `make logs` | View application logs |
| `make clean` | Clean up logs and files |
| `make dev` | Start in development mode |
| `make quick` | Quick start (minimal output) |
| `make install` | Install dependencies |
| `make test` | Run tests |
| `make backup` | Backup data directories |

### 4. **System Service** (Linux)

| File | Description |
|------|-------------|
| `docusearch.service` | Systemd service file for production deployment |

## 🎯 Quick Start Guide

### Option 1: Full-Featured (Recommended)
```bash
# Linux/macOS
./start_all_services.sh

# Windows
start_all_services.bat
```

### Option 2: Simple Quick Start
```bash
# Linux/macOS only
./quick_start.sh
```

### Option 3: Make Commands
```bash
# Install and start
make install
make start

# Or quick start
make quick
```

## 🔧 What Gets Started

### Services:
1. **GROBID Service** (Docker)
   - Port: 8070
   - Purpose: PDF parsing and metadata extraction
   - Health check: `http://localhost:8070/api/isalive`

2. **DocuSearch Application** (Flask)
   - Port: 5000
   - Purpose: Main web interface and API
   - Health check: `http://localhost:5000`

### Directories Created:
- `uploads/` - File upload storage
- `parsed_documents/` - Processed document storage
- `job_results/` - Job processing results
- `job_metadata/` - Job metadata storage
- `schemas/` - JSON schema definitions

### Environment Setup:
- Python virtual environment (`venv/`)
- Dependencies installed from `requirements.txt`
- Application logs (`app.log`)

## 🌐 Access Points

Once started, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Web Interface** | http://localhost:5000 | Main DocuSearch UI |
| **Metrics** | http://localhost:5000/metrics | System metrics |
| **Search API** | http://localhost:5000/search?q=query | Document search |
| **Upload API** | http://localhost:5000/upload | Single file upload |
| **Bulk Upload** | http://localhost:5000/bulk_upload | Multiple file upload |
| **S3 Upload** | http://localhost:5000/bulk_upload_s3 | S3 bulk upload |
| **GROBID** | http://localhost:8070 | PDF parsing service |

## 🛠️ Service Management

### Using the Full Script:
```bash
# Start all services
./start_all_services.sh start

# Stop all services
./start_all_services.sh stop

# Restart all services
./start_all_services.sh restart

# Check status
./start_all_services.sh status

# View logs
./start_all_services.sh logs

# Clean up
./start_all_services.sh clean
```

### Using Make:
```bash
# Start services
make start

# Stop services
make stop

# Check status
make status

# View logs
make logs

# Development mode
make dev
```

## 🐛 Troubleshooting

### Common Issues:

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :5000
   lsof -i :8070
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Docker Not Running**
   ```bash
   # Start Docker Desktop (macOS/Windows)
   # Or start Docker daemon (Linux)
   sudo systemctl start docker
   ```

3. **Python Dependencies Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   make install
   ```

4. **GROBID Not Starting**
   ```bash
   # Check GROBID logs
   docker-compose logs grobid
   
   # Restart GROBID
   docker-compose restart grobid
   ```

### Manual Service Management:

```bash
# Start GROBID only
docker-compose up -d grobid

# Start DocuSearch only
source venv/bin/activate
python3 app.py

# Stop all services
pkill -f "python.*app.py"
docker-compose down
```

## 📊 Monitoring

### Check Service Health:
```bash
# Using scripts
./start_all_services.sh status
make status

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

# All logs
make logs
```

## 🔄 Development Mode

For development with auto-reload:

```bash
# Using make
make dev

# Manual
docker-compose up -d grobid
sleep 30
source venv/bin/activate
export FLASK_ENV=development
python3 app.py
```

## 🧹 Cleanup

### Complete Cleanup:
```bash
# Using scripts
./start_all_services.sh clean
make clean

# Manual cleanup
pkill -f "python.*app.py"
docker-compose down -v
rm -rf venv
rm -f app.log
```

## 📝 Notes

- **First Run**: May take longer due to Docker image downloads
- **Memory**: GROBID requires at least 4GB RAM
- **Ports**: Ensure ports 5000 and 8070 are available
- **Logs**: Application logs are saved to `app.log`
- **Data**: All data is stored in the project directory

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs: `./start_all_services.sh logs` or `make logs`
3. Check status: `./start_all_services.sh status` or `make status`
4. Restart services: `./start_all_services.sh restart` or `make restart`

For additional help, refer to:
- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - Detailed startup guide
- [README.md](README.md) - Main project documentation
