# Agent Development Kit (ADK) - Documentación Organizada

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
