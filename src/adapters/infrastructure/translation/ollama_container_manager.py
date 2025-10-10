import os
import time
import requests
import json
from typing import Optional, Any
from configuration import service_logger


class OllamaContainerManager:

    def __init__(self, ollama_host: str = None):
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.api_base_url = f"{self.ollama_host}/api"
        self.timeout = 600
        self.max_retries = 5

    def is_ollama_available(self) -> bool:
        try:
            response = requests.get(f"{self.api_base_url}/tags", timeout=10)
            return response.status_code == 200
        except Exception as e:
            service_logger.debug(f"Ollama availability check failed: {e}")
            return False

    def ensure_model_available(self, model_name: str) -> bool:
        try:
            if self._is_model_available(model_name):
                service_logger.info(f"\033[92mModel '{model_name}' is available\033[0m")
                return True

            service_logger.info(f"\033[93mModel '{model_name}' not found. Downloading...\033[0m")
            return self._download_model(model_name)

        except Exception as e:
            service_logger.error(f"Error ensuring model availability: {e}")
            return False

    def _is_model_available(self, model_name: str) -> bool:
        try:
            response = requests.get(f"{self.api_base_url}/tags", timeout=10)
            if response.status_code != 200:
                return False

            models_data = response.json()
            available_models = [model["name"] for model in models_data.get("models", [])]

            model_variants = {model_name, f"{model_name}:latest", model_name.split(":")[0]}
            return any(variant in available_models for variant in model_variants)

        except Exception as e:
            service_logger.error(f"Error checking model availability: {e}")
            return False

    def _download_model(self, model_name: str) -> bool:
        try:
            response = requests.post(f"{self.api_base_url}/pull", json={"name": model_name}, stream=True)

            if response.status_code != 200:
                service_logger.error(f"Failed to start model download: {response.text}")
                return False

            for idx, line in enumerate(response.iter_lines()):
                if line:
                    try:
                        data = json.loads(line)
                        if "status" in data and idx % 100 == 0:
                            service_logger.info(f"Model download: {data['status']}")
                        if data.get("status") == "success":
                            service_logger.info(f"Model '{model_name}' downloaded successfully")
                            return True
                    except json.JSONDecodeError:
                        continue

            return True

        except Exception as e:
            service_logger.error(f"Error downloading model '{model_name}': {e}")
            return False

    def chat_with_timeout(
        self, model: str, messages: list[dict], source_markup: str, timeout: Optional[int] = None
    ) -> dict[str, Any] | str:
        timeout = timeout or self.timeout

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    service_logger.info(f"Retrying chat request (attempt {attempt + 1}/{self.max_retries + 1})")
                    time.sleep(10)

                return self._make_chat_request(
                    model,
                    messages,
                    timeout,
                )

            except requests.exceptions.Timeout:
                service_logger.warning(f"Chat request timed out after {timeout} seconds (attempt {attempt})")
                if attempt < self.max_retries:
                    continue
                else:
                    service_logger.error(f"Chat request failed after {self.max_retries} attempts due to timeout")
                    return source_markup

            except Exception as e:
                service_logger.error(f"Chat request failed (attempt {attempt}): {e}")
                if attempt < self.max_retries:
                    continue
                else:
                    service_logger.error(f"Chat request failed after {self.max_retries} attempts")
                    return source_markup

        return source_markup

    def _make_chat_request(self, model: str, messages: list, timeout: int) -> dict[str, Any]:
        payload = {"model": model, "messages": messages, "stream": False}

        response = requests.post(f"{self.api_base_url}/chat", json=payload, timeout=timeout)

        if response.status_code != 200:
            raise Exception(f"Chat request failed with status {response.status_code}: {response.text}")

        return response.json()

    def ensure_service_ready(self, model_name: str) -> bool:
        try:
            if not self.is_ollama_available():
                service_logger.error("Ollama service is not available. Make sure the Ollama container is running.")
                return False

            return self.ensure_model_available(model_name)

        except Exception as e:
            service_logger.error(f"Error ensuring service readiness: {e}")
            return False
