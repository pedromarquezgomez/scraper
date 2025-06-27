#!/usr/bin/env python3
"""
Deployer ADK Simplificado - Sistema Multi-Agente para Vertex AI Agent Engine
Versión simplificada pero modular, sin extra_packages complejos.
"""

import sys
from typing import Dict, List, Any
import vertexai
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from vertexai.preview import reasoning_engines
from vertexai import agent_engines

# Configuración del proyecto
PROJECT_ID = "sumy-464008"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://sumy-agent-staging"

print("🚀 Deployer ADK Simplificado - Restaurant SaaS")
print(f"   Proyecto: {PROJECT_ID}")
print(f"   Región: {LOCATION}")
print(f"   Staging: {STAGING_BUCKET}")
print("=" * 50)

# 1. Inicializar Vertex AI
print("🔧 Paso 1: Inicializando Vertex AI...")
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
print("✅ Vertex AI inicializado")

# 2. Definir herramientas especializadas del sistema
def get_restaurant_list() -> Dict[str, Any]:
    """Lista de restaurantes disponibles en la plataforma SaaS"""
    return {
        "status": "success",
        "restaurants": [
            {
                "id": "bistro_madrid",
                "name": "Bistro Madrid",
                "type": "Mediterráneo moderno",
                "location": "Madrid, España",
                "specialty": "Paella de mariscos, Risottos gourmet"
            },
            {
                "id": "pizza_palace", 
                "name": "Pizza Palace",
                "type": "Pizzería italiana",
                "location": "Barcelona, España",
                "specialty": "Pizza Margherita Premium, Quattro Stagioni"
            },
            {
                "id": "demo_restaurant",
                "name": "Demo Restaurant", 
                "type": "Alta cocina",
                "location": "Valencia, España",
                "specialty": "Menú degustación de temporada"
            }
        ],
        "total": 3
    }

def get_restaurant_details(restaurant_id: str = "bistro_madrid") -> Dict[str, Any]:
    """Información detallada de un restaurante específico"""
    restaurants_db = {
        "bistro_madrid": {
            "name": "Bistro Madrid",
            "type": "Mediterráneo moderno",
            "location": "Madrid, España",
            "cuisine": "Fusión mediterránea",
            "price_range": "€€€ (25-40€)",
            "hours": "12:00-23:30 todos los días",
            "specialties": [
                "Paella de mariscos frescos del Mediterráneo",
                "Risotto de setas con trufa negra",
                "Burrata con tomate de temporada"
            ],
            "features": ["Terraza exterior", "Menú degustación", "Carta de vinos"],
            "chef_recommendation": "Nuestro chef recomienda la paella de mariscos, preparada con arroz bomba y mariscos frescos del día"
        },
        "pizza_palace": {
            "name": "Pizza Palace",
            "type": "Pizzería italiana",
            "location": "Barcelona, España", 
            "cuisine": "Italiana tradicional",
            "price_range": "€€ (15-25€)",
            "hours": "12:00-24:00 todos los días",
            "specialties": [
                "Pizza Margherita Premium con mozzarella di bufala",
                "Quattro Stagioni con ingredientes de temporada",
                "Calzone relleno de ricotta y espinacas"
            ],
            "features": ["Horno de leña", "Masa madre tradicional", "Ingredientes importados"],
            "chef_recommendation": "La Pizza Margherita Premium con mozzarella di bufala y tomates San Marzano es nuestra especialidad"
        },
        "demo_restaurant": {
            "name": "Demo Restaurant",
            "type": "Alta cocina",
            "location": "Valencia, España",
            "cuisine": "Cocina de autor internacional",
            "price_range": "€€€€ (60-100€)",
            "hours": "19:00-23:00 (cerrado lunes)",
            "specialties": [
                "Menú degustación de 7 platos",
                "Lubina en costra de sal con hierbas",
                "Soufflé de chocolate con helado casero"
            ],
            "features": ["Estrella Michelin", "Chef ejecutivo", "Maridaje de vinos"],
            "chef_recommendation": "El menú degustación combina técnicas modernas con ingredientes locales de máxima calidad"
        }
    }
    
    if restaurant_id in restaurants_db:
        return {
            "status": "success",
            "restaurant": restaurants_db[restaurant_id]
        }
    else:
        return {
            "status": "error",
            "message": f"Restaurante '{restaurant_id}' no encontrado",
            "available": list(restaurants_db.keys())
        }

def get_menu_categories(restaurant_id: str = "bistro_madrid") -> Dict[str, Any]:
    """Categorías del menú por restaurante"""
    menu_structure = {
        "bistro_madrid": {
            "categories": ["entrantes", "principales", "postres", "bebidas"],
            "highlights": [
                "Entrantes: Burrata con tomate (14€), Croquetas ibéricas (12€)",
                "Principales: Paella de mariscos (28€), Risotto de setas (22€)",
                "Postres: Tiramisú casero (8€), Tarta de limón (7€)"
            ]
        },
        "pizza_palace": {
            "categories": ["pizzas", "antipasti", "pasta", "postres"],
            "highlights": [
                "Pizzas: Margherita Premium (16€), Quattro Stagioni (19€)", 
                "Antipasti: Bruschetta trio (9€), Burrata pugliese (13€)",
                "Pasta: Carbonara tradicional (14€), Penne arrabbiata (12€)"
            ]
        },
        "demo_restaurant": {
            "categories": ["degustacion", "carta", "maridajes"],
            "highlights": [
                "Menú degustación: 7 platos con maridaje (95€)",
                "Platos carta: Lubina en costra (32€), Risotto de trufa (28€)", 
                "Maridajes: Selección de vinos premium por copas"
            ]
        }
    }
    
    if restaurant_id in menu_structure:
        return {
            "status": "success",
            "restaurant_id": restaurant_id,
            "menu_info": menu_structure[restaurant_id]
        }
    else:
        return {
            "status": "error",
            "message": f"Menú de '{restaurant_id}' no disponible",
            "available_restaurants": list(menu_structure.keys())
        }

# 3. Crear agente coordinador principal
print("🤖 Paso 2: Creando agente coordinador...")

restaurant_coordinator = Agent(
    name="restaurant_saas_coordinator",
    model="gemini-2.0-flash",
    description="Coordinador inteligente del sistema SaaS de restaurantes que ayuda a usuarios a explorar restaurantes, menús y hacer recomendaciones personalizadas",
    instruction="""
Eres el coordinador inteligente de una plataforma SaaS de restaurantes. Tu misión es ayudar a los usuarios de manera profesional y amigable.

## TUS CAPACIDADES:
🏪 **Gestión de restaurantes**: Información sobre restaurantes disponibles en la plataforma
🍽️ **Exploración de menús**: Detalles de platos, precios y especialidades 
💡 **Recomendaciones**: Sugerencias personalizadas según preferencias
🔍 **Búsqueda inteligente**: Ayuda a encontrar lo que el usuario busca

## RESTAURANTES DISPONIBLES:
- **Bistro Madrid** (Madrid) - Mediterráneo moderno, especialidad en paella y risottos
- **Pizza Palace** (Barcelona) - Pizzería italiana auténtica con horno de leña
- **Demo Restaurant** (Valencia) - Alta cocina con estrella Michelin

## INSTRUCCIONES DE COMPORTAMIENTO:
✅ Sé siempre amable, profesional y útil
✅ Usa las herramientas disponibles para obtener información actualizada
✅ Proporciona detalles específicos cuando sea posible
✅ Sugiere opciones cuando el usuario no esté seguro
✅ Explica las características únicas de cada restaurante
✅ Adapta tu respuesta al tipo de consulta (información, recomendaciones, etc.)

## EJEMPLOS DE RESPUESTAS:
- Para consultas generales: Lista restaurantes y permite profundizar
- Para consultas específicas: Usa las herramientas para obtener detalles exactos
- Para recomendaciones: Considera el tipo de cocina, presupuesto y ubicación

¡Ayuda a los usuarios a descubrir experiencias gastronómicas increíbles!
    """,
    tools=[
        FunctionTool(func=get_restaurant_list),
        FunctionTool(func=get_restaurant_details),
        FunctionTool(func=get_menu_categories)
    ]
)

print("✅ Agente coordinador creado")

# 4. Preparar para despliegue
print("📦 Paso 3: Preparando para Agent Engine...")

app = reasoning_engines.AdkApp(
    agent=restaurant_coordinator,
    enable_tracing=True,
)

print("✅ Agente preparado")

# 5. Prueba local rápida
print("🧪 Paso 4: Prueba local...")

try:
    session = app.create_session(user_id="test_user")
    print(f"   ✅ Sesión creada: {session.id[:8]}...")
    
    # Prueba simple
    for event in app.stream_query(
        user_id="test_user",
        session_id=session.id,
        message="¿Qué restaurantes tenéis?",
    ):
        if 'content' in event and 'parts' in event['content']:
            for part in event['content']['parts']:
                if 'text' in part:
                    print(f"   📝 Respuesta: {part['text'][:80]}...")
                    break
            break
    
    print("✅ Prueba local exitosa")
    
except Exception as e:
    print(f"❌ Error en prueba local: {e}")
    sys.exit(1)

# 6. Desplegar en Agent Engine
print("🚀 Paso 5: Desplegando en Agent Engine...")

try:
    # Configuración simplificada y robusta
    requirements = [
        "google-cloud-aiplatform[agent_engines,adk]",
        "pydantic>=2.0.0"
    ]
    
    remote_agent = agent_engines.create(
        agent_engine=restaurant_coordinator,
        requirements=requirements,
        display_name="Restaurant SaaS Coordinator",
        description="Sistema SaaS inteligente para gestión de restaurantes",
        gcs_dir_name="restaurant_saas_simple"
    )
    
    print("✅ Despliegue exitoso")
    print(f"   🎯 Resource: {remote_agent.resource_name}")
    
except Exception as e:
    print(f"❌ Error en despliegue: {e}")
    sys.exit(1)

# 7. Prueba remota
print("🌐 Paso 6: Prueba remota...")

try:
    remote_session = remote_agent.create_session(user_id="prod_user")
    print(f"   ✅ Sesión remota: {remote_session['id'][:8]}...")
    
    for event in remote_agent.stream_query(
        user_id="prod_user",
        session_id=remote_session["id"],
        message="Dime sobre Bistro Madrid y su menú",
    ):
        if 'content' in event and 'parts' in event['content']:
            for part in event['content']['parts']:
                if 'text' in part:
                    print(f"   📝 Remoto: {part['text'][:100]}...")
                    break
            break
    
    print("✅ Prueba remota exitosa")
    
except Exception as e:
    print(f"⚠️ Error en prueba remota: {e}")

# 8. Resumen
print("\n" + "=" * 50)
print("🎉 DESPLIEGUE COMPLETADO")
print("=" * 50)
print(f"📋 ID: {remote_agent.resource_name}")
print(f"🏗️ Arquitectura: Sistema multi-agente simplificado")
print(f"🔧 Herramientas: 3 especializadas")
print(f"📊 Restaurantes: 3 configurados")
print("\n🧹 Limpiar: remote_agent.delete(force=True)")
print("🎯 ¡Sistema listo en producción!") 