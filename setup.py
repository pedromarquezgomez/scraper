"""
Setup configuration for Restaurant Multi-Agent System
Following ADK best practices from https://github.com/google/adk-python.git
"""

from setuptools import setup, find_packages

setup(
    name="restaurant-multiagent-system",
    version="1.0.0",
    description="Sistema multiagente para restaurante basado en Google ADK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pedro",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "google-adk>=1.5.0",
        "google-genai",
        "fastapi",
        "uvicorn",
        "pydantic",
        "pytest",
        "pytest-cov",
        "black",
        "isort",
        "mypy",
        "flake8",
    ],
    extras_require={
        "dev": [
            "pytest-asyncio",
            "pytest-mock",
            "coverage[toml]",
        ],
        "deployment": [
            "docker",
            "kubernetes",
        ],
    },
    entry_points={
        "console_scripts": [
            "restaurant-cli=restaurant.cli:main",
            "restaurant-web=restaurant.web_config:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: FastAPI",
    ],
) 