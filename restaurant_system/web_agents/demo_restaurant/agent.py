#!/usr/bin/env python3
"""
Agente web para La Tavola Italiana
Auto-generado para adk web
"""

import sys
from pathlib import Path

# Agregar src al path para importaciones
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from restaurant.config.config_manager import ConfigManager
from restaurant.agents.food_agent import FoodSpecialistAgent

def create_agent():
    """Crear agente para La Tavola Italiana"""
    
    # Configurar el directorio de datos absoluto
    import os
    os.chdir(project_root)
    
    # Cargar configuración específica
    config_manager = ConfigManager()
    config = config_manager.load_restaurant_config("demo_restaurant")
    
    # Crear agente dinámico
    food_agent = FoodSpecialistAgent(restaurant_config=config)
    
    return food_agent.agent

# Exportar el agente
agent = create_agent()
