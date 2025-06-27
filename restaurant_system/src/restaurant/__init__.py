"""
Restaurant Multi-Agent System
Sistema multiagente para restaurante basado en Google ADK
Reorganizado siguiendo mejores prácticas de https://github.com/google/adk-python.git
"""

__version__ = "1.0.0"

# Importar agente principal para facilitar el uso
from .agents import root_agent

__all__ = ["root_agent"]
__author__ = "Restaurant AI Team"
