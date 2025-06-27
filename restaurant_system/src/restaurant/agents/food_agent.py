# Copyright 2025 Restaurant AI System
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""
Agente Especialista en Comida
Maneja consultas sobre menú, ingredientes, alérgenos y gastronomía
"""

import json
from typing import Any, Dict, List, Optional

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

from config.system_config import AGENT_CONFIGS, RESTAURANT_DATA, SystemConfig


class FoodSpecialistAgent:
    """
    Agente Especialista en Comida y Gastronomía

    Responsabilidades:
    - Información detallada sobre platos del menú
    - Ingredientes y métodos de preparación
    - Identificación de alérgenos
    - Recomendaciones personalizadas de comida
    - Información sobre origen y calidad de productos
    """

    def __init__(self, config: SystemConfig):
        self.config = config
        self.agent_config = AGENT_CONFIGS["food_agent"]
        self.menu_data = RESTAURANT_DATA["menu"]

        # Crear herramientas específicas para consultas de comida
        self.tools = self._create_food_tools()

        # Crear agente usando ADK
        self.agent = self._create_agent()

    def _create_food_tools(self) -> List[FunctionTool]:
        """Crea herramientas específicas para consultas gastronómicas"""

        def get_menu_items(
            category: str = None, dietary_restrictions: List[str] = None
        ) -> Dict[str, Any]:
            """
            Obtiene elementos del menú filtrados por categoría y restricciones dietéticas

            Args:
                category: Categoría del menú (appetizers, main_courses, desserts)
                dietary_restrictions: Lista de restricciones (sin_gluten, vegano, etc.)

            Returns:
                Diccionario con los platos que coinciden con los filtros
            """
            result = {"items": [], "total_count": 0}

            # Obtener todas las categorías si no se especifica una
            categories = [category] if category else list(self.menu_data.keys())

            for cat in categories:
                if cat in self.menu_data:
                    items = self.menu_data[cat]

                    # Filtrar por restricciones dietéticas si se especifican
                    if dietary_restrictions:
                        filtered_items = []
                        for item in items:
                            # Verificar si el plato cumple con las restricciones
                            diet_tags = item.get("diet_tags", [])
                            allergens = item.get("allergens", [])

                            meets_restrictions = True
                            for restriction in dietary_restrictions:
                                if (
                                    restriction == "sin_gluten"
                                    and "gluten" in allergens
                                ):
                                    meets_restrictions = False
                                elif (
                                    restriction == "vegano"
                                    and restriction not in diet_tags
                                ):
                                    meets_restrictions = False
                                elif (
                                    restriction == "vegetariano"
                                    and restriction not in diet_tags
                                ):
                                    meets_restrictions = False

                            if meets_restrictions:
                                filtered_items.append(item)
                        items = filtered_items

                    result["items"].extend(
                        [{"category": cat, **item} for item in items]
                    )

            result["total_count"] = len(result["items"])
            return result

        def get_dish_details(dish_name: str) -> Dict[str, Any]:
            """
            Obtiene información detallada de un plato específico

            Args:
                dish_name: Nombre del plato a consultar

            Returns:
                Información completa del plato o None si no se encuentra
            """
            dish_name_lower = dish_name.lower()

            for category, items in self.menu_data.items():
                for item in items:
                    if dish_name_lower in item["name"].lower():
                        return {
                            "found": True,
                            "category": category,
                            "details": item,
                            "preparation_info": self._get_preparation_info(
                                item["name"]
                            ),
                            "allergen_details": self._get_allergen_details(
                                item.get("allergens", [])
                            ),
                        }

            return {
                "found": False,
                "suggestions": self._suggest_similar_dishes(dish_name),
            }

        def check_allergens(allergens_to_avoid: List[str]) -> Dict[str, Any]:
            """
            Identifica platos seguros para personas con alergias específicas

            Args:
                allergens_to_avoid: Lista de alérgenos a evitar

            Returns:
                Lista de platos seguros y platos a evitar
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
                    }

                    if has_allergen:
                        unsafe_dishes.append(dish_info)
                    else:
                        safe_dishes.append(dish_info)

            return {
                "safe_dishes": safe_dishes,
                "unsafe_dishes": unsafe_dishes,
                "total_safe": len(safe_dishes),
                "allergens_checked": allergens_to_avoid,
            }

        def get_ingredient_info(ingredient: str) -> Dict[str, Any]:
            """
            Obtiene información sobre un ingrediente específico

            Args:
                ingredient: Nombre del ingrediente a consultar

            Returns:
                Información sobre el ingrediente y en qué platos se usa
            """
            ingredient_lower = ingredient.lower()
            dishes_with_ingredient = []

            for category, items in self.menu_data.items():
                for item in items:
                    ingredients = [ing.lower() for ing in item.get("ingredients", [])]
                    if any(ingredient_lower in ing for ing in ingredients):
                        dishes_with_ingredient.append(
                            {
                                "dish": item["name"],
                                "category": category,
                                "price": item["price"],
                            }
                        )

            return {
                "ingredient": ingredient,
                "found_in_dishes": dishes_with_ingredient,
                "total_dishes": len(dishes_with_ingredient),
                "ingredient_info": self._get_ingredient_details(ingredient),
            }

        def recommend_dishes(preferences: Dict[str, Any]) -> Dict[str, Any]:
            """
            Recomienda platos basándose en preferencias del cliente

            Args:
                preferences: Diccionario con preferencias (tipo, precio, restricciones)

            Returns:
                Lista de platos recomendados
            """
            recommendations = []
            max_price = preferences.get("max_price", float("inf"))
            preferred_type = preferences.get("type", "").lower()
            dietary_restrictions = preferences.get("dietary_restrictions", [])

            for category, items in self.menu_data.items():
                # Filtrar por tipo preferido si se especifica
                if preferred_type and preferred_type not in category.lower():
                    continue

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
                        # Calcular score de recomendación
                        score = self._calculate_recommendation_score(item, preferences)
                        recommendations.append(
                            {
                                **item,
                                "category": category,
                                "recommendation_score": score,
                                "reasons": self._get_recommendation_reasons(
                                    item, preferences
                                ),
                            }
                        )

            # Ordenar por score y retornar top 5
            recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)

            return {
                "recommendations": recommendations[:5],
                "total_analyzed": len(recommendations),
                "criteria": preferences,
            }

        # Crear herramientas FunctionTool
        return [
            FunctionTool(get_menu_items),
            FunctionTool(get_dish_details),
            FunctionTool(check_allergens),
            FunctionTool(get_ingredient_info),
            FunctionTool(recommend_dishes),
        ]

    def _create_agent(self) -> LlmAgent:
        """Crea el agente especialista en comida usando LlmAgent de ADK"""

        return LlmAgent(
            name=self.agent_config.name,
            model=Gemini(model=self.config.default_model),
            instruction=f"""
{self.agent_config.instruction}

**DATOS DEL MENÚ DISPONIBLES**:
{json.dumps(self.menu_data, indent=2, ensure_ascii=False)}

**HERRAMIENTAS DISPONIBLES**:
- get_menu_items: Para obtener listas de platos por categoría y restricciones
- get_dish_details: Para información detallada de platos específicos
- check_allergens: Para verificar seguridad alimentaria con alergias
- get_ingredient_info: Para consultar ingredientes específicos
- recommend_dishes: Para hacer recomendaciones personalizadas

**PROTOCOLO DE RESPUESTA**:
1. Usa las herramientas apropiadas para obtener información precisa
2. Proporciona detalles completos sobre ingredientes y preparación
3. SIEMPRE menciona alérgenos cuando sea relevante
4. Ofrece alternativas si algo no está disponible
5. Mantén un tono profesional pero cálido de chef experto

**EJEMPLOS DE CONSULTAS QUE MANEJAS**:
- "¿Qué platos tienen salmón?"
- "¿Hay opciones sin gluten?"
- "¿Cómo se prepara la ensalada César?"
- "¿Qué me recomienda para alguien vegetariano?"
- "¿Qué ingredientes tiene el plato X?"

Recuerda: La seguridad alimentaria es PRIORIDAD en casos de alergias.
""",
            tools=self.tools,
            description=self.agent_config.description,
        )

    # Métodos auxiliares para las herramientas
    def _get_preparation_info(self, dish_name: str) -> str:
        """Información de preparación del plato (datos dummy)"""
        preparation_methods = {
            "ensalada césar gourmet": "Lechuga romana fresca, cortada y mezclada con nuestro aderezo césar casero, parmesano rallado al momento y crutones dorados.",
            "salmón a la plancha": "Salmón fresco del atlántico, cocinado a la plancha con hierbas mediterráneas, acompañado de quinoa orgánica y verduras de temporada asadas.",
        }
        return preparation_methods.get(
            dish_name.lower(),
            "Preparado con técnicas tradicionales y ingredientes frescos de primera calidad.",
        )

    def _get_allergen_details(self, allergens: List[str]) -> Dict[str, str]:
        """Detalles sobre alérgenos específicos"""
        allergen_info = {
            "gluten": "Contiene proteínas de trigo, puede causar reacciones en personas celíacas",
            "pescado": "Contiene proteínas de pescado, importante para alergias a mariscos",
            "lácteos": "Contiene proteínas de leche, incluye lactosa",
            "huevos": "Contiene proteínas de huevo",
            "frutos secos": "Puede contener trazas de almendras, nueces u otros frutos secos",
        }
        return {
            allergen: allergen_info.get(allergen, f"Contiene {allergen}")
            for allergen in allergens
        }

    def _suggest_similar_dishes(self, dish_name: str) -> List[str]:
        """Sugiere platos similares cuando no se encuentra el solicitado"""
        all_dishes = []
        for category, items in self.menu_data.items():
            all_dishes.extend([item["name"] for item in items])

        # Implementación simple de sugerencias
        suggestions = []
        dish_lower = dish_name.lower()

        for dish in all_dishes:
            if any(word in dish.lower() for word in dish_lower.split()):
                suggestions.append(dish)

        return suggestions[:3]

    def _get_ingredient_details(self, ingredient: str) -> str:
        """Información adicional sobre ingredientes"""
        ingredient_details = {
            "salmón": "Salmón fresco del Atlántico, rico en omega-3 y proteínas de alta calidad",
            "quinoa": "Grano andino orgánico, libre de gluten y rico en proteínas completas",
            "parmesano": "Queso italiano curado 24 meses, denominación de origen protegida",
        }
        return ingredient_details.get(
            ingredient.lower(), f"Ingrediente de primera calidad: {ingredient}"
        )

    def _calculate_recommendation_score(self, item: Dict, preferences: Dict) -> float:
        """Calcula score de recomendación para un plato"""
        score = 0.5  # Score base

        # Factores de score
        if item["price"] <= preferences.get("max_price", float("inf")):
            score += 0.2

        if "saludable" in item.get("diet_tags", []):
            score += 0.15

        if len(item.get("allergens", [])) == 0:
            score += 0.1

        return min(score, 1.0)

    def _get_recommendation_reasons(self, item: Dict, preferences: Dict) -> List[str]:
        """Genera razones para la recomendación"""
        reasons = []

        if item["price"] <= preferences.get("max_price", 30):
            reasons.append("Dentro de tu presupuesto")

        if not item.get("allergens", []):
            reasons.append("Sin alérgenos principales")

        if "sin gluten" in item.get("diet_tags", []):
            reasons.append("Opción sin gluten")

        if item.get("calories", 0) < 400:
            reasons.append("Opción ligera")

        return reasons or ["Plato popular del chef"]

    # Métodos para herramientas (deben estar en el nivel de clase)
    def get_menu_items(
        self, category: str = None, dietary_restrictions: List[str] = None
    ) -> Dict[str, Any]:
        """Obtiene elementos del menú filtrados"""
        # Implementación ya incluida en _create_food_tools
        pass

    def get_dish_details(self, dish_name: str) -> Dict[str, Any]:
        """Obtiene información detallada de un plato específico"""
        # Implementación ya incluida en _create_food_tools
        pass

    def check_allergens(self, allergens_to_avoid: List[str]) -> Dict[str, Any]:
        """Identifica platos seguros para personas con alergias específicas"""
        # Implementación ya incluida en _create_food_tools
        pass

    def get_ingredient_info(self, ingredient: str) -> Dict[str, Any]:
        """Obtiene información sobre un ingrediente específico"""
        # Implementación ya incluida en _create_food_tools
        pass

    def recommend_dishes(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Recomienda platos basándose en preferencias del cliente"""
        # Implementación ya incluida en _create_food_tools
        pass
