#!/usr/bin/env python3
"""
🌐 SERVIDOR API REST PARA EL META-AGENTE MULTI-TENANT
====================================================

Servidor web simple para probar el sistema SaaS con curl.
Basado en la simulación validada del meta-agente.

Uso:
    python api_server.py

Endpoints:
    POST /query - Consulta directa
    POST /stream - Consulta con streaming
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

# FastAPI para el servidor web
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ Error: FastAPI no está instalado")
    print("💡 Instalar con: pip install fastapi uvicorn")
    exit(1)

# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class QueryRequest(BaseModel):
    """Modelo para las consultas a la API"""
    restaurant_id: str
    query: str
    user_id: str = "default_user"
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    """Modelo para las respuestas de la API"""
    status: str
    response: str
    restaurant_name: str
    chef_name: str
    cuisine_type: str
    session_id: str
    timestamp: str

# ============================================================================
# CONFIGURACIÓN DE RESTAURANTE SIMPLIFICADA (AUTO-CONTENIDA)
# ============================================================================

class SimpleRestaurantConfig:
    """Configuración simplificada de restaurante"""
    
    def __init__(self, restaurant_id: str, data: Dict[str, Any]):
        self.restaurant_id = restaurant_id
        self.name = data.get('metadata', {}).get('name', 'Restaurante')
        self.chef_name = data.get('metadata', {}).get('chef_name', 'Chef')
        self.cuisine_type = data.get('restaurant_info', {}).get('cuisine_type', 'variada')
        self.menu = data.get('menu', {})

class SimpleConfigManager:
    """ConfigManager auto-contenido para el servidor API"""
    
    def __init__(self):
        self._restaurants = self._get_hardcoded_restaurants()
    
    def _get_hardcoded_restaurants(self) -> Dict[str, SimpleRestaurantConfig]:
        """Datos hardcodeados para el servidor"""
        restaurants = {}
        
        # Demo Restaurant - La Tavola Italiana
        demo_data = {
            'metadata': {
                'name': 'La Tavola Italiana',
                'chef_name': 'MaestroChef'
            },
            'restaurant_info': {
                'cuisine_type': 'italiana'
            },
            'menu': {
                'entrantes': [
                    {'name': 'Bruschetta al Pomodoro', 'description': 'Pan tostado con tomate fresco'},
                    {'name': 'Antipasto Misto', 'description': 'Selección de embutidos y quesos'}
                ],
                'pasta': [
                    {'name': 'Spaghetti Carbonara', 'description': 'Pasta con huevo, panceta y queso'},
                    {'name': 'Fettuccine Alfredo', 'description': 'Pasta con salsa cremosa de queso'}
                ],
                'pizza': [
                    {'name': 'Pizza Margherita', 'description': 'Tomate, mozzarella y albahaca'},
                    {'name': 'Pizza Quattro Stagioni', 'description': 'Cuatro estaciones en una pizza'}
                ]
            }
        }
        restaurants['demo_restaurant'] = SimpleRestaurantConfig('demo_restaurant', demo_data)
        
        # Pizza Palace
        pizza_data = {
            'metadata': {
                'name': 'Pizza Palace',
                'chef_name': 'PizzaioloAntonio'
            },
            'restaurant_info': {
                'cuisine_type': 'Italiana'
            },
            'menu': {
                'entrantes': [
                    {'name': 'Focaccia al Rosmarino', 'description': 'Pan plano con romero'},
                    {'name': 'Ensalada Caprese', 'description': 'Tomate, mozzarella y albahaca'}
                ],
                'pizzas': [
                    {'name': 'Pizza Vegana Supreme', 'description': 'Base vegana con vegetales frescos'},
                    {'name': 'Pizza Napolitana', 'description': 'Pizza tradicional con anchoas'}
                ],
                'postres': [
                    {'name': 'Tiramisú', 'description': 'Postre tradicional italiano'},
                    {'name': 'Gelato', 'description': 'Helado artesanal'}
                ]
            }
        }
        restaurants['pizza_palace'] = SimpleRestaurantConfig('pizza_palace', pizza_data)
        
        # Bistro Madrid
        bistro_data = {
            'metadata': {
                'name': 'Bistro Madrid',
                'chef_name': 'ChefDimitri'
            },
            'restaurant_info': {
                'cuisine_type': 'Mediterránea'
            },
            'menu': {
                'entrantes': [
                    {'name': 'Hummus con Pita', 'description': 'Crema de garbanzos con pan pita'},
                    {'name': 'Dolmades', 'description': 'Hojas de vid rellenas'}
                ],
                'principales': [
                    {'name': 'Moussaka', 'description': 'Plato griego con berenjenas'},
                    {'name': 'Paella Mediterránea', 'description': 'Arroz con mariscos y vegetales'}
                ],
                'postres': [
                    {'name': 'Baklava', 'description': 'Postre griego con nueces y miel'},
                    {'name': 'Flan de Coco', 'description': 'Postre cremoso de coco'}
                ]
            }
        }
        restaurants['bistro_madrid'] = SimpleRestaurantConfig('bistro_madrid', bistro_data)
        
        return restaurants
    
    def get_restaurant(self, restaurant_id: str) -> SimpleRestaurantConfig:
        """Obtener configuración de restaurante"""
        if restaurant_id not in self._restaurants:
            available = list(self._restaurants.keys())
            raise ValueError(f"Restaurante '{restaurant_id}' no encontrado. Disponibles: {available}")
        
        return self._restaurants[restaurant_id]
    
    def list_restaurants(self) -> list:
        """Listar restaurantes disponibles"""
        return list(self._restaurants.keys())

# ============================================================================
# LÓGICA DEL META-AGENTE (MISMA QUE LA SIMULACIÓN VALIDADA)
# ============================================================================

class RestaurantMetaAgent:
    """Meta-agente que maneja múltiples restaurantes"""
    
    def __init__(self):
        self.config_manager = SimpleConfigManager()
        self._sessions = {}  # Gestión de sesiones
    
    def process_query(self, restaurant_id: str, user_query: str, user_id: str = "default", session_id: Optional[str] = None) -> Dict[str, Any]:
        """Procesar consulta del meta-agente"""
        
        try:
            # 1. Cargar configuración del restaurante
            restaurant = self.config_manager.get_restaurant(restaurant_id)
            
            # 2. Crear sesión si no existe
            if not session_id:
                session_id = f"session_{user_id}_{int(time.time())}"
            
            # 3. Generar información del menú
            menu_details = []
            menu_summary = []
            
            for category, dishes in restaurant.menu.items():
                menu_summary.append(f"{category.title()}: {len(dishes)} platos")
                for dish in dishes[:2]:  # Primeros 2 platos de cada categoría
                    menu_details.append(f"• {dish['name']} - {dish.get('description', 'Delicioso plato')}")
            
            # 4. Generar respuesta contextual
            response_text = self._generate_contextual_response(restaurant, user_query, menu_details, menu_summary)
            
            # 5. Guardar sesión
            self._sessions[session_id] = {
                "restaurant_id": restaurant_id,
                "user_id": user_id,
                "last_query": user_query,
                "timestamp": time.time()
            }
            
            return {
                "status": "success",
                "response": response_text,
                "restaurant_name": restaurant.name,
                "chef_name": restaurant.chef_name,
                "cuisine_type": restaurant.cuisine_type,
                "session_id": session_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except ValueError as e:
            # Error de restaurante no encontrado
            available = self.config_manager.list_restaurants()
            return {
                "status": "error",
                "error": str(e),
                "available_restaurants": available,
                "session_id": session_id or f"error_{int(time.time())}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": f"Error interno: {str(e)}",
                "session_id": session_id or f"error_{int(time.time())}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _generate_contextual_response(self, restaurant, user_query: str, menu_details: List[str], menu_summary: List[str]) -> str:
        """Generar respuesta contextual basada en la consulta"""
        
        if "especialidad" in user_query.lower():
            return f"""🍽️ ¡Hola! Soy {restaurant.chef_name} de {restaurant.name}.

🌟 Mi especialidad es la cocina {restaurant.cuisine_type}. Me enorgullezco de crear experiencias culinarias auténticas.

📋 Nuestras especialidades incluyen:
{chr(10).join(menu_details[:3])}

¿Te gustaría conocer más detalles sobre algún plato en particular?"""
            
        elif "vegano" in user_query.lower() or "vegana" in user_query.lower():
            return f"""🌱 ¡Por supuesto! En {restaurant.name} tenemos excelentes opciones veganas.

Como {restaurant.chef_name}, me especializo en adaptar nuestros platos tradicionales de cocina {restaurant.cuisine_type} para dietas veganas sin perder el sabor auténtico.

🥗 Algunas opciones veganas disponibles:
{chr(10).join(menu_details[:2])}

¿Te gustaría que te recomiende algo específico según tus preferencias?"""
            
        elif "recomend" in user_query.lower():
            return f"""👨‍🍳 Como {restaurant.chef_name} de {restaurant.name}, te recomiendo especialmente:

🍜 Para cocina {restaurant.cuisine_type} auténtica:
{chr(10).join(menu_details[:3])}

📋 Nuestro menú completo incluye: {', '.join(menu_summary)}

¿Hay algún tipo de plato específico que te interese? ¿Prefieres algo ligero o más contundente?"""
            
        else:
            return f"""🍽️ ¡Bienvenido a {restaurant.name}! Soy {restaurant.chef_name}, tu chef especializado en cocina {restaurant.cuisine_type}.

📋 Te puedo ayudar con:
• Recomendaciones de platos
• Información nutricional y alergenos  
• Opciones especiales (veganas, sin gluten, etc.)
• Sugerencias de maridaje

Nuestro menú incluye: {', '.join(menu_summary)}

¿En qué puedo ayudarte específicamente?"""

# ============================================================================
# SERVIDOR FASTAPI
# ============================================================================

# Crear aplicación FastAPI
app = FastAPI(
    title="🏪 Meta-Agente SaaS para Restaurantes",
    description="API REST para el sistema multi-tenant de restaurantes",
    version="1.0.0"
)

# Instancia global del meta-agente
meta_agent = RestaurantMetaAgent()

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "🏪 Meta-Agente SaaS para Restaurantes",
        "version": "1.0.0",
        "restaurantes_disponibles": meta_agent.config_manager.list_restaurants(),
        "endpoints": {
            "POST /query": "Consulta directa al meta-agente",
            "POST /stream": "Consulta con streaming",
            "GET /restaurants": "Listar restaurantes disponibles"
        },
        "ejemplo_uso": {
            "restaurant_id": "demo_restaurant",
            "query": "¿Cuál es tu especialidad?",
            "user_id": "cliente_001"
        }
    }

@app.get("/restaurants")
async def list_restaurants():
    """Listar restaurantes disponibles"""
    restaurants = meta_agent.config_manager.list_restaurants()
    details = {}
    
    for restaurant_id in restaurants:
        config = meta_agent.config_manager.get_restaurant(restaurant_id)
        details[restaurant_id] = {
            "name": config.name,
            "chef": config.chef_name,
            "cuisine": config.cuisine_type
        }
    
    return {
        "status": "success",
        "total": len(restaurants),
        "restaurants": details
    }

@app.post("/query")
async def query_restaurant(request: QueryRequest):
    """Endpoint principal de consulta al meta-agente"""
    
    try:
        result = meta_agent.process_query(
            restaurant_id=request.restaurant_id,
            user_query=request.query,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

@app.post("/stream")
async def stream_restaurant(request: QueryRequest):
    """Endpoint de streaming para respuestas incrementales"""
    
    async def generate_stream():
        try:
            # Procesar consulta
            result = meta_agent.process_query(
                restaurant_id=request.restaurant_id,
                user_query=request.query,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            if result["status"] == "error":
                yield f"data: {json.dumps(result)}\n\n"
                return
            
            # Simular streaming dividiendo la respuesta
            response_text = result["response"]
            words = response_text.split()
            
            # Enviar metadata inicial
            metadata = {
                "event": "metadata",
                "restaurant_name": result["restaurant_name"],
                "chef_name": result["chef_name"],
                "cuisine_type": result["cuisine_type"],
                "session_id": result["session_id"]
            }
            yield f"data: {json.dumps(metadata)}\n\n"
            
            # Enviar palabras en chunks
            chunk_size = 3  # 3 palabras por chunk
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                chunk_data = {
                    "event": "chunk",
                    "data": chunk,
                    "chunk_number": i // chunk_size + 1
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                await asyncio.sleep(0.1)  # Simular latencia
            
            # Enviar evento final
            final_data = {
                "event": "complete",
                "status": "success",
                "total_chunks": len(words) // chunk_size + 1
            }
            yield f"data: {json.dumps(final_data)}\n\n"
            
        except Exception as e:
            error_data = {
                "event": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

def main():
    """Función principal para arrancar el servidor"""
    print("🚀 ARRANCANDO SERVIDOR API DEL META-AGENTE")
    print("=" * 50)
    print("🌐 URL: http://localhost:8080")
    print("📋 Documentación: http://localhost:8080/docs")
    print("🏪 Restaurantes disponibles:")
    
    restaurants = meta_agent.config_manager.list_restaurants()
    for restaurant_id in restaurants:
        config = meta_agent.config_manager.get_restaurant(restaurant_id)
        print(f"   • {restaurant_id}: {config.name} ({config.chef_name})")
    
    print("\n🧪 EJEMPLOS DE CURL:")
    print("-" * 30)
    print('curl -X POST http://localhost:8080/query \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"restaurant_id": "demo_restaurant", "query": "¿Cuál es tu especialidad?", "user_id": "cliente_001"}\'')
    print()
    print("🎬 Arrancando servidor...")
    
    # Arrancar servidor
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

if __name__ == "__main__":
    main() 