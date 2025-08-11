from drivers.web.fastapi_app import create_app
from drivers.web.dependency_injection import setup_dependencies

controllers = setup_dependencies()

app = create_app(controllers)
