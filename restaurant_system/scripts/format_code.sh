#!/bin/bash
# Formateo automático de código para el proyecto Restaurant Multi-Agent System
# Siguiendo las mejores prácticas del repositorio oficial de ADK

echo "🚀 Iniciando formateo de código..."

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: No se encontró pyproject.toml. Ejecuta desde el directorio raíz del proyecto."
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "restaurant_env" ]; then
    echo "📦 Activando entorno virtual..."
    source restaurant_env/bin/activate
fi

echo "🔧 Formateando código con black..."
black . --line-length 88 --target-version py39 --exclude restaurant_env

echo "📐 Organizando imports con isort..."
isort . --profile black --skip restaurant_env

echo "🔍 Ejecutando linting con flake8..."
flake8 . --max-line-length=88 --extend-ignore=E203,W503 --exclude restaurant_env

echo "🧹 Verificando tipos con mypy..."
mypy . --ignore-missing-imports --exclude restaurant_env

echo "✅ Formateo completado!"

# Mostrar estadísticas
echo ""
echo "📊 Estadísticas del código:"
find . -name "*.py" -not -path "./restaurant_env/*" -exec wc -l {} + | tail -n 1 | awk '{print "Líneas de código: " $1}'
find . -name "*.py" -not -path "./restaurant_env/*" | wc -l | awk '{print "Archivos Python: " $1}'

echo ""
echo "🎯 Para ejecutar tests:"
echo "  pytest"
echo ""
echo "🎯 Para evaluar agentes:"
echo "  adk eval . tests/evaluation/restaurant_eval_set.evalset.json" 