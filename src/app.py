from configuration import RESTART_IF_NO_GPU
from drivers.web.fastapi_app import create_app
from drivers.web.dependency_injection import setup_dependencies
import torch

if RESTART_IF_NO_GPU:
    if not torch.cuda.is_available():
        raise RuntimeError("No GPU available. Restarting the service is required.")

controllers = setup_dependencies()

app = create_app(controllers)
