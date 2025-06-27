"""
Sistema multiagente moderno para restaurante siguiendo mejores prácticas de ADK.
Basado en el repositorio oficial: https://github.com/google/adk-python.git
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..config.system_config import RESTAURANT_DATA


def create_food_specialist():
    """Crear agente especialista en comida usando mejores prácticas ADK."""
    
    def get_menu_items(category: str = "all") -> str:
        """Obtener elementos del menú por categoría."""
        menu = RESTAURANT_DATA["menu"]
        if category == "all":
            result = "🍽️ **MENÚ COMPLETO DEL RESTAURANTE**\n\n"
            for cat, items in menu.items():
                result += f"**{cat.upper().replace('_', ' ')}:**\n"
                for item in items:
                    name = item.get("name", "Sin nombre")
                    price = item.get("price", "Consultar")
                    ingredients = item.get("ingredients", [])
                    desc = f"Ingredientes: {', '.join(ingredients)}" if ingredients else ""
                    result += f"• {name} - ${price}\n  {desc}\n\n"
            return result
        elif category in menu:
            result = f"🍽️ **{category.upper().replace('_', ' ')}**\n\n"
            for item in menu[category]:
                name = item.get("name", "Sin nombre")
                price = item.get("price", "Consultar")
                ingredients = item.get("ingredients", [])
                desc = f"Ingredientes: {', '.join(ingredients)}" if ingredients else ""
                result += f"• {name} - ${price}\n  {desc}\n\n"
            return result
        else:
            return f"Categoría '{category}' no encontrada. Categorías disponibles: {', '.join(menu.keys())}"

    def get_dish_details(dish_name: str) -> str:
        """Obtener detalles específicos de un plato."""
        menu = RESTAURANT_DATA["menu"]
        for category, dishes in menu.items():
            for dish in dishes:  # dishes es una lista, no diccionario
                if dish_name.lower() in dish.get("name", "").lower():
                    name = dish.get("name", "Sin nombre")
                    ingredients = dish.get("ingredients", [])
                    allergens = dish.get("allergens", [])
                    price = dish.get("price", "Consultar")
                    calories = dish.get("calories", "No disponible")
                    diet_tags = dish.get("diet_tags", [])
                    
                    result = f"🍽️ **{name}** (${price})\n\n"
                    if ingredients:
                        result += f"🥘 **Ingredientes:** {', '.join(ingredients)}\n\n"
                    if allergens:
                        result += f"⚠️ **Alérgenos:** {', '.join(allergens)}\n\n"
                    if diet_tags:
                        result += f"🌱 **Características:** {', '.join(diet_tags)}\n\n"
                    result += f"📊 **Calorías:** {calories}\n\n"
                    return result
        return f"Plato '{dish_name}' no encontrado en nuestro menú."

    def check_dietary_options(diet_type: str) -> str:
        """Verificar opciones dietéticas disponibles."""
        menu = RESTAURANT_DATA["menu"]
        options = []
        
        for category, dishes in menu.items():
            for dish in dishes:  # dishes es una lista
                name = dish.get("name", "Sin nombre")
                allergens = dish.get("allergens", [])
                diet_tags = dish.get("diet_tags", [])
                price = dish.get("price", "Consultar")
                
                # Verificar opciones dietéticas
                is_suitable = False
                if diet_type.lower() in ["sin gluten", "gluten-free", "celiac"]:
                    if "gluten" not in [a.lower() for a in allergens]:
                        is_suitable = True
                elif diet_type.lower() in ["vegetariano", "vegetarian"]:
                    if "vegetariano" in [d.lower() for d in diet_tags]:
                        is_suitable = True
                elif diet_type.lower() in ["vegano", "vegan"]:
                    if "vegano" in [d.lower() for d in diet_tags]:
                        is_suitable = True
                
                if is_suitable:
                    category_name = category.replace('_', ' ').title()
                    options.append(f"• {name} - ${price} ({category_name})")
        
        if options:
            return f"🌱 **Opciones {diet_type}:**\n\n" + "\n".join(options)
        else:
            return f"Lo siento, actualmente no tenemos opciones específicas para {diet_type}. ¿Te gustaría que consulte con el chef sobre adaptaciones?"

    # Crear agente especialista en comida usando la nueva API Agent
    food_agent = Agent(
        name="FoodSpecialist",
        model="gemini-2.0-flash-exp",  # Simplificado según mejores prácticas
        instruction="""
Eres el especialista en comida del restaurante. Tu expertise incluye:

🍽️ **MENÚ Y PLATOS:**
- Conoces todos los platos del menú al detalle
- Puedes recomendar según preferencias del cliente
- Explicas ingredientes y preparación

⚠️ **ALERGIAS Y DIETAS:**
- Identificas alérgenos en cada plato
- Ofreces alternativas para dietas especiales
- Priorizas la seguridad alimentaria

🎯 **ESTILO DE COMUNICACIÓN:**
- Sé entusiasta sobre la comida
- Ofrece detalles específicos y útiles
- Haz recomendaciones personalizadas
- Mantén un tono cálido y profesional

**INSTRUCCIONES:**
1. Usa las herramientas disponibles para consultar información precisa
2. Siempre verifica alérgenos cuando sea relevante
3. Ofrece alternativas cuando algo no esté disponible
4. Sé descriptivo sobre sabores y preparación
""",
        description="Especialista en menú, ingredientes y opciones dietéticas",
        tools=[
            FunctionTool(get_menu_items),
            FunctionTool(get_dish_details),
            FunctionTool(check_dietary_options)
        ]
    )
    
    return food_agent


def create_coordinator_agent():
    """Crear agente coordinador principal usando el patrón sub_agents moderno."""
    
    # Crear agentes especialistas
    food_specialist = create_food_specialist()
    
    # Crear agente coordinador con sub_agents usando la nueva API Agent
    coordinator = Agent(
        name="RestaurantCoordinator",
        model="gemini-2.0-flash-exp",  # Simplificado según mejores prácticas
        instruction="""
Eres el coordinador principal de un restaurante premium. Tu misión es brindar una experiencia excepcional mediante:

🎯 **TU PAPEL PRINCIPAL:**
- Eres la cara visible del restaurante
- Coordinas con especialistas para respuestas precisas
- Mantienes conversaciones fluidas y naturales

🧠 **ANÁLISIS DE CONSULTAS:**
- Comida/Menú → Deriva a FoodSpecialist
- Bebidas/Vinos → (Próximamente: DrinksSpecialist)
- Nutrición/Dietas → Usa FoodSpecialist para opciones dietéticas
- Consultas generales → Responde directamente

🗣️ **COMUNICACIÓN:**
- Detecta y responde en el idioma del cliente
- Mantén un tono cálido y profesional
- Haz preguntas clarificadoras cuando sea necesario
- Unifica respuestas de especialistas en una conversación coherente

🔄 **FLUJO DE TRABAJO:**
1. Analiza la intención del cliente
2. Si es sobre comida/menú → colabora con FoodSpecialist
3. Presenta la información de manera conversacional
4. Ofrece seguimiento o información adicional

**EJEMPLOS:**
Cliente: "¿Qué tienen de menú?"
→ Colabora con FoodSpecialist para obtener el menú completo

Cliente: "¿Tienen opciones sin gluten?"
→ Colabora con FoodSpecialist para verificar opciones dietéticas

Cliente: "¿Cuáles son los ingredientes de la paella?"
→ Colabora con FoodSpecialist para detalles específicos del plato
""",
        description="Coordinador principal del restaurante con acceso a especialistas",
        sub_agents=[food_specialist]  # ¡ESTO ES LA CLAVE! Patrón moderno ADK
    )
    
    return coordinator


def create_modern_restaurant_system():
    """Crear sistema completo usando mejores prácticas ADK."""
    coordinator = create_coordinator_agent()
    return coordinator


# Crear instancia del sistema para uso directo
restaurant_system = create_modern_restaurant_system() 