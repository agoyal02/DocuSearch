# DocuSearch Makefile
# Simple commands to manage DocuSearch services

.PHONY: help start stop restart status logs clean install test

# Default target
.DEFAULT_GOAL := help

# Help target
help: ## Show this help message
	@echo "DocuSearch Service Management"
	@echo "============================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and setup environment
	@echo "📦 Setting up DocuSearch environment..."
	@echo "🔍 Checking pip installation..."
	@if ! command -v pip3 >/dev/null 2>&1; then \
		echo "⚠️  pip3 not found. Installing pip..."; \
		if [ -f "get-pip.py" ]; then \
			python3 get-pip.py --user; \
		else \
			curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py; \
			python3 get-pip.py --user; \
			rm get-pip.py; \
		fi; \
		export PATH="$$HOME/.local/bin:$$PATH"; \
	fi
	@echo "🐳 Checking Docker installation..."
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "⚠️  Docker not found. Installing Docker..."; \
		if [[ "$$OSTYPE" == "linux-gnu"* ]]; then \
			if command -v apt-get >/dev/null 2>&1; then \
				sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release; \
				curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg; \
				echo "deb [arch=$$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; \
				sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin; \
				sudo systemctl start docker && sudo usermod -aG docker $$USER; \
			elif command -v yum >/dev/null 2>&1; then \
				sudo yum install -y yum-utils; \
				sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo; \
				sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin; \
				sudo systemctl start docker && sudo usermod -aG docker $$USER; \
			fi; \
		elif [[ "$$OSTYPE" == "darwin"* ]]; then \
			if command -v brew >/dev/null 2>&1; then \
				brew install --cask docker; \
				echo "⚠️  Docker Desktop installed. Please start it manually."; \
			fi; \
		fi; \
	fi
	@if ! command -v docker-compose >/dev/null 2>&1; then \
		echo "⚠️  docker-compose not found. Installing..."; \
		if [[ "$$OSTYPE" == "linux-gnu"* ]]; then \
			sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$$(uname -s)-$$(uname -m)" -o /usr/local/bin/docker-compose; \
			sudo chmod +x /usr/local/bin/docker-compose; \
		elif [[ "$$OSTYPE" == "darwin"* ]]; then \
			if command -v brew >/dev/null 2>&1; then \
				brew install docker-compose; \
			fi; \
		fi; \
	fi
	@python3 -m venv venv
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt
	@mkdir -p uploads parsed_documents job_results job_metadata schemas
	@echo "✅ Installation complete!"

start: ## Start all services
	@echo "🚀 Starting DocuSearch services..."
	@./start_all_services.sh start

stop: ## Stop all services
	@echo "🛑 Stopping DocuSearch services..."
	@./start_all_services.sh stop

restart: ## Restart all services
	@echo "🔄 Restarting DocuSearch services..."
	@./start_all_services.sh restart

status: ## Show service status
	@./start_all_services.sh status

logs: ## Show application logs
	@./start_all_services.sh logs

clean: ## Clean up logs and temporary files
	@echo "🧹 Cleaning up..."
	@./start_all_services.sh clean

test: ## Run basic tests
	@echo "🧪 Running tests..."
	@. venv/bin/activate && python -m pytest test_*.py -v

dev: ## Start in development mode
	@echo "🔧 Starting in development mode..."
	@docker-compose up -d grobid
	@sleep 30
	@. venv/bin/activate && FLASK_ENV=development python app.py

quick: ## Quick start (minimal output)
	@echo "⚡ Quick starting DocuSearch..."
	@./quick_start.sh

# Docker-specific targets
docker-up: ## Start only Docker services
	@echo "🐳 Starting Docker services..."
	@docker-compose up -d

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	@docker-compose down

docker-logs: ## Show Docker logs
	@docker-compose logs -f

# Maintenance targets
update: ## Update dependencies
	@echo "📥 Updating dependencies..."
	@. venv/bin/activate && pip install --upgrade -r requirements.txt

backup: ## Backup data directories
	@echo "💾 Creating backup..."
	@tar -czf docusearch_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz uploads/ parsed_documents/ job_results/ job_metadata/

restore: ## Restore from backup (usage: make restore BACKUP_FILE=backup.tar.gz)
	@echo "📤 Restoring from backup..."
	@tar -xzf $(BACKUP_FILE)
