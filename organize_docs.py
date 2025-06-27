import os
import shutil
from pathlib import Path

# Directorios
SOURCE_DIR = "adk_docs_txt"
ORGANIZED_DIR = "adk_docs_organized"

# Estructura jerárquica del framework ADK
STRUCTURE = {
    "01_introduccion": [
        "index.txt",
        "adk_docs_get_started_about.txt"
    ],
    "02_instalacion_inicio": [
        "adk_docs_get_started_installation.txt",
        "adk_docs_get_started_quickstart.txt",
        "adk_docs_get_started_testing.txt"
    ],
    "03_agentes": {
        "conceptos_generales": [
            "adk_docs_agents.txt"
        ],
        "tipos_de_agentes": [
            "adk_docs_agents_llm_agents.txt",
            "adk_docs_agents_custom_agents.txt",
            "adk_docs_agents_multi_agents.txt"
        ],
        "workflow_agents": [
            "adk_docs_agents_workflow_agents.txt",
            "adk_docs_agents_workflow_agents_sequential_agents.txt",
            "adk_docs_agents_workflow_agents_parallel_agents.txt",
            "adk_docs_agents_workflow_agents_loop_agents.txt"
        ],
        "modelos": [
            "adk_docs_agents_models.txt"
        ]
    },
    "04_herramientas": {
        "conceptos_generales": [
            "adk_docs_tools.txt"
        ],
        "tipos_de_herramientas": [
            "adk_docs_tools_built_in_tools.txt",
            "adk_docs_tools_function_tools.txt",
            "adk_docs_tools_google_cloud_tools.txt",
            "adk_docs_tools_third_party_tools.txt"
        ],
        "integraciones": [
            "adk_docs_tools_mcp_tools.txt",
            "adk_docs_tools_openapi_tools.txt",
            "adk_docs_mcp.txt"
        ],
        "autenticacion": [
            "adk_docs_tools_authentication.txt"
        ]
    },
    "05_streaming": {
        "conceptos_generales": [
            "adk_docs_streaming.txt",
            "adk_docs_get_started_streaming.txt"
        ],
        "configuracion": [
            "adk_docs_streaming_configuration.txt"
        ],
        "implementacion": [
            "adk_docs_streaming_custom_streaming.txt",
            "adk_docs_streaming_custom_streaming_ws.txt",
            "adk_docs_streaming_streaming_tools.txt"
        ],
        "quickstart": [
            "adk_docs_get_started_streaming_quickstart_streaming.txt",
            "adk_docs_get_started_streaming_quickstart_streaming_java.txt"
        ]
    },
    "06_sesiones_contexto": [
        "adk_docs_sessions.txt",
        "adk_docs_sessions_session.txt",
        "adk_docs_sessions_memory.txt",
        "adk_docs_sessions_state.txt",
        "adk_docs_context.txt"
    ],
    "07_callbacks_eventos": [
        "adk_docs_callbacks.txt",
        "adk_docs_callbacks_types_of_callbacks.txt",
        "adk_docs_callbacks_design_patterns_and_best_practices.txt",
        "adk_docs_events.txt"
    ],
    "08_runtime_ejecucion": [
        "adk_docs_runtime.txt",
        "adk_docs_runtime_runconfig.txt"
    ],
    "09_deploy_despliegue": {
        "conceptos_generales": [
            "adk_docs_deploy.txt"
        ],
        "plataformas": [
            "adk_docs_deploy_agent_engine.txt",
            "adk_docs_deploy_cloud_run.txt",
            "adk_docs_deploy_gke.txt"
        ]
    },
    "10_observabilidad_evaluacion": [
        "adk_docs_evaluate.txt",
        "adk_docs_observability_arize_ax.txt",
        "adk_docs_observability_phoenix.txt"
    ],
    "11_seguridad": [
        "adk_docs_safety.txt"
    ],
    "12_api_reference": [
        "adk_docs_api_reference.txt",
        "adk_docs_api_reference_python.txt",
        "adk_docs_api_reference_java.txt"
    ],
    "13_tutoriales_ejemplos": [
        "adk_docs_tutorials.txt",
        "adk_docs_tutorials_agent_team.txt"
    ],
    "14_comunidad_contribucion": [
        "adk_docs_community.txt",
        "adk_docs_contributing_guide.txt"
    ],
    "15_recursos_adicionales": [
        "adk_docs_artifacts.txt"
    ]
}

def create_directory_structure(base_dir):
    """Crea la estructura de directorios"""
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    os.makedirs(base_dir)
    
    for section, content in STRUCTURE.items():
        if isinstance(content, dict):
            # Crear subdirectorios
            section_dir = os.path.join(base_dir, section)
            os.makedirs(section_dir)
            for subsection in content.keys():
                os.makedirs(os.path.join(section_dir, subsection))
        else:
            # Crear directorio simple
            os.makedirs(os.path.join(base_dir, section))

def copy_files():
    """Copia y organiza los archivos según la estructura"""
    files_copied = 0
    files_not_found = []
    
    for section, content in STRUCTURE.items():
        if isinstance(content, dict):
            # Sección con subdirectorios
            for subsection, files in content.items():
                target_dir = os.path.join(ORGANIZED_DIR, section, subsection)
                for filename in files:
                    source_path = os.path.join(SOURCE_DIR, filename)
                    if os.path.exists(source_path):
                        target_path = os.path.join(target_dir, filename)
                        shutil.copy2(source_path, target_path)
                        files_copied += 1
                        print(f"✅ Copiado: {filename} -> {section}/{subsection}/")
                    else:
                        files_not_found.append(filename)
        else:
            # Sección simple
            target_dir = os.path.join(ORGANIZED_DIR, section)
            for filename in content:
                source_path = os.path.join(SOURCE_DIR, filename)
                if os.path.exists(source_path):
                    target_path = os.path.join(target_dir, filename)
                    shutil.copy2(source_path, target_path)
                    files_copied += 1
                    print(f"✅ Copiado: {filename} -> {section}/")
                else:
                    files_not_found.append(filename)
    
    return files_copied, files_not_found

def create_master_index():
    """Crea un archivo índice maestro con toda la estructura"""
    index_content = """# Agent Development Kit (ADK) - Documentación Organizada

Esta documentación está organizada jerárquicamente para facilitar su comprensión por parte de LLMs.

## Estructura de la Documentación

### 1. INTRODUCCIÓN Y CONCEPTOS BÁSICOS
- **¿Qué es ADK?**: Framework flexible y modular para desarrollo de agentes de IA
- **Optimizado para**: Gemini y ecosistema Google, pero compatible con otros frameworks
- **Características**: Model-agnostic, deployment-agnostic, compatible con frameworks existentes

### 2. INSTALACIÓN E INICIO RÁPIDO
- **Instalación**: pip install google-adk (Python) o dependencias Maven/Gradle (Java)
- **Quickstart**: Primeros pasos para crear y ejecutar agentes
- **Testing**: Herramientas y patrones para probar agentes

### 3. AGENTES (Core del Framework)
#### 3.1 Conceptos Generales
- Tipos de agentes y su propósito
- Arquitectura y diseño de agentes

#### 3.2 Tipos de Agentes
- **LLM Agents**: Agentes basados en modelos de lenguaje
- **Custom Agents**: Agentes personalizados
- **Multi-Agents**: Sistemas de múltiples agentes colaborando

#### 3.3 Workflow Agents (Orquestación)
- **Sequential Agents**: Ejecución secuencial de tareas
- **Parallel Agents**: Ejecución paralela de tareas
- **Loop Agents**: Ejecución iterativa con bucles

#### 3.4 Modelos
- Integración con diferentes modelos de IA
- Configuración y optimización

### 4. HERRAMIENTAS (Tools)
#### 4.1 Conceptos Generales
- Ecosistema de herramientas disponibles
- Cómo integrar herramientas con agentes

#### 4.2 Tipos de Herramientas
- **Built-in Tools**: Herramientas integradas (Search, Code Exec)
- **Function Tools**: Funciones personalizadas
- **Google Cloud Tools**: Herramientas específicas de Google Cloud
- **Third-party Tools**: Integración con bibliotecas externas (LangChain, CrewAI)

#### 4.3 Integraciones
- **MCP Tools**: Model Context Protocol
- **OpenAPI Tools**: Integración con APIs REST
- **Autenticación**: Gestión de credenciales y permisos

### 5. STREAMING
#### 5.1 Conceptos y Configuración
- Streaming en tiempo real para agentes
- Configuración de streaming

#### 5.2 Implementación
- **Custom Streaming**: Implementación personalizada
- **WebSocket Streaming**: Streaming vía WebSocket
- **Streaming Tools**: Herramientas específicas para streaming

#### 5.3 Quickstart
- Guías rápidas para Python y Java

### 6. SESIONES Y CONTEXTO
- **Sessions**: Gestión de sesiones de usuario
- **Memory**: Manejo de memoria persistente
- **State**: Gestión de estado de agentes
- **Context**: Contexto compartido entre agentes

### 7. CALLBACKS Y EVENTOS
- **Callbacks**: Patrones de callbacks para monitoreo
- **Tipos de Callbacks**: Diferentes tipos y casos de uso
- **Design Patterns**: Mejores prácticas y patrones
- **Events**: Sistema de eventos del framework

### 8. RUNTIME Y EJECUCIÓN
- **Runtime**: Gestión del tiempo de ejecución
- **RunConfig**: Configuración de ejecución

### 9. DEPLOYMENT (Despliegue)
#### 9.1 Conceptos Generales
- Estrategias de despliegue

#### 9.2 Plataformas
- **Vertex AI Agent Engine**: Despliegue en Vertex AI
- **Cloud Run**: Despliegue en Google Cloud Run
- **GKE**: Despliegue en Google Kubernetes Engine

### 10. OBSERVABILIDAD Y EVALUACIÓN
- **Evaluation**: Evaluación sistemática de agentes
- **Arize AX**: Integración con Arize AX
- **Phoenix**: Observabilidad con Phoenix

### 11. SEGURIDAD
- **Safety**: Patrones de seguridad y mejores prácticas
- Construcción de agentes seguros y confiables

### 12. API REFERENCE
- **Python API**: Referencia completa de la API de Python
- **Java API**: Referencia completa de la API de Java

### 13. TUTORIALES Y EJEMPLOS
- **Tutoriales**: Guías paso a paso
- **Agent Team**: Tutorial completo de equipos de agentes

### 14. COMUNIDAD Y CONTRIBUCIÓN
- **Community**: Recursos de la comunidad
- **Contributing**: Guía para contribuir al proyecto

### 15. RECURSOS ADICIONALES
- **Artifacts**: Recursos adicionales y herramientas

## Flujo de Aprendizaje Recomendado

1. **Inicio**: Introducción → Instalación → Quickstart
2. **Core**: Agentes → Herramientas → Workflow Agents
3. **Avanzado**: Streaming → Sesiones → Callbacks
4. **Producción**: Runtime → Deployment → Observabilidad
5. **Especialización**: Seguridad → API Reference → Tutoriales

## Casos de Uso Principales

- **Simple Tasks**: Agentes individuales con herramientas específicas
- **Complex Workflows**: Workflow agents para pipelines predecibles
- **Dynamic Routing**: LLM-driven routing para comportamiento adaptativo
- **Multi-Agent Systems**: Coordinación y delegación compleja
- **Production Deployment**: Escalado con infraestructura robusta
"""
    
    with open(os.path.join(ORGANIZED_DIR, "README_ESTRUCTURA.md"), "w", encoding="utf-8") as f:
        f.write(index_content)

def main():
    print("🚀 Organizando documentación del ADK jerárquicamente...")
    
    # Crear estructura de directorios
    print("📁 Creando estructura de directorios...")
    create_directory_structure(ORGANIZED_DIR)
    
    # Copiar y organizar archivos
    print("📋 Copiando y organizando archivos...")
    files_copied, files_not_found = copy_files()
    
    # Crear índice maestro
    print("📖 Creando índice maestro...")
    create_master_index()
    
    # Reporte final
    print(f"\n✅ Organización completada!")
    print(f"📊 Archivos copiados: {files_copied}")
    
    if files_not_found:
        print(f"⚠️  Archivos no encontrados: {len(files_not_found)}")
        for filename in files_not_found:
            print(f"   - {filename}")
    
    print(f"\n📁 Documentación organizada en: {ORGANIZED_DIR}")
    print(f"📖 Ver README_ESTRUCTURA.md para guía completa")

if __name__ == "__main__":
    main() 