# Copyright 2025 Restaurant AI System - SaaS Platform
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""
ConfigManager - Sistema de Gestión de Configuración Dinámica SaaS
Permite cargar configuraciones específicas por restaurant_id para multi-tenancy.
Diseñado para trabajar nativamente con google/adk-python sin modificar el núcleo.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from jsonschema import validate, ValidationError

from .system_config import AgentConfig, SystemConfig, AGENT_CONFIGS


@dataclass
class RestaurantMetadata:
    """Metadatos del restaurante para configuración SaaS"""
    restaurant_id: str
    name: str
    type: str  # fine_dining, modern_casual, fast_food, etc.
    location: str
    languages: List[str] = field(default_factory=lambda: ["es"])
    timezone: str = "Europe/Madrid"
    created_at: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass
class RestaurantConfig:
    """Configuración completa de un restaurante"""
    metadata: RestaurantMetadata
    system_config: SystemConfig
    agent_configs: Dict[str, AgentConfig]
    menu_data: Dict[str, Any]
    restaurant_data: Dict[str, Any]


class ConfigValidationError(Exception):
    """Error de validación de configuración"""
    pass


class RestaurantNotFoundError(Exception):
    """Error cuando no se encuentra el restaurante"""
    pass


class ConfigManager:
    """
    Gestor de Configuración Dinámica SaaS
    
    Responsabilidades:
    - Cargar configuraciones por restaurant_id
    - Validar configuraciones contra schemas
    - Manejar templates y configuraciones por defecto
    - Proporcionar fallbacks seguros
    - Facilitar la transición a Firestore en el futuro
    """
    
    def __init__(self, 
                 base_path: str = "restaurant_data",
                 templates_path: str = "templates",
                 schemas_path: str = "schemas"):
        """
        Inicializa el ConfigManager
        
        Args:
            base_path: Ruta base donde están las configuraciones de restaurantes
            templates_path: Ruta donde están los templates de configuración
            schemas_path: Ruta donde están los schemas de validación
        """
        self.base_path = Path(base_path)
        self.templates_path = Path(templates_path)
        self.schemas_path = Path(schemas_path)
        
        # Cache para configuraciones cargadas
        self._config_cache: Dict[str, RestaurantConfig] = {}
        self._schema_cache: Dict[str, Dict] = {}
        
        # Crear directorios si no existen
        self._ensure_directories()
        
        # Cargar schemas de validación
        self._load_schemas()
    
    def _ensure_directories(self):
        """Crea los directorios necesarios si no existen"""
        directories = [self.base_path, self.templates_path, self.schemas_path]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_schemas(self):
        """Carga los schemas de validación JSON"""
        schema_files = {
            'restaurant_config': 'restaurant_config_schema.json',
            'menu_data': 'menu_data_schema.json',
            'metadata': 'metadata_schema.json'
        }
        
        for schema_name, filename in schema_files.items():
            schema_path = self.schemas_path / filename
            if schema_path.exists():
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        self._schema_cache[schema_name] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Warning: Could not load schema {filename}: {e}")
            else:
                # Crear schema básico si no existe
                self._create_default_schema(schema_name, schema_path)
    
    def _create_default_schema(self, schema_name: str, schema_path: Path):
        """Crea schemas por defecto si no existen"""
        schemas = {
            'restaurant_config': {
                "type": "object",
                "required": ["restaurant_info", "agents", "system"],
                "properties": {
                    "restaurant_info": {
                        "type": "object",
                        "required": ["name", "type", "location"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "location": {"type": "string"}
                        }
                    },
                    "agents": {"type": "object"},
                    "system": {"type": "object"}
                }
            },
            'menu_data': {
                "type": "object",
                "required": ["menu"],
                "properties": {
                    "menu": {"type": "object"}
                }
            },
            'metadata': {
                "type": "object",
                "required": ["restaurant_id", "name", "type"],
                "properties": {
                    "restaurant_id": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string"}
                }
            }
        }
        
        if schema_name in schemas:
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(schemas[schema_name], f, indent=2, ensure_ascii=False)
            self._schema_cache[schema_name] = schemas[schema_name]
    
    def get_restaurant_path(self, restaurant_id: str) -> Path:
        """Obtiene la ruta del directorio de un restaurante"""
        return self.base_path / restaurant_id
    
    def restaurant_exists(self, restaurant_id: str) -> bool:
        """Verifica si existe la configuración para un restaurante"""
        restaurant_path = self.get_restaurant_path(restaurant_id)
        required_files = ['metadata.json', 'restaurant_config.json', 'menu_data.json']
        return all((restaurant_path / file).exists() for file in required_files)
    
    def load_restaurant_config(self, restaurant_id: str, use_cache: bool = True) -> RestaurantConfig:
        """
        Carga la configuración completa de un restaurante
        
        Args:
            restaurant_id: ID único del restaurante
            use_cache: Si usar el cache de configuraciones
            
        Returns:
            RestaurantConfig: Configuración completa del restaurante
            
        Raises:
            RestaurantNotFoundError: Si no se encuentra el restaurante
            ConfigValidationError: Si hay errores de validación
        """
        # Verificar cache primero
        if use_cache and restaurant_id in self._config_cache:
            return self._config_cache[restaurant_id]
        
        # Verificar que el restaurante existe
        if not self.restaurant_exists(restaurant_id):
            raise RestaurantNotFoundError(f"Restaurant '{restaurant_id}' not found")
        
        restaurant_path = self.get_restaurant_path(restaurant_id)
        
        try:
            # Cargar metadata
            metadata = self._load_metadata(restaurant_path / 'metadata.json')
            
            # Cargar configuración del restaurante
            restaurant_config_data = self._load_json_file(restaurant_path / 'restaurant_config.json')
            self._validate_config(restaurant_config_data, 'restaurant_config')
            
            # Cargar datos del menú
            menu_data = self._load_json_file(restaurant_path / 'menu_data.json')
            self._validate_config(menu_data, 'menu_data')
            
            # Construir configuración ADK
            system_config = self._build_system_config(restaurant_config_data.get('system', {}))
            agent_configs = self._build_agent_configs(restaurant_config_data.get('agents', {}))
            restaurant_data = self._build_restaurant_data(restaurant_config_data, menu_data)
            
            # Crear configuración completa
            config = RestaurantConfig(
                metadata=metadata,
                system_config=system_config,
                agent_configs=agent_configs,
                menu_data=menu_data,
                restaurant_data=restaurant_data
            )
            
            # Guardar en cache
            if use_cache:
                self._config_cache[restaurant_id] = config
            
            return config
            
        except Exception as e:
            raise ConfigValidationError(f"Error loading config for '{restaurant_id}': {str(e)}")
    
    def _load_metadata(self, metadata_path: Path) -> RestaurantMetadata:
        """Carga los metadatos del restaurante"""
        metadata_data = self._load_json_file(metadata_path)
        self._validate_config(metadata_data, 'metadata')
        
        return RestaurantMetadata(
            restaurant_id=metadata_data['restaurant_id'],
            name=metadata_data['name'],
            type=metadata_data['type'],
            location=metadata_data['location'],
            languages=metadata_data.get('languages', ['es']),
            timezone=metadata_data.get('timezone', 'Europe/Madrid'),
            created_at=metadata_data.get('created_at'),
            last_updated=metadata_data.get('last_updated')
        )
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Carga un archivo JSON con manejo de errores"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise RestaurantNotFoundError(f"Required file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON in {file_path}: {str(e)}")
    
    def _validate_config(self, config_data: Dict[str, Any], schema_name: str):
        """Valida configuración contra schema"""
        if schema_name in self._schema_cache:
            try:
                validate(instance=config_data, schema=self._schema_cache[schema_name])
            except ValidationError as e:
                raise ConfigValidationError(f"Schema validation failed for {schema_name}: {str(e)}")
    
    def _build_system_config(self, system_data: Dict[str, Any]) -> SystemConfig:
        """Construye SystemConfig desde datos JSON"""
        return SystemConfig(
            app_name=system_data.get('app_name', f"restaurant_multiagent_system"),
            default_model=system_data.get('default_model', 'gemini-2.0-flash-exp'),
            supported_languages=system_data.get('supported_languages', ['es', 'en']),
            max_session_duration=system_data.get('max_session_duration', 3600)
        )
    
    def _build_agent_configs(self, agents_data: Dict[str, Any]) -> Dict[str, AgentConfig]:
        """Construye configuraciones de agentes desde datos JSON"""
        agent_configs = {}
        
        # Comenzar con configuraciones por defecto y sobrescribir con personalizaciones
        for agent_id, default_config in AGENT_CONFIGS.items():
            if agent_id in agents_data:
                custom_config = agents_data[agent_id]
                agent_configs[agent_id] = AgentConfig(
                    name=custom_config.get('name', default_config.name),
                    description=custom_config.get('description', default_config.description),
                    specialization=custom_config.get('specialization', default_config.specialization),
                    instruction=custom_config.get('instruction', default_config.instruction),
                    keywords=custom_config.get('keywords', default_config.keywords)
                )
            else:
                agent_configs[agent_id] = default_config
        
        # Agregar agentes personalizados adicionales
        for agent_id, agent_data in agents_data.items():
            if agent_id not in AGENT_CONFIGS:
                agent_configs[agent_id] = AgentConfig(
                    name=agent_data['name'],
                    description=agent_data['description'],
                    specialization=agent_data['specialization'],
                    instruction=agent_data['instruction'],
                    keywords=agent_data.get('keywords', [])
                )
        
        return agent_configs
    
    def _build_restaurant_data(self, restaurant_config: Dict[str, Any], menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construye datos del restaurante combinando configuración y menú"""
        return {
            'menu': menu_data.get('menu', {}),
            'restaurant_info': restaurant_config.get('restaurant_info', {}),
            'branding': restaurant_config.get('branding', {}),
            'operational_hours': restaurant_config.get('operational_hours', {}),
            'contact_info': restaurant_config.get('contact_info', {}),
            'features': restaurant_config.get('features', {})
        }
    
    def save_restaurant_config(self, restaurant_id: str, config: RestaurantConfig):
        """
        Guarda la configuración de un restaurante
        
        Args:
            restaurant_id: ID del restaurante
            config: Configuración a guardar
        """
        restaurant_path = self.get_restaurant_path(restaurant_id)
        restaurant_path.mkdir(parents=True, exist_ok=True)
        
        # Guardar metadata
        metadata_dict = {
            'restaurant_id': config.metadata.restaurant_id,
            'name': config.metadata.name,
            'type': config.metadata.type,
            'location': config.metadata.location,
            'languages': config.metadata.languages,
            'timezone': config.metadata.timezone,
            'created_at': config.metadata.created_at,
            'last_updated': config.metadata.last_updated
        }
        
        with open(restaurant_path / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        
        # Guardar configuración del restaurante (structure compatible con schemas)
        restaurant_config_dict = {
            'restaurant_info': config.restaurant_data.get('restaurant_info', {}),
            'agents': {
                agent_id: {
                    'name': agent_config.name,
                    'description': agent_config.description,
                    'specialization': agent_config.specialization,
                    'instruction': agent_config.instruction,
                    'keywords': agent_config.keywords
                }
                for agent_id, agent_config in config.agent_configs.items()
            },
            'system': {
                'app_name': config.system_config.app_name,
                'default_model': config.system_config.default_model,
                'supported_languages': config.system_config.supported_languages,
                'max_session_duration': config.system_config.max_session_duration
            },
            'branding': config.restaurant_data.get('branding', {}),
            'operational_hours': config.restaurant_data.get('operational_hours', {}),
            'contact_info': config.restaurant_data.get('contact_info', {}),
            'features': config.restaurant_data.get('features', {})
        }
        
        with open(restaurant_path / 'restaurant_config.json', 'w', encoding='utf-8') as f:
            json.dump(restaurant_config_dict, f, indent=2, ensure_ascii=False)
        
        # Guardar datos del menú
        with open(restaurant_path / 'menu_data.json', 'w', encoding='utf-8') as f:
            json.dump(config.menu_data, f, indent=2, ensure_ascii=False)
        
        # Actualizar cache
        self._config_cache[restaurant_id] = config
    
    def list_restaurants(self) -> List[str]:
        """Lista todos los restaurantes configurados"""
        restaurants = []
        if self.base_path.exists():
            for item in self.base_path.iterdir():
                if item.is_dir() and self.restaurant_exists(item.name):
                    restaurants.append(item.name)
        return sorted(restaurants)
    
    def get_restaurant_metadata(self, restaurant_id: str) -> RestaurantMetadata:
        """Obtiene solo los metadatos de un restaurante (más rápido que cargar todo)"""
        if not self.restaurant_exists(restaurant_id):
            raise RestaurantNotFoundError(f"Restaurant '{restaurant_id}' not found")
        
        restaurant_path = self.get_restaurant_path(restaurant_id)
        return self._load_metadata(restaurant_path / 'metadata.json')
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """
        Carga un template de configuración
        
        Args:
            template_name: Nombre del template (e.g., 'modern_casual', 'fine_dining')
            
        Returns:
            Dict con la configuración del template
        """
        template_path = self.templates_path / f"{template_name}.json"
        if not template_path.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found")
        
        return self._load_json_file(template_path)
    
    def list_templates(self) -> List[str]:
        """Lista todos los templates disponibles"""
        templates = []
        if self.templates_path.exists():
            for template_file in self.templates_path.glob("*.json"):
                templates.append(template_file.stem)
        return sorted(templates)
    
    def clear_cache(self, restaurant_id: Optional[str] = None):
        """Limpia el cache de configuraciones"""
        if restaurant_id:
            self._config_cache.pop(restaurant_id, None)
        else:
            self._config_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        return {
            'cached_restaurants': list(self._config_cache.keys()),
            'cache_size': len(self._config_cache),
            'schemas_loaded': list(self._schema_cache.keys())
        }


# Función de conveniencia para obtener una instancia global
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager(**kwargs) -> ConfigManager:
    """Obtiene una instancia global del ConfigManager"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager(**kwargs)
    return _global_config_manager


def reset_config_manager():
    """Resetea la instancia global del ConfigManager"""
    global _global_config_manager
    _global_config_manager = None 