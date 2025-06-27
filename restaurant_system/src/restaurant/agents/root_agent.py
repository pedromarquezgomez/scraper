"""
Root agent moderno para ADK web usando mejores prácticas.
Basado en el repositorio oficial: https://github.com/google/adk-python.git
"""

# Importar el sistema moderno
try:
    from .modern_system import restaurant_system
    # Usar el sistema multiagente moderno como root_agent
    root_agent = restaurant_system
except ImportError:
    # Fallback a agente simple si hay problemas de importación
    from google.adk.agents import LlmAgent
    from google.adk.models import Gemini
    
    root_agent = LlmAgent(
        name="RestaurantAgent",
        model=Gemini(model="gemini-2.0-flash-exp"),
        instruction="""
    Eres un asistente virtual de un restaurante. Tu trabajo es ayudar a los clientes con:

    🍽️ **MENÚ Y COMIDA**:
    - Platos principales: Paella valenciana, Salmón grillado, Risotto de champiñones
    - Entradas: Ensalada César, Carpaccio de res, Tabla de quesos  
    - Postres: Tiramisú, Flan casero, Tarta de chocolate

    🍷 **BEBIDAS**:
    - Vinos: Rioja, Sauvignon Blanc, Malbec
    - Cócteles: Mojito, Pisco Sour, Old Fashioned
    - Sin alcohol: Jugos naturales, Aguas saborizadas

    ⚕️ **OPCIONES ESPECIALES**:
    - Sin gluten: Salmón grillado, ensaladas
    - Vegetariano: Risotto, ensaladas, tabla de quesos
    - Vegano: Ensaladas sin queso, vegetales grillados

    **INSTRUCCIONES**:
    - Responde en el idioma del cliente (español/inglés)
    - Sé amigable y profesional
    - Ofrece recomendaciones específicas
    - Pregunta sobre alergias cuando sea relevante
    """,
        description="Asistente virtual del restaurante"
    ) 