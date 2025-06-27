# Copyright 2025 Restaurant AI System - SaaS Platform
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""
Agente Especialista en Comida - Refactorizado para Arquitectura SaaS
Configuración dinámica multi-tenant usando ConfigManager
Compatible con google/adk-python v1.5.0+
"""

import json
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent  # Usando Agent en lugar de LlmAgent (ADK v1.5+)
from google.adk.tools import FunctionTool

# Importar tipos de configuración del ConfigManager
from ..config.config_manager import RestaurantConfig, RestaurantMetadata
from ..config.system_config import AgentConfig


class FoodSpecialistAgent:
    """
    Agente Especialista en Comida y Gastronomía - Arquitectura SaaS
    
    FASE 2: Configuración Dinámica Multi-Tenant

    Responsabilidades:
    - Información detallada sobre platos del menú del restaurante específico
    - Ingredientes y métodos de preparación personalizados
    - Identificación de alérgenos según datos del cliente
    - Recomendaciones personalizadas basadas en configuración del restaurante
    - Branding y personalidad del restaurante específico
    
    Características SaaS:
    - Sin referencias estáticas a archivos de configuración
    - Recibe configuración dinámica en el constructor
    - Completamente reutilizable entre restaurantes
    - Compatible con google/adk-python mejores prácticas
    """

    def __init__(self, 
                 restaurant_config: RestaurantConfig,
                 agent_config: Optional[AgentConfig] = None):
        """
        Inicializa el agente con configuración dinámica del ConfigManager
        
        Args:
            restaurant_config: Configuración completa del restaurante (de ConfigManager)
            agent_config: Configuración específica del agente (opcional, usa food_agent por defecto)
        """
        # Configuración dinámica recibida del ConfigManager
        self.restaurant_config = restaurant_config
        self.metadata = restaurant_config.metadata
        self.menu_data = restaurant_config.restaurant_data["menu"]
        self.branding = restaurant_config.restaurant_data.get("branding", {})
        self.restaurant_info = restaurant_config.restaurant_data.get("restaurant_info", {})
        
        # Configuración del agente (inyectada dinámicamente)
        self.agent_config = agent_config or restaurant_config.agent_configs.get("food_agent")
        if not self.agent_config:
            raise ValueError("No se pudo encontrar configuración para food_agent")

        # Crear herramientas específicas usando datos dinámicos del restaurante
        self.tools = self._create_food_tools()

        # Crear agente ADK usando configuración dinámica
        self.agent = self._create_agent()

    def _create_food_tools(self) -> List[FunctionTool]:
        """
        Crea herramientas específicas para consultas gastronómicas
        Usa datos dinámicos del restaurante específico (no estáticos)
        """

        def get_menu_items(
            category: str = None, 
            dietary_restrictions: List[str] = None
        ) -> Dict[str, Any]:
            """
            Obtiene elementos del menú filtrados por categoría y restricciones dietéticas

            Args:
                category: Categoría del menú del restaurante específico
                dietary_restrictions: Lista de restricciones (sin_gluten, vegano, etc.)

            Returns:
                Diccionario con los platos que coinciden con los filtros
            """
            result = {
                "restaurant": self.metadata.name,
                "restaurant_type": self.metadata.type,
                "items": [], 
                "total_count": 0
            }

            # Obtener todas las categorías disponibles en este restaurante específico
            available_categories = list(self.menu_data.keys())
            categories = [category] if category else available_categories

            for cat in categories:
                if cat in self.menu_data:
                    items = self.menu_data[cat]

                    # Filtrar por restricciones dietéticas usando datos del restaurante
                    if dietary_restrictions:
                        filtered_items = []
                        for item in items:
                            diet_tags = item.get("diet_tags", [])
                            allergens = item.get("allergens", [])

                            meets_restrictions = True
                            for restriction in dietary_restrictions:
                                if restriction == "sin_gluten" and "gluten" in allergens:
                                    meets_restrictions = False
                                elif restriction == "vegano" and restriction not in diet_tags:
                                    meets_restrictions = False
                                elif restriction == "vegetariano" and restriction not in diet_tags:
                                    meets_restrictions = False

                            if meets_restrictions:
                                filtered_items.append(item)
                        items = filtered_items

                    result["items"].extend([{"category": cat, **item} for item in items])

            result["total_count"] = len(result["items"])
            result["available_categories"] = available_categories
            return result

        def get_dish_details(dish_name: str) -> Dict[str, Any]:
            """
            Obtiene información detallada de un plato específico del restaurante

            Args:
                dish_name: Nombre del plato a consultar

            Returns:
                Información completa del plato o sugerencias si no se encuentra
            """
            dish_name_lower = dish_name.lower()

            for category, items in self.menu_data.items():
                for item in items:
                    if dish_name_lower in item["name"].lower():
                        return {
                            "found": True,
                            "restaurant": self.metadata.name,
                            "category": category,
                            "details": item,
                            "preparation_info": self._get_preparation_info(item["name"]),
                            "allergen_details": self._get_allergen_details(item.get("allergens", [])),
                            "restaurant_specialty": self._is_restaurant_specialty(item["name"])
                        }

            return {
                "found": False,
                "restaurant": self.metadata.name,
                "suggestions": self._suggest_similar_dishes(dish_name),
                "available_categories": list(self.menu_data.keys())
            }

        def check_allergens(allergens_to_avoid: List[str]) -> Dict[str, Any]:
            """
            Identifica platos seguros para personas con alergias específicas
            Usando datos específicos del restaurante

            Args:
                allergens_to_avoid: Lista de alérgenos a evitar

            Returns:
                Lista de platos seguros y platos a evitar del restaurante específico
            """
            safe_dishes = []
            unsafe_dishes = []

            for category, items in self.menu_data.items():
                for item in items:
                    item_allergens = item.get("allergens", [])

                    # Verificar si contiene algún alérgeno a evitar
                    has_allergen = any(
                        allergen in item_allergens for allergen in allergens_to_avoid
                    )

                    dish_info = {
                        "name": item["name"],
                        "category": category,
                        "price": item["price"],
                        "allergens": item_allergens,
                        "id": item.get("id", "")
                    }

                    if has_allergen:
                        unsafe_dishes.append(dish_info)
                    else:
                        safe_dishes.append(dish_info)

            return {
                "restaurant": self.metadata.name,
                "safe_dishes": safe_dishes,
                "unsafe_dishes": unsafe_dishes,
                "total_safe": len(safe_dishes),
                "total_unsafe": len(unsafe_dishes),
                "allergens_checked": allergens_to_avoid,
                "safety_note": f"Análisis de seguridad para {self.metadata.name}"
            }

        def get_ingredient_info(ingredient: str) -> Dict[str, Any]:
            """
            Obtiene información sobre un ingrediente específico en este restaurante

            Args:
                ingredient: Nombre del ingrediente a consultar

            Returns:
                Información sobre el ingrediente y en qué platos se usa en este restaurante
            """
            ingredient_lower = ingredient.lower()
            dishes_with_ingredient = []

            for category, items in self.menu_data.items():
                for item in items:
                    ingredients = [ing.lower() for ing in item.get("ingredients", [])]
                    if any(ingredient_lower in ing for ing in ingredients):
                        dishes_with_ingredient.append({
                                "dish": item["name"],
                                "category": category,
                                "price": item["price"],
                            "dish_id": item.get("id", ""),
                            "all_ingredients": item.get("ingredients", [])
                        })

            return {
                "restaurant": self.metadata.name,
                "ingredient": ingredient,
                "found_in_dishes": dishes_with_ingredient,
                "total_dishes": len(dishes_with_ingredient),
                "ingredient_details": self._get_ingredient_details(ingredient),
                "restaurant_type": self.metadata.type
            }

        def recommend_dishes(preferences: Dict[str, Any]) -> Dict[str, Any]:
            """
            Recomienda platos basándose en preferencias del cliente
            Usando datos y personalidad específicos del restaurante

            Args:
                preferences: Diccionario con preferencias (max_price, dietary_restrictions, etc.)

            Returns:
                Recomendaciones personalizadas para este restaurante específico
            """
            recommendations = []
            max_price = preferences.get("max_price", float("inf"))
            dietary_restrictions = preferences.get("dietary_restrictions", [])

            for category, items in self.menu_data.items():
                for item in items:
                    # Filtrar por precio
                    if item["price"] > max_price:
                        continue

                    # Verificar restricciones dietéticas
                    meets_restrictions = True
                    if dietary_restrictions:
                        for restriction in dietary_restrictions:
                            if restriction in item.get("allergens", []):
                                meets_restrictions = False
                                break

                    if meets_restrictions:
                        # Calcular score usando datos del restaurante
                        score = self._calculate_recommendation_score(item, preferences)
                        recommendations.append({
                                **item,
                                "category": category,
                                "recommendation_score": score,
                            "reasons": self._get_recommendation_reasons(item, preferences),
                            "restaurant_specialty": self._is_restaurant_specialty(item["name"])
                        })

            # Ordenar por score y retornar top 5
            recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)

            return {
                "restaurant": self.metadata.name,
                "restaurant_type": self.metadata.type,
                "recommendations": recommendations[:5],
                "total_analyzed": len(recommendations),
                "criteria": preferences,
                "chef_note": self._get_chef_personalized_note()
            }

        # Crear herramientas FunctionTool siguiendo patrones ADK
        return [
            FunctionTool(get_menu_items),
            FunctionTool(get_dish_details),
            FunctionTool(check_allergens),
            FunctionTool(get_ingredient_info),
            FunctionTool(recommend_dishes),
        ]

    def _create_agent(self) -> Agent:
        """
        Crea el agente especialista usando google/adk-python v1.5+ y configuración dinámica
        """
        # Construir instrucciones personalizadas usando datos del restaurante
        personalized_instruction = self._build_personalized_instruction()
        
        # Usar Agent (recomendado en ADK v1.5+) en lugar de LlmAgent
        return Agent(
            name=self.agent_config.name,
            model=self.restaurant_config.system_config.default_model,
            instruction=personalized_instruction,
            tools=self.tools,
            description=f"{self.agent_config.description} - {self.metadata.name}"
        )

    def _build_personalized_instruction(self) -> str:
        """
        Construye instrucciones personalizadas usando configuración dinámica del restaurante
        """
        # Obtener saludo personalizado según idioma principal
        main_language = self.metadata.languages[0] if self.metadata.languages else "es"
        greeting_key = f"greeting_{main_language}"
        greeting = self.branding.get(greeting_key, "¡Hola! Soy tu especialista gastronómico.")
        
        # Personalizar saludo con nombre del agente
        if "{agent_name}" in greeting:
            greeting = greeting.replace("{agent_name}", self.agent_config.name)

        # Construir instrucciones dinámicas
        return f"""
{self.agent_config.instruction}

**INFORMACIÓN DEL RESTAURANTE**:
- Nombre: {self.metadata.name}
- Ubicación: {self.metadata.location}
- Tipo de cocina: {self.restaurant_info.get('cuisine_type', self.metadata.type)}
- Descripción: {self.restaurant_info.get('description', 'Experiencia gastronómica excepcional')}

**PERSONALIDAD Y BRANDING**:
- Tono: {self.branding.get('tone', 'profesional y cálido')}
- Personalidad: {self.branding.get('personality', 'chef experto y apasionado')}
- Saludo: {greeting}

**DATOS DEL MENÚ ESPECÍFICO**:
{json.dumps(self.menu_data, indent=2, ensure_ascii=False)}

**CATEGORÍAS DISPONIBLES**: {', '.join(self.menu_data.keys())}
**TOTAL DE PLATOS**: {sum(len(items) for items in self.menu_data.values())}

**HERRAMIENTAS DISPONIBLES**:
- get_menu_items: Lista platos por categoría y restricciones
- get_dish_details: Información detallada de platos específicos
- check_allergens: Verificación de seguridad alimentaria
- get_ingredient_info: Consulta de ingredientes específicos
- recommend_dishes: Recomendaciones personalizadas

**PROTOCOLO DE RESPUESTA PERSONALIZADO**:
1. Mantén la personalidad de {self.metadata.name} ({self.branding.get('personality', 'chef experto')})
2. Usa el tono {self.branding.get('tone', 'profesional')} característico del restaurante
3. Menciona la especialización en {self.restaurant_info.get('cuisine_type', 'gastronomía')}
4. SIEMPRE verifica alérgenos para seguridad alimentaria
5. Destaca ingredientes premium y técnicas especiales del restaurante
6. Ofrece alternativas si algo no está disponible

**IDIOMAS SOPORTADOS**: {', '.join(self.metadata.languages)}

**EJEMPLOS CONTEXTUALIZADOS PARA {self.metadata.name}**:
- "¿Qué especialidades tienen de {self.restaurant_info.get('cuisine_type', 'nuestra cocina')}?"
- "¿Hay opciones para personas con restricciones dietéticas?"
- "¿Cuál es la preparación especial de sus platos estrella?"
- "¿Qué me recomienda que sea representativo de {self.metadata.name}?"

RECUERDA: Eres {self.agent_config.name} de {self.metadata.name}, especialista en {self.restaurant_info.get('cuisine_type', 'gastronomía')} con la personalidad {self.branding.get('personality', 'chef experto')}.
"""

    # === MÉTODOS AUXILIARES PERSONALIZADOS POR RESTAURANTE ===

    def _get_preparation_info(self, dish_name: str) -> str:
        """Información de preparación específica del restaurante"""
        # En producción, esto vendría de la configuración del restaurante
        cuisine_type = self.restaurant_info.get('cuisine_type', 'internacional')
        
        base_preparation = f"Preparado siguiendo las técnicas tradicionales de {cuisine_type}, "
        base_preparation += f"con ingredientes frescos seleccionados especialmente para {self.metadata.name}."
        
        return base_preparation

    def _get_allergen_details(self, allergens: List[str]) -> Dict[str, str]:
        """Detalles sobre alérgenos con información del restaurante"""
        allergen_info = {
            "gluten": f"Contiene gluten. En {self.metadata.name} podemos ofrecer alternativas sin gluten.",
            "lactosa": f"Contiene lácteos. Consulta opciones veganas en {self.metadata.name}.",
            "frutos secos": f"Puede contener frutos secos. {self.metadata.name} toma precauciones especiales.",
            "pescado": f"Contiene pescado fresco. Especialidad de {self.metadata.name}.",
            "huevo": "Contiene huevo fresco de origen local."
        }
        
        return {
            allergen: allergen_info.get(allergen, f"Contiene {allergen} - {self.metadata.name} garantiza calidad")
            for allergen in allergens
        }

    def _suggest_similar_dishes(self, dish_name: str) -> List[str]:
        """Sugiere platos similares del menú específico del restaurante"""
        all_dishes = []
        for category, items in self.menu_data.items():
            all_dishes.extend([item["name"] for item in items])

        suggestions = []
        dish_lower = dish_name.lower()

        for dish in all_dishes:
            if any(word in dish.lower() for word in dish_lower.split()):
                suggestions.append(dish)

        return suggestions[:3] if suggestions else all_dishes[:3]

    def _get_ingredient_details(self, ingredient: str) -> str:
        """Información de ingredientes con contexto del restaurante"""
        cuisine_type = self.restaurant_info.get('cuisine_type', 'internacional')
        location = self.metadata.location
        
        return f"Ingrediente de primera calidad usado en {self.metadata.name}. " \
               f"Seleccionado especialmente para nuestra cocina {cuisine_type} en {location}."

    def _calculate_recommendation_score(self, item: Dict, preferences: Dict) -> float:
        """Calcula score de recomendación considerando especialidades del restaurante"""
        score = 0.5  # Score base

        # Bonificación por especialidades del restaurante
        if self._is_restaurant_specialty(item["name"]):
            score += 0.25

        # Factores estándar
        if item["price"] <= preferences.get("max_price", float("inf")):
            score += 0.15

        if "vegetariano" in item.get("diet_tags", []):
            score += 0.1

        if len(item.get("allergens", [])) <= 1:  # Pocos alérgenos
            score += 0.1

        return min(score, 1.0)

    def _get_recommendation_reasons(self, item: Dict, preferences: Dict) -> List[str]:
        """Genera razones personalizadas para recomendaciones"""
        reasons = []

        if self._is_restaurant_specialty(item["name"]):
            reasons.append(f"Especialidad de {self.metadata.name}")

        if item["price"] <= preferences.get("max_price", 50):
            reasons.append("Excelente relación calidad-precio")

        if not item.get("allergens", []):
            reasons.append("Sin alérgenos principales")

        cuisine_type = self.restaurant_info.get('cuisine_type', '')
        if cuisine_type and cuisine_type.lower() in item["name"].lower():
            reasons.append(f"Auténtica {cuisine_type}")

        return reasons or [f"Recomendación del chef de {self.metadata.name}"]

    def _is_restaurant_specialty(self, dish_name: str) -> bool:
        """Determina si un plato es especialidad del restaurante"""
        # Lógica simple: platos con precio premium o keywords de especialidad
        cuisine_type = self.restaurant_info.get('cuisine_type', '').lower()
        dish_lower = dish_name.lower()

        return cuisine_type in dish_lower or any(
            keyword in dish_lower 
            for keyword in ['especial', 'chef', 'casa', 'signature', 'premium']
        )

    def _get_chef_personalized_note(self) -> str:
        """Nota personalizada del chef según configuración del restaurante"""
        chef_name = self.agent_config.name
        restaurant_name = self.metadata.name
        cuisine_type = self.restaurant_info.get('cuisine_type', 'gastronomía')
        
        return f"Recomendación especial de {chef_name} para {restaurant_name}. " \
               f"Nuestra pasión por la {cuisine_type} se refleja en cada plato."

    # === MÉTODOS PÚBLICOS PARA HERRAMIENTAS ===
    # (Estos mantienen compatibilidad pero usan los internos dinámicos)

    def get_menu_items(self, category: str = None, dietary_restrictions: List[str] = None) -> Dict[str, Any]:
        """Interfaz pública para herramientas - usa configuración dinámica"""
        tool_functions = {tool.func.__name__: tool.func for tool in self.tools}
        return tool_functions["get_menu_items"](category, dietary_restrictions)

    def get_dish_details(self, dish_name: str) -> Dict[str, Any]:
        """Interfaz pública para herramientas - usa configuración dinámica"""
        tool_functions = {tool.func.__name__: tool.func for tool in self.tools}
        return tool_functions["get_dish_details"](dish_name)

    def check_allergens(self, allergens_to_avoid: List[str]) -> Dict[str, Any]:
        """Interfaz pública para herramientas - usa configuración dinámica"""
        tool_functions = {tool.func.__name__: tool.func for tool in self.tools}
        return tool_functions["check_allergens"](allergens_to_avoid)

    def get_ingredient_info(self, ingredient: str) -> Dict[str, Any]:
        """Interfaz pública para herramientas - usa configuración dinámica"""
        tool_functions = {tool.func.__name__: tool.func for tool in self.tools}
        return tool_functions["get_ingredient_info"](ingredient)

    def recommend_dishes(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Interfaz pública para herramientas - usa configuración dinámica"""
        tool_functions = {tool.func.__name__: tool.func for tool in self.tools}
        return tool_functions["recommend_dishes"](preferences)
