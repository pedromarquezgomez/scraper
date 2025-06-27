#!/usr/bin/env python3
"""
Demo de ConfigManager - Fase 1 de la Arquitectura SaaS
Demuestra cómo el ConfigManager permite configuración dinámica multi-tenant
manteniendo total compatibilidad con google/adk-python.
"""

import asyncio
from pathlib import Path

from src.restaurant.config.config_manager import ConfigManager, RestaurantNotFoundError
from src.restaurant.agents.modern_system import create_food_specialist
from google.adk.agents import Agent


def demo_basic_functionality():
    """Demuestra la funcionalidad básica del ConfigManager"""
    print("🚀 DEMO: ConfigManager - Fase 1 SaaS")
    print("=" * 60)
    
    # Inicializar ConfigManager
    config_manager = ConfigManager()
    
    # Listar restaurantes disponibles
    restaurants = config_manager.list_restaurants()
    print(f"📋 Restaurantes configurados: {restaurants}")
    
    if not restaurants:
        print("❌ No hay restaurantes configurados. Ejecuta setup_restaurant.py primero.")
        return
    
    # Cargar configuración del primer restaurante
    restaurant_id = restaurants[0]
    print(f"\n🏪 Cargando configuración para: {restaurant_id}")
    
    try:
        config = config_manager.load_restaurant_config(restaurant_id)
        
        # Mostrar información básica
        print(f"✅ Restaurante: {config.metadata.name}")
        print(f"📍 Ubicación: {config.metadata.location}")
        print(f"🍽️ Tipo: {config.metadata.type}")
        print(f"🗣️ Idiomas: {', '.join(config.metadata.languages)}")
        
        # Mostrar configuración de agentes
        print(f"\n🤖 AGENTES CONFIGURADOS:")
        for agent_id, agent_config in config.agent_configs.items():
            print(f"  • {agent_config.name} ({agent_id})")
            print(f"    Especialización: {agent_config.specialization}")
            print(f"    Keywords: {', '.join(agent_config.keywords[:5])}...")
        
        # Mostrar datos del menú
        menu = config.restaurant_data['menu']
        total_dishes = sum(len(dishes) for dishes in menu.values())
        print(f"\n🍝 MENÚ:")
        print(f"  Categorías: {', '.join(menu.keys())}")
        print(f"  Total de platos: {total_dishes}")
        
        # Mostrar algunas características del restaurante
        features = config.restaurant_data.get('features', {})
        enabled_features = [f for f, enabled in features.items() if enabled]
        print(f"\n📱 Características habilitadas: {', '.join(enabled_features)}")
        
        return config
        
    except RestaurantNotFoundError as e:
        print(f"❌ Error: {e}")
        return None


def demo_adk_integration(config):
    """Demuestra la integración con ADK usando configuración dinámica"""
    print("\n" + "=" * 60)
    print("🔗 DEMO: Integración ConfigManager + ADK")
    print("=" * 60)
    
    if not config:
        print("❌ No hay configuración disponible")
        return
    
    # Crear agente usando datos dinámicos del ConfigManager
    print("🛠️ Creando agente con configuración dinámica...")
    
    # Obtener configuración específica del food_agent
    food_agent_config = config.agent_configs.get('food_agent')
    
    if food_agent_config:
        print(f"✅ Configuración del agente encontrada:")
        print(f"  Nombre: {food_agent_config.name}")
        print(f"  Especialización: {food_agent_config.specialization}")
        
        # Aquí es donde se integrará con el agente ADK en la Fase 2
        # Por ahora mostramos cómo se accedería a los datos
        print(f"\n📊 Datos disponibles para el agente:")
        print(f"  • Menú: {len(config.restaurant_data['menu'])} categorías")
        print(f"  • Instrucciones personalizadas: {'Sí' if food_agent_config.instruction else 'No'}")
        print(f"  • Keywords específicas: {len(food_agent_config.keywords)} términos")
        print(f"  • Configuración del sistema: {config.system_config.default_model}")
        
        # Mostrar preview de la personalización
        branding = config.restaurant_data.get('branding', {})
        if branding:
            print(f"\n🎨 Personalización de marca:")
            print(f"  Tono: {branding.get('tone', 'N/A')}")
            print(f"  Personalidad: {branding.get('personality', 'N/A')}")
            
            # Mostrar saludo personalizado
            greeting = branding.get('greeting_es', 'Saludo por defecto')
            if '{agent_name}' in greeting:
                personalized_greeting = greeting.replace('{agent_name}', food_agent_config.name)
                print(f"  Saludo personalizado: {personalized_greeting[:100]}...")


def demo_multi_tenant_simulation():
    """Simula el comportamiento multi-tenant"""
    print("\n" + "=" * 60)
    print("🏢 DEMO: Simulación Multi-Tenant")
    print("=" * 60)
    
    config_manager = ConfigManager()
    
    # Simular múltiples restaurantes (en producción vendrían de Firestore)
    restaurants = config_manager.list_restaurants()
    
    print(f"🏪 Procesando {len(restaurants)} restaurante(s):")
    
    for restaurant_id in restaurants:
        try:
            config = config_manager.load_restaurant_config(restaurant_id)
            
            print(f"\n📋 {config.metadata.name}:")
            print(f"  ID: {restaurant_id}")
            print(f"  Tipo: {config.metadata.type}")
            print(f"  Idiomas: {', '.join(config.metadata.languages)}")
            print(f"  Agentes: {len(config.agent_configs)}")
            print(f"  Platos: {sum(len(dishes) for dishes in config.restaurant_data['menu'].values())}")
            
            # Simulación de carga balanceada
            print(f"  ✅ Configuración cargada desde cache: {'Sí' if restaurant_id in config_manager._config_cache else 'No'}")
            
        except Exception as e:
            print(f"  ❌ Error cargando {restaurant_id}: {e}")
    
    # Mostrar estadísticas del cache
    stats = config_manager.get_cache_stats()
    print(f"\n📈 Estadísticas del sistema:")
    print(f"  Configuraciones en cache: {stats['cache_size']}")
    print(f"  Schemas cargados: {len(stats['schemas_loaded'])}")


def demo_extensibility():
    """Demuestra la extensibilidad del sistema"""
    print("\n" + "=" * 60)
    print("🔧 DEMO: Extensibilidad y Flexibilidad")
    print("=" * 60)
    
    config_manager = ConfigManager()
    
    # Mostrar directorios creados automáticamente
    print("📁 Estructura de directorios auto-creada:")
    base_dirs = [config_manager.base_path, config_manager.templates_path, config_manager.schemas_path]
    for directory in base_dirs:
        print(f"  • {directory}: {'✅ Existe' if directory.exists() else '❌ No existe'}")
    
    # Mostrar schemas automáticos
    print(f"\n📋 Schemas de validación disponibles:")
    for schema_name in config_manager._schema_cache.keys():
        print(f"  • {schema_name}_schema.json")
    
    # Mostrar templates disponibles
    templates = config_manager.list_templates()
    print(f"\n🎨 Templates disponibles: {templates if templates else 'Ninguno (se crearán en Fase 4)'}")
    
    print(f"\n🚀 Preparado para:")
    print(f"  ✅ Firestore integration (Fase 5)")
    print(f"  ✅ Template system (Fase 4)")
    print(f"  ✅ API REST wrapper (Fase 5)")
    print(f"  ✅ Multi-region deployment")


def main():
    """Función principal del demo"""
    print("🎯 ConfigManager Demo - Arquitectura SaaS")
    print("Fase 1: Gestión de Configuración Dinámica")
    print()
    
    # Demo 1: Funcionalidad básica
    config = demo_basic_functionality()
    
    # Demo 2: Integración con ADK
    demo_adk_integration(config)
    
    # Demo 3: Multi-tenant simulation
    demo_multi_tenant_simulation()
    
    # Demo 4: Extensibilidad
    demo_extensibility()
    
    print("\n" + "=" * 60)
    print("✅ FASE 1 COMPLETADA")
    print("=" * 60)
    print("🎉 ConfigManager implementado con éxito!")
    print("📋 Características implementadas:")
    print("  • Carga de configuración por restaurant_id")
    print("  • Validación automática con JSON Schema")
    print("  • Cache inteligente para rendimiento")
    print("  • Manejo de errores robusto")
    print("  • Preparado para integración con ADK")
    print("  • Base sólida para migración a Firestore")
    print()
    print("🚀 Listo para Fase 2: Refactorización del Agente Principal")


if __name__ == "__main__":
    main() 