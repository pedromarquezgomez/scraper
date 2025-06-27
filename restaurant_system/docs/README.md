# 📚 Documentación del Sistema Multiagente de Restaurante

## Estructura del Proyecto

Este proyecto sigue las mejores prácticas del [Agent Development Kit (ADK) de Google](https://github.com/google/adk-python.git):

```
restaurant_system/
├── src/restaurant/           # Código fuente principal
│   ├── agents/              # Agentes especializados
│   ├── config/              # Configuraciones del sistema
│   ├── main.py              # Aplicación principal
│   ├── cli.py               # Interfaz de línea de comandos
│   └── web_config.py        # Configuración web
├── tests/                   # Tests unitarios e integración
├── docs/                    # Documentación
├── scripts/                 # Scripts de desarrollo y deployment
├── coverage_reports/        # Reportes de cobertura de código
└── pyproject.toml          # Configuración del proyecto
```

## Arquitectura

### Agentes Especializados
- **RestaurantCoordinator**: Agente coordinador principal
- **FoodSpecialist**: Especialista en comida y menú
- **DrinksSpecialist**: Especialista en bebidas (próximamente)
- **NutritionSpecialist**: Especialista en nutrición (próximamente)

### Tecnologías
- **Google ADK**: Framework principal para agentes
- **Gemini 2.0**: Modelo de lenguaje
- **FastAPI**: API web
- **pytest**: Testing
- **Coverage**: Cobertura de código

## Instalación

```bash
# Desarrollo
pip install -e ".[dev]"

# Producción
pip install -e "."
```

## Uso

```bash
# CLI
restaurant-cli --help

# Web
adk web
```

## Testing

```bash
# Tests completos
pytest

# Con cobertura
pytest --cov=src/restaurant --cov-report=html
```

## Desarrollo

Seguimos las mejores prácticas de ADK:
- Code-first development
- Modular multi-agent systems
- Rich tool ecosystem
- Comprehensive testing 