# run.ps1

param(
    [Parameter(Position=0)]
    [string]$Target = "start"
)

# Detect NVIDIA GPU
$HAS_GPU = $false
if (Get-Command "nvidia-smi" -ErrorAction SilentlyContinue) {
    $HAS_GPU = $true
}

function Start-Services {
    # Create models directory if it doesn't exist
    if (-not (Test-Path -Path ".\models")) {
        New-Item -ItemType Directory -Path ".\models" | Out-Null
    }

    if ($HAS_GPU) {
        Write-Host "NVIDIA GPU detected, starting with translation support (GPU-enabled Ollama)"
        Write-Host "Starting Ollama GPU container first..."
        docker compose -f docker-compose-gpu.yml up -d ollama-gpu

        Write-Host "Waiting for Ollama to be healthy..."
        $timeout = 60
        while ($timeout -gt 0) {
            $status = docker inspect --format='{{.State.Health.Status}}' ollama-service-gpu 2>$null
            if ($status -eq "healthy") {
                Write-Host "Ollama GPU container is healthy!"
                break
            }
            Write-Host "Waiting for Ollama GPU container to be healthy... ($timeout seconds remaining)"
            Start-Sleep -Seconds 5
            $timeout -= 5
        }

        $status = docker inspect --format='{{.State.Health.Status}}' ollama-service-gpu 2>$null
        if ($status -ne "healthy") {
            Write-Host "Warning: Ollama GPU container may not be fully healthy yet, but continuing..."
        }

        Write-Host "Starting all services with translation support..."
        docker compose -f docker-compose-gpu.yml up --build pdf-document-layout-analysis-gpu pdf-document-layout-analysis-gui-gpu
    } else {
        Write-Host "No NVIDIA GPU detected, starting with translation support (CPU Ollama)"
        Write-Host "Starting Ollama container first..."
        docker compose -f docker-compose.yml up -d ollama

        Write-Host "Waiting for Ollama to be healthy..."
        $timeout = 60
        while ($timeout -gt 0) {
            $status = docker inspect --format='{{.State.Health.Status}}' ollama-service 2>$null
            if ($status -eq "healthy") {
                Write-Host "Ollama container is healthy!"
                break
            }
            Write-Host "Waiting for Ollama container to be healthy... ($timeout seconds remaining)"
            Start-Sleep -Seconds 5
            $timeout -= 5
        }

        $status = docker inspect --format='{{.State.Health.Status}}' ollama-service 2>$null
        if ($status -ne "healthy") {
            Write-Host "Warning: Ollama container may not be fully healthy yet, but continuing..."
        }

        Write-Host "Starting all services with translation support..."
        docker compose -f docker-compose.yml up --build pdf-document-layout-analysis pdf-document-layout-analysis-gui
    }
}

function Start-NoGpu {
    if (-not (Test-Path -Path ".\models")) {
        New-Item -ItemType Directory -Path ".\models" | Out-Null
    }

    Write-Host "Starting with CPU-only configuration and translation support"
    Write-Host "Starting Ollama container first..."
    docker compose up -d ollama

    Write-Host "Waiting for Ollama to be healthy..."
    $timeout = 60
    while ($timeout -gt 0) {
        $status = docker inspect --format='{{.State.Health.Status}}' ollama-service 2>$null
        if ($status -eq "healthy") {
            Write-Host "Ollama container is healthy!"
            break
        }
        Write-Host "Waiting for Ollama container to be healthy... ($timeout seconds remaining)"
        Start-Sleep -Seconds 5
        $timeout -= 5
    }

    $status = docker inspect --format='{{.State.Health.Status}}' ollama-service 2>$null
    if ($status -ne "healthy") {
        Write-Host "Warning: Ollama container may not be fully healthy yet, but continuing..."
    }

    Write-Host "Starting all services with translation support..."
    docker compose up --build pdf-document-layout-analysis pdf-document-layout-analysis-gui
}

function Stop-Services {
    docker compose stop
    docker compose -f docker-compose-gpu.yml stop
}

function Start-Detached {
    if (-not (Test-Path -Path ".\models")) {
        New-Item -ItemType Directory -Path ".\models" | Out-Null
    }

    Write-Host "Starting in detached mode"
    docker compose up --build -d pdf-document-layout-analysis
    Write-Host "Main application started in background. Check status with: docker compose ps"
    Write-Host "View logs with: docker compose logs -f pdf-document-layout-analysis"
}

function Start-DetachedGpu {
    if (-not (Test-Path -Path ".\models")) {
        New-Item -ItemType Directory -Path ".\models" | Out-Null
    }

    Write-Host "Starting in detached mode with GPU"
    $env:RESTART_IF_NO_GPU = "true"
    docker compose -f docker-compose-gpu.yml up --build -d pdf-document-layout-analysis-gpu
    Write-Host "Main application started in background. Check status with: docker compose ps"
    Write-Host "View logs with: docker compose logs -f pdf-document-layout-analysis-gpu"
}

# Target dispatcher
switch ($Target) {
    "start"               { Start-Services }
    "start_no_gpu"        { Start-NoGpu }
    "stop"                { Stop-Services }
    "start_detached"      { Start-Detached }
    "start_detached_gpu"  { Start-DetachedGpu }
    default {
        Write-Host "Unknown target: $Target"
        Write-Host "Available targets: start, start_no_gpu, stop, start_detached, start_detached_gpu"
        exit 1
    }
}