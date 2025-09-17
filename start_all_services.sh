#!/bin/bash

# DocuSearch - Complete Service Startup Script
# This script starts all required services for the DocuSearch application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_PORT=5000
GROBID_PORT=8070
GROBID_HEALTH_URL="http://localhost:${GROBID_PORT}/api/isalive"
APP_URL="http://localhost:${APP_PORT}"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $((max_attempts * 2)) seconds"
    return 1
}

# Function to check and install pip
check_and_install_pip() {
    print_status "Checking pip installation..."
    
    if ! command_exists pip3; then
        print_warning "pip3 not found. Attempting to install pip..."
        
        # Try to install pip using get-pip.py
        if [ -f "get-pip.py" ]; then
            print_status "Using local get-pip.py to install pip..."
            python3 get-pip.py --user
        else
            print_status "Downloading get-pip.py..."
            curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            if [ $? -eq 0 ]; then
                python3 get-pip.py --user
                rm get-pip.py
            else
                print_error "Failed to download get-pip.py"
                print_status "Please install pip manually:"
                print_status "  - Ubuntu/Debian: sudo apt install python3-pip"
                print_status "  - CentOS/RHEL: sudo yum install python3-pip"
                print_status "  - macOS: brew install python3"
                print_status "  - Or visit: https://pip.pypa.io/en/stable/installation/"
                exit 1
            fi
        fi
        
        # Add user bin to PATH if pip was installed with --user
        if [ -d "$HOME/.local/bin" ]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi
        
        # Verify pip installation
        if command_exists pip3; then
            print_success "pip3 installed successfully"
        else
            print_error "pip3 installation failed"
            exit 1
        fi
    else
        print_success "pip3 is already installed"
    fi
}

# Function to check Python dependencies
check_python_dependencies() {
    print_status "Checking Python dependencies..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.7 or higher."
        exit 1
    fi
    
    # Check and install pip if needed
    check_and_install_pip
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip in virtual environment
    print_status "Upgrading pip in virtual environment..."
    pip install --upgrade pip
    
    # Check if requirements are installed
    if ! python3 -c "import flask" 2>/dev/null; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        print_success "Python dependencies are already installed"
    fi
}

# Function to check and install Docker
check_and_install_docker() {
    print_status "Checking Docker installation..."
    
    if ! command_exists docker; then
        print_warning "Docker not found. Attempting to install Docker..."
        
        # Detect OS and install Docker accordingly
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux installation
            if command_exists apt-get; then
                print_status "Installing Docker using apt (Ubuntu/Debian)..."
                sudo apt-get update
                sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                sudo apt-get update
                sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            elif command_exists yum; then
                print_status "Installing Docker using yum (CentOS/RHEL)..."
                sudo yum install -y yum-utils
                sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            elif command_exists dnf; then
                print_status "Installing Docker using dnf (Fedora)..."
                sudo dnf install -y dnf-plugins-core
                sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
                sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            else
                print_error "Unsupported Linux distribution. Please install Docker manually."
                print_status "Installation instructions: https://docs.docker.com/engine/install/"
                exit 1
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS installation
            if command_exists brew; then
                print_status "Installing Docker using Homebrew (macOS)..."
                brew install --cask docker
                print_warning "Docker Desktop has been installed. Please start Docker Desktop manually."
                print_status "After starting Docker Desktop, run this script again."
                exit 0
            else
                print_error "Homebrew not found. Please install Docker Desktop manually."
                print_status "Download from: https://docs.docker.com/desktop/mac/install/"
                exit 1
            fi
        else
            print_error "Unsupported operating system. Please install Docker manually."
            print_status "Installation instructions: https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        # Start Docker service on Linux
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            print_status "Starting Docker service..."
            sudo systemctl start docker
            sudo systemctl enable docker
            
            # Add current user to docker group
            print_status "Adding current user to docker group..."
            sudo usermod -aG docker $USER
            print_warning "Please log out and log back in for docker group changes to take effect."
            print_status "Or run: newgrp docker"
        fi
        
        # Verify Docker installation
        if command_exists docker; then
            print_success "Docker installed successfully"
        else
            print_error "Docker installation failed"
            exit 1
        fi
    else
        print_success "Docker is already installed"
    fi
    
    # Check for docker-compose
    if ! command_exists docker-compose; then
        print_warning "docker-compose not found. Attempting to install..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Install docker-compose on Linux
            print_status "Installing docker-compose..."
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # Install docker-compose on macOS
            if command_exists brew; then
                brew install docker-compose
            else
                print_error "Homebrew not found. Please install docker-compose manually."
                print_status "Download from: https://github.com/docker/compose/releases"
                exit 1
            fi
        fi
        
        # Verify docker-compose installation
        if command_exists docker-compose; then
            print_success "docker-compose installed successfully"
        else
            print_error "docker-compose installation failed"
            exit 1
        fi
    else
        print_success "docker-compose is already installed"
    fi
}

# Function to start GROBID service
start_grobid() {
    print_status "Starting GROBID service..."
    
    # Check and install Docker if needed
    check_and_install_docker
    
    # Check if GROBID is already running
    if port_in_use $GROBID_PORT; then
        print_warning "GROBID appears to be already running on port $GROBID_PORT"
        if curl -f -s "$GROBID_HEALTH_URL" >/dev/null 2>&1; then
            print_success "GROBID is already running and healthy"
            return 0
        else
            print_warning "Port $GROBID_PORT is in use but GROBID is not responding. Stopping existing service..."
            docker-compose down grobid 2>/dev/null || true
        fi
    fi
    
    # Start GROBID using docker-compose
    docker-compose up -d grobid
    
    # Wait for GROBID to be ready
    if wait_for_service "$GROBID_HEALTH_URL" "GROBID"; then
        print_success "GROBID service started successfully"
        print_status "GROBID is available at: http://localhost:$GROBID_PORT"
    else
        print_error "Failed to start GROBID service"
        print_status "Check GROBID logs with: docker-compose logs grobid"
        exit 1
    fi
}

# Function to start the DocuSearch application
start_app() {
    print_status "Starting DocuSearch application..."
    
    # Check if app port is already in use
    if port_in_use $APP_PORT; then
        print_warning "Port $APP_PORT is already in use. Stopping existing application..."
        pkill -f "python.*app.py" 2>/dev/null || true
        sleep 2
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start the application in background
    print_status "Starting DocuSearch Flask application..."
    nohup python3 app.py > app.log 2>&1 &
    APP_PID=$!
    
    # Wait for the application to start
    if wait_for_service "$APP_URL" "DocuSearch Application"; then
        print_success "DocuSearch application started successfully"
        print_status "Application is available at: $APP_URL"
        print_status "Application PID: $APP_PID"
        print_status "Application logs: tail -f app.log"
    else
        print_error "Failed to start DocuSearch application"
        print_status "Check application logs: cat app.log"
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "uploads"
        "parsed_documents"
        "job_results"
        "job_metadata"
        "schemas"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Function to display service status
show_status() {
    echo
    print_status "=== DocuSearch Services Status ==="
    
    # Check GROBID
    if curl -f -s "$GROBID_HEALTH_URL" >/dev/null 2>&1; then
        print_success "GROBID: Running (http://localhost:$GROBID_PORT)"
    else
        print_error "GROBID: Not running"
    fi
    
    # Check DocuSearch App
    if curl -f -s "$APP_URL" >/dev/null 2>&1; then
        print_success "DocuSearch App: Running ($APP_URL)"
    else
        print_error "DocuSearch App: Not running"
    fi
    
    echo
    print_status "=== Quick Access ==="
    echo "🌐 Web Interface: $APP_URL"
    echo "📊 Metrics: $APP_URL/metrics"
    echo "🔍 Search API: $APP_URL/search?q=your_query"
    echo "📁 Upload API: $APP_URL/upload"
    echo "📦 Bulk Upload: $APP_URL/bulk_upload"
    echo "☁️  S3 Upload: $APP_URL/bulk_upload_s3"
    echo
}

# Function to stop all services
stop_services() {
    print_status "Stopping all DocuSearch services..."
    
    # Stop DocuSearch application
    pkill -f "python.*app.py" 2>/dev/null || true
    
    # Stop GROBID
    docker-compose down 2>/dev/null || true
    
    print_success "All services stopped"
}

# Function to show help
show_help() {
    echo "DocuSearch Service Manager"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     Start all services (default)"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  status    Show service status"
    echo "  logs      Show application logs"
    echo "  clean     Clean up logs and temporary files"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start    # Start all services"
    echo "  $0 stop     # Stop all services"
    echo "  $0 status   # Check service status"
    echo "  $0 logs     # View application logs"
}

# Main execution
main() {
    echo "🚀 DocuSearch Service Manager"
    echo "=============================="
    echo
    
    case "${1:-start}" in
        "start")
            create_directories
            check_python_dependencies
            start_grobid
            start_app
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 3
            create_directories
            check_python_dependencies
            start_grobid
            start_app
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            if [ -f "app.log" ]; then
                tail -f app.log
            else
                print_error "No application logs found"
            fi
            ;;
        "clean")
            print_status "Cleaning up logs and temporary files..."
            rm -f app.log
            docker-compose down 2>/dev/null || true
            print_success "Cleanup completed"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
