import os
from pathlib import Path

ORGANIZED_DIR = "adk_docs_organized"
OUTPUT_FILE = "ADK_DOCUMENTACION_COMPLETA.md"

# Orden de secciones para el flujo lógico
SECTION_ORDER = [
    "01_introduccion",
    "02_instalacion_inicio", 
    "03_agentes",
    "04_herramientas",
    "05_streaming",
    "06_sesiones_contexto",
    "07_callbacks_eventos",
    "08_runtime_ejecucion",
    "09_deploy_despliegue",
    "10_observabilidad_evaluacion",
    "11_seguridad",
    "12_api_reference",
    "13_tutoriales_ejemplos",
    "14_comunidad_contribucion",
    "15_recursos_adicionales"
]

# Mapeo de secciones a títulos legibles
SECTION_TITLES = {
    "01_introduccion": "INTRODUCCIÓN Y CONCEPTOS BÁSICOS",
    "02_instalacion_inicio": "INSTALACIÓN E INICIO RÁPIDO",
    "03_agentes": "AGENTES (CORE DEL FRAMEWORK)",
    "04_herramientas": "HERRAMIENTAS (TOOLS)",
    "05_streaming": "STREAMING EN TIEMPO REAL",
    "06_sesiones_contexto": "SESIONES Y CONTEXTO",
    "07_callbacks_eventos": "CALLBACKS Y EVENTOS",
    "08_runtime_ejecucion": "RUNTIME Y EJECUCIÓN",
    "09_deploy_despliegue": "DEPLOYMENT (DESPLIEGUE)",
    "10_observabilidad_evaluacion": "OBSERVABILIDAD Y EVALUACIÓN",
    "11_seguridad": "SEGURIDAD Y SAFETY",
    "12_api_reference": "REFERENCIA DE API",
    "13_tutoriales_ejemplos": "TUTORIALES Y EJEMPLOS",
    "14_comunidad_contribucion": "COMUNIDAD Y CONTRIBUCIÓN",
    "15_recursos_adicionales": "RECURSOS ADICIONALES"
}

# Mapeo de subsecciones a títulos
SUBSECTION_TITLES = {
    "conceptos_generales": "Conceptos Generales",
    "tipos_de_agentes": "Tipos de Agentes",
    "workflow_agents": "Workflow Agents (Orquestación)",
    "modelos": "Modelos",
    "tipos_de_herramientas": "Tipos de Herramientas",
    "integraciones": "Integraciones",
    "autenticacion": "Autenticación",
    "configuracion": "Configuración",
    "implementacion": "Implementación",
    "quickstart": "Quickstart",
    "plataformas": "Plataformas de Despliegue"
}

def read_file_content(filepath):
    """Lee el contenido de un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        return f"Error leyendo {filepath}: {e}"

def clean_filename(filename):
    """Limpia el nombre del archivo para mostrar"""
    return filename.replace('adk_docs_', '').replace('.txt', '').replace('_', ' ').title()

def consolidate_documentation():
    """Consolida toda la documentación en un archivo maestro"""
    
    content = ["""# Agent Development Kit (ADK) - Documentación Completa

Este documento contiene la documentación completa del framework ADK (Agent Development Kit) organizada jerárquicamente para facilitar su comprensión y uso por parte de LLMs.

## Índice General

1. **INTRODUCCIÓN Y CONCEPTOS BÁSICOS**: ¿Qué es ADK?, características principales
2. **INSTALACIÓN E INICIO RÁPIDO**: Instalación, quickstart, testing
3. **AGENTES (CORE)**: Tipos de agentes, workflow agents, modelos
4. **HERRAMIENTAS (TOOLS)**: Herramientas integradas, tipos, integraciones
5. **STREAMING**: Streaming en tiempo real, configuración, implementación
6. **SESIONES Y CONTEXTO**: Gestión de sesiones, memoria, estado
7. **CALLBACKS Y EVENTOS**: Patrones de callbacks, eventos del sistema
8. **RUNTIME Y EJECUCIÓN**: Gestión del tiempo de ejecución, configuración
9. **DEPLOYMENT**: Estrategias de despliegue, plataformas
10. **OBSERVABILIDAD Y EVALUACIÓN**: Monitoreo, evaluación de agentes
11. **SEGURIDAD**: Patrones de seguridad, construcción de agentes seguros
12. **API REFERENCE**: Referencias completas de Python y Java
13. **TUTORIALES Y EJEMPLOS**: Guías paso a paso, ejemplos prácticos
14. **COMUNIDAD Y CONTRIBUCIÓN**: Recursos de la comunidad
15. **RECURSOS ADICIONALES**: Herramientas adicionales

---

"""]

    total_files = 0
    
    for section_dir in SECTION_ORDER:
        section_path = os.path.join(ORGANIZED_DIR, section_dir)
        
        if not os.path.exists(section_path):
            continue
            
        # Título de la sección principal
        section_title = SECTION_TITLES.get(section_dir, section_dir)
        content.append(f"# {section_title}\n")
        content.append("=" * len(section_title) + "\n\n")
        
        # Procesar subsecciones o archivos directos
        items = sorted(os.listdir(section_path))
        
        for item in items:
            item_path = os.path.join(section_path, item)
            
            if os.path.isdir(item_path):
                # Es una subsección
                subsection_title = SUBSECTION_TITLES.get(item, item.replace('_', ' ').title())
                content.append(f"## {subsection_title}\n")
                content.append("-" * len(subsection_title) + "\n\n")
                
                # Procesar archivos en la subsección
                subfiles = sorted([f for f in os.listdir(item_path) if f.endswith('.txt')])
                for subfile in subfiles:
                    subfile_path = os.path.join(item_path, subfile)
                    file_title = clean_filename(subfile)
                    
                    content.append(f"### {file_title}\n\n")
                    file_content = read_file_content(subfile_path)
                    content.append(f"```\n{file_content}\n```\n\n")
                    total_files += 1
                    
            elif item.endswith('.txt'):
                # Es un archivo directo
                file_title = clean_filename(item)
                content.append(f"## {file_title}\n\n")
                file_content = read_file_content(item_path)
                content.append(f"```\n{file_content}\n```\n\n")
                total_files += 1
        
        content.append("\n---\n\n")
    
    # Agregar pie de página
    content.append(f"""
## Resumen de Documentación

- **Total de archivos procesados**: {total_files}
- **Estructura**: 15 secciones principales organizadas jerárquicamente
- **Framework**: Agent Development Kit (ADK) de Google
- **Compatibilidad**: Python y Java
- **Enfoque**: Model-agnostic, deployment-agnostic

## Flujo de Aprendizaje Recomendado para LLMs

1. **Conceptos Básicos**: Leer secciones 1-2 para entender qué es ADK
2. **Core Framework**: Secciones 3-4 para agentes y herramientas
3. **Características Avanzadas**: Secciones 5-8 para streaming, sesiones, callbacks, runtime
4. **Producción**: Secciones 9-11 para deployment, observabilidad y seguridad
5. **Referencia**: Secciones 12-15 para APIs, tutoriales y recursos

Este documento está optimizado para ser procesado por LLMs y proporciona una comprensión completa del framework ADK.
""")
    
    return ''.join(content), total_files

def main():
    print("🚀 Consolidando documentación del ADK...")
    
    consolidated_content, total_files = consolidate_documentation()
    
    # Escribir archivo consolidado
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(consolidated_content)
    
    # Obtener tamaño del archivo
    file_size = os.path.getsize(OUTPUT_FILE)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Documentación consolidada creada:")
    print(f"📄 Archivo: {OUTPUT_FILE}")
    print(f"📊 Archivos procesados: {total_files}")
    print(f"📏 Tamaño: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    print(f"🎯 Optimizado para LLMs con estructura jerárquica clara")

if __name__ == "__main__":
    main() 