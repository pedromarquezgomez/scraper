#!/usr/bin/env python3
"""
🧪 Demo Local del Meta-Agente Multi-Tenant
==========================================

Prueba local de la arquitectura del meta-agente antes del despliegue en Vertex AI.
Simula el comportamiento del meta-agente desplegado usando nuestro sistema local.

Uso:
    python demo_meta_agent_local.py
"""

import asyncio
import logging
from datetime import datetime

# Configurar logging más detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importaciones del meta-agente
from deployer_meta_agent import RestaurantMetaAgent, create_meta_agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types

class MetaAgentLocalDemo:
    """Demo local del meta-agente para pruebas sin despliegue"""
    
    def __init__(self):
        self.meta_agent_instance = RestaurantMetaAgent()
        self.meta_agent = create_meta_agent()
        self.session_service = InMemorySessionService()
        self.runner = InMemoryRunner(
            agent=self.meta_agent,
            app_name="meta_agent_demo"
        )
        
    def format_query_for_meta_agent(self, restaurant_id: str, user_query: str) -> str:
        """Formatear consulta como lo haría una aplicación cliente"""
        return f"restaurant_id={restaurant_id} {user_query}"
    
    async def test_meta_agent_direct(self, restaurant_id: str, user_query: str):
        """Probar directamente la función del meta-agente"""
        logger.info(f"\n🔧 PRUEBA DIRECTA - Función del Meta-Agente")
        logger.info(f"🏪 Restaurante: {restaurant_id}")
        logger.info(f"❓ Consulta: {user_query}")
        
        try:
            response = await self.meta_agent_instance.get_restaurant_response(
                restaurant_id=restaurant_id,
                user_query=user_query
            )
            logger.info(f"✅ Respuesta directa: {response[:200]}...")
            return response
        except Exception as e:
            logger.error(f"❌ Error en prueba directa: {e}")
            return None
    
    async def test_meta_agent_via_adk(self, restaurant_id: str, user_query: str):
        """Probar vía ADK Runner (simulando el comportamiento del despliegue)"""
        logger.info(f"\n🤖 PRUEBA VÍA ADK - Simulando Despliegue")
        logger.info(f"🏪 Restaurante: {restaurant_id}")
        logger.info(f"❓ Consulta: {user_query}")
        
        try:
            # Formatear consulta como lo haría el cliente
            formatted_query = self.format_query_for_meta_agent(restaurant_id, user_query)
            logger.info(f"📝 Query formateada: {formatted_query}")
            
            # Crear sesión
            user_id = "demo_user"
            session = await self.session_service.create_session(
                app_name="meta_agent_demo",
                user_id=user_id
            )
            
            # Crear contenido para el runner
            content = types.Content(role="user", parts=[types.Part(text=formatted_query)])
            
            # Ejecutar vía ADK Runner
            response_parts = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
            
            # Extraer respuesta
            agent_response = "\n".join(response_parts) if response_parts else ""
            
            logger.info(f"✅ Respuesta vía ADK: {agent_response[:200]}...")
            return agent_response
            
        except Exception as e:
            logger.error(f"❌ Error en prueba vía ADK: {e}")
            return None

    async def run_comprehensive_demo(self):
        """Ejecutar demo completo con múltiples restaurantes y consultas"""
        
        print("🚀 DEMO DEL META-AGENTE MULTI-TENANT")
        print("=" * 50)
        print("Probando la arquitectura escalable antes del despliegue")
        print()
        
        # Casos de prueba
        test_cases = [
            {
                "restaurant_id": "demo_restaurant",
                "queries": [
                    "¿Cuál es la especialidad del chef?",
                    "¿Qué platos italianos recomiendan?",
                    "¿Tienen opciones vegetarianas?"
                ]
            },
            {
                "restaurant_id": "pizza_palace", 
                "queries": [
                    "¿Tienen pizzas veganas?",
                    "¿Cuál es su pizza más popular?",
                    "¿Hacen delivery?"
                ]
            },
            {
                "restaurant_id": "bistro_madrid",
                "queries": [
                    "¿Qué platos mediterráneos tienen?",
                    "¿Cuál es el precio promedio?",
                    "¿Tienen mariscos frescos?"
                ]
            },
            {
                "restaurant_id": "restaurante_inexistente",
                "queries": [
                    "¿Qué tienen de especial?"
                ]
            }
        ]
        
        total_tests = 0
        successful_tests = 0
        
        for test_case in test_cases:
            restaurant_id = test_case["restaurant_id"]
            
            print(f"\n🏪 RESTAURANTE: {restaurant_id.upper()}")
            print("-" * 40)
            
            for i, query in enumerate(test_case["queries"], 1):
                total_tests += 1
                
                print(f"\n📝 Consulta {i}: {query}")
                
                # Prueba directa
                direct_response = await self.test_meta_agent_direct(restaurant_id, query)
                
                # Prueba vía ADK (simula despliegue)
                adk_response = await self.test_meta_agent_via_adk(restaurant_id, query)
                
                if direct_response and adk_response:
                    successful_tests += 1
                    print("✅ Ambas pruebas exitosas")
                else:
                    print("❌ Alguna prueba falló")
                
                # Pausa entre consultas
                await asyncio.sleep(1)
        
        # Resumen final
        print(f"\n🎉 RESUMEN DEL DEMO")
        print("=" * 30)
        print(f"✅ Pruebas exitosas: {successful_tests}/{total_tests}")
        print(f"📊 Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print("\n🎯 DEMO COMPLETADO EXITOSAMENTE")
            print("🚀 El meta-agente está listo para despliegue en Vertex AI")
        else:
            print("\n⚠️  Algunas pruebas fallaron - revisar configuración")
        
        return successful_tests, total_tests

async def interactive_demo():
    """Demo interactivo para probar consultas personalizadas"""
    demo = MetaAgentLocalDemo()
    
    print("\n🎮 DEMO INTERACTIVO DEL META-AGENTE")
    print("=" * 40)
    print("Ingresa consultas personalizadas para probar el sistema")
    print("Comandos especiales:")
    print("  'exit' - Salir del demo")
    print("  'list' - Ver restaurantes disponibles")
    print()
    
    while True:
        try:
            # Solicitar restaurant_id
            restaurant_id = input("🏪 Restaurant ID (ej: demo_restaurant): ").strip()
            
            if restaurant_id.lower() == 'exit':
                break
            elif restaurant_id.lower() == 'list':
                available = demo.meta_agent_instance.config_manager.get_available_restaurants()
                print(f"📋 Restaurantes disponibles: {list(available)}")
                continue
            
            if not restaurant_id:
                print("❌ Debes especificar un restaurant_id")
                continue
            
            # Solicitar consulta
            user_query = input("❓ Tu consulta: ").strip()
            
            if not user_query:
                print("❌ Debes especificar una consulta")
                continue
            
            print(f"\n🔄 Procesando consulta...")
            
            # Ejecutar prueba
            response = await demo.test_meta_agent_direct(restaurant_id, user_query)
            
            if response:
                print(f"\n💬 RESPUESTA COMPLETA:")
                print("-" * 50)
                print(response)
                print("-" * 50)
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Demo interrumpido por el usuario")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_deployment_readiness():
    """Mostrar información sobre la preparación para el despliegue"""
    
    readiness_info = """
🎯 PREPARACIÓN PARA EL DESPLIEGUE
================================

✅ COMPONENTES LISTOS:
• Meta-Agente implementado con arquitectura escalable
• Función de enrutamiento multi-tenant funcional
• Reutilización completa del sistema de las Fases 1-4
• Manejo de errores robusto
• Logging detallado para monitoreo

🔧 SIGUIENTE PASO - DESPLIEGUE EN VERTEX AI:

1. Configurar credenciales de Google Cloud:
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"

2. Configurar variables del proyecto:
   python deployer_meta_agent.py --deploy \\
     --project-id=tu-project-id \\
     --staging-bucket=tu-staging-bucket

3. Probar el agente desplegado:
   python deployer_meta_agent.py --test --agent-id=AGENT_ID

💡 VENTAJAS DE ESTA ARQUITECTURA:
• 💰 Costo: Un solo recurso desplegado vs N recursos
• 📈 Escalabilidad: Infinita sin límites por restaurante  
• 🛠️ Mantenimiento: Un solo punto de actualización
• ⚡ Performance: Reutilización eficiente de recursos

🎉 CAPACIDADES DEL SISTEMA:
• {count} restaurantes configurados y listos
• Onboarding automático con setup_restaurant.py
• Respuestas personalizadas por restaurante
• Cache inteligente para performance optimizada
"""
    
    # Contar restaurantes disponibles
    try:
        from src.restaurant.config.config_manager import ConfigManager
        config_manager = ConfigManager()
        restaurant_count = len(list(config_manager.get_available_restaurants()))
        print(readiness_info.format(count=restaurant_count))
    except Exception as e:
        print(readiness_info.format(count="N"))
        print(f"⚠️  No se pudo contar restaurantes: {e}")

async def main():
    """Función principal del demo"""
    import sys
    
    print("🤖 META-AGENTE MULTI-TENANT - DEMO LOCAL")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_demo()
    else:
        demo = MetaAgentLocalDemo()
        successful, total = await demo.run_comprehensive_demo()
        
        if successful == total:
            show_deployment_readiness()

if __name__ == "__main__":
    asyncio.run(main()) 