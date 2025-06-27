import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://google.github.io/adk-docs/"
OUTPUT_DIR = "adk_docs_txt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_page(url):
    print(f"Descargando: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error al descargar {url}: {e}")
        return None

def save_text(html, filename):
    soup = BeautifulSoup(html, "html.parser")
    
    # Quita scripts, estilos y navegación para limpiar el texto
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n", strip=True)

    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"✅ Guardado: {filename}")

def extract_all_links(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # Buscar enlaces en diferentes elementos de navegación
    nav_elements = soup.find_all(["nav", "aside", "div"], class_=lambda x: x and any(
        nav_class in str(x).lower() for nav_class in ["nav", "sidebar", "menu", "toc"]
    ))
    
    links = set()
    
    # También buscar todos los enlaces internos
    all_links = soup.find_all("a", href=True)
    
    for a in all_links:
        href = a.get('href', '')
        if href:
            full_url = urljoin(BASE_URL, href)
            # Solo incluir enlaces del mismo dominio
            if urlparse(full_url).netloc == urlparse(BASE_URL).netloc:
                links.add(full_url)
    
    return sorted(links)

def get_filename_from_url(url):
    """Genera un nombre de archivo limpio basado en la URL"""
    path = urlparse(url).path.strip('/')
    if not path:
        return "index.txt"
    
    # Reemplazar caracteres especiales y crear nombre de archivo
    filename = path.replace('/', '_').replace('-', '_')
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    return filename

# URLs específicas conocidas del framework ADK
specific_urls = [
    "https://google.github.io/adk-docs/",
    "https://google.github.io/adk-docs/get_started/",
    "https://google.github.io/adk-docs/agents/",
    "https://google.github.io/adk-docs/workflow_agents/",
    "https://google.github.io/adk-docs/api_reference/",
    "https://google.github.io/adk-docs/tools/",
    "https://google.github.io/adk-docs/deploy/",
    "https://google.github.io/adk-docs/streaming/",
    "https://google.github.io/adk-docs/observability/",
    "https://google.github.io/adk-docs/runtime/",
    "https://google.github.io/adk-docs/sessions/",
    "https://google.github.io/adk-docs/callbacks/",
    "https://google.github.io/adk-docs/tutorials/",
    "https://google.github.io/adk-docs/sample_agents/",
    "https://google.github.io/adk-docs/contribute/"
]

print("🚀 Iniciando descarga de documentación ADK...")

# Conjunto para evitar duplicados
visited_urls = set()
all_urls = set(specific_urls)

# Paso 1: Página principal para extraer más enlaces
main_html = get_page(BASE_URL)
if main_html:
    save_text(main_html, "index.txt")
    visited_urls.add(BASE_URL)
    
    # Extraer enlaces adicionales de la página principal
    discovered_links = extract_all_links(main_html)
    all_urls.update(discovered_links)
    
    print(f"📋 Encontrados {len(all_urls)} enlaces totales")

# Paso 2: Descargar todas las páginas
for url in sorted(all_urls):
    if url in visited_urls:
        continue
        
    # Pequeña pausa para no sobrecargar el servidor
    time.sleep(1)
    
    html = get_page(url)
    if html:
        filename = get_filename_from_url(url)
        save_text(html, filename)
        visited_urls.add(url)

print(f"✅ Descarga completada! {len(visited_urls)} páginas guardadas en: {OUTPUT_DIR}")
print(f"📁 Archivos creados:")

# Mostrar lista de archivos creados
for filename in sorted(os.listdir(OUTPUT_DIR)):
    if filename.endswith('.txt'):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, filename))
        print(f"  - {filename} ({size} bytes)") 