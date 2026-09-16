HAS_GPU := $(shell command -v nvidia-smi > /dev/null && echo 1 || echo 0)

# Black's output changes between releases, so a stale local venv can pass
# `make check_format` while CI (which installs dev-requirements.txt) fails.
# The formatter targets below assert the installed version matches this pin.
BLACK_PIN := $(shell sed -n 's/^black==//p' dev-requirements.txt)

.DEFAULT_GOAL := help

help:
	@echo "PDF Document Layout Analysis - Available Commands:"
	@echo ""
	@echo "📄 PDF Analysis with Translation (API + Gradio UI + Ollama):"
	@echo "  make start              - Auto-detects GPU, starts API, UI and translation"
	@echo "  make start_no_gpu       - Forces CPU mode, starts API, UI and translation"
	@echo "  make start_detached     - Background mode, API only (CPU)"
	@echo "  make start_detached_gpu - Background mode, API only (GPU)"
	@echo ""
	@echo "📄 Without Translation (API + Gradio UI only):"
	@echo "  make start_no_translation        - Auto-detects GPU, no Ollama"
	@echo "  make start_no_translation_no_gpu - Forces CPU mode, no Ollama"
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
	@echo "  make free_up_space            - Free up system space"
	@echo ""
	@echo "💡 Tip: 'make start' launches API (port 5060), UI (port 7860) and translation support"
	@echo "💡 GPU stack override: GPU_STACK_PROFILE=legacy|nextgen|grace make start"

start:
ifeq ($(OS), Windows_NT)
	cmd /C "if not exist models mkdir models"
else
	mkdir -p ./models
endif
ifeq ($(HAS_GPU), 1)
	@echo "NVIDIA GPU detected, starting with translation support (GPU-enabled Ollama)"
	bash ./select_gpu_stack.sh .docker.gpu.env
	@echo "Starting Ollama GPU container first..."
	docker compose --env-file .docker.gpu.env -f docker-compose-gpu.yml up -d ollama-gpu
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
	docker compose --env-file .docker.gpu.env -f docker-compose-gpu.yml up --build pdf-document-layout-analysis-gpu pdf-document-layout-analysis-gui-gpu
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
	docker compose -f docker-compose.yml up --build pdf-document-layout-analysis pdf-document-layout-analysis-gui
endif


start_no_gpu:
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
	docker compose up --build pdf-document-layout-analysis pdf-document-layout-analysis-gui

start_no_translation:
	mkdir -p ./models
ifeq ($(HAS_GPU), 1)
	@echo "NVIDIA GPU detected, using docker-compose-gpu.yml"
	bash ./select_gpu_stack.sh .docker.gpu.env
	docker compose --env-file .docker.gpu.env -f docker-compose-gpu.yml up --build pdf-document-layout-analysis-gpu pdf-document-layout-analysis-gui-gpu
else
	@echo "No NVIDIA GPU detected, using docker-compose.yml"
	docker compose -f docker-compose.yml up --build pdf-document-layout-analysis pdf-document-layout-analysis-gui
endif

start_no_translation_no_gpu:
	mkdir -p ./models
	@echo "Starting with CPU-only configuration (no translation support)"
	docker compose up --build pdf-document-layout-analysis pdf-document-layout-analysis-gui

stop:
	docker compose stop
	docker compose -f docker-compose-gpu.yml stop

start_detached:
	mkdir -p ./models
	@echo "Starting in detached mode"
	docker compose up --build -d pdf-document-layout-analysis
	@echo "Main application started in background. Check status with: docker compose ps"
	@echo "View logs with: docker compose logs -f pdf-document-layout-analysis"

start_detached_gpu:
	mkdir -p ./models
	@echo "Starting in detached mode with GPU"
	bash ./select_gpu_stack.sh .docker.gpu.env
	RESTART_IF_NO_GPU=true docker compose --env-file .docker.gpu.env -f docker-compose-gpu.yml up --build -d pdf-document-layout-analysis-gpu
	@echo "Main application started in background. Check status with: docker compose ps"
	@echo "View logs with: docker compose logs -f pdf-document-layout-analysis-gpu"

install:
	. .venv/bin/activate; pip install -Ur requirements.txt

activate:
	. .venv/bin/activate

install_venv:
	python -m venv .venv
	. .venv/bin/activate; python -m pip install --upgrade pip
	. .venv/bin/activate; python -m pip install -r dev-requirements.txt

check_black_version:
	@. .venv/bin/activate; \
	installed="$$( { command black --version 2>/dev/null || true; } | sed -n 's/^black, \([^ ]*\).*/\1/p')"; \
	if [ "$$installed" != "$(BLACK_PIN)" ]; then \
		echo "black $$installed does not match dev-requirements.txt pin $(BLACK_PIN)" >&2; \
		echo "Run 'make install_venv' to install the pinned version." >&2; \
		exit 1; \
	fi

formatter: check_black_version
	. .venv/bin/activate; command black .

check_format: check_black_version
	. .venv/bin/activate; command black . --check

test:
	. .venv/bin/activate; command cd src; command python -m pytest

remove_docker_containers:
	docker compose ps -q | xargs docker rm

remove_docker_images:
	docker compose config --images | xargs docker rmi

free_up_space:
	df -h
	sudo rm -rf /usr/share/dotnet
	sudo rm -rf /opt/ghc
	sudo rm -rf "/usr/local/share/boost"
	sudo rm -rf "$$AGENT_TOOLSDIRECTORY"
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

upgrade:
	. .venv/bin/activate; pip-upgrade

tag:
	@CURRENT_DATE=$$(date +%Y.%-m.%-d); \
	echo "Current date: $$CURRENT_DATE"; \
	LATEST_TAG=$$(git tag --list "$$CURRENT_DATE.*" --sort=-version:refname | head -n1); \
	if [ -z "$$LATEST_TAG" ]; then \
		REVISION=1; \
	else \
		REVISION=$$(echo $$LATEST_TAG | cut -d. -f4); \
		REVISION=$$((REVISION + 1)); \
	fi; \
	NEW_TAG="$$CURRENT_DATE.$$REVISION"; \
	echo "Creating new tag: $$NEW_TAG"; \
	git tag $$NEW_TAG; \
	git push --tag
