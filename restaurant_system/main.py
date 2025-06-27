#!/usr/bin/env python3
"""
Punto de Entrada Principal - Sistema de Restaurante SaaS
Fase 3: Integración ConfigManager + FoodSpecialistAgent dinámico

Uso:
    python main.py --restaurant_id demo_restaurant
    python main.py --restaurant_id mi_restaurante_favorito
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Agregar src al path para importaciones
sys.path.insert(0, str(Path(__file__).parent / "src"))

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from restaurant.config.config_manager import (
    ConfigManager, 
    RestaurantNotFoundError, 
    ConfigValidationError
)
from restaurant.agents.food_agent import FoodSpecialistAgent


class RestaurantAISystem:
    """
    Sistema de IA para Restaurante Multi-Tenant
    
    Utiliza ConfigManager + FoodSpecialistAgent dinámico para crear
    experiencias personalizadas por restaurante usando google/adk-python.
    """
    
    def __init__(self, restaurant_id: str):
        """
        Inicializa el sistema para un restaurante específico
        
        Args:
            restaurant_id: ID único del restaurante a cargar
        """
        self.restaurant_id = restaurant_id
        self.config_manager = ConfigManager()
        
        # Cargar configuración del restaurante
        self.restaurant_config = self._load_restaurant_config()
        
        # Crear agente dinámico
        self.food_agent = FoodSpecialistAgent(restaurant_config=self.restaurant_config)
        
        # Configurar ADK Runner
        self.session_service = InMemorySessionService()
        self.runner = InMemoryRunner(
            agent=self.food_agent.agent,
            app_name=f"restaurant_{restaurant_id}"
        )
        
        print(f"🎉 Sistema inicializado para: {self.restaurant_config.metadata.name}")
        print(f"👨‍🍳 Agente activo: {self.food_agent.agent_config.name}")
        print(f"🍽️ Especialización: {self.food_agent.agent_config.specialization}")
    
    def _load_restaurant_config(self):
        """Carga y valida la configuración del restaurante"""
        try:
            print(f"📋 Cargando configuración para restaurante: {self.restaurant_id}")
            config = self.config_manager.load_restaurant_config(self.restaurant_id)
            print(f"✅ Configuración cargada exitosamente")
            return config
            
        except RestaurantNotFoundError:
            print(f"❌ Error: Restaurante '{self.restaurant_id}' no encontrado")
            available = self.config_manager.list_restaurants()
            if available:
                print(f"🏪 Restaurantes disponibles: {', '.join(available)}")
            else:
                print("🏪 No hay restaurantes configurados")
            sys.exit(1)
            
        except ConfigValidationError as e:
            print(f"❌ Error de validación en configuración: {e}")
            sys.exit(1)
            
        except Exception as e:
            print(f"❌ Error inesperado cargando configuración: {e}")
            sys.exit(1)
    
    async def create_session(self, user_id: str = "default_user") -> str:
        """Crea una nueva sesión para un usuario"""
        session = await self.session_service.create_session(
            app_name=f"restaurant_{self.restaurant_id}",
            user_id=user_id
        )
        return session.id
    
    async def chat_with_agent(self, message: str, session_id: str, user_id: str = "default_user") -> str:
        """
        Envía un mensaje al agente y retorna la respuesta
        
        Args:
            message: Mensaje del usuario
            session_id: ID de la sesión
            user_id: ID del usuario
            
        Returns:
            Respuesta del agente
        """
        try:
            # Crear contenido para el runner
            content = types.Content(role="user", parts=[types.Part(text=message)])
            
            # Procesar usando ADK Runner
            response_parts = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
            
            if response_parts:
                return "\n".join(response_parts)
            else:
                return "🤖 Lo siento, no pude procesar tu mensaje. ¿Podrías intentar de nuevo?"
                
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
            return "🤖 Disculpa, hubo un error técnico. Por favor, inténtalo de nuevo."
    
    def show_restaurant_info(self):
        """Muestra información del restaurante cargado"""
        config = self.restaurant_config
        print(f"\n🏪 INFORMACIÓN DEL RESTAURANTE")
        print("=" * 50)
        print(f"📋 Nombre: {config.metadata.name}")
        print(f"📍 Ubicación: {config.metadata.location}")
        print(f"🍽️ Tipo: {config.metadata.type}")
        print(f"🗣️ Idiomas: {', '.join(config.metadata.languages)}")
        print(f"👨‍🍳 Chef: {self.food_agent.agent_config.name}")
        print(f"🎯 Especialización: {self.food_agent.agent_config.specialization}")
        
        # Mostrar branding
        branding = config.restaurant_data.get('branding', {})
        if branding:
            print(f"🎨 Personalidad: {branding.get('personality', 'N/A')}")
            print(f"💭 Tono: {branding.get('tone', 'N/A')}")
    
    def show_menu_summary(self):
        """Muestra un resumen del menú"""
        menu = self.restaurant_config.restaurant_data['menu']
        total_dishes = sum(len(dishes) for dishes in menu.values())
        
        print(f"\n🍝 RESUMEN DEL MENÚ")
        print("=" * 50)
        print(f"📋 Categorías: {', '.join(menu.keys())}")
        print(f"🍽️ Total de platos: {total_dishes}")
        print(f"💡 Pregunta al chef sobre cualquier plato específico!")
    
    async def start_chat_loop(self):
        """Inicia el bucle de chat interactivo"""
        print(f"\n💬 CHAT CON {self.food_agent.agent_config.name}")
        print("=" * 50)
        
        # Mostrar saludo personalizado
        branding = self.restaurant_config.restaurant_data.get('branding', {})
        greeting = branding.get('greeting_es', f"¡Hola! Soy {self.food_agent.agent_config.name}")
        if '{agent_name}' in greeting:
            greeting = greeting.replace('{agent_name}', self.food_agent.agent_config.name)
        
        print(f"👨‍🍳 {greeting}")
        print("\nComandos especiales:")
        print("  • 'info' - Información del restaurante")
        print("  • 'menu' - Resumen del menú") 
        print("  • 'salir' - Terminar chat")
        print("-" * 50)
        
        # Crear sesión
        session_id = await self.create_session()
        
        while True:
            try:
                user_input = input(f"\n🍽️ Tú: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiales
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print(f"\n👨‍🍳 {self.food_agent.agent_config.name}: ¡Gracias por visitarnos! ¡Esperamos verte pronto!")
                    break
                
                if user_input.lower() == 'info':
                    self.show_restaurant_info()
                    continue
                
                if user_input.lower() == 'menu':
                    self.show_menu_summary()
                    continue
                
                # Procesar mensaje con el agente
                print("🤖 Procesando...")
                response = await self.chat_with_agent(user_input, session_id)
                print(f"\n👨‍🍳 {self.food_agent.agent_config.name}: {response}")
                
            except KeyboardInterrupt:
                print(f"\n\n👨‍🍳 {self.food_agent.agent_config.name}: ¡Hasta la próxima!")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")


def parse_arguments():
    """Configura y parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Sistema de IA para Restaurante Multi-Tenant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --restaurant_id demo_restaurant
  python main.py --restaurant_id mi_pizzeria
  python main.py --restaurant_id restaurant_tokyo

El sistema cargará la configuración específica del restaurante
y creará una experiencia personalizada con el chef virtual.
        """
    )
    
    parser.add_argument(
        '--restaurant_id',
        type=str,
        required=True,
        help='ID único del restaurante a cargar (obligatorio)'
    )
    
    return parser.parse_args()


def main():
    """Función principal del sistema"""
    print("🎯 Sistema de Restaurante SaaS - Fase 3")
    print("Integración ConfigManager + FoodSpecialistAgent Dinámico")
    print()
    
    # Parsear argumentos
    args = parse_arguments()
    
    try:
        # Inicializar sistema para el restaurante específico
        restaurant_system = RestaurantAISystem(restaurant_id=args.restaurant_id)
        
        # Mostrar información del restaurante
        restaurant_system.show_restaurant_info()
        restaurant_system.show_menu_summary()
        
        # Iniciar chat interactivo
        asyncio.run(restaurant_system.start_chat_loop())
        
    except KeyboardInterrupt:
        print("\n\n👋 Sistema interrumpido. ¡Hasta pronto!")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 