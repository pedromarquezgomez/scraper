# Copyright 2025 Restaurant AI System
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""
Agente Orquestador Principal
Maneja la comunicación con el cliente y enruta consultas a agentes especializados
"""

import asyncio
from typing import Dict, List, Optional, Tuple
import json
import re

from google.adk.agents import LlmAgent, Agent
from google.adk.tools import FunctionTool, AgentTool
from google.adk.models import Gemini
from google.genai import types

from ..config.system_config import (
    AGENT_CONFIGS, ROUTING_CONFIG, SYSTEM_MESSAGES, SystemConfig
)

class RestaurantOrchestrator:
    """
    Agente Orquestador Principal del Sistema Multiagente
    
    Responsabilidades:
    - Comunicación directa con el cliente
    - Identificación de intención y routing inteligente
    - Coordinación entre agentes especializados
    - Soporte multiidioma
    - Unificación de respuestas
    """
    
    def __init__(self, specialist_agents: Dict[str, Agent], config: SystemConfig):
        self.config = config
        self.specialist_agents = specialist_agents
        self.routing_config = ROUTING_CONFIG
        
        # Crear herramientas para comunicación con agentes especializados
        self.agent_tools = self._create_agent_tools()
        
        # Crear el agente orquestador usando ADK
        self.orchestrator_agent = self._create_orchestrator_agent()
    
    def _create_agent_tools(self) -> List[AgentTool]:
        """Crea AgentTools para comunicación con agentes especializados"""
        agent_tools = []
        
        for agent_id, agent in self.specialist_agents.items():
            config = AGENT_CONFIGS[agent_id]
            
            # Crear AgentTool para cada especialista
            agent_tool = AgentTool(
                agent=agent,
                name=f"consult_{config.specialization}_specialist",
                description=f"Consulta al especialista en {config.specialization}: {config.description}"
            )
            agent_tools.append(agent_tool)
        
        return agent_tools
    
    def _create_orchestrator_agent(self) -> LlmAgent:
        """Crea el agente orquestador principal usando LlmAgent de ADK"""
        
        # Función para detectar idioma
        def detect_language(text: str) -> str:
            """Detecta el idioma del texto del usuario"""
            # Implementación simple basada en palabras clave
            spanish_keywords = ["hola", "gracias", "por favor", "menú", "comida", "bebida"]
            english_keywords = ["hello", "thank", "please", "menu", "food", "drink"]
            
            text_lower = text.lower()
            spanish_count = sum(1 for word in spanish_keywords if word in text_lower)
            english_count = sum(1 for word in english_keywords if word in text_lower)
            
            return "es" if spanish_count > english_count else "en"
        
        # Función para routing inteligente
        def analyze_user_intent(query: str, context: str = "") -> Dict:
            """Analiza la intención del usuario y determina el agente apropiado"""
            query_lower = query.lower()
            
            # Scoring por keywords
            scores = {}
            for agent_id, config in AGENT_CONFIGS.items():
                score = 0
                for keyword in config.keywords:
                    if keyword.lower() in query_lower:
                        score += 1
                scores[agent_id] = score
            
            # Determinar el mejor agente
            best_agent = max(scores, key=scores.get) if scores else "food_agent"
            confidence = scores.get(best_agent, 0) / len(AGENT_CONFIGS[best_agent].keywords)
            
            return {
                "recommended_agent": best_agent,
                "confidence": confidence,
                "scores": scores,
                "needs_clarification": confidence < self.routing_config["confidence_threshold"]
            }
        
        # Agregar funciones como herramientas
        function_tools = [
            FunctionTool.create(self.__class__, "detect_language"),
            FunctionTool.create(self.__class__, "analyze_user_intent"),
        ]
        
        # Combinar con agent tools
        all_tools = function_tools + self.agent_tools
        
        # Crear agente orquestador
        orchestrator = LlmAgent(
            name="RestaurantOrchestrator",
            model=Gemini(model=self.config.default_model),
            instruction=f"""
Eres el orquestador principal de un sistema multiagente para un restaurante.

Tu misión es proporcionar la mejor experiencia de atención al cliente mediante:

1. **COMUNICACIÓN DIRECTA**: Eres la cara visible del restaurante
   - Saluda cordialmente a los clientes
   - Mantén un tono amigable y profesional
   - Adapta el idioma del cliente automáticamente

2. **ANÁLISIS DE INTENCIÓN**: Identifica qué necesita el cliente
   - Comida: menú, platos, ingredientes, alérgenos
   - Bebidas: vinos, cócteles, maridajes
   - Nutrición: dietas, alergias, información nutricional

3. **ROUTING INTELIGENTE**: Deriva consultas a especialistas cuando sea necesario
   - Usa las herramientas disponibles para consultar especialistas
   - Si la intención no está clara, pregunta al cliente para clarificar
   - Para consultas simples, responde directamente

4. **UNIFICACIÓN DE RESPUESTAS**: Integra información de múltiples fuentes
   - Combina respuestas de diferentes especialistas cuando sea útil
   - Mantén coherencia en el tono y estilo
   - Asegúrate de que la respuesta final sea completa y útil

**AGENTES ESPECIALIZADOS DISPONIBLES**:
{json.dumps({k: v.description for k, v in AGENT_CONFIGS.items()}, indent=2, ensure_ascii=False)}

**INSTRUCCIONES ESPECIALES**:
- Siempre prioriza la seguridad alimentaria en casos de alergias
- Ofrece alternativas cuando algo no esté disponible
- Mantén las respuestas concisas pero informativas
- Usa un tono cálido y acogedor del restaurante

Ejemplo de flujo:
Cliente: "¿Tienen algo sin gluten?"
1. Detecta que es sobre dieta/nutrición
2. Consulta al especialista en nutrición
3. Opcionalmente consulta al especialista en comida
4. Unifica la respuesta con opciones concretas del menú
""",
            tools=all_tools,
            description="Orquestador principal del sistema multiagente del restaurante"
        )
        
        return orchestrator

    async def process_customer_query(self, query: str, session_context: Dict = None) -> str:
        """
        Procesa una consulta del cliente usando el agente orquestador
        
        Args:
            query: Consulta del cliente
            session_context: Contexto de la sesión (idioma, preferencias, etc.)
            
        Returns:
            Respuesta unificada para el cliente
        """
        try:
            # Detectar idioma si no está en el contexto
            if session_context is None:
                session_context = {}
            
            if "language" not in session_context:
                session_context["language"] = self.detect_language(query)
            
            # Crear contenido para el agente
            content = types.Content(
                role='user',
                parts=[types.Part(text=query)]
            )
            
            # Aquí se integraría con el Runner de ADK
            # Por ahora simulamos la respuesta del orquestador
            intent_analysis = self.analyze_user_intent(query)
            
            if intent_analysis["needs_clarification"]:
                lang = session_context.get("language", "es")
                return SYSTEM_MESSAGES[lang]["routing_clarification"]
            
            # Simular consulta al agente especializado apropiado
            recommended_agent = intent_analysis["recommended_agent"]
            specialist_response = await self._consult_specialist(
                recommended_agent, query, session_context
            )
            
            # Unificar respuesta
            unified_response = self._unify_response(
                query, specialist_response, session_context
            )
            
            return unified_response
            
        except Exception as e:
            lang = session_context.get("language", "es") if session_context else "es"
            return SYSTEM_MESSAGES[lang]["error"]
    
    async def _consult_specialist(self, agent_id: str, query: str, context: Dict) -> str:
        """Consulta a un agente especializado"""
        # Aquí se integraría con AgentTool en el sistema real
        # Por ahora retornamos respuesta simulada
        config = AGENT_CONFIGS[agent_id]
        return f"[Respuesta simulada del {config.name}] Procesando consulta sobre {config.specialization}: '{query}'"
    
    def _unify_response(self, original_query: str, specialist_response: str, context: Dict) -> str:
        """Unifica y mejora la respuesta del especialista"""
        lang = context.get("language", "es")
        
        # En el sistema real, esto usaría el LlmAgent para generar una respuesta unificada
        unified = f"""
Basándome en tu consulta "{original_query}":

{specialist_response}

¿Hay algo más en lo que pueda ayudarte hoy?
"""
        return unified.strip()
    
    # Métodos auxiliares para las herramientas
    def detect_language(self, text: str) -> str:
        """Detecta el idioma del texto del usuario"""
        spanish_keywords = ["hola", "gracias", "por favor", "menú", "comida", "bebida"]
        english_keywords = ["hello", "thank", "please", "menu", "food", "drink"]
        
        text_lower = text.lower()
        spanish_count = sum(1 for word in spanish_keywords if word in text_lower)
        english_count = sum(1 for word in english_keywords if word in text_lower)
        
        return "es" if spanish_count > english_count else "en"
    
    def analyze_user_intent(self, query: str, context: str = "") -> Dict:
        """Analiza la intención del usuario y determina el agente apropiado"""
        query_lower = query.lower()
        
        # Scoring por keywords
        scores = {}
        for agent_id, config in AGENT_CONFIGS.items():
            score = 0
            for keyword in config.keywords:
                if keyword.lower() in query_lower:
                    score += 1
            scores[agent_id] = score
        
        # Determinar el mejor agente
        best_agent = max(scores, key=scores.get) if scores else "food_agent"
        confidence = scores.get(best_agent, 0) / len(AGENT_CONFIGS[best_agent].keywords) if AGENT_CONFIGS[best_agent].keywords else 0
        
        return {
            "recommended_agent": best_agent,
            "confidence": confidence,
            "scores": scores,
            "needs_clarification": confidence < self.routing_config["confidence_threshold"]
        } 