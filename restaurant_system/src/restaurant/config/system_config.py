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

# Configuración de la base de datos del restaurante - CARTA COMPLETA
RESTAURANT_DATA = {
    "menu": {
        "entrantes": [
            {
                "id": "ent01",
                "name": "Pane all'aglio",
                "category": "entrantes",
                "description": "Nuestra masa de pizza al horno con ajo, mantequilla y mozzarella Fiordilatte.",
                "price": 8.90,
                "ingredients": ["masa de pizza", "ajo", "mantequilla", "mozzarella"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "ent02",
                "name": "Pane al tartufo",
                "category": "entrantes",
                "description": "Nuestra masa de pizza al horno con mozzarella Fiordilatte y salsa de trufa blanca.",
                "price": 9.90,
                "ingredients": ["masa de pizza", "mozzarella", "salsa de trufa blanca"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "ent03",
                "name": "Bruschetta fatta in casa",
                "category": "entrantes",
                "description": "Nuestra masa de pizza al horno, con tomate natural, aceite de oliva, albahaca, ajo y orégano.",
                "price": 8.90,
                "ingredients": ["masa de pizza", "tomate natural", "aceite de oliva", "albahaca", "ajo", "orégano"],
                "allergens": ["gluten"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "ent04",
                "name": "Provoleta classica",
                "category": "entrantes",
                "description": "Queso Provola fundido al horno, con base de tomate, orégano y tostas.",
                "price": 9.50,
                "ingredients": ["queso provola", "tomate", "orégano", "tostas"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "ent05",
                "name": "Carpaccio di Manzo",
                "category": "entrantes",
                "description": "Finas lonchas de ternera, parmesano, pimienta negra, aceite de oliva virgen extra, rúcula, pistachos crujientes y vinagreta suave de limón.",
                "price": 14.90,
                "ingredients": ["ternera", "parmesano", "rúcula", "pistachos", "vinagreta de limón"],
                "allergens": ["lactosa", "frutos secos"],
                "diet_tags": []
            },
            {
                "id": "ent06",
                "name": "Vitello Tonnato",
                "category": "entrantes",
                "description": "Ternera asada a baja temperatura, con salsa mayonesa de alcaparras anchoas y atún.",
                "price": 14.50,
                "ingredients": ["ternera asada", "mayonesa", "alcaparras", "anchoas", "atún"],
                "allergens": ["huevo", "pescado"],
                "diet_tags": []
            }
        ],
        "insalate": [
            {
                "id": "ins01",
                "name": "Mixta di Carciofi",
                "category": "insalate",
                "description": "Mix de lechugas, tomatitos Cherry, cebolla, tomatitos secos, alcachofitas italianas y aceitunas Gaeta, aliñada con vinagreta de mostaza y miel.",
                "price": 11.50,
                "ingredients": ["mix de lechugas", "tomate cherry", "cebolla", "tomate seco", "alcachofas", "aceitunas gaeta", "vinagreta de mostaza y miel"],
                "allergens": ["mostaza"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "ins02",
                "name": "Caprese",
                "category": "insalate",
                "description": "Milhojas de tomate de campo fresco, rúcula, mozzarella, pesto de albahaca y vinagre de Módena.",
                "price": 12.50,
                "ingredients": ["tomate", "rúcula", "mozzarella", "pesto de albahaca", "vinagre de módena"],
                "allergens": ["lactosa", "frutos secos"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "ins03",
                "name": "César",
                "category": "insalate",
                "description": "Lechuga romana, crutones, bacón, pollo, queso Parmesano y nuestra salsa César casera.",
                "price": 13.50,
                "ingredients": ["lechuga romana", "crutones", "bacón", "pollo", "parmesano", "salsa césar"],
                "allergens": ["gluten", "huevo", "pescado", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "ins04",
                "name": "Burrata fresca",
                "category": "insalate",
                "description": "Rúcula, tomatitos secos, tomatitos Cherry, Prosciutto di Parma, pan de Carasatu, vinagreta de Módena y pesto de albahaca.",
                "price": 15.50,
                "ingredients": ["burrata", "rúcula", "tomate seco", "tomate cherry", "prosciutto di parma", "pan de carasatu", "pesto"],
                "allergens": ["gluten", "lactosa", "frutos secos"],
                "diet_tags": []
            }
        ],
        "paste": [
            {
                "id": "pas01",
                "name": "Spaghetti Bolognese",
                "category": "paste",
                "description": "Salsa boloñesa casera con carne de ternera, hecha con tomate, zanahoria, apio y cebolla.",
                "price": 13.90,
                "ingredients": ["spaghetti", "carne de ternera", "tomate", "zanahoria", "apio", "cebolla"],
                "allergens": ["gluten", "lactosa", "apio"],
                "diet_tags": []
            },
            {
                "id": "pas02",
                "name": "Linguine al Pesto",
                "category": "paste",
                "description": "Salsa pesto casera con albahaca fresca, aceite de oliva, piñones y queso Parmesano.",
                "price": 14.50,
                "ingredients": ["linguine", "albahaca", "aceite de oliva", "piñones", "parmesano"],
                "allergens": ["gluten", "lactosa", "frutos secos"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "pas03",
                "name": "Spaghetti Carbonara originale",
                "category": "paste",
                "description": "Receta original con Guanciale, yema de huevo, queso Pecorino Romano y pimienta negra.",
                "price": 14.90,
                "ingredients": ["spaghetti", "guanciale", "yema de huevo", "queso pecorino"],
                "allergens": ["gluten", "huevo", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "pas04",
                "name": "Rigatoni Amatriciana",
                "category": "paste",
                "description": "Salsa casera con tomate, Guanciale y queso Pecorino romano DOP.",
                "price": 14.90,
                "ingredients": ["rigatoni", "tomate", "guanciale", "queso pecorino"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "pas05",
                "name": "Pappardelle al tartufo",
                "category": "paste",
                "description": "Mix de setas y Boletus (Funghi Porcini), champiñones frescos, nata y crema de trufa.",
                "price": 15.90,
                "ingredients": ["pappardelle", "setas", "boletus", "champiñones", "nata", "crema de trufa"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "pas06",
                "name": "Tagliatelle Gamberi al Pil Pil",
                "category": "paste",
                "description": "Gambas salteadas al Pil Pil con ajo, Pomodorini, aceite de oliva virgen extra y guindillas.",
                "price": 15.90,
                "ingredients": ["tagliatelle", "gambas", "ajo", "pomodorini", "guindilla"],
                "allergens": ["gluten", "crustaceos"],
                "diet_tags": ["picante"]
            },
            {
                "id": "pas07",
                "name": "Spaghetti Nere ai Frutti di Mare",
                "category": "paste",
                "description": "Pasta negra con tinta de calamar, almejas, gambas, calamares, mejillones y tomate fresco.",
                "price": 16.90,
                "ingredients": ["spaghetti nero", "almejas", "gambas", "calamares", "mejillones", "tomate"],
                "allergens": ["gluten", "crustaceos", "pescado", "moluscos"],
                "diet_tags": []
            },
            {
                "id": "pas08",
                "name": "Bucatini a la Putanesca",
                "category": "paste",
                "description": "Salsa de tomate, anchoas, alcaparras, aceitunas negras Gaeta y tomate seco.",
                "price": 14.90,
                "ingredients": ["bucatini", "salsa de tomate", "anchoas", "alcaparras", "aceitunas gaeta"],
                "allergens": ["gluten", "pescado"],
                "diet_tags": []
            }
        ],
        "pasta_gratinada": [
            {
                "id": "pgr01",
                "name": "Rigatoni Bolognese al Forno",
                "category": "pasta_gratinada",
                "description": "Salsa boloñesa casera con bechamel, gratinados al horno con queso Parmesano.",
                "price": 15.90,
                "ingredients": ["rigatoni", "salsa boloñesa", "bechamel", "parmesano"],
                "allergens": ["gluten", "lactosa", "apio"],
                "diet_tags": []
            },
            {
                "id": "pgr02",
                "name": "Lasagna di Carne",
                "category": "pasta_gratinada",
                "description": "Receta original con salsa boloñesa, mozzarella y bechamel, gratinada con Parmesano.",
                "price": 15.90,
                "ingredients": ["pasta de lasaña", "salsa boloñesa", "mozzarella", "bechamel", "parmesano"],
                "allergens": ["gluten", "huevo", "lactosa", "apio"],
                "diet_tags": []
            },
            {
                "id": "pgr03",
                "name": "Lasagna di Verdure",
                "category": "pasta_gratinada",
                "description": "Selección de verduras de temporada, tomate, mozzarella y bechamel, gratinada con Parmesano.",
                "price": 14.90,
                "ingredients": ["pasta de lasaña", "verduras de temporada", "tomate", "mozzarella", "bechamel", "parmesano"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            }
        ],
        "pasta_ripiena": [
            {
                "id": "prl01",
                "name": "Raviolis de Pesto",
                "category": "pasta_ripiena",
                "description": "Raviolis con salsa de pesto, tomates, ajo, aceite de oliva, albahaca y piñones.",
                "price": 14.90,
                "ingredients": ["ravioli", "pesto", "tomates", "ajo", "albahaca", "piñones"],
                "allergens": ["gluten", "huevo", "lactosa", "frutos secos"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "prl02",
                "name": "Tortellini del Mar",
                "category": "pasta_ripiena",
                "description": "Rellenos de gambas y vieras, con reducción casera de caldo de marisco.",
                "price": 15.90,
                "ingredients": ["tortellini", "gambas", "vieiras", "caldo de marisco"],
                "allergens": ["gluten", "crustaceos", "huevo", "pescado", "lactosa", "moluscos"],
                "diet_tags": []
            },
            {
                "id": "prl03",
                "name": "Fagotti",
                "category": "pasta_ripiena",
                "description": "Saquitos rellenos de pera con una salsa de nata, gorgonzola, nueces salteadas y queso Pecorino.",
                "price": 14.90,
                "ingredients": ["fagotti", "pera", "nata", "gorgonzola", "nueces", "pecorino"],
                "allergens": ["gluten", "huevo", "lactosa", "frutos secos"],
                "diet_tags": ["vegetariano"]
            }
        ],
        "pizze": [
            {
                "id": "piz01",
                "name": "Margherita",
                "category": "pizze",
                "description": "Tomate con albahaca, Mozzarella Fiordilatte y orégano.",
                "price": 9.90,
                "ingredients": ["tomate", "albahaca", "mozzarella fiordilatte", "orégano"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "piz02",
                "name": "Prosciutto",
                "category": "pizze",
                "description": "Tomate, Mozzarella Fiordilatte y jamón cocido.",
                "price": 11.50,
                "ingredients": ["tomate", "mozzarella fiordilatte", "jamón cocido"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz03",
                "name": "Prosciutto e Funghi",
                "category": "pizze",
                "description": "Tomate, Mozzarella Fiordilatte, jamón cocido y champiñón.",
                "price": 12.90,
                "ingredients": ["tomate", "mozzarella fiordilatte", "jamón cocido", "champiñón"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz04",
                "name": "Hawaiana",
                "category": "pizze",
                "description": "Tomate, Mozzarella Fiordilatte, jamón cocido y piña natural.",
                "price": 13.90,
                "ingredients": ["tomate", "mozzarella fiordilatte", "jamón cocido", "piña"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz05",
                "name": "Carbonara",
                "category": "pizze",
                "description": "Base de nata, Mozzarella, bacón, champiñones y Parmesano.",
                "price": 13.50,
                "ingredients": ["nata", "mozzarella", "bacón", "champiñones", "parmesano"],
                "allergens": ["gluten", "huevo", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz06",
                "name": "Diavola",
                "category": "pizze",
                "description": "Tomate, Mozzarella Fiordilatte y pepperoni (salami picante).",
                "price": 13.90,
                "ingredients": ["tomate", "mozzarella fiordilatte", "pepperoni"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["picante"]
            },
            {
                "id": "piz07",
                "name": "5 Formaggi",
                "category": "pizze",
                "description": "Base blanca de Mozzarella, Gorgonzola, Scamorza, Parmesano y queso azul.",
                "price": 13.90,
                "ingredients": ["mozzarella", "gorgonzola", "scamorza", "parmesano", "queso azul"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "piz08",
                "name": "4 Stagioni",
                "category": "pizze",
                "description": "Tomate, Mozzarella, champiñones, jamón cocido, alcachofas y aceitunas negras.",
                "price": 13.90,
                "ingredients": ["tomate", "mozzarella", "champiñones", "jamón cocido", "alcachofas", "aceitunas"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz09",
                "name": "Vegetariana",
                "category": "pizze",
                "description": "Tomate, Mozzarella, berenjena, calabacín, champiñones, cebolla y pimientos.",
                "price": 13.90,
                "ingredients": ["tomate", "mozzarella", "berenjena", "calabacín", "champiñones", "cebolla", "pimientos"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": ["vegetariano"]
            },
            {
                "id": "piz10",
                "name": "BBQ",
                "category": "pizze",
                "description": "Tomate, Mozzarella, pollo asado, bacón y salsa barbacoa.",
                "price": 13.90,
                "ingredients": ["tomate", "mozzarella", "pollo asado", "bacón", "salsa barbacoa"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz11",
                "name": "Granjera",
                "category": "pizze",
                "description": "Tomate, Mozzarella, champiñón, maíz, pollo asado y huevo.",
                "price": 13.90,
                "ingredients": ["tomate", "mozzarella", "champiñón", "maíz", "pollo asado", "huevo"],
                "allergens": ["gluten", "huevo", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz12",
                "name": "Mexicana",
                "category": "pizze",
                "description": "Tomate, Mozzarella, salsa especial con ternera, pimientos, cebolla, chiles y jalapeños.",
                "price": 13.90,
                "ingredients": ["tomate", "mozzarella", "ternera", "pimientos", "cebolla", "chiles", "jalapeños"],
                "allergens": ["gluten", "lactosa", "apio"],
                "diet_tags": ["muy_picante"]
            },
            {
                "id": "piz13",
                "name": "Calzone",
                "category": "pizze",
                "description": "Pizza cerrada con tomate, Mozzarella, champiñones y Jamón cocido.",
                "price": 14.90,
                "ingredients": ["tomate", "mozzarella", "champiñones", "jamón cocido"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz14",
                "name": "Carnivora",
                "category": "pizze",
                "description": "Tomate, Mozzarella, salsa boloñesa, pollo y bacón.",
                "price": 14.50,
                "ingredients": ["tomate", "mozzarella", "salsa boloñesa", "pollo", "bacón"],
                "allergens": ["gluten", "lactosa", "apio"],
                "diet_tags": []
            },
            {
                "id": "piz15",
                "name": "La Favorita",
                "category": "pizze",
                "description": "Tomate, Mozzarella, Boletus (Funghi Porcini) y Jamón Serrano.",
                "price": 14.90,
                "ingredients": ["tomate", "mozzarella", "boletus", "jamón serrano"],
                "allergens": ["gluten", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz16",
                "name": "Gamberi e Peperoncino",
                "category": "pizze",
                "description": "Base blanca, mozzarella, langostinos, Nduja, ajo, cebolla y mix de chiles.",
                "price": 16.90,
                "ingredients": ["mozzarella", "langostinos", "nduja", "ajo", "cebolla", "chiles"],
                "allergens": ["gluten", "crustaceos", "lactosa"],
                "diet_tags": ["muy_picante"]
            },
            {
                "id": "piz17",
                "name": "Al Salmone",
                "category": "pizze",
                "description": "Base de tomate, mozzarella y salmón ahumado.",
                "price": 16.90,
                "ingredients": ["tomate", "mozzarella", "salmón ahumado"],
                "allergens": ["gluten", "pescado", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "piz18",
                "name": "Marinera",
                "category": "pizze",
                "description": "Tomate, atún, gambas, calamares y aceite de ajo.",
                "price": 15.90,
                "ingredients": ["tomate", "atún", "gambas", "calamares"],
                "allergens": ["gluten", "crustaceos", "pescado", "lactosa", "moluscos"],
                "diet_tags": []
            },
            {
                "id": "piz19",
                "name": "Burrata e Pistacchio Croccante",
                "category": "pizze",
                "description": "Base de pesto de pistacho, Burrata, tomates Cherry, Mortadela y crujiente de pistachos.",
                "price": 16.90,
                "ingredients": ["pesto de pistacho", "burrata", "tomate cherry", "mortadela", "pistachos"],
                "allergens": ["gluten", "lactosa", "frutos secos"],
                "diet_tags": []
            }
        ],
        "postres": [
            {
                "id": "pos01",
                "name": "Panna Cotta",
                "category": "postres",
                "description": "Postre de nata cocida con sirope de frutos rojos.",
                "price": 6.50,
                "ingredients": ["nata", "azúcar", "gelatina", "frutos rojos"],
                "allergens": ["lactosa"],
                "diet_tags": []
            },
            {
                "id": "pos02",
                "name": "Tiramisú Casero del Chef",
                "category": "postres",
                "description": "Receta tradicional con bizcochos, café, mascarpone y cacao.",
                "price": 7.00,
                "ingredients": ["mascarpone", "bizcochos", "café", "huevo", "cacao"],
                "allergens": ["gluten", "huevo", "lactosa"],
                "diet_tags": []
            },
            {
                "id": "pos03",
                "name": "Cannoli Siciliani",
                "category": "postres",
                "description": "Rollo de masa frita relleno de crema de ricotta, con trocitos de chocolate y pistacho.",
                "price": 7.00,
                "ingredients": ["harina", "ricotta", "chocolate", "pistacho"],
                "allergens": ["gluten", "huevo", "lactosa", "frutos secos"],
                "diet_tags": []
            },
            {
                "id": "pos04",
                "name": "Salami de Chocolate",
                "category": "postres",
                "description": "Postre de chocolate y galletas con forma de salami.",
                "price": 6.50,
                "ingredients": ["chocolate", "galletas", "huevo", "mantequilla"],
                "allergens": ["gluten", "huevo", "lactosa", "frutos secos"],
                "diet_tags": []
            },
            {
                "id": "pos05",
                "name": "Calzone de Nutella",
                "category": "postres",
                "description": "Pizza calzone rellena de Nutella y espolvoreada con azúcar glass.",
                "price": 8.00,
                "ingredients": ["masa de pizza", "nutella"],
                "allergens": ["gluten", "lactosa", "frutos secos", "soja"],
                "diet_tags": []
            }
        ]
    }
}
