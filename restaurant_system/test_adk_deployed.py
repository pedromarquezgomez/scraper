#!/usr/bin/env python3
"""
Test del Agente ADK Desplegado - Restaurant SaaS System
Prueba comprehensiva del sistema multi-agente desplegado en Vertex AI
"""

import vertexai
from vertexai import agent_engines
import time

# Configuración
PROJECT_ID = "sumy-464008"
LOCATION = "us-central1"
AGENT_RESOURCE_NAME = "projects/904733965277/locations/us-central1/reasoningEngines/7145778845474357248"

print("🧪 Test del Sistema ADK Restaurant SaaS")
print(f"   Proyecto: {PROJECT_ID}")
print(f"   Agente: {AGENT_RESOURCE_NAME}")
print("=" * 60)

# 1. Inicializar y conectar al agente
print("🔌 Paso 1: Conectando al agente desplegado...")

vertexai.init(project=PROJECT_ID, location=LOCATION)
remote_agent = agent_engines.get(AGENT_RESOURCE_NAME)

print("✅ Conectado al agente ADK desplegado")

# 2. Crear sesión de prueba
print("📱 Paso 2: Creando sesión de prueba...")

session = remote_agent.create_session(user_id="test_comprehensive_user")
session_id = session["id"]
print(f"   ✅ Sesión creada: {session_id[:12]}...")

# 3. Definir pruebas comprehensivas
test_queries = [
    {
        "name": "Lista de restaurantes",
        "query": "¿Qué restaurantes tenéis disponibles en la plataforma?",
        "expected": ["bistro_madrid", "pizza_palace", "demo_restaurant"]
    },
    {
        "name": "Información específica de Bistro Madrid",
        "query": "Dime todo sobre Bistro Madrid: ubicación, tipo de cocina, especialidades y precios",
        "expected": ["Madrid", "mediterráneo", "paella", "€€€"]
    },
    {
        "name": "Menú de Pizza Palace",
        "query": "¿Qué categorías de menú tiene Pizza Palace y cuáles son sus especialidades?",
        "expected": ["pizzas", "margherita", "quattro stagioni"]
    },
    {
        "name": "Recomendación por ubicación",
        "query": "Estoy en Madrid, ¿qué restaurante me recomiendas?",
        "expected": ["Bistro Madrid", "Madrid"]
    },
    {
        "name": "Consulta de alta cocina",
        "query": "¿Tenéis algún restaurante de alta cocina o con estrella Michelin?",
        "expected": ["Demo Restaurant", "Michelin", "degustación"]
    },
    {
        "name": "Información de precios",
        "query": "¿Cuáles son los rangos de precios de vuestros restaurantes?",
        "expected": ["€€", "€€€", "€€€€"]
    }
]

# 4. Ejecutar pruebas
print("🎯 Paso 3: Ejecutando pruebas comprehensivas...")
print("-" * 60)

results = {
    "total": len(test_queries),
    "passed": 0,
    "failed": 0,
    "details": []
}

for i, test in enumerate(test_queries, 1):
    print(f"\n📋 Test {i}/{len(test_queries)}: {test['name']}")
    print(f"   ❓ Consulta: {test['query']}")
    
    try:
        # Enviar consulta
        response_text = ""
        for event in remote_agent.stream_query(
            user_id="test_comprehensive_user",
            session_id=session_id,
            message=test['query']
        ):
            if 'content' in event and 'parts' in event['content']:
                for part in event['content']['parts']:
                    if 'text' in part:
                        response_text += part['text']
        
        print(f"   📝 Respuesta: {response_text[:150]}...")
        
        # Verificar si contiene palabras clave esperadas
        response_lower = response_text.lower()
        matches = sum(1 for keyword in test['expected'] if keyword.lower() in response_lower)
        match_ratio = matches / len(test['expected'])
        
        if match_ratio >= 0.5:  # Al menos 50% de las palabras clave
            print(f"   ✅ EXITOSO ({matches}/{len(test['expected'])} keywords)")
            results["passed"] += 1
            test_result = "PASS"
        else:
            print(f"   ❌ FALLIDO ({matches}/{len(test['expected'])} keywords)")
            results["failed"] += 1
            test_result = "FAIL"
        
        results["details"].append({
            "test": test['name'],
            "result": test_result,
            "matches": f"{matches}/{len(test['expected'])}",
            "response_length": len(response_text)
        })
        
        # Pausa entre consultas para evitar rate limiting
        time.sleep(2)
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results["failed"] += 1
        results["details"].append({
            "test": test['name'],
            "result": "ERROR",
            "error": str(e)
        })

# 5. Prueba de funcionalidades específicas
print(f"\n🔧 Paso 4: Pruebas de funcionalidades específicas...")

specific_tests = [
    "¿Cuánto cuesta la paella en Bistro Madrid?",
    "¿Qué restaurante recomendáis para una cena romántica?",
    "¿Tenéis opciones vegetarianas en vuestros restaurantes?"
]

for query in specific_tests:
    print(f"\n🔍 Consulta específica: {query}")
    try:
        response_text = ""
        for event in remote_agent.stream_query(
            user_id="test_comprehensive_user",
            session_id=session_id,
            message=query
        ):
            if 'content' in event and 'parts' in event['content']:
                for part in event['content']['parts']:
                    if 'text' in part:
                        response_text += part['text']
        
        print(f"   📝 Respuesta: {response_text[:200]}...")
        time.sleep(2)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 6. Resumen de resultados
print("\n" + "=" * 60)
print("📊 RESUMEN DE PRUEBAS ADK")
print("=" * 60)

print(f"🎯 Pruebas totales: {results['total']}")
print(f"✅ Exitosas: {results['passed']}")
print(f"❌ Fallidas: {results['failed']}")

success_rate = (results['passed'] / results['total']) * 100
print(f"📈 Tasa de éxito: {success_rate:.1f}%")

if success_rate >= 80:
    print("🏆 RESULTADO: EXCELENTE - Sistema funcionando correctamente")
elif success_rate >= 60:
    print("👍 RESULTADO: BUENO - Sistema funcional con mejoras menores")
else:
    print("⚠️ RESULTADO: NECESITA ATENCIÓN - Revisar fallos")

print(f"\n📋 Detalles por prueba:")
for detail in results['details']:
    status_icon = "✅" if detail['result'] == "PASS" else "❌"
    print(f"   {status_icon} {detail['test']}: {detail['result']}")

print(f"\n🔗 Resource name: {AGENT_RESOURCE_NAME}")
print("🎉 ¡Pruebas completadas!") 