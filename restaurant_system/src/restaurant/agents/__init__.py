# Agents module

# Importar el root_agent para que ADK web pueda encontrarlo
from .root_agent import root_agent

# Importar sistema moderno
try:
    from .modern_system import (
        restaurant_system,
        create_modern_restaurant_system,
        create_food_specialist,
        create_coordinator_agent
    )
    # Sistema moderno disponible
    modern_available = True
except ImportError:
    # Fallback a sistema anterior si hay problemas
    modern_available = False

# Exponer agentes originales para compatibilidad
from .food_agent import FoodSpecialistAgent

__all__ = [
    "root_agent",
    "FoodSpecialistAgent"
]

# Agregar exports del sistema moderno si está disponible
if modern_available:
    __all__.extend([
        "restaurant_system",
        "create_modern_restaurant_system",
        "create_food_specialist", 
        "create_coordinator_agent"
    ])
