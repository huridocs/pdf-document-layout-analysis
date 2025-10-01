import subprocess
import time
from configuration import service_logger

OLLAMA_NOT_RUNNING_MSG = "could not connect to ollama server"


def is_ollama_running():
    try:
        result = subprocess.run(["ollama", "ls"], capture_output=True, text=True)
        msg = result.stderr.lower() + result.stdout.lower()
        return OLLAMA_NOT_RUNNING_MSG not in msg and result.returncode == 0
    except FileNotFoundError:
        service_logger.error("Ollama is not installed or not in PATH.")
        return False


def start_ollama():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        service_logger.info("Starting Ollama server...")
        time.sleep(5)
        return True
    except Exception as e:
        service_logger.error(f"Failed to start Ollama server: {e}")
        return False


def model_name_variants(name):
    base = name.split(":")[0]
    return {base, f"{base}:latest", name}


def ensure_ollama_model(model_name):
    if not is_ollama_running():
        service_logger.info("Ollama server is not running. Attempting to start it...")
        if not start_ollama():
            service_logger.error("Could not start Ollama server. Exiting.")
            return False
        for _ in range(5):
            if is_ollama_running():
                break
            time.sleep(2)
        else:
            service_logger.error("Ollama server did not start in time.")
            return False

    try:
        result = subprocess.run(["ollama", "ls"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        service_logger.error(f"Error running 'ollama ls': {e}")
        return False

    model_lines = [line.split()[0] for line in result.stdout.splitlines() if line and not line.startswith("NAME")]
    available_models = set(model_lines)
    variants = model_name_variants(model_name)

    if available_models & variants:
        service_logger.info(f"Model '{model_name}' already exists in Ollama.")
        return True

    service_logger.info(f"Model '{model_name}' not found. Pulling...")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        service_logger.info(f"Model '{model_name}' pulled successfully.")
        return True
    except subprocess.CalledProcessError as e:
        service_logger.error(f"Failed to pull model '{model_name}': {e}")
        return False
