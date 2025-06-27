# Copyright 2025 Restaurant AI System
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""
Sistema Principal del Restaurante Multiagente
Integra todos los agentes especializados usando Agent Development Kit (ADK)
"""

import asyncio
import os
from typing import Any, Dict

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents.food_agent import FoodSpecialistAgent
from .agents.modern_system import create_modern_restaurant_system
from .config.system_config import SYSTEM_MESSAGES, SystemConfig


class RestaurantMultiAgentSystem:
    """
    Sistema Multiagente Principal para Restaurante

    Integra todos los componentes usando ADK:
    - Orquestador principal
    - Agentes especializados (comida, bebidas, nutrición)
    - Gestión de sesiones
    - Routing inteligente
    """

    def __init__(self):
        self.config = SystemConfig()
        self.session_service = InMemorySessionService()

        # Inicializar agentes especializados
        self.specialist_agents = self._initialize_specialist_agents()

        # Crear sistema moderno
        self.modern_system = create_modern_restaurant_system()

        # Crear runner principal
        self.runner = InMemoryRunner(
            agent=self.modern_system, app_name=self.config.app_name
        )

        print("🍽️ Sistema Multiagente del Restaurante inicializado correctamente!")
        print(
            f"📋 Agentes especializados activos: {list(self.specialist_agents.keys())}"
        )

    def _initialize_specialist_agents(self) -> Dict[str, Any]:
        """Inicializa todos los agentes especializados"""
        agents = {}

        # Agente especialista en comida
        food_agent = FoodSpecialistAgent(self.config)
        agents["food_agent"] = food_agent.agent

        # TODO: Agregar otros agentes especializados
        # drinks_agent = DrinksSpecialistAgent(self.config)
        # agents["drinks_agent"] = drinks_agent.agent

        # nutrition_agent = NutritionSpecialistAgent(self.config)
        # agents["nutrition_agent"] = nutrition_agent.agent

        return agents

    async def create_session(self, user_id: str = "default_user") -> str:
        """Crea una nueva sesión para un usuario"""
        session = await self.session_service.create_session(
            app_name=self.config.app_name, user_id=user_id
        )
        return session.id

    async def process_query(
        self, query: str, session_id: str = None, user_id: str = "default_user"
    ) -> str:
        """
        Procesa una consulta del cliente usando el sistema multiagente

        Args:
            query: Consulta del cliente
            session_id: ID de la sesión (se crea una nueva si no se proporciona)
            user_id: ID del usuario

        Returns:
            Respuesta del sistema
        """
        try:
            # Crear sesión si no existe
            if session_id is None:
                session_id = await self.create_session(user_id)

            # Crear contenido para el runner
            content = types.Content(role="user", parts=[types.Part(text=query)])

            # Procesar usando el runner de ADK
            response_parts = []
            async for event in self.runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)

            # El runner de ADK maneja automáticamente la respuesta del sistema moderno
            if response_parts:
                return "\n".join(response_parts)
            else:
                return "Sistema moderno procesando tu consulta..."

        except Exception as e:
            print(f"❌ Error procesando consulta: {e}")
            return SYSTEM_MESSAGES["es"]["error"]

    async def start_interactive_mode(self):
        """Inicia el modo interactivo para testing"""
        print("\n🎯 Modo Interactivo del Sistema Multiagente")
        print("=" * 50)
        print("Escribe 'salir' para terminar")
        print("Escribe 'menu' para ver opciones del menú")
        print("Escribe 'agentes' para ver agentes disponibles")
        print("-" * 50)

        session_id = await self.create_session()

        while True:
            try:
                user_input = input("\n🍽️ Tu consulta: ").strip()

                if user_input.lower() in ["salir", "exit", "quit"]:
                    print("\n👋 ¡Gracias por usar nuestro sistema! ¡Hasta pronto!")
                    break

                if user_input.lower() == "menu":
                    self._show_menu()
                    continue

                if user_input.lower() == "agentes":
                    self._show_agents()
                    continue

                if not user_input:
                    continue

                print("\n🤖 Procesando...")
                response = await self.process_query(user_input, session_id)
                print(f"\n💬 Respuesta: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Sistema interrumpido. ¡Hasta pronto!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def _show_menu(self):
        """Muestra el menú disponible"""
        print("\n📋 MENÚ DEL RESTAURANTE")
        print("=" * 40)

        from .config.system_config import RESTAURANT_DATA

        for category, items in RESTAURANT_DATA["menu"].items():
            print(f"\n🍽️ {category.upper()}:")
            for item in items:
                print(f"  • {item['name']} - €{item['price']}")
                print(f"    Ingredientes: {', '.join(item['ingredients'])}")
                if item.get("allergens"):
                    print(f"    ⚠️ Alérgenos: {', '.join(item['allergens'])}")
                print()

    def _show_agents(self):
        """Muestra los agentes disponibles"""
        print("\n🤖 AGENTES ESPECIALIZADOS")
        print("=" * 40)

        from .config.system_config import AGENT_CONFIGS

        for agent_id, config in AGENT_CONFIGS.items():
            status = (
                "✅ Activo" if agent_id in self.specialist_agents else "⏳ Pendiente"
            )
            print(f"\n{status} {config.name}")
            print(f"   Especialidad: {config.specialization}")
            print(f"   Descripción: {config.description}")
            print(f"   Palabras clave: {', '.join(config.keywords[:5])}...")


# Funciones de demostración
async def demo_basic_functionality():
    """Demuestra la funcionalidad básica del sistema"""
    print("\n🚀 DEMO: Funcionalidad Básica del Sistema")
    print("=" * 50)

    system = RestaurantMultiAgentSystem()

    # Casos de prueba
    test_queries = [
        "Hola, ¿qué platos recomiendan?",
        "¿Tienen opciones sin gluten?",
        "¿Qué ingredientes tiene la ensalada César?",
        "¿Hay algo para alguien alérgico al pescado?",
        "¿Cuál es su especialidad de la casa?",
    ]

    session_id = await system.create_session("demo_user")

    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Consulta {i} ---")
        print(f"Cliente: {query}")

        response = await system.process_query(query, session_id, "demo_user")
        print(f"Sistema: {response}")

        await asyncio.sleep(1)  # Pausa para mejor visualización


async def demo_agent_routing():
    """Demuestra el routing entre agentes especializados"""
    print("\n🎯 DEMO: Routing de Agentes Especializados")
    print("=" * 50)

    system = RestaurantMultiAgentSystem()

    # Consultas específicas para cada agente
    routing_tests = [
        ("food_agent", "¿Qué platos tienen salmón en el menú?"),
        ("nutrition_agent", "¿Qué opciones hay para una dieta vegana?"),
        ("drinks_agent", "¿Qué vino recomiendan con el salmón?"),
        ("general", "¿Están abiertos los domingos?"),  # Consulta general
    ]

    for expected_agent, query in routing_tests:
        print(f"\n--- Routing Test: {expected_agent} ---")
        print(f"Consulta: {query}")

        # Analizar intención
        intent = system.orchestrator.analyze_user_intent(query)
        print(f"Agente recomendado: {intent['recommended_agent']}")
        print(f"Confianza: {intent['confidence']:.2f}")

        response = await system.process_query(query)
        print(f"Respuesta: {response[:100]}...")


# Función principal
async def main():
    """Función principal del sistema"""
    print("🍽️ SISTEMA MULTIAGENTE PARA RESTAURANTE")
    print("Basado en Agent Development Kit (ADK) de Google")
    print("=" * 60)

    # Verificar configuración del entorno
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("⚠️ ADVERTENCIA: No se encontraron credenciales de Google AI/Cloud")
        print("Por favor, configura GOOGLE_API_KEY o las credenciales de Google Cloud")
        print("Para esta demo, el sistema funcionará con respuestas simuladas\n")

    # Crear sistema
    system = RestaurantMultiAgentSystem()

    # Mostrar opciones
    while True:
        print("\n📋 OPCIONES DISPONIBLES:")
        print("1. 🎮 Modo Interactivo")
        print("2. 🧪 Demo Funcionalidad Básica")
        print("3. 🎯 Demo Routing de Agentes")
        print("4. 📋 Ver Menú")
        print("5. 🤖 Ver Agentes")
        print("6. 🚪 Salir")

        choice = input("\nElige una opción (1-6): ").strip()

        if choice == "1":
            await system.start_interactive_mode()
        elif choice == "2":
            await demo_basic_functionality()
        elif choice == "3":
            await demo_agent_routing()
        elif choice == "4":
            system._show_menu()
        elif choice == "5":
            system._show_agents()
        elif choice == "6":
            print("\n👋 ¡Gracias por usar el sistema! ¡Hasta pronto!")
            break
        else:
            print("❌ Opción no válida. Por favor, elige 1-6.")


if __name__ == "__main__":
    asyncio.run(main())
