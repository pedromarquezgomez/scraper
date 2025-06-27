#!/usr/bin/env python3
"""
Deployer para Vertex AI Agent Engine
Siguiendo el tutorial oficial paso a paso
"""

import datetime
from zoneinfo import ZoneInfo
import vertexai
from google.adk.agents import Agent
from vertexai.preview import reasoning_engines
from vertexai import agent_engines

# 1.2. Inicializa Vertex AI
PROJECT_ID = "sumy-464008"
LOCATION = "us-central1"  # Región compatible con Agent Engine
STAGING_BUCKET = "gs://sumy-agent-staging"

print("🔧 Paso 1.2: Inicializando Vertex AI...")
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
print(f"✅ Vertex AI inicializado - Proyecto: {PROJECT_ID}, Región: {LOCATION}")

# 2. Prepara tu Agente - Define tus herramientas (funciones Python)
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city."""
    if city.lower() == "madrid":
        return {
            "status": "success",
            "report": "El clima en Madrid es soleado con una temperatura de 22 grados Celsius."
        }
    elif city.lower() == "new york":
        return {
            "status": "success", 
            "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit)."
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available."
        }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    if city.lower() == "madrid":
        tz_identifier = "Europe/Madrid"
    elif city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}."
        }
    
    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    return {"status": "success", "report": report}

def get_restaurant_info(restaurant_type: str = "general") -> dict:
    """Provides information about restaurants."""
    restaurants = {
        "italian": {
            "name": "La Tavola Italiana",
            "specialty": "Pasta fresca y risottos auténticos",
            "recommended_dish": "Risotto ai funghi porcini"
        },
        "pizza": {
            "name": "Pizza Palace", 
            "specialty": "Pizzas artesanales al horno de leña",
            "recommended_dish": "Pizza Margherita Premium"
        },
        "mediterranean": {
            "name": "Bistro Madrid",
            "specialty": "Cocina mediterránea moderna",
            "recommended_dish": "Paella de mariscos"
        }
    }
    
    if restaurant_type.lower() in restaurants:
        return {
            "status": "success",
            "restaurant": restaurants[restaurant_type.lower()]
        }
    else:
        return {
            "status": "success",
            "available_types": list(restaurants.keys()),
            "message": "Available restaurant types: " + ", ".join(restaurants.keys())
        }

# Crea tu instancia de Agente
print("🤖 Paso 2: Creando el agente principal...")
root_agent = Agent(
    name="restaurant_system_agent",
    model="gemini-2.0-flash",
    description="Agente del sistema de restaurante que puede proporcionar información sobre clima, hora y restaurantes",
    instruction="Eres un asistente útil para un sistema de restaurante. Puedes responder preguntas sobre el clima, la hora actual y proporcionar información sobre restaurantes. Siempre sé amable y profesional.",
    tools=[get_weather, get_current_time, get_restaurant_info],
)
print("✅ Agente creado exitosamente")

# Envuelve tu agente para el despliegue
print("📦 Paso 2: Envolviendo el agente para despliegue...")
app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,  # Habilita el tracing para depuración
)
print("✅ Agente envuelto para Agent Engine")

# Prueba local antes del despliegue
print("🧪 Probando agente localmente...")
try:
    session = app.create_session(user_id="test_user")
    print(f"   Sesión local creada: {session.id}")
    
    print("   Enviando consulta de prueba...")
    for event in app.stream_query(
        user_id="test_user",
        session_id=session.id,
        message="¿Cuál es el clima en Madrid?",
    ):
        if 'content' in event and 'parts' in event['content']:
            for part in event['content']['parts']:
                if 'text' in part:
                    print(f"   Respuesta: {part['text'].strip()}")
    
    print("✅ Prueba local exitosa")
except Exception as e:
    print(f"❌ Error en prueba local: {e}")
    exit(1)

# 3. Despliega tu Agente en Agent Engine
print("🚀 Paso 3: Desplegando agente en Agent Engine...")
try:
    remote_app = agent_engines.create(
        agent_engine=root_agent,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
        ]
    )
    
    print("✅ Despliegue completado exitosamente")
    print(f"   Resource name: {remote_app.resource_name}")
    
except Exception as e:
    print(f"❌ Error en despliegue: {e}")
    print(f"   Tipo de error: {type(e)}")
    exit(1)

# 4. Prueba tu Agente Remotamente
print("🌐 Paso 4: Probando agente remotamente...")
try:
    # Crea una sesión (remota)
    remote_session = remote_app.create_session(user_id="u_456")
    print(f"   Sesión remota creada: {remote_session}")
    
    # Envía consultas a tu agente (remoto)
    print("   Enviando consulta remota...")
    for event in remote_app.stream_query(
        user_id="u_456",
        session_id=remote_session["id"],  # remote_session["id"] para sesiones remotas
        message="¿Qué información tienes sobre restaurantes italianos?",
    ):
        if 'content' in event and 'parts' in event['content']:
            for part in event['content']['parts']:
                if 'text' in part:
                    print(f"   Respuesta remota: {part['text'].strip()}")
    
    print("✅ Prueba remota exitosa")
    
except Exception as e:
    print(f"❌ Error en prueba remota: {e}")

# 5. Información para limpieza
print("\n📋 Información del despliegue:")
print(f"   Resource name: {remote_app.resource_name}")
print("\n🧹 Para limpiar recursos (opcional):")
print("   remote_app.delete(force=True)")
print("\n🎉 ¡Despliegue completado! Tu agente está funcionando en Vertex AI Agent Engine.") 