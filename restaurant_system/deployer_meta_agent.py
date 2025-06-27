#!/usr/bin/env python3
"""
🚀 FASE 5: Meta-Agente Multi-Tenant para Vertex AI
==================================================

Arquitectura SaaS Escalable: Un único agente desplegado que puede atender
a cualquier restaurante configurado en nuestro sistema.

Características:
- Un solo despliegue en Vertex AI para todos los restaurantes
- Enrutamiento inteligente basado en restaurant_id
- Reutilización completa de ConfigManager y FoodSpecialistAgent
- Escalabilidad infinita sin costos adicionales por restaurante
- Mantenimiento simplificado de un único punto de despliegue

Uso:
    python deployer_meta_agent.py --deploy
    python deployer_meta_agent.py --test
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Importaciones de Google Cloud y Vertex AI
import vertexai
from vertexai.agent_engines import create, get
from google.cloud import storage

# Importaciones de ADK
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Importaciones de nuestro sistema
from src.restaurant.config.config_manager import ConfigManager, RestaurantNotFoundError
from src.restaurant.agents.food_agent import FoodSpecialistAgent

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """Configuración para el despliegue en Vertex AI"""
    project_id: str = "your-project-id"  # 🔧 Cambiar por tu Project ID
    location: str = "us-central1"
    staging_bucket: str = "your-staging-bucket"  # 🔧 Cambiar por tu bucket
    agent_engine_name: str = "restaurant-meta-agent"
    display_name: str = "Restaurant SaaS Meta-Agent"
    description: str = "Multi-tenant restaurant assistant powered by ADK"

class RestaurantMetaAgent:
    """
    Meta-Agente que enruta consultas a restaurantes específicos
    
    Este agente actúa como un proxy inteligente que:
    1. Recibe restaurant_id + consulta del usuario
    2. Carga la configuración del restaurante dinámicamente  
    3. Crea una instancia temporal del FoodSpecialistAgent
    4. Ejecuta la consulta y devuelve la respuesta personalizada
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()
        
    async def get_restaurant_response(self, restaurant_id: str, user_query: str) -> str:
        """
        Herramienta principal del meta-agente que maneja consultas multi-tenant
        
        Args:
            restaurant_id: ID del restaurante (ej: "demo_restaurant", "pizza_palace")
            user_query: Consulta del usuario (ej: "¿Cuál es la especialidad del chef?")
            
        Returns:
            str: Respuesta personalizada del agente del restaurante específico
        """
        try:
            logger.info(f"🔄 Procesando consulta para restaurante: {restaurant_id}")
            
            # 1. Cargar configuración del restaurante
            restaurant_config = self.config_manager.load_restaurant_config(restaurant_id)
            logger.info(f"✅ Configuración cargada para: {restaurant_config.metadata.name}")
            
            # 2. Crear instancia temporal del FoodSpecialistAgent
            food_agent = FoodSpecialistAgent(restaurant_config)
            logger.info(f"✅ Agente creado: {food_agent.agent_config.name}")
            
            # 3. Configurar runner para procesar la consulta
            session_service = InMemorySessionService()
            runner = InMemoryRunner(
                agent=food_agent.agent,
                app_name=f"restaurant_{restaurant_id}"
            )
            
            # 4. Ejecutar consulta
            logger.info(f"🧠 Ejecutando consulta: {user_query[:50]}...")
            session_id = "meta_session"
            user_id = "meta_user"
            
            # Crear sesión
            session = await session_service.create_session(
                app_name=f"restaurant_{restaurant_id}",
                user_id=user_id
            )
            
            # Crear contenido para el runner
            content = types.Content(role="user", parts=[types.Part(text=user_query)])
            
            # Procesar la consulta de forma asíncrona
            response_parts = []
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
            
            # 5. Extraer respuesta del agente
            agent_response = "\n".join(response_parts) if response_parts else ""
            
            if not agent_response:
                agent_response = f"El {food_agent.agent_config.name} de {restaurant_config.metadata.name} está listo para ayudarte. ¿En qué puedo asistirte?"
            
            logger.info(f"✅ Respuesta generada exitosamente")
            return agent_response
            
        except RestaurantNotFoundError:
            error_msg = f"❌ Restaurante '{restaurant_id}' no encontrado. Restaurantes disponibles: {list(self.config_manager.get_available_restaurants())}"
            logger.error(error_msg)
            return error_msg
            
        except Exception as e:
            error_msg = f"❌ Error procesando consulta para {restaurant_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg

def create_meta_agent_tools(meta_agent: RestaurantMetaAgent) -> list:
    """Crear las herramientas para el meta-agente"""
    
    def restaurant_response_sync(restaurant_id: str, user_query: str) -> str:
        """
        Obtiene respuesta personalizada de un restaurante específico basado en su configuración y menú.
        
        Args:
            restaurant_id (str): ID único del restaurante (ej: 'demo_restaurant', 'pizza_palace', 'bistro_madrid')
            user_query (str): Consulta o pregunta del usuario sobre el restaurante
            
        Returns:
            str: Respuesta personalizada del agente del restaurante específico
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                meta_agent.get_restaurant_response(restaurant_id, user_query)
            )
        finally:
            loop.close()
    
    return [
        FunctionTool(restaurant_response_sync)
    ]

def create_meta_agent() -> Agent:
    """
    Crea el meta-agente con su única herramienta de enrutamiento
    """
    meta_agent_instance = RestaurantMetaAgent()
    tools = create_meta_agent_tools(meta_agent_instance)
    
    instructions = """
🏪 Soy el Meta-Agente del Sistema SaaS de Restaurantes

MI MISIÓN: Conectar usuarios con el asistente especializado de su restaurante específico.

IMPORTANTE: Para cada consulta debo:
1. Identificar el restaurant_id en la consulta del usuario
2. Usar SIEMPRE la herramienta get_restaurant_response con:
   - restaurant_id: El ID del restaurante
   - user_query: La pregunta completa del usuario

EJEMPLOS DE USO CORRECTO:
- Usuario: "restaurant_id=demo_restaurant ¿Cuál es tu especialidad?"
  → Llamo: get_restaurant_response("demo_restaurant", "¿Cuál es tu especialidad?")

- Usuario: "restaurant_id=pizza_palace ¿Tienen opciones veganas?"
  → Llamo: get_restaurant_response("pizza_palace", "¿Tienen opciones veganas?")

NUNCA debo responder directamente sobre comida o restaurantes. SIEMPRE debo usar la herramienta para obtener respuestas personalizadas del restaurante específico.

Si no se proporciona restaurant_id, pediré al usuario que lo especifique.
"""
    
    return Agent(
        name="RestaurantMetaAgent",
        model="gemini-2.0-flash-exp",
        instruction=instructions,
        tools=tools
    )

class VertexAIDeployer:
    """Manejador del despliegue en Vertex AI Agent Engine"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self._initialize_vertex_ai()
    
    def _initialize_vertex_ai(self):
        """Inicializar Vertex AI con las credenciales del proyecto"""
        try:
            vertexai.init(
                project=self.config.project_id,
                location=self.config.location,
                staging_bucket=self.config.staging_bucket
            )
            logger.info(f"✅ Vertex AI inicializado: {self.config.project_id}")
        except Exception as e:
            logger.error(f"❌ Error inicializando Vertex AI: {e}")
            raise
    
    def deploy_meta_agent(self) -> str:
        """
        Despliega el meta-agente en Vertex AI Agent Engine
        
        Returns:
            str: ID del agente desplegado
        """
        try:
            logger.info("🚀 Iniciando despliegue del Meta-Agente...")
            
            # Crear el meta-agente
            meta_agent = create_meta_agent()
            
            # Configuración para el despliegue
            agent_config = {
                "display_name": self.config.display_name,
                "description": self.config.description,
                "instructions": meta_agent.instructions,
                "tools": [tool.to_dict() for tool in meta_agent.tools],
                "model": "gemini-2.0-flash-exp",  # Usar el modelo más reciente
            }
            
            # Desplegar en Vertex AI
            logger.info("📡 Desplegando en Vertex AI Agent Engine...")
            deployed_agent = create(
                agent_config,
                location=self.config.location
            )
            
            agent_id = deployed_agent.name
            logger.info(f"✅ Meta-Agente desplegado exitosamente!")
            logger.info(f"🆔 Agent ID: {agent_id}")
            logger.info(f"🌐 Endpoint: {deployed_agent.agent_engine.display_name}")
            
            return agent_id
            
        except Exception as e:
            logger.error(f"❌ Error en el despliegue: {e}")
            raise
    
    def test_deployed_agent(self, agent_id: str, test_queries: Optional[list] = None):
        """
        Prueba el agente desplegado con consultas de ejemplo
        
        Args:
            agent_id: ID del agente desplegado
            test_queries: Lista de consultas de prueba
        """
        if not test_queries:
            test_queries = [
                {
                    "restaurant_id": "demo_restaurant",
                    "query": "¿Cuál es la especialidad del chef?"
                },
                {
                    "restaurant_id": "pizza_palace", 
                    "query": "¿Tienen pizzas veganas?"
                },
                {
                    "restaurant_id": "bistro_madrid",
                    "query": "¿Qué platos mediterráneos recomiendan?"
                }
            ]
        
        try:
            logger.info("🧪 Iniciando pruebas del Meta-Agente desplegado...")
            
            # Obtener referencia al agente desplegado
            deployed_agent = get(agent_id, location=self.config.location)
            
            for i, test in enumerate(test_queries, 1):
                logger.info(f"\n🔍 Prueba {i}: {test['restaurant_id']}")
                logger.info(f"❓ Consulta: {test['query']}")
                
                # Formatear consulta para el meta-agente
                formatted_query = f"restaurant_id={test['restaurant_id']} {test['query']}"
                
                try:
                    # Invocar agente remoto
                    response = deployed_agent.query(formatted_query)
                    logger.info(f"✅ Respuesta: {response[:200]}...")
                    
                except Exception as e:
                    logger.error(f"❌ Error en prueba {i}: {e}")
            
            logger.info("\n🎉 Pruebas completadas!")
            
        except Exception as e:
            logger.error(f"❌ Error en las pruebas: {e}")
            raise

def create_requirements_file():
    """Crear archivo requirements.txt para el despliegue"""
    requirements = """
# Dependencias principales del proyecto
google-adk-python>=1.5.0
google-cloud-aiplatform
google-cloud-storage
vertexai
jsonschema>=4.0.0

# Dependencias adicionales
asyncio
logging
dataclasses
typing
""".strip()
    
    with open("requirements_deployment.txt", "w") as f:
        f.write(requirements)
    
    logger.info("✅ Archivo requirements_deployment.txt creado")

def show_usage_examples(agent_id: str):
    """Mostrar ejemplos de uso del meta-agente desplegado"""
    
    examples = f"""
🚀 META-AGENTE DESPLEGADO EXITOSAMENTE
=====================================

🆔 Agent ID: {agent_id}

📖 EJEMPLOS DE USO:

1. 🍝 Consulta a Restaurante Italiano:
   Query: "restaurant_id=demo_restaurant ¿Cuál es la especialidad del chef?"
   
2. 🍕 Consulta a Pizzería:
   Query: "restaurant_id=pizza_palace ¿Tienen pizzas veganas?"
   
3. 🥘 Consulta a Bistro Mediterráneo:
   Query: "restaurant_id=bistro_madrid ¿Qué platos mediterráneos recomiendan?"

💡 INTEGRACIÓN CON APLICACIONES:

# Python Client Example:
from vertexai.agent_engines import get

agent = get("{agent_id}", location="us-central1")
response = agent.query("restaurant_id=demo_restaurant ¿Cuál es tu menú?")
print(response)

# REST API Example:
curl -X POST "https://{{location}}-aiplatform.googleapis.com/v1/projects/{{project_id}}/locations/{{location}}/agents/{{agent_id}}:query" \\
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "restaurant_id=demo_restaurant ¿Cuál es tu especialidad?"}}'

🏗️ ARQUITECTURA IMPLEMENTADA:
• Un único agente desplegado para todos los restaurantes
• Enrutamiento dinámico basado en restaurant_id
• Escalabilidad infinita sin costos adicionales
• Reutilización completa del sistema multi-tenant
"""
    
    print(examples)

def main():
    """Función principal del deployer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Meta-Agente SaaS Deployer")
    parser.add_argument("--deploy", action="store_true", help="Desplegar meta-agente en Vertex AI")
    parser.add_argument("--test", action="store_true", help="Probar meta-agente desplegado")
    parser.add_argument("--agent-id", type=str, help="ID del agente para pruebas")
    parser.add_argument("--project-id", type=str, help="Google Cloud Project ID")
    parser.add_argument("--staging-bucket", type=str, help="Staging bucket para el despliegue")
    
    args = parser.parse_args()
    
    # Configuración de despliegue
    config = DeploymentConfig()
    if args.project_id:
        config.project_id = args.project_id
    if args.staging_bucket:
        config.staging_bucket = args.staging_bucket
    
    deployer = VertexAIDeployer(config)
    
    if args.deploy:
        logger.info("🚀 FASE 5: Desplegando Meta-Agente Multi-Tenant...")
        
        # Crear archivo de requisitos
        create_requirements_file()
        
        # Desplegar agente
        agent_id = deployer.deploy_meta_agent()
        
        # Mostrar ejemplos de uso
        show_usage_examples(agent_id)
        
    elif args.test:
        if not args.agent_id:
            logger.error("❌ Se requiere --agent-id para las pruebas")
            return
        
        deployer.test_deployed_agent(args.agent_id)
        
    else:
        logger.info("ℹ️  Uso: python deployer_meta_agent.py --deploy o --test --agent-id=AGENT_ID")
        logger.info("ℹ️  Para más opciones: python deployer_meta_agent.py --help")

if __name__ == "__main__":
    main() 