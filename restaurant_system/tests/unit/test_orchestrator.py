"""
Tests unitarios para el orquestador del sistema multiagente.
Siguiendo las mejores prácticas de testing de ADK.
"""

import asyncio
import os
import sys
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from restaurant.config.system_config import AGENT_CONFIGS
from restaurant.agents.orchestrator_agent import RestaurantOrchestrator
from restaurant.agents.food_agent import FoodSpecialistAgent


class TestMainOrchestrator:
    """Tests para el orquestador principal del sistema."""

    @pytest.fixture
    def mock_specialist_agents(self):
        """Crea agentes especializados mock para testing."""
        agents = {}
        for agent_id in AGENT_CONFIGS.keys():
            mock_agent = Mock()
            mock_agent.name = f"Mock_{agent_id}"
            agents[agent_id] = mock_agent
        return agents

    @pytest.fixture 
    def config(self):
        """Configuración mock para testing."""
        from restaurant.config.system_config import SystemConfig
        return SystemConfig()

    @pytest.fixture
    def orchestrator(self, mock_specialist_agents, config):
        """Crea una instancia del orquestador para testing."""
        return RestaurantOrchestrator(mock_specialist_agents, config)

    def test_orchestrator_initialization(self, orchestrator):
        """Test inicialización correcta del orquestador."""
        assert orchestrator.orchestrator_agent is not None
        assert orchestrator.orchestrator_agent.name == "RestaurantOrchestrator"
        assert len(orchestrator.specialist_agents) == len(AGENT_CONFIGS)

    def test_language_detection_spanish(self, orchestrator):
        """Test detección de idioma español."""
        spanish_queries = [
            "¿Qué platos tienen en el menú?",
            "Hola, ¿tienen opciones veganas?", 
            "Gracias por la información sobre vinos",
        ]

        for query in spanish_queries:
            language = orchestrator.detect_language(query)
            assert language == "es"

    def test_language_detection_english(self, orchestrator):
        """Test detección de idioma inglés."""
        english_queries = [
            "What dishes do you have on the menu?",
            "Hello, do you have vegan options?",
            "Thank you for the wine information",
        ]

        for query in english_queries:
            language = orchestrator.detect_language(query)
            assert language == "en"

    def test_intent_analysis(self, orchestrator):
        """Test análisis de intención de consultas."""
        test_cases = [
            ("¿Qué platos tienen?", "food_agent"),
            ("¿Qué vinos recomiendan?", "drinks_agent"), 
            ("¿Tienen opciones sin gluten?", "nutrition_agent"),
        ]

        for query, expected_agent in test_cases:
            intent = orchestrator.analyze_user_intent(query, "")
            intent_str = str(intent).lower() if isinstance(intent, dict) else intent.lower()
            assert expected_agent in intent_str

    @pytest.mark.asyncio
    async def test_process_customer_query(self, orchestrator):
        """Test procesamiento básico de consultas."""
        query = "¿Qué platos tienen en el menú?"
        
        response = await orchestrator.process_customer_query(query)
        assert isinstance(response, str)
        assert len(response) > 0
        
    def test_system_with_real_agents(self):
        """Test con agentes reales del sistema."""
        # Test simplificado sin dependencias externas
        from restaurant.config.system_config import SystemConfig
        from restaurant.agents.food_agent import FoodSpecialistAgent
        
        config = SystemConfig()
        food_agent = FoodSpecialistAgent(config)
        specialist_agents = {"food_agent": food_agent}
        
        orchestrator = RestaurantOrchestrator(specialist_agents, config)
        assert orchestrator.orchestrator_agent is not None
        assert len(orchestrator.specialist_agents) > 0
        assert "food_agent" in orchestrator.specialist_agents


# Fixtures globales para testing
@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para toda la sesión de testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Marcadores personalizados para pytest
pytestmark = [pytest.mark.unit, pytest.mark.asyncio]
