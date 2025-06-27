#!/usr/bin/env python3
"""
Deployer ADK - Sistema Multi-Agente para Vertex AI Agent Engine
Arquitectura modular usando extra_packages en lugar de código autocontenido.
"""

import os
import sys
from pathlib import Path
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

print("🚀 Deployer ADK - Sistema Multi-Agente para Restaurant SaaS")
print(f"   Proyecto: {PROJECT_ID}")
print(f"   Región: {LOCATION}")
print(f"   Staging: {STAGING_BUCKET}")
print("=" * 60)

# 1. Inicializar Vertex AI
print("🔧 Paso 1: Inicializando Vertex AI...")
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
print(f"✅ Vertex AI inicializado correctamente")

# 2. Definir herramientas del sistema multiagente
def get_available_restaurants() -> Dict[str, Any]:
    """Obtiene la lista de restaurantes disponibles en el sistema SaaS"""
    return {
        "status": "success",
        "restaurants": [
            {
                "id": "bistro_madrid",
                "name": "Bistro Madrid",
                "type": "modern_casual",
                "location": "Madrid, España",
                "description": "Restaurante moderno con fusión mediterránea"
            },
            {
                "id": "pizza_palace", 
                "name": "Pizza Palace",
                "type": "pizzeria",
                "location": "Barcelona, España",
                "description": "Pizzería auténtica italiana"
            },
            {
                "id": "demo_restaurant",
                "name": "Demo Restaurant",
                "type": "fine_dining",
                "location": "Valencia, España", 
                "description": "Restaurante de demostración para pruebas"
            },
            {
                "id": "caf_madrid_test",
                "name": "Café Madrid Test",
                "type": "cafe",
                "location": "Madrid, España",
                "description": "Café de pruebas en Madrid"
            }
        ],
        "total_count": 4
    }

def get_restaurant_info(restaurant_id: str = "bistro_madrid") -> Dict[str, Any]:
    """Obtiene información específica de un restaurante"""
    restaurants = {
        "bistro_madrid": {
            "name": "Bistro Madrid",
            "type": "modern_casual",
            "location": "Madrid, España",
            "cuisine": "Mediterránea moderna",
            "specialty": "Paella de mariscos y risottos gourmet",
            "price_range": "€€€",
            "hours": "12:00-23:30",
            "features": ["Terraza", "Menú degustación", "Vinos selectos"],
            "description": "Restaurante que fusiona la cocina mediterránea tradicional con técnicas modernas"
        },
        "pizza_palace": {
            "name": "Pizza Palace",
            "type": "pizzeria", 
            "location": "Barcelona, España",
            "cuisine": "Italiana",
            "specialty": "Pizza Margherita Premium y Quattro Stagioni",
            "price_range": "€€",
            "hours": "12:00-24:00",
            "features": ["Horno de leña", "Masa madre", "Ingredientes importados"],
            "description": "Pizzería auténtica italiana con recetas tradicionales"
        },
        "demo_restaurant": {
            "name": "Demo Restaurant",
            "type": "fine_dining",
            "location": "Valencia, España",
            "cuisine": "Alta cocina internacional",
            "specialty": "Menú degustación de temporada",
            "price_range": "€€€€",
            "hours": "19:00-23:00",
            "features": ["Estrella Michelin", "Chef ejecutivo", "Maridaje"],
            "description": "Restaurante de alta cocina para demostraciones del sistema"
        },
        "caf_madrid_test": {
            "name": "Café Madrid Test",
            "type": "cafe",
            "location": "Madrid, España", 
            "cuisine": "Cafetería y repostería",
            "specialty": "Café de especialidad y tartas caseras",
            "price_range": "€",
            "hours": "07:00-22:00",
            "features": ["Café de origen", "Repostería casera", "WiFi gratuito"],
            "description": "Café acogedor para pruebas del sistema"
        }
    }
    
    if restaurant_id in restaurants:
        return {
            "status": "success",
            "restaurant_id": restaurant_id,
            "info": restaurants[restaurant_id]
        }
    else:
        return {
            "status": "error",
            "error_message": f"Restaurante '{restaurant_id}' no encontrado",
            "available_restaurants": list(restaurants.keys())
        }

def get_menu_sample(restaurant_id: str = "bistro_madrid", category: str = "entrantes") -> Dict[str, Any]:
    """Obtiene una muestra del menú de un restaurante específico"""
    menus = {
        "bistro_madrid": {
            "entrantes": [
                {
                    "name": "Burrata con tomate y albahaca",
                    "price": "14€",
                    "description": "Burrata fresca con tomates de temporada"
                },
                {
                    "name": "Croquetas de jamón ibérico",
                    "price": "12€", 
                    "description": "Croquetas cremosas con jamón ibérico de bellota"
                }
            ],
            "principales": [
                {
                    "name": "Paella de mariscos",
                    "price": "28€",
                    "description": "Paella tradicional con mariscos frescos del Mediterráneo"
                },
                {
                    "name": "Risotto de setas",
                    "price": "22€",
                    "description": "Risotto cremoso con setas de temporada y trufa"
                }
            ]
        },
        "pizza_palace": {
            "pizzas": [
                {
                    "name": "Margherita Premium",
                    "price": "16€",
                    "description": "Salsa de tomate San Marzano, mozzarella di bufala, albahaca"
                },
                {
                    "name": "Quattro Stagioni", 
                    "price": "19€",
                    "description": "Tomate, mozzarella, jamón, setas, alcachofas, aceitunas"
                }
            ]
        }
    }
    
    if restaurant_id in menus:
        restaurant_menu = menus[restaurant_id]
        if category in restaurant_menu:
            return {
                "status": "success",
                "restaurant_id": restaurant_id,
                "category": category,
                "items": restaurant_menu[category],
                "available_categories": list(restaurant_menu.keys())
            }
        else:
            return {
                "status": "error", 
                "error_message": f"Categoría '{category}' no encontrada",
                "available_categories": list(restaurant_menu.keys())
            }
    else:
        return {
            "status": "error",
            "error_message": f"Restaurante '{restaurant_id}' no encontrado",
            "available_restaurants": list(menus.keys())
        }

# 3. Crear agente coordinador principal
print("🤖 Paso 2: Creando sistema multi-agente...")

restaurant_system_agent = Agent(
    name="restaurant_system_coordinator",
    model="gemini-2.0-flash",
    description="Coordinador principal del sistema SaaS de restaurantes que puede proporcionar información sobre múltiples restaurantes, sus menús y servicios",
    instruction="""
Eres el coordinador principal de un sistema SaaS para restaurantes. Puedes ayudar con:

1. **Información de restaurantes**: Proporcionar detalles sobre los restaurantes disponibles en la plataforma
2. **Gestión de menús**: Mostrar platos, precios y descripciones de los menús
3. **Recomendaciones**: Sugerir restaurantes y platos según las preferencias del usuario
4. **Navegación del sistema**: Ayudar a los usuarios a explorar las opciones disponibles

**Instrucciones específicas:**
- Siempre sé amable y profesional
- Proporciona información detallada y útil
- Si no tienes información específica, usa las herramientas disponibles
- Explica las opciones disponibles cuando sea relevante
- Adapta tu respuesta al tipo de consulta del usuario

**Restaurantes disponibles:**
- Bistro Madrid (moderna mediterránea)
- Pizza Palace (pizzería italiana) 
- Demo Restaurant (alta cocina)
- Café Madrid Test (cafetería)

Cuando recibas una consulta, evalúa qué tipo de información necesita el usuario y utiliza las herramientas apropiadas.
    """,
    tools=[
        FunctionTool(func=get_available_restaurants),
        FunctionTool(func=get_restaurant_info), 
        FunctionTool(func=get_menu_sample)
    ],
)

print("✅ Agente coordinador creado exitosamente")

# 4. Preparar agente para Agent Engine
print("📦 Paso 3: Preparando agente para despliegue...")

app = reasoning_engines.AdkApp(
    agent=restaurant_system_agent,
    enable_tracing=True,
)

print("✅ Agente preparado para Agent Engine")

# 5. Prueba local
print("🧪 Paso 4: Probando agente localmente...")

try:
    session = app.create_session(user_id="test_user")
    print(f"   ✅ Sesión local creada: {session.id}")
    
    print("   🔍 Enviando consulta de prueba...")
    response_events = []
    for event in app.stream_query(
        user_id="test_user",
        session_id=session.id,
        message="¿Qué restaurantes tenéis disponibles?",
    ):
        response_events.append(event)
        if 'content' in event and 'parts' in event['content']:
            for part in event['content']['parts']:
                if 'text' in part:
                    print(f"   📝 Respuesta: {part['text'].strip()[:100]}...")
    
    print("✅ Prueba local exitosa")
    
except Exception as e:
    print(f"❌ Error en prueba local: {e}")
    sys.exit(1)

# 6. Desplegar en Agent Engine  
print("🚀 Paso 5: Desplegando en Vertex AI Agent Engine...")

try:
    # Configuración para despliegue modular
    requirements = [
        "google-cloud-aiplatform[agent_engines,adk]==1.88.0",
        "google-adk-python>=1.5.0",
        "jsonschema>=4.0.0"
    ]
    
    # Archivos y directorios locales a incluir (en lugar de código autocontenido)
    extra_packages = [
        "src/",           # Todo el código fuente modular
        "schemas/",       # Schemas de validación
        "restaurant_data/", # Datos de configuración de restaurantes
        "templates/"      # Templates de configuración
    ]
    
    # Variables de entorno para el agente desplegado
    env_vars = {
        "RESTAURANT_SYSTEM_MODE": "production",
        "LOG_LEVEL": "INFO",
        "VERTEX_AI_REGION": LOCATION
    }
    
    remote_agent = agent_engines.create(
        agent_engine=restaurant_system_agent,
        requirements=requirements,
        extra_packages=extra_packages,
        env_vars=env_vars,
        display_name="Restaurant SaaS System - ADK Multi-Agent",
        description="Sistema SaaS multi-tenant para restaurantes usando arquitectura multi-agente ADK",
        gcs_dir_name="restaurant_saas_adk_v1"
    )
    
    print("✅ Despliegue completado exitosamente")
    print(f"   🎯 Resource name: {remote_agent.resource_name}")
    
except Exception as e:
    print(f"❌ Error en despliegue: {e}")
    print(f"   🔍 Tipo de error: {type(e)}")
    sys.exit(1)

# 7. Prueba remota
print("🌐 Paso 6: Probando agente remotamente...")

try:
    # Crear sesión remota
    remote_session = remote_agent.create_session(user_id="production_user")
    print(f"   ✅ Sesión remota creada: {remote_session['id']}")
    
    # Probar consulta remota
    print("   🔍 Enviando consulta remota...")
    remote_events = []
    for event in remote_agent.stream_query(
        user_id="production_user",
        session_id=remote_session["id"],
        message="Dime información sobre Bistro Madrid y muéstrame algunos platos del menú",
    ):
        remote_events.append(event)
        if 'content' in event and 'parts' in event['content']:
            for part in event['content']['parts']:
                if 'text' in part:
                    print(f"   📝 Respuesta remota: {part['text'].strip()[:150]}...")
    
    print("✅ Prueba remota exitosa")
    
except Exception as e:
    print(f"❌ Error en prueba remota: {e}")

# 8. Resumen final
print("\n" + "=" * 60)
print("🎉 DESPLIEGUE COMPLETADO - Sistema Multi-Agente ADK")
print("=" * 60)
print(f"📋 Resource ID: {remote_agent.resource_name}")
print(f"🏗️  Arquitectura: Multi-agente modular con extra_packages")
print(f"🔧 Herramientas: {len(restaurant_system_agent.tools)} herramientas especializadas")
print(f"📊 Restaurantes: 4 restaurantes demo configurados")
print(f"⚙️  Modo: Producción con configuración dinámica")
print("\n🧹 Para limpiar recursos:")
print("   remote_agent.delete(force=True)")
print("\n🎯 El agente está listo para recibir consultas en producción!") 