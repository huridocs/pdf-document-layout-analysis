HAS_GPU := $(shell command -v nvidia-smi > /dev/null && echo 1 || echo 0)

help:
	@echo "PDF Document Layout Analysis - Available Commands:"
	@echo ""
	@echo "📄 Standard PDF Analysis (main app only):"
	@echo "  make start              - Auto-detects GPU, starts main app only"
	@echo "  make start_no_gpu       - Forces CPU mode, starts main app only"
	@echo "  make start_detached     - Background mode, main app only (CPU)"
	@echo "  make start_detached_gpu - Background mode, main app only (GPU)"
	@echo ""
	@echo "🌐 With Translation Features (includes Ollama):"
	@echo "  make start_translation           - Auto-detects GPU, includes Ollama"
	@echo "  make start_translation_no_gpu    - Forces CPU mode, includes Ollama"
	@echo ""
	@echo "🧪 Testing & Utilities:"
	@echo "  make test              - Run Python tests"
	@echo "  make stop              - Stop all services"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make install_venv      - Create virtual environment"
	@echo "  make install           - Install dependencies"
	@echo "  make formatter         - Format code with black"
	@echo "  make check_format      - Check code formatting"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make remove_docker_containers - Remove Docker containers"
	@echo "  make remove_docker_images     - Remove Docker images"
	@echo "  make free_up_space           - Free up system space"
	@echo ""
	@echo "💡 Tip: Use 'make start' for basic PDF analysis, 'make start_translation' for translation features"

install:
	. .venv/bin/activate; pip install -Ur requirements.txt

activate:
	. .venv/bin/activate

install_venv:
	python3 -m venv .venv
	. .venv/bin/activate; python -m pip install --upgrade pip
	. .venv/bin/activate; python -m pip install -r dev-requirements.txt

formatter:
	. .venv/bin/activate; command black --line-length 125 .

check_format:
	. .venv/bin/activate; command black --line-length 125 . --check

remove_docker_containers:
	docker compose ps -q | xargs docker rm

remove_docker_images:
	docker compose config --images | xargs docker rmi

start:
ifeq ($(OS), Windows_NT)
	if not exist models mkdir models
else
	mkdir -p ./models
endif
ifeq ($(HAS_GPU), 1)
	@echo "NVIDIA GPU detected, using docker-compose-gpu.yml"
	docker compose -f docker-compose-gpu.yml up --build pdf-document-layout-analysis-gpu
else
	@echo "No NVIDIA GPU detected, using docker-compose.yml"
	docker compose -f docker-compose.yml up --build pdf-document-layout-analysis
endif


start_no_gpu:
	mkdir -p ./models
	@echo "Starting with CPU-only configuration"
	docker compose up --build pdf-document-layout-analysis

start_translation:
ifeq ($(OS), Windows_NT)
	if not exist models mkdir models
else
	mkdir -p ./models
endif
ifeq ($(HAS_GPU), 1)
	@echo "NVIDIA GPU detected, starting with translation support (GPU-enabled Ollama)"
	@echo "Starting Ollama GPU container first..."
	docker compose -f docker-compose-gpu.yml up -d ollama-gpu
	@echo "Waiting for Ollama to be healthy..."
	@timeout=60; while [ $$timeout -gt 0 ]; do \
		if docker inspect --format='{{.State.Health.Status}}' ollama-service-gpu 2>/dev/null | grep -q "healthy"; then \
			echo "Ollama GPU container is healthy!"; \
			break; \
		fi; \
		echo "Waiting for Ollama GPU container to be healthy... ($$timeout seconds remaining)"; \
		sleep 5; \
		timeout=$$((timeout-5)); \
	done
	@if ! docker inspect --format='{{.State.Health.Status}}' ollama-service-gpu 2>/dev/null | grep -q "healthy"; then \
		echo "Warning: Ollama GPU container may not be fully healthy yet, but continuing..."; \
	fi
	@echo "Starting all services with translation support..."
	docker compose -f docker-compose-gpu.yml up --build pdf-document-layout-analysis-gpu-translation
else
	@echo "No NVIDIA GPU detected, starting with translation support (CPU Ollama)"
	@echo "Starting Ollama container first..."
	docker compose -f docker-compose.yml up -d ollama
	@echo "Waiting for Ollama to be healthy..."
	@timeout=60; while [ $$timeout -gt 0 ]; do \
		if docker inspect --format='{{.State.Health.Status}}' ollama-service 2>/dev/null | grep -q "healthy"; then \
			echo "Ollama container is healthy!"; \
			break; \
		fi; \
		echo "Waiting for Ollama container to be healthy... ($$timeout seconds remaining)"; \
		sleep 5; \
		timeout=$$((timeout-5)); \
	done
	@if ! docker inspect --format='{{.State.Health.Status}}' ollama-service 2>/dev/null | grep -q "healthy"; then \
		echo "Warning: Ollama container may not be fully healthy yet, but continuing..."; \
	fi
	@echo "Starting all services with translation support..."
	docker compose -f docker-compose.yml up --build pdf-document-layout-analysis-translation
endif

start_translation_no_gpu:
	mkdir -p ./models
	@echo "Starting with CPU-only configuration and translation support"
	@echo "Starting Ollama container first..."
	docker compose up -d ollama
	@echo "Waiting for Ollama to be healthy..."
	@timeout=60; while [ $$timeout -gt 0 ]; do \
		if docker inspect --format='{{.State.Health.Status}}' ollama-service 2>/dev/null | grep -q "healthy"; then \
			echo "Ollama container is healthy!"; \
			break; \
		fi; \
		echo "Waiting for Ollama container to be healthy... ($$timeout seconds remaining)"; \
		sleep 5; \
		timeout=$$((timeout-5)); \
	done
	@if ! docker inspect --format='{{.State.Health.Status}}' ollama-service 2>/dev/null | grep -q "healthy"; then \
		echo "Warning: Ollama container may not be fully healthy yet, but continuing..."; \
	fi
	@echo "Starting all services with translation support..."
	docker compose up --build pdf-document-layout-analysis-translation

stop:
	docker compose stop
	docker compose -f docker-compose-gpu.yml stop

test:
	. .venv/bin/activate; command cd src; command python -m pytest

free_up_space:
	df -h
	sudo rm -rf /usr/share/dotnet
	sudo rm -rf /opt/ghc
	sudo rm -rf "/usr/local/share/boost"
	sudo rm -rf "$AGENT_TOOLSDIRECTORY"
	sudo apt-get remove -y '^llvm-.*' || true
	sudo apt-get remove -y 'php.*' || true
	sudo apt-get remove -y google-cloud-sdk hhvm google-chrome-stable firefox mono-devel || true
	sudo apt-get autoremove -y
	sudo apt-get clean
	sudo rm -rf /usr/share/dotnet
	sudo rm -rf /usr/local/lib/android
	sudo rm -rf /opt/hostedtoolcache/CodeQL
	sudo docker image prune --all --force
	df -h


start_detached:
	mkdir -p ./models
	@echo "Starting in detached mode"
	docker compose up --build -d pdf-document-layout-analysis
	@echo "Main application started in background. Check status with: docker compose ps"
	@echo "View logs with: docker compose logs -f pdf-document-layout-analysis"

start_detached_gpu:
	mkdir -p ./models
	@echo "Starting in detached mode with GPU"
	RESTART_IF_NO_GPU=true docker compose -f docker-compose-gpu.yml up --build -d pdf-document-layout-analysis-gpu
	@echo "Main application started in background. Check status with: docker compose ps"
	@echo "View logs with: docker compose logs -f pdf-document-layout-analysis-gpu"


upgrade:
	. .venv/bin/activate; pip-upgrade