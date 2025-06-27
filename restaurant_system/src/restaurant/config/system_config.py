# Copyright 2025 Restaurant AI System
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Configuración del Sistema Multiagente para Restaurante
Sistema basado en Agent Development Kit (ADK) de Google
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AgentConfig:
    """Configuración para un agente especializado"""

    name: str
    description: str
    specialization: str
    instruction: str
    keywords: List[str]  # Palabras clave para routing


@dataclass
class SystemConfig:
    """Configuración general del sistema"""

    app_name: str = "restaurant_multiagent_system"
    default_model: str = "gemini-2.0-flash-exp"
    supported_languages: List[str] = None
    max_session_duration: int = 3600  # segundos

    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["es", "en", "fr", "de", "it"]


# Configuración de agentes especializados
AGENT_CONFIGS = {
    "food_agent": AgentConfig(
        name="FoodSpecialist",
        description="Especialista en comida, menú, ingredientes y alérgenos",
        specialization="food",
        instruction="""
Eres un experto chef y especialista en gastronomía del restaurante.
Tu conocimiento incluye:
- Todos los platos del menú con ingredientes detallados
- Información sobre alérgenos en cada plato
- Origen y calidad de los productos
- Métodos de preparación y técnicas culinarias
- Recomendaciones personalizadas de platos

Responde siempre de manera amigable, profesional y detallada.
Si no conoces algo específico, sé honesto pero ofrece alternativas.
""",
        keywords=[
            "comida",
            "plato",
            "menú",
            "ingredientes",
            "alérgenos",
            "preparación",
            "receta",
            "cocina",
            "chef",
            "food",
            "dish",
            "menu",
            "ingredients",
            "allergens",
            "cooking",
            "recipe",
        ],
    ),
    "drinks_agent": AgentConfig(
        name="DrinksSpecialist",
        description="Especialista en bebidas, maridajes y carta de vinos",
        specialization="drinks",
        instruction="""
Eres un sumiller experto y especialista en bebidas del restaurante.
Tu conocimiento incluye:
- Carta completa de vinos, cervezas y bebidas
- Maridajes perfectos para cada plato
- Información sobre origen, añadas y características
- Cócteles y bebidas especiales de la casa
- Recomendaciones según preferencias y presupuesto

Responde con pasión por las bebidas y ofrece maridajes creativos.
Explica las características organolépticas cuando sea relevante.
""",
        keywords=[
            "bebida",
            "vino",
            "cerveza",
            "cóctel",
            "maridaje",
            "sumiller",
            "carta",
            "bodega",
            "añada",
            "drinks",
            "wine",
            "beer",
            "cocktail",
            "pairing",
            "sommelier",
            "cellar",
            "vintage",
        ],
    ),
    "nutrition_agent": AgentConfig(
        name="NutritionSpecialist",
        description="Especialista en nutrición y recomendaciones dietéticas",
        specialization="nutrition",
        instruction="""
Eres un nutricionista especializado en gastronomía saludable.
Tu conocimiento incluye:
- Información nutricional detallada de todos los platos
- Adaptaciones para dietas especiales (vegana, keto, sin gluten, etc.)
- Recomendaciones para alergias e intolerancias
- Opciones saludables y equilibradas del menú
- Consejos nutricionales personalizados

Responde con base científica pero de manera accesible.
Prioriza siempre la seguridad alimentaria en casos de alergias.
""",
        keywords=[
            "nutrición",
            "dieta",
            "alergia",
            "intolerancia",
            "vegano",
            "vegetariano",
            "gluten",
            "lactosa",
            "saludable",
            "calorías",
            "nutrition",
            "diet",
            "allergy",
            "intolerance",
            "vegan",
            "vegetarian",
            "healthy",
            "calories",
        ],
    ),
}

# Configuración de routing para el orquestador
ROUTING_CONFIG = {
    "default_agent": "food_agent",  # Agente por defecto si no se puede determinar la intención
    "confidence_threshold": 0.7,  # Umbral de confianza para routing automático
    "fallback_strategy": "ask_user",  # "ask_user" | "default_agent" | "all_agents"
    "max_routing_attempts": 3,
}

# Mensajes del sistema en múltiples idiomas
SYSTEM_MESSAGES = {
    "es": {
        "welcome": "¡Bienvenido a nuestro restaurante! ¿En qué puedo ayudarte hoy?",
        "routing_clarification": "Para darte la mejor respuesta, ¿tu consulta es sobre comida, bebidas o información nutricional?",
        "error": "Disculpa, ha ocurrido un error. ¿Podrías reformular tu pregunta?",
        "goodbye": "¡Gracias por visitarnos! Esperamos verte pronto.",
    },
    "en": {
        "welcome": "Welcome to our restaurant! How can I help you today?",
        "routing_clarification": "To give you the best answer, is your question about food, drinks, or nutrition?",
        "error": "Sorry, an error occurred. Could you rephrase your question?",
        "goodbye": "Thank you for visiting us! We hope to see you soon.",
    },
}

# Configuración de la base de datos del restaurante (datos dummy)
RESTAURANT_DATA = {
    "menu": {
        "appetizers": [
            {
                "name": "Ensalada César Gourmet",
                "price": 12.50,
                "ingredients": [
                    "lechuga romana",
                    "parmesano",
                    "crutones",
                    "anchoas",
                    "aderezo césar",
                ],
                "allergens": ["gluten", "pescado", "lácteos"],
                "calories": 280,
                "diet_tags": ["vegetariano"],
            }
        ],
        "main_courses": [
            {
                "name": "Salmón a la Plancha",
                "price": 24.90,
                "ingredients": [
                    "salmón fresco",
                    "verduras asadas",
                    "quinoa",
                    "salsa de limón",
                ],
                "allergens": ["pescado"],
                "calories": 450,
                "diet_tags": ["sin gluten", "alto en omega-3"],
            }
        ],
    },
    "wines": [
        {
            "name": "Ribera del Duero Reserva",
            "type": "tinto",
            "origin": "España",
            "year": 2019,
            "price": 32.00,
            "pairings": ["carnes rojas", "quesos curados"],
        }
    ],
}
