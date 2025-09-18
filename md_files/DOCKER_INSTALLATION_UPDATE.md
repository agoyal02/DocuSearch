# 🐳 Docker Installation Update

This document describes the Docker installation features added to all DocuSearch startup scripts.

## 📋 What's New

All startup scripts now include **automatic Docker and docker-compose installation** if they're missing:

### ✅ **Updated Scripts with Docker Installation**

1. **`start_all_services.sh`** (Linux/macOS)
   - ✅ Checks for Docker installation
   - ✅ Installs Docker using package managers (apt, yum, dnf, brew)
   - ✅ Starts and enables Docker service
   - ✅ Adds user to docker group
   - ✅ Installs docker-compose if missing
   - ✅ Provides fallback installation instructions

2. **`start_all_services.bat`** (Windows)
   - ✅ Checks for Docker Desktop installation
   - ✅ Installs Docker Desktop using Chocolatey or winget
   - ✅ Installs docker-compose via pip
   - ✅ Provides fallback installation instructions

3. **`quick_start.sh`** (Linux/macOS)
   - ✅ Quick Docker installation check
   - ✅ Installs Docker and docker-compose if missing
   - ✅ Starts Docker service

4. **`Makefile`**
   - ✅ Includes Docker installation in `make install`
   - ✅ Installs Docker and docker-compose if missing
   - ✅ Configures Docker service

### 🆕 **New Standalone Docker Installation Scripts**

5. **`install_docker.sh`** (Linux/macOS)
   - ✅ Comprehensive Docker installation script
   - ✅ Multiple installation methods (package managers)
   - ✅ Automatic fallback if one method fails
   - ✅ Docker service configuration
   - ✅ User group management

6. **`install_docker.bat`** (Windows)
   - ✅ Windows Docker Desktop installation script
   - ✅ Uses Chocolatey or winget for installation
   - ✅ Installs docker-compose via pip

## 🔧 **Installation Methods**

The scripts try multiple methods in order:

### **Linux:**
1. **apt** (Ubuntu/Debian) - Official Docker repository
2. **yum** (CentOS/RHEL) - Official Docker repository
3. **dnf** (Fedora) - Official Docker repository
4. **Manual instructions** - If automatic installation fails

### **macOS:**
1. **Homebrew** - `brew install --cask docker`
2. **Manual instructions** - If Homebrew not available

### **Windows:**
1. **Chocolatey** - `choco install docker-desktop`
2. **winget** - `winget install Docker.DockerDesktop`
3. **Manual instructions** - If package managers not available

## 🚀 **Usage Examples**

### **Automatic Installation (Recommended)**
```bash
# All startup scripts now include Docker installation
./start_all_services.sh
./quick_start.sh
make install
```

### **Standalone Docker Installation**
```bash
# Linux/macOS
./install_docker.sh

# Windows
install_docker.bat
```

### **Manual Installation (Fallback)**
If automatic installation fails, the scripts provide manual instructions:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

**CentOS/RHEL:**
```bash
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

**macOS:**
```bash
brew install --cask docker
```

**Windows:**
Download from: https://www.docker.com/products/docker-desktop

## 🔍 **What Gets Installed**

### **Docker Engine:**
- **Docker CE** - Community Edition
- **Docker CLI** - Command line interface
- **containerd** - Container runtime
- **Docker Compose Plugin** - Built-in compose support

### **Docker Compose:**
- **Standalone docker-compose** - If plugin not available
- **Latest version** - From official releases

### **Service Configuration:**
- **Docker service** - Started and enabled
- **User permissions** - Added to docker group
- **Auto-start** - Enabled on boot

## 🛠️ **Technical Details**

### **Installation Process:**
1. **Check** if Docker is already installed
2. **Detect OS** and package manager
3. **Add Docker repository** (Linux)
4. **Install Docker** using package manager
5. **Start Docker service** (Linux)
6. **Add user to docker group** (Linux)
7. **Install docker-compose** if missing
8. **Verify** installation success

### **Error Handling:**
- ✅ Graceful fallback between methods
- ✅ Clear error messages with solutions
- ✅ Manual installation instructions
- ✅ Exit codes for automation

### **Platform Support:**
- ✅ **Linux** (Ubuntu, CentOS, RHEL, Debian, Fedora)
- ✅ **macOS** (with Homebrew or without)
- ✅ **Windows** (10, 11)
- ✅ **Docker Engine** (all supported versions)

## 📊 **Benefits**

1. **Zero Configuration** - Works out of the box
2. **No Manual Setup** - Automatic installation and configuration
3. **Multiple Fallbacks** - Robust installation process
4. **Cross-Platform** - Works on all major operating systems
5. **Service Management** - Automatic service startup and configuration
6. **User Permissions** - Automatic docker group management

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **Permission Issues (Linux)**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Docker Service Not Running (Linux)**
   ```bash
   # Start Docker service
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Docker Desktop Not Running (Windows/macOS)**
   - Start Docker Desktop application manually
   - Wait for it to fully initialize

4. **Network Issues**
   ```bash
   # Check Docker connectivity
   docker run --rm hello-world
   ```

### **Manual Verification:**
```bash
# Check Docker installation
docker --version
docker-compose --version

# Test Docker functionality
docker run --rm hello-world

# Check Docker service status (Linux)
sudo systemctl status docker
```

## 📝 **Notes**

- **First Run**: May take longer due to Docker installation
- **Network Required**: For downloading Docker packages
- **Admin Required**: Docker installation requires sudo/admin privileges
- **Service Restart**: May require logout/login for group changes
- **Docker Desktop**: On Windows/macOS, requires manual start after installation

## 🆘 **Support**

If you encounter issues:

1. **Check Prerequisites**: Ensure you have admin/sudo privileges
2. **Check Network**: Ensure internet connection is available
3. **Check Permissions**: Ensure proper user group membership
4. **Manual Installation**: Use provided manual installation instructions
5. **Check Logs**: Review script output for specific error messages

## 🎯 **Complete Automation**

With these updates, the DocuSearch startup scripts now provide **complete automation**:

1. **Python 3.7+** - Check and install if missing
2. **pip** - Check and install if missing
3. **Docker** - Check and install if missing
4. **docker-compose** - Check and install if missing
5. **Python dependencies** - Install from requirements.txt
6. **GROBID service** - Start via Docker
7. **DocuSearch application** - Start Flask app

The application can now be started with a **single command** on any supported platform!
