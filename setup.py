from pathlib import Path

from setuptools import setup


requirements_path = Path("requirements.txt")
dependency_links = [r for r in requirements_path.read_text().splitlines() if r.startswith("git+")]
requirements = [r for r in requirements_path.read_text().splitlines() if not r.startswith("git+")]

PROJECT_NAME = "pdf-document-layout-analysis"

setup(
    name=PROJECT_NAME,
    packages=["pdf_tokens_type_trainer", "pdf_features", "pdf_token_type_labels", "fast_trainer"],
    package_dir={"": "src"},
    version="0.10",
    url="https://github.com/huridocs/pdf-document-layout-analysis",
    author="HURIDOCS",
    description="This tool is for PDF document layout analysis",
    install_requires=requirements,
    setup_requires=requirements,
    dependency_links=dependency_links,
)
