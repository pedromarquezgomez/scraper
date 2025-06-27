#!/usr/bin/env python3
"""
🌐 SERVIDOR HTTP SIMPLE PARA EL META-AGENTE
===========================================

Servidor minimalista usando solo la librería estándar de Python.
No requiere dependencias externas.

Uso:
    python3 simple_server.py
    
Pruebas:
    curl "http://localhost:8080/demo_restaurant/¿Cuál es tu especialidad?"
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

class RestaurantData:
    """Datos hardcodeados de restaurantes"""
    
    @staticmethod
    def get_restaurants():
        return {
            'demo_restaurant': {
                'name': 'La Tavola Italiana',
                'chef': 'MaestroChef',
                'cuisine': 'italiana',
                'menu': ['Spaghetti Carbonara', 'Pizza Margherita', 'Bruschetta al Pomodoro']
            },
            'pizza_palace': {
                'name': 'Pizza Palace', 
                'chef': 'PizzaioloAntonio',
                'cuisine': 'Italiana',
                'menu': ['Pizza Vegana Supreme', 'Focaccia al Rosmarino', 'Tiramisú']
            },
            'bistro_madrid': {
                'name': 'Bistro Madrid',
                'chef': 'ChefDimitri', 
                'cuisine': 'Mediterránea',
                'menu': ['Moussaka', 'Hummus con Pita', 'Baklava']
            }
        }

def generate_response(restaurant_id: str, query: str) -> Dict[str, Any]:
    """Generar respuesta del meta-agente"""
    
    restaurants = RestaurantData.get_restaurants()
    
    if restaurant_id not in restaurants:
        return {
            "status": "error",
            "message": f"Restaurante '{restaurant_id}' no encontrado",
            "available": list(restaurants.keys())
        }
    
    restaurant = restaurants[restaurant_id]
    
    # Generar respuesta contextual
    if "especialidad" in query.lower():
        response = f"""🍽️ ¡Hola! Soy {restaurant['chef']} de {restaurant['name']}.

🌟 Mi especialidad es la cocina {restaurant['cuisine']}. 

📋 Nuestras especialidades incluyen:
• {restaurant['menu'][0]}
• {restaurant['menu'][1]}
• {restaurant['menu'][2]}

¿Te gustaría conocer más detalles sobre algún plato?"""

    elif "vegano" in query.lower() or "vegana" in query.lower():
        response = f"""🌱 ¡Por supuesto! En {restaurant['name']} tenemos excelentes opciones veganas.

Como {restaurant['chef']}, me especializo en adaptar nuestros platos de cocina {restaurant['cuisine']} para dietas veganas.

🥗 Te recomiendo especialmente: {restaurant['menu'][0]}

¿Te gustaría que te recomiende algo específico?"""

    elif "recomend" in query.lower():
        response = f"""👨‍🍳 Como {restaurant['chef']} de {restaurant['name']}, te recomiendo:

🍜 Para cocina {restaurant['cuisine']} auténtica:
• {restaurant['menu'][0]} - Nuestro plato estrella
• {restaurant['menu'][1]} - Muy popular
• {restaurant['menu'][2]} - Perfecto para compartir

¿Qué tipo de sabores prefieres?"""

    else:
        response = f"""🍽️ ¡Bienvenido a {restaurant['name']}! 

Soy {restaurant['chef']}, tu chef especializado en cocina {restaurant['cuisine']}.

📋 Te puedo ayudar con:
• Recomendaciones de platos
• Opciones especiales (veganas, sin gluten, etc.)
• Información nutricional

Nuestro menú incluye: {', '.join(restaurant['menu'])}

¿En qué puedo ayudarte?"""
    
    return {
        "status": "success",
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant['name'],
        "chef_name": restaurant['chef'],
        "cuisine_type": restaurant['cuisine'],
        "query": query,
        "response": response
    }

class MetaAgentHandler(BaseHTTPRequestHandler):
    """Handler HTTP para el meta-agente"""
    
    def do_GET(self):
        """Manejar peticiones GET"""
        
        if self.path == '/':
            # Página de información
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            info = {
                "message": "🏪 Meta-Agente SaaS para Restaurantes",
                "usage": "GET /{restaurant_id}/{query}",
                "restaurants": list(RestaurantData.get_restaurants().keys()),
                "examples": [
                    "/demo_restaurant/¿Cuál es tu especialidad?",
                    "/pizza_palace/¿Tienen opciones veganas?", 
                    "/bistro_madrid/¿Qué recomiendan?"
                ]
            }
            self.wfile.write(json.dumps(info, ensure_ascii=False, indent=2).encode('utf-8'))
            
        elif self.path == '/restaurants':
            # Listar restaurantes
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            restaurants = RestaurantData.get_restaurants()
            result = {
                "status": "success",
                "total": len(restaurants),
                "restaurants": {rid: {"name": r["name"], "chef": r["chef"], "cuisine": r["cuisine"]} 
                              for rid, r in restaurants.items()}
            }
            self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
            
        else:
            # Parsear consulta: /{restaurant_id}/{query}
            path_parts = self.path.strip('/').split('/', 1)
            
            if len(path_parts) < 2:
                self.send_error(400, "Formato: /{restaurant_id}/{query}")
                return
            
            restaurant_id = path_parts[0]
            query = urllib.parse.unquote(path_parts[1])
            
            # Generar respuesta
            result = generate_response(restaurant_id, query)
            
            # Enviar respuesta
            if result["status"] == "error":
                self.send_response(404)
            else:
                self.send_response(200)
                
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def do_POST(self):
        """Manejar peticiones POST"""
        
        if self.path == '/query':
            try:
                # Leer datos JSON
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                restaurant_id = data.get('restaurant_id')
                query = data.get('query', '')
                
                if not restaurant_id:
                    self.send_error(400, "restaurant_id requerido")
                    return
                
                # Generar respuesta
                result = generate_response(restaurant_id, query)
                
                # Enviar respuesta
                if result["status"] == "error":
                    self.send_response(404)
                else:
                    self.send_response(200)
                    
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
                
            except Exception as e:
                self.send_error(500, f"Error: {str(e)}")
        else:
            self.send_error(404, "Endpoint no encontrado")
    
    def log_message(self, format, *args):
        """Personalizar logging"""
        print(f"🌐 {self.address_string()} - {format % args}")

def main():
    """Función principal del servidor"""
    
    port = 8080
    server_address = ('', port)
    
    print("🚀 SERVIDOR META-AGENTE SaaS")
    print("=" * 40)
    print(f"🌐 URL: http://localhost:{port}")
    print(f"📋 Info: http://localhost:{port}/")
    print(f"🏪 Restaurantes: http://localhost:{port}/restaurants")
    print()
    print("🧪 EJEMPLOS DE CURL:")
    print("-" * 30)
    print('# GET simple:')
    print(f'curl "http://localhost:{port}/demo_restaurant/¿Cuál es tu especialidad?"')
    print()
    print('# POST JSON:')
    print(f'curl -X POST http://localhost:{port}/query \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"restaurant_id": "demo_restaurant", "query": "¿Cuál es tu especialidad?"}\'')
    print()
    print("🎬 Servidor arrancando...")
    
    # Crear y arrancar servidor
    httpd = HTTPServer(server_address, MetaAgentHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
        httpd.server_close()

if __name__ == "__main__":
    main() 