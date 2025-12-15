HAS_GPU := $(shell command -v nvidia-smi > /dev/null && echo 1 || echo 0)

start:
ifeq ($(OS), Windows_NT)
	cmd /C "if not exist models mkdir models"
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
	docker compose -f docker-compose-gpu.yml up --build pdf-document-layout-analysis-gpu pdf-document-layout-analysis-gui-gpu
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
	RESTART_IF_NO_GPU=true docker compose -f docker-compose-gpu.yml up --build -d pdf-document-layout-analysis-gpu
	@echo "Main application started in background. Check status with: docker compose ps"
	@echo "View logs with: docker compose logs -f pdf-document-layout-analysis-gpu"
