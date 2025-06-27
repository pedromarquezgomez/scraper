"""
CLI moderna para el Sistema Multiagente del Restaurante
Siguiendo las mejores prácticas de ADK v1.5.0+
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config.system_config import SystemConfig
    from main import RestaurantMultiAgentSystem
except ImportError:
    # Para desarrollo, cuando se ejecuta desde el directorio del proyecto
    from restaurant_system.config.system_config import SystemConfig
    from restaurant_system.main import RestaurantMultiAgentSystem


@click.group()
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx):
    """
    🍽️ Restaurant Multi-Agent System CLI

    Sistema multiagente sofisticado para restaurantes basado en ADK.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "--mode",
    type=click.Choice(["interactive", "api", "eval"]),
    default="interactive",
    help="Modo de ejecución del sistema",
)
@click.option(
    "--port", type=int, default=8000, help="Puerto para modo API (default: 8000)"
)
@click.option(
    "--host",
    type=str,
    default="localhost",
    help="Host para modo API (default: localhost)",
)
@click.option("--debug", is_flag=True, help="Activar modo debug")
def run(mode: str, port: int, host: str, debug: bool):
    """Ejecuta el sistema multiagente del restaurante."""

    click.echo(
        "🍽️ " + click.style("Restaurant Multi-Agent System", fg="green", bold=True)
    )
    click.echo(f"📍 Modo: {click.style(mode, fg='blue')}")

    # Verificar variables de entorno
    if not os.getenv("GOOGLE_API_KEY"):
        click.echo(
            click.style(
                "⚠️  GOOGLE_API_KEY no encontrada en variables de entorno", fg="yellow"
            )
        )
        click.echo("💡 Copia env_example.txt a .env y configura tu API key")
        return

    if mode == "interactive":
        asyncio.run(_run_interactive_mode(debug))
    elif mode == "api":
        _run_api_mode(host, port, debug)
    elif mode == "eval":
        _run_evaluation_mode()


@cli.command()
@click.option("--query", "-q", required=True, help="Consulta para procesar")
@click.option(
    "--user-id", default="cli_user", help="ID del usuario (default: cli_user)"
)
@click.option(
    "--format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Formato de salida",
)
def query(query: str, user_id: str, format: str):
    """Procesa una consulta única y muestra la respuesta."""

    click.echo(f"🤖 Procesando: {click.style(query, fg='cyan')}")

    async def process_single_query():
        system = RestaurantMultiAgentSystem()
        response = await system.process_query(query, user_id=user_id)

        if format == "json":
            import json

            result = {
                "query": query,
                "user_id": user_id,
                "response": response,
                "timestamp": "2025-01-27T08:00:00Z",
            }
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n💬 {click.style('Respuesta:', fg='green')}")
            click.echo(response)

    asyncio.run(process_single_query())


@cli.command()
@click.option(
    "--eval-set",
    type=click.Path(exists=True),
    default="tests/evaluation/restaurant_eval_set.evalset.json",
    help="Archivo de conjunto de evaluación",
)
@click.option("--output", type=click.Path(), help="Archivo de salida para resultados")
@click.option("--verbose", is_flag=True, help="Salida detallada")
def evaluate(eval_set: str, output: Optional[str], verbose: bool):
    """Ejecuta evaluación del sistema usando conjunto de pruebas."""

    click.echo(
        "📊 " + click.style("Iniciando evaluación del sistema", fg="blue", bold=True)
    )

    try:
        # Usar el comando de evaluación de ADK
        import subprocess

        cmd = ["adk", "eval", ".", eval_set]
        if output:
            cmd.extend(["--output", output])
        if verbose:
            cmd.append("--verbose")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            click.echo(
                "✅ " + click.style("Evaluación completada exitosamente", fg="green")
            )
            if verbose:
                click.echo(result.stdout)
        else:
            click.echo("❌ " + click.style("Error en evaluación", fg="red"))
            click.echo(result.stderr)

    except FileNotFoundError:
        click.echo("❌ " + click.style("ADK CLI no encontrado", fg="red"))
        click.echo("💡 Instala ADK: pip install google-adk")


@cli.command()
@click.option(
    "--agent",
    type=click.Choice(["food", "drinks", "nutrition", "orchestrator"]),
    help="Agente específico para testing",
)
def test(agent: Optional[str]):
    """Ejecuta tests del sistema."""

    click.echo("🧪 " + click.style("Ejecutando tests", fg="blue", bold=True))

    import subprocess

    cmd = ["pytest"]

    if agent:
        # Ejecutar tests específicos del agente
        test_file = f"tests/unit/test_{agent}_agent.py"
        if Path(test_file).exists():
            cmd.append(test_file)
        else:
            click.echo(f"❌ Tests para {agent} no encontrados")
            return

    cmd.extend(["-v", "--cov=restaurant_system", "--cov-report=term-missing"])

    result = subprocess.run(cmd)

    if result.returncode == 0:
        click.echo("✅ " + click.style("Todos los tests pasaron", fg="green"))
    else:
        click.echo("❌ " + click.style("Algunos tests fallaron", fg="red"))


@cli.command()
def format_code():
    """Formatea el código usando las mejores prácticas."""

    click.echo("🎨 " + click.style("Formateando código", fg="blue", bold=True))

    import subprocess

    # Ejecutar script de formateo
    script_path = Path("scripts/format_code.sh")
    if script_path.exists():
        result = subprocess.run(["bash", str(script_path)])
        if result.returncode == 0:
            click.echo(
                "✅ " + click.style("Código formateado correctamente", fg="green")
            )
        else:
            click.echo("❌ " + click.style("Error en formateo", fg="red"))
    else:
        click.echo("❌ " + click.style("Script de formateo no encontrado", fg="red"))


@cli.command()
@click.option(
    "--platform",
    type=click.Choice(["local", "cloud-run", "vertex-ai"]),
    default="local",
    help="Plataforma de deployment",
)
@click.option(
    "--project-id",
    help="ID del proyecto de Google Cloud (requerido para cloud deployment)",
)
@click.option(
    "--region",
    default="us-central1",
    help="Región para deployment (default: us-central1)",
)
def deploy(platform: str, project_id: Optional[str], region: str):
    """Despliega el sistema en la plataforma especificada."""

    click.echo(f"🚀 Desplegando en {click.style(platform, fg='blue')}")

    if platform == "local":
        click.echo("💻 Deployment local - usar 'run --mode api'")
    elif platform == "cloud-run":
        if not project_id:
            click.echo("❌ project-id requerido para Cloud Run")
            return
        _deploy_cloud_run(project_id, region)
    elif platform == "vertex-ai":
        if not project_id:
            click.echo("❌ project-id requerido para Vertex AI")
            return
        _deploy_vertex_ai(project_id, region)


async def _run_interactive_mode(debug: bool):
    """Ejecuta el modo interactivo."""
    try:
        system = RestaurantMultiAgentSystem()
        await system.start_interactive_mode()
    except KeyboardInterrupt:
        click.echo("\n👋 Sistema interrumpido por el usuario")
    except Exception as e:
        if debug:
            raise
        click.echo(f"❌ Error: {e}")


def _run_api_mode(host: str, port: int, debug: bool):
    """Ejecuta el modo API."""
    try:
        import uvicorn

        click.echo(f"🌐 Iniciando API en http://{host}:{port}")
        uvicorn.run(
            "api:app",
            host=host,
            port=port,
            reload=debug,
            log_level="debug" if debug else "info",
        )
    except ImportError:
        click.echo("❌ uvicorn no instalado. Instala: pip install uvicorn")
    except Exception as e:
        click.echo(f"❌ Error iniciando API: {e}")


def _run_evaluation_mode():
    """Ejecuta el modo de evaluación."""
    click.echo("📊 Modo evaluación - usar comando 'evaluate'")


def _deploy_cloud_run(project_id: str, region: str):
    """Despliega en Cloud Run."""
    click.echo(f"☁️  Desplegando en Cloud Run - Proyecto: {project_id}")

    import subprocess

    cmd = [
        "gcloud",
        "run",
        "deploy",
        "restaurant-system",
        "--source",
        ".",
        "--platform",
        "managed",
        "--region",
        region,
        "--project",
        project_id,
        "--allow-unauthenticated",
    ]

    result = subprocess.run(cmd)
    if result.returncode == 0:
        click.echo("✅ Deployment en Cloud Run exitoso")
    else:
        click.echo("❌ Error en deployment")


def _deploy_vertex_ai(project_id: str, region: str):
    """Despliega en Vertex AI."""
    click.echo(f"🧠 Desplegando en Vertex AI - Proyecto: {project_id}")
    # Implementación de deployment en Vertex AI
    click.echo("💡 Funcionalidad en desarrollo")


def main():
    """Punto de entrada principal."""
    cli()


if __name__ == "__main__":
    main()
