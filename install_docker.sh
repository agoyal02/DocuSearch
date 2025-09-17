#!/bin/bash

# DocuSearch - Docker Installation Script
# This script installs Docker and docker-compose if they're not already available

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🐳 DocuSearch Docker Installation"
echo "=================================="
echo

# Check if Docker is already installed
if command_exists docker; then
    print_success "Docker is already installed: $(docker --version)"
    DOCKER_INSTALLED=true
else
    print_warning "Docker not found. Installing Docker..."
    DOCKER_INSTALLED=false
fi

# Check if docker-compose is already installed
if command_exists docker-compose; then
    print_success "docker-compose is already installed: $(docker-compose --version)"
    COMPOSE_INSTALLED=true
else
    print_warning "docker-compose not found. Installing docker-compose..."
    COMPOSE_INSTALLED=false
fi

# Install Docker if needed
if [ "$DOCKER_INSTALLED" = false ]; then
    print_status "Installing Docker..."
    
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
            print_status "After starting Docker Desktop, run this script again to install docker-compose."
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
        print_success "Docker installed successfully: $(docker --version)"
    else
        print_error "Docker installation failed"
        exit 1
    fi
fi

# Install docker-compose if needed
if [ "$COMPOSE_INSTALLED" = false ]; then
    print_status "Installing docker-compose..."
    
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
        print_success "docker-compose installed successfully: $(docker-compose --version)"
    else
        print_error "docker-compose installation failed"
        exit 1
    fi
fi

# Test Docker installation
print_status "Testing Docker installation..."
if docker run --rm hello-world >/dev/null 2>&1; then
    print_success "Docker is working correctly!"
else
    print_warning "Docker installation may need additional configuration"
    print_status "Try running: newgrp docker (if on Linux)"
fi

echo
print_success "🎉 Docker installation completed successfully!"
print_status "You can now run the DocuSearch startup scripts."

# Show Docker status
echo
print_status "=== Docker Status ==="
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker-compose --version)"
echo "Docker service status: $(systemctl is-active docker 2>/dev/null || echo 'N/A (not systemd)')"
