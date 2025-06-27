#!/usr/bin/env python3
"""
Setup Restaurant - Sistema de Onboarding Automatizado
Fase 4: Creación de nuevos restaurantes usando plantillas predefinidas

Uso:
    python setup_restaurant.py --template modern_casual --name "Pizza Palace" --location "Madrid, España" --cuisine "Pizzeria"
    python setup_restaurant.py --template pizzeria --name "Bella Napoli" --location "Barcelona, España" --cuisine "Italiana"
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class RestaurantSetup:
    """
    Sistema de configuración automatizada para nuevos restaurantes
    
    Utiliza plantillas predefinidas para crear configuraciones completas
    de restaurantes listos para usar con el sistema SaaS.
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.templates_path = self.base_path / "templates"
        self.restaurant_data_path = self.base_path / "restaurant_data"
        self.schemas_path = self.base_path / "schemas"
        
        # Asegurar que los directorios existen
        self.restaurant_data_path.mkdir(exist_ok=True)
        
    def list_available_templates(self) -> List[str]:
        """Lista las plantillas disponibles"""
        if not self.templates_path.exists():
            return []
        
        templates = []
        for template_dir in self.templates_path.iterdir():
            if template_dir.is_dir():
                templates.append(template_dir.name)
        
        return sorted(templates)
    
    def validate_template(self, template_name: str) -> bool:
        """Valida que la plantilla existe y tiene los archivos necesarios"""
        template_path = self.templates_path / template_name
        
        if not template_path.exists():
            return False
        
        required_files = ["metadata.json", "restaurant_config.json", "menu_data.json"]
        for file_name in required_files:
            if not (template_path / file_name).exists():
                print(f"❌ Error: Plantilla '{template_name}' incompleta. Falta archivo: {file_name}")
                return False
        
        return True
    
    def generate_restaurant_id(self, restaurant_name: str) -> str:
        """Genera un ID único para el restaurante basado en su nombre"""
        # Convertir a minúsculas y reemplazar espacios y caracteres especiales
        restaurant_id = restaurant_name.lower()
        restaurant_id = re.sub(r'[^a-z0-9\s]', '', restaurant_id)  # Solo letras, números y espacios
        restaurant_id = re.sub(r'\s+', '_', restaurant_id.strip())  # Espacios por guiones bajos
        restaurant_id = re.sub(r'_+', '_', restaurant_id)  # Múltiples guiones bajos por uno solo
        
        return restaurant_id
    
    def check_restaurant_exists(self, restaurant_id: str) -> bool:
        """Verifica si ya existe un restaurante con el mismo ID"""
        restaurant_path = self.restaurant_data_path / restaurant_id
        return restaurant_path.exists()
    
    def get_cuisine_mapping(self, cuisine_type: str) -> Dict[str, str]:
        """Mapea el tipo de cocina a valores específicos para las plantillas"""
        cuisine_lower = cuisine_type.lower()
        
        # Mapeos específicos para diferentes tipos de cocina
        mappings = {
            'italiana': {
                'cuisine_specialization': 'italian_cuisine',
                'chef_name': 'Antonio'
            },
            'pizzeria': {
                'cuisine_specialization': 'pizza_traditional',
                'chef_name': 'Giuseppe'
            },
            'mexicana': {
                'cuisine_specialization': 'mexican_cuisine',
                'chef_name': 'Carlos'
            },
            'japonesa': {
                'cuisine_specialization': 'japanese_cuisine',
                'chef_name': 'Hiroshi'
            },
            'china': {
                'cuisine_specialization': 'chinese_cuisine',
                'chef_name': 'Wei'
            },
            'francesa': {
                'cuisine_specialization': 'french_cuisine',
                'chef_name': 'Pierre'
            },
            'mediterránea': {
                'cuisine_specialization': 'mediterranean_cuisine',
                'chef_name': 'Dimitri'
            },
            'argentina': {
                'cuisine_specialization': 'argentine_cuisine',
                'chef_name': 'Diego'
            }
        }
        
        # Buscar mapeo específico o usar genérico
        for key, mapping in mappings.items():
            if key in cuisine_lower:
                return mapping
        
        # Mapeo genérico
        return {
            'cuisine_specialization': f"{cuisine_lower.replace(' ', '_')}_cuisine",
            'chef_name': 'Chef'
        }
    
    def create_restaurant_config(self, template_name: str, restaurant_name: str, 
                               location: str, cuisine_type: str) -> bool:
        """
        Crea la configuración completa de un nuevo restaurante
        
        Args:
            template_name: Nombre de la plantilla a usar
            restaurant_name: Nombre oficial del restaurante
            location: Ubicación del restaurante
            cuisine_type: Tipo de cocina
            
        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        
        # 1. Validar plantilla
        if not self.validate_template(template_name):
            print(f"❌ Error: Plantilla '{template_name}' no válida")
            return False
        
        # 2. Generar restaurant_id
        restaurant_id = self.generate_restaurant_id(restaurant_name)
        print(f"📋 ID generado: {restaurant_id}")
        
        # 3. Verificar que no existe
        if self.check_restaurant_exists(restaurant_id):
            print(f"❌ Error: Ya existe un restaurante con ID '{restaurant_id}'")
            print(f"💡 Sugerencia: Usa un nombre diferente o más específico")
            return False
        
        # 4. Crear directorio del restaurante
        restaurant_path = self.restaurant_data_path / restaurant_id
        restaurant_path.mkdir(exist_ok=True)
        print(f"📁 Directorio creado: {restaurant_path}")
        
        try:
            # 5. Obtener mapeo de cocina
            cuisine_mapping = self.get_cuisine_mapping(cuisine_type)
            
            # 6. Preparar variables de sustitución
            current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            app_name = f"{restaurant_id}_system"
            phone_placeholder = "+34 91 XXX XXXX"  # Placeholder por defecto
            
            substitutions = {
                "{{RESTAURANT_ID}}": restaurant_id,
                "{{RESTAURANT_NAME}}": restaurant_name,
                "{{LOCATION}}": location,
                "{{CUISINE_TYPE}}": cuisine_type,
                "{{CUISINE_LOWER}}": cuisine_type.lower(),
                "{{CUISINE_SPECIALIZATION}}": cuisine_mapping['cuisine_specialization'],
                "{{CHEF_NAME}}": cuisine_mapping['chef_name'],
                "{{CREATED_AT}}": current_time,
                "{{APP_NAME}}": app_name,
                "{{PHONE}}": phone_placeholder
            }
            
            # 7. Copiar y personalizar archivos
            template_path = self.templates_path / template_name
            files_processed = []
            
            for template_file in template_path.glob("*.json"):
                # Leer archivo de plantilla
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aplicar sustituciones
                for placeholder, value in substitutions.items():
                    content = content.replace(placeholder, value)
                
                # Validar que es JSON válido
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"❌ Error: JSON inválido en {template_file.name}: {e}")
                    return False
                
                # Escribir archivo personalizado
                output_file = restaurant_path / template_file.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_processed.append(template_file.name)
                print(f"✅ Archivo creado: {output_file}")
            
            # 8. Validar configuración creada
            if self._validate_created_config(restaurant_id):
                print(f"\n🎉 ¡Restaurante '{restaurant_name}' configurado exitosamente!")
                print(f"📋 ID del restaurante: {restaurant_id}")
                print(f"📁 Ubicación: {restaurant_path}")
                print(f"📄 Archivos creados: {', '.join(files_processed)}")
                print(f"\n🚀 Para usar el restaurante:")
                print(f"   python main.py --restaurant_id {restaurant_id}")
                return True
            else:
                print(f"❌ Error: Configuración creada pero falló la validación")
                return False
                
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            # Limpiar directorio creado en caso de error
            if restaurant_path.exists():
                shutil.rmtree(restaurant_path)
            return False
    
    def _validate_created_config(self, restaurant_id: str) -> bool:
        """Valida que la configuración creada es correcta"""
        try:
            # Intentar cargar usando ConfigManager
            sys.path.insert(0, str(self.base_path / "src"))
            from restaurant.config.config_manager import ConfigManager
            
            config_manager = ConfigManager()
            config = config_manager.load_restaurant_config(restaurant_id)
            
            # Verificaciones básicas
            if not config.metadata.name:
                return False
            if not config.metadata.location:
                return False
            if not config.agent_configs:
                return False
            if not config.restaurant_data.get('menu'):
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error en validación: {e}")
            return False
    
    def show_template_info(self, template_name: str):
        """Muestra información detallada sobre una plantilla"""
        if not self.validate_template(template_name):
            print(f"❌ Plantilla '{template_name}' no encontrada o incompleta")
            return
        
        template_path = self.templates_path / template_name
        print(f"\n📋 INFORMACIÓN DE PLANTILLA: {template_name}")
        print("=" * 50)
        
        # Leer metadata de ejemplo
        try:
            with open(template_path / "metadata.json", 'r', encoding='utf-8') as f:
                metadata_content = f.read()
            
            with open(template_path / "restaurant_config.json", 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            with open(template_path / "menu_data.json", 'r', encoding='utf-8') as f:
                menu_content = f.read()
            
            # Contar elementos del menú
            menu_categories = menu_content.count('"category":')
            
            print(f"📁 Ubicación: {template_path}")
            print(f"📄 Archivos: metadata.json, restaurant_config.json, menu_data.json")
            print(f"🍽️ Categorías de menú: ~{menu_categories}")
            print(f"🤖 Agentes configurados: 2 (food_agent, drinks_agent)")
            print(f"🎨 Personalización: Incluida")
            
            # Mostrar variables que se sustituirán
            print(f"\n🔧 Variables que se personalizarán:")
            variables = [
                "{{RESTAURANT_NAME}} - Nombre del restaurante",
                "{{RESTAURANT_ID}} - ID único generado",
                "{{LOCATION}} - Ubicación proporcionada",
                "{{CUISINE_TYPE}} - Tipo de cocina",
                "{{CHEF_NAME}} - Nombre del chef (automático)",
                "{{CREATED_AT}} - Fecha de creación"
            ]
            for var in variables:
                print(f"  • {var}")
                
        except Exception as e:
            print(f"❌ Error leyendo plantilla: {e}")


def parse_arguments():
    """Configura y parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Sistema de Onboarding Automatizado para Restaurantes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python setup_restaurant.py --template modern_casual --name "Bistro Moderno" --location "Madrid, España" --cuisine "Fusión"
  python setup_restaurant.py --template pizzeria --name "Pizza Palace" --location "Barcelona, España" --cuisine "Italiana"
  python setup_restaurant.py --list-templates
  python setup_restaurant.py --info pizzeria

El script creará automáticamente toda la configuración necesaria
para que el restaurante esté listo para usar con main.py
        """
    )
    
    parser.add_argument(
        '--template',
        type=str,
        help='Nombre de la plantilla a usar (ej: modern_casual, pizzeria)'
    )
    
    parser.add_argument(
        '--name',
        type=str,
        help='Nombre oficial del restaurante (ej: "Pizza Palace")'
    )
    
    parser.add_argument(
        '--location',
        type=str,
        help='Ubicación del restaurante (ej: "Madrid, España")'
    )
    
    parser.add_argument(
        '--cuisine',
        type=str,
        help='Tipo de cocina (ej: "Italiana", "Mexicana", "Fusión")'
    )
    
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='Listar plantillas disponibles'
    )
    
    parser.add_argument(
        '--info',
        type=str,
        metavar='TEMPLATE',
        help='Mostrar información detallada sobre una plantilla'
    )
    
    return parser.parse_args()


def main():
    """Función principal del sistema de setup"""
    print("🎯 Setup Restaurant - Sistema de Onboarding Automatizado")
    print("Fase 4: Creación de restaurantes con plantillas")
    print()
    
    args = parse_arguments()
    setup = RestaurantSetup()
    
    # Comando: Listar plantillas
    if args.list_templates:
        templates = setup.list_available_templates()
        print("📋 PLANTILLAS DISPONIBLES:")
        print("=" * 40)
        if templates:
            for template in templates:
                print(f"  • {template}")
        else:
            print("  No hay plantillas disponibles")
        print(f"\n💡 Para ver detalles de una plantilla:")
        print(f"   python setup_restaurant.py --info NOMBRE_PLANTILLA")
        return
    
    # Comando: Información de plantilla
    if args.info:
        setup.show_template_info(args.info)
        return
    
    # Comando: Crear restaurante
    if not all([args.template, args.name, args.location, args.cuisine]):
        print("❌ Error: Se requieren todos los argumentos para crear un restaurante")
        print("💡 Uso: python setup_restaurant.py --template PLANTILLA --name \"NOMBRE\" --location \"UBICACIÓN\" --cuisine \"COCINA\"")
        print("💡 Ver plantillas disponibles: python setup_restaurant.py --list-templates")
        sys.exit(1)
    
    # Validar plantillas disponibles
    available_templates = setup.list_available_templates()
    if not available_templates:
        print("❌ Error: No hay plantillas disponibles")
        print("💡 Verifica que el directorio 'templates/' existe y contiene plantillas válidas")
        sys.exit(1)
    
    if args.template not in available_templates:
        print(f"❌ Error: Plantilla '{args.template}' no disponible")
        print(f"📋 Plantillas disponibles: {', '.join(available_templates)}")
        sys.exit(1)
    
    # Crear restaurante
    print(f"🏪 Creando restaurante con plantilla '{args.template}'...")
    print(f"📋 Nombre: {args.name}")
    print(f"📍 Ubicación: {args.location}")
    print(f"🍽️ Cocina: {args.cuisine}")
    print()
    
    success = setup.create_restaurant_config(
        template_name=args.template,
        restaurant_name=args.name,
        location=args.location,
        cuisine_type=args.cuisine
    )
    
    if success:
        print(f"\n✅ FASE 4 COMPLETADA: Restaurante creado exitosamente")
        print(f"🚀 Listo para Fase 5: Contenerización y API REST")
    else:
        print(f"\n❌ Error: No se pudo crear el restaurante")
        sys.exit(1)


if __name__ == "__main__":
    main() 