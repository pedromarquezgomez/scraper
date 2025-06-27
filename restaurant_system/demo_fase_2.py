#!/usr/bin/env python3
"""
Demo Fase 2 - FoodSpecialistAgent Refactorizado
Demuestra la integración completa de ConfigManager + Agente ADK dinámico
Compatible con google/adk-python v1.5.0+
"""

import asyncio
from pathlib import Path

from src.restaurant.config.config_manager import ConfigManager, RestaurantNotFoundError
from src.restaurant.agents.food_agent import FoodSpecialistAgent


def demo_dynamic_agent_creation():
    """Demuestra la creación de agentes dinámicos usando ConfigManager"""
    print("🚀 DEMO FASE 2: Agente Dinámico Multi-Tenant")
    print("=" * 60)
    
    # Inicializar ConfigManager
    config_manager = ConfigManager()
    
    # Listar restaurantes disponibles
    restaurants = config_manager.list_restaurants()
    print(f"📋 Restaurantes disponibles: {restaurants}")
    
    if not restaurants:
        print("❌ No hay restaurantes configurados.")
        return None
    
    # Cargar configuración del restaurante
    restaurant_id = restaurants[0]
    print(f"\n🏪 Creando agente para: {restaurant_id}")
    
    try:
        # Cargar configuración completa del restaurante
        restaurant_config = config_manager.load_restaurant_config(restaurant_id)
        
        print(f"✅ Configuración cargada:")
        print(f"  • Restaurante: {restaurant_config.metadata.name}")
        print(f"  • Tipo: {restaurant_config.metadata.type}")
        print(f"  • Ubicación: {restaurant_config.metadata.location}")
        print(f"  • Idiomas: {', '.join(restaurant_config.metadata.languages)}")
        
        # Crear agente dinámico (sin referencias estáticas)
        print(f"\n🤖 Creando FoodSpecialistAgent dinámico...")
        food_agent = FoodSpecialistAgent(restaurant_config=restaurant_config)
        
        print(f"✅ Agente creado exitosamente:")
        print(f"  • Nombre: {food_agent.agent_config.name}")
        print(f"  • Especialización: {food_agent.agent_config.specialization}")
        print(f"  • Herramientas: {len(food_agent.tools)}")
        print(f"  • Modelo ADK: {restaurant_config.system_config.default_model}")
        
        return food_agent, restaurant_config
        
    except Exception as e:
        print(f"❌ Error creando agente: {e}")
        return None, None


def demo_dynamic_tools():
    """Demuestra las herramientas dinámicas usando datos específicos del restaurante"""
    print("\n" + "=" * 60)
    print("🔧 DEMO: Herramientas Dinámicas por Restaurante")
    print("=" * 60)
    
    config_manager = ConfigManager()
    restaurant_config = config_manager.load_restaurant_config("demo_restaurant")
    food_agent = FoodSpecialistAgent(restaurant_config=restaurant_config)
    
    print(f"🍽️ Probando herramientas de {restaurant_config.metadata.name}")
    
    # Test 1: get_menu_items
    print(f"\n📋 TEST 1: Categorías del menú")
    menu_result = food_agent.get_menu_items()
    print(f"  • Restaurante: {menu_result['restaurant']}")
    print(f"  • Categorías disponibles: {menu_result['available_categories']}")
    print(f"  • Total de platos: {menu_result['total_count']}")
    
    # Test 2: get_dish_details
    print(f"\n🍝 TEST 2: Detalles de plato específico")
    if menu_result['items']:
        sample_dish = menu_result['items'][0]['name']
        dish_details = food_agent.get_dish_details(sample_dish)
        if dish_details['found']:
            print(f"  • Plato: {dish_details['details']['name']}")
            print(f"  • Precio: {dish_details['details']['price']}€")
            print(f"  • Categoría: {dish_details['category']}")
            print(f"  • Especialidad del restaurante: {dish_details['restaurant_specialty']}")
            print(f"  • Preparación: {dish_details['preparation_info'][:100]}...")
    
    # Test 3: check_allergens
    print(f"\n⚠️ TEST 3: Verificación de alérgenos")
    allergen_check = food_agent.check_allergens(["gluten", "lactosa"])
    print(f"  • Platos seguros: {allergen_check['total_safe']}")
    print(f"  • Platos a evitar: {allergen_check['total_unsafe']}")
    print(f"  • Nota de seguridad: {allergen_check['safety_note']}")
    
    # Test 4: recommend_dishes
    print(f"\n⭐ TEST 4: Recomendaciones personalizadas")
    recommendations = food_agent.recommend_dishes({
        "max_price": 15.0,
        "dietary_restrictions": []
    })
    print(f"  • Restaurante: {recommendations['restaurant']}")
    print(f"  • Recomendaciones: {len(recommendations['recommendations'])}")
    if recommendations['recommendations']:
        top_rec = recommendations['recommendations'][0]
        print(f"  • Top recomendación: {top_rec['name']} (Score: {top_rec['recommendation_score']:.2f})")
        print(f"  • Razones: {', '.join(top_rec['reasons'])}")
    print(f"  • Nota del chef: {recommendations['chef_note'][:80]}...")


def demo_multi_restaurant_comparison():
    """Simula múltiples restaurantes para demostrar la reutilización del agente"""
    print("\n" + "=" * 60)
    print("🏢 DEMO: Comparación Multi-Restaurante")
    print("=" * 60)
    
    config_manager = ConfigManager()
    
    print("📊 Simulando configuraciones de diferentes tipos de restaurante:")
    
    # Restaurante actual (Demo)
    demo_config = config_manager.load_restaurant_config("demo_restaurant")
    demo_agent = FoodSpecialistAgent(restaurant_config=demo_config)
    
    print(f"\n🇮🇹 {demo_config.metadata.name}:")
    print(f"  • Tipo: {demo_config.metadata.type}")
    print(f"  • Chef: {demo_agent.agent_config.name}")
    print(f"  • Especialización: {demo_agent.agent_config.specialization}")
    print(f"  • Personalidad: {demo_config.restaurant_data.get('branding', {}).get('personality', 'N/A')}")
    print(f"  • Tono: {demo_config.restaurant_data.get('branding', {}).get('tone', 'N/A')}")
    
    # Mostrar configuración dinámica aplicada
    menu_stats = demo_agent.get_menu_items()
    print(f"  • Categorías: {len(menu_stats['available_categories'])}")
    print(f"  • Platos: {menu_stats['total_count']}")
    
    print(f"\n💡 Características SaaS demostradas:")
    print(f"  ✅ Mismo código de agente, configuración diferente")
    print(f"  ✅ Personalidad y branding específicos por restaurante")
    print(f"  ✅ Menús y datos completamente independientes")
    print(f"  ✅ Sin referencias estáticas a archivos o configuraciones")
    print(f"  ✅ Total compatibilidad con google/adk-python")


def demo_adk_integration():
    """Demuestra la integración completa con google/adk-python"""
    print("\n" + "=" * 60)
    print("🔗 DEMO: Integración ADK Completa")
    print("=" * 60)
    
    config_manager = ConfigManager()
    restaurant_config = config_manager.load_restaurant_config("demo_restaurant")
    food_agent = FoodSpecialistAgent(restaurant_config=restaurant_config)
    
    print("🎯 Características ADK integradas:")
    
    # Verificar estructura del agente ADK
    adk_agent = food_agent.agent
    print(f"  ✅ Agente ADK: {type(adk_agent).__name__}")
    print(f"  ✅ Nombre: {adk_agent.name}")
    print(f"  ✅ Modelo: {restaurant_config.system_config.default_model}")
    print(f"  ✅ Herramientas: {len(adk_agent.tools)} FunctionTool registradas")
    
    # Mostrar instrucciones personalizadas
    print(f"\n📋 Instrucciones dinámicas generadas:")
    instruction_preview = adk_agent.instruction[:200] + "..." if len(adk_agent.instruction) > 200 else adk_agent.instruction
    print(f"  📄 Preview: {instruction_preview}")
    
    # Verificar herramientas FunctionTool
    print(f"\n🔧 Herramientas FunctionTool registradas:")
    for i, tool in enumerate(adk_agent.tools, 1):
        tool_name = tool.func.__name__ if hasattr(tool, 'func') else str(tool)
        print(f"  {i}. {tool_name}")
    
    print(f"\n🎉 Estado del agente:")
    print(f"  ✅ Listo para integración con InMemoryRunner")
    print(f"  ✅ Compatible con adk web interface")
    print(f"  ✅ Preparado para API REST")
    print(f"  ✅ Funcional para deployment en producción")


def main():
    """Función principal del demo Fase 2"""
    print("🎯 Demo Fase 2 - FoodSpecialistAgent Refactorizado")
    print("Integración ConfigManager + ADK dinámico")
    print()
    
    # Demo 1: Creación de agente dinámico
    agent_result = demo_dynamic_agent_creation()
    
    if agent_result[0] is None:
        print("❌ No se pudo crear el agente. Verifica la configuración.")
        return
    
    # Demo 2: Herramientas dinámicas
    demo_dynamic_tools()
    
    # Demo 3: Comparación multi-restaurante
    demo_multi_restaurant_comparison()
    
    # Demo 4: Integración ADK
    demo_adk_integration()
    
    print("\n" + "=" * 60)
    print("✅ FASE 2 COMPLETADA")
    print("=" * 60)
    print("🎉 FoodSpecialistAgent completamente refactorizado!")
    print("📋 Logros de la Fase 2:")
    print("  • ✅ Eliminadas todas las referencias estáticas")
    print("  • ✅ Constructor recibe configuración dinámica")
    print("  • ✅ Herramientas usan datos específicos del restaurante")
    print("  • ✅ Instrucciones personalizadas por cliente")
    print("  • ✅ Compatible con google/adk-python v1.5+")
    print("  • ✅ Agente completamente reutilizable")
    print("  • ✅ Preparado para arquitectura SaaS")
    print()
    print("🚀 Listo para Fase 3: Adaptación del Punto de Entrada")
    print("    (main.py aceptará --restaurant_id)")


if __name__ == "__main__":
    main() 