# Copyright 2025 Restaurant AI System
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""
Configuración para ADK Web UI
Permite probar y debuggear el sistema multiagente del restaurante
"""

import os
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.models import Gemini

from .config.system_config import SystemConfig, AGENT_CONFIGS
from .agents.food_agent import FoodSpecialistAgent

class RestaurantWebConfig:
    """
    Configuración para ADK Web UI
    Expone los agentes para testing en la interfaz web
    """
    
    def __init__(self):
        self.config = SystemConfig()
        self.session_service = InMemorySessionService()
        
        # Configurar agentes para web testing
        self.agents = self._setup_agents_for_web()
        
    def _setup_agents_for_web(self) -> Dict[str, LlmAgent]:
        """Configura los agentes para ser probados en ADK Web UI"""
        agents = {}
        
        # 1. Agente Especialista en Comida
        food_specialist = FoodSpecialistAgent(self.config)
        agents["food_specialist"] = food_specialist.agent
        
        # 2. Agente Orquestador Simplificado para testing directo
        orchestrator_simple = LlmAgent(
            name="RestaurantOrchestrator_WebTest",
            model=Gemini(model=self.config.default_model),
            instruction="""
Eres el orquestador principal de un sistema multiagente para un restaurante.

Tu misión es proporcionar la mejor experiencia de atención al cliente mediante:

1. **COMUNICACIÓN DIRECTA**: Eres la cara visible del restaurante
   - Saluda cordialmente a los clientes
   - Mantén un tono amigable y profesional
   - Adapta el idioma del cliente automáticamente

2. **INFORMACIÓN DEL RESTAURANTE**: Conoces todo sobre nuestro restaurante
   - Menú: Ensalada César Gourmet (€12.50), Salmón a la Plancha (€24.90)
   - Horarios: Lunes a Domingo 12:00-23:00
   - Especialidades: Cocina mediterránea con ingredientes frescos
   - Opciones especiales: Sin gluten, vegetarianos, veganos

3. **ATENCIÓN AL CLIENTE**: Responde de forma útil y completa
   - Para consultas sobre comida, proporciona información detallada
   - Menciona alérgenos cuando sea relevante
   - Ofrece recomendaciones personalizadas
   - Si no sabes algo específico, sé honesto pero ofrece alternativas

**MENÚ DISPONIBLE**:
- Ensalada César Gourmet (€12.50): lechuga romana, parmesano, crutones, anchoas, aderezo césar
  - Alérgenos: gluten, pescado, lácteos
  - Calorías: 280
- Salmón a la Plancha (€24.90): salmón fresco, verduras asadas, quinoa, salsa de limón
  - Alérgenos: pescado
  - Calorías: 450
  - Sin gluten, alto en omega-3

**INSTRUCCIONES ESPECIALES**:
- Siempre prioriza la seguridad alimentaria en casos de alergias
- Ofrece alternativas cuando algo no esté disponible
- Mantén las respuestas concisas pero informativas
- Usa un tono cálido y acogedor del restaurante

Ejemplos de respuestas:
- Cliente: "¿Tienen algo sin gluten?" → "¡Por supuesto! Nuestro Salmón a la Plancha es una excelente opción sin gluten..."
- Cliente: "¿Qué me recomiendan?" → "Me encanta recomendar nuestras especialidades. Si te gusta el pescado..."
""",
            description="Orquestador principal del restaurante para testing web"
        )
        agents["orchestrator"] = orchestrator_simple
        
        # 3. Agente de Demostración para casos específicos
        demo_agent = LlmAgent(
            name="RestaurantDemo",
            model=Gemini(model=self.config.default_model),
            instruction="""
Eres un agente de demostración para el sistema multiagente del restaurante.

Responde siempre con ejemplos específicos de nuestro menú:

**RESPUESTAS DE DEMOSTRACIÓN**:
- Si preguntan por recomendaciones: "Te recomiendo nuestra Ensalada César Gourmet (€12.50) o el Salmón a la Plancha (€24.90)"
- Si preguntan por alérgenos: "La Ensalada César contiene gluten, pescado y lácteos. El Salmón solo contiene pescado."
- Si preguntan por opciones saludables: "El Salmón a la Plancha es perfecto: 450 calorías, rico en omega-3 y sin gluten"
- Si preguntan por vegetarianos: "La Ensalada César es vegetariana, aunque contiene anchoas para el sabor auténtico"

Mantén respuestas cortas y específicas para demostración rápida.
""",
            description="Agente de demostración con respuestas predefinidas"
        )
        agents["demo"] = demo_agent
        
        return agents
    
    def get_agent_configs_for_web(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene configuraciones de agentes para ADK Web UI"""
        configs = {}
        
        for agent_name, agent in self.agents.items():
            configs[agent_name] = {
                "name": agent.name,
                "description": agent.description,
                "model": self.config.default_model,
                "instructions_preview": agent.instruction[:200] + "..." if len(agent.instruction) > 200 else agent.instruction,
                "tools_count": len(getattr(agent, 'tools', [])),
                "agent_type": "LlmAgent"
            }
        
        return configs
    
    def create_runner_for_agent(self, agent_name: str) -> InMemoryRunner:
        """Crea un runner para un agente específico para testing web"""
        if agent_name not in self.agents:
            raise ValueError(f"Agente '{agent_name}' no encontrado")
        
        agent = self.agents[agent_name]
        
        runner = InMemoryRunner(
            agent=agent,
            app_name=f"restaurant_web_test_{agent_name}",
            session_service=self.session_service
        )
        
        return runner

# Configuración global para ADK Web
def get_web_config():
    """Función para obtener la configuración web global"""
    return RestaurantWebConfig()

# Casos de prueba predefinidos para ADK Web
WEB_TEST_CASES = [
    {
        "name": "Consulta General",
        "query": "Hola, ¿qué me recomiendan para comer hoy?",
        "expected_topics": ["recomendaciones", "menú", "especialidades"],
        "agent": "orchestrator"
    },
    {
        "name": "Consulta sobre Alérgenos",
        "query": "¿Qué opciones tienen sin gluten?",
        "expected_topics": ["sin gluten", "alérgenos", "salmón"],
        "agent": "food_specialist"
    },
    {
        "name": "Información de Plato",
        "query": "¿Qué ingredientes tiene la ensalada César?",
        "expected_topics": ["ingredientes", "ensalada césar", "alérgenos"],
        "agent": "food_specialist"
    },
    {
        "name": "Consulta de Precios",
        "query": "¿Cuánto cuesta el salmón?",
        "expected_topics": ["precio", "salmón", "24.90"],
        "agent": "demo"
    },
    {
        "name": "Opciones Vegetarianas",
        "query": "¿Tienen opciones vegetarianas?",
        "expected_topics": ["vegetariano", "ensalada", "opciones"],
        "agent": "orchestrator"
    }
]

# Variables de entorno para ADK Web
WEB_ENV_CONFIG = {
    "ADK_WEB_PORT": "8080",
    "ADK_WEB_HOST": "localhost",
    "ADK_WEB_DEBUG": "true",
    "ADK_WEB_AUTO_RELOAD": "true"
} 