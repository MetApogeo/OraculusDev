import click
from oraculus.utils.config import cargar_entorno
from oraculus.core.engine import ejecutar_motor_analisis
from oraculus.cli.display import mostrar_reporte, mostrar_resumen_financiero, mostrar_banner

@click.group()
def cli():
    """Oraculus: Herramienta CLI de Analitica Financiera de Repositorios."""
    pass

@click.command(name="analyze")
@click.option('--repo', default='.', help='Ruta local del repo o usuario/repo de GitHub.')
@click.option('--limite', default=10, type=int, help='Límite de commits a analizar.')
@click.option('--salario', type=float, help='Salario mensual promedio.')
@click.option('--horas', type=int, default=160, help='Horas efectivas al mes.')
@click.option('--loc-por-hora', type=float, default=60.0, help='LOC promedio por hora.')
def analyze(repo, limite, salario, horas, loc_por_hora):
    """Analiza los costos de desarrollo de un repositorio y calcula el IEF."""
    mostrar_banner()
    cargar_entorno(repo if es_local_path(repo) else None)

    if salario is None:
        salario = click.prompt("Salario mensual promedio (USD)", type=float)

    click.echo("\n¿Qué lenguaje deseas analizar?")
    click.echo("  [ 1 ] Python   (Radon)")
    click.echo("  [ 2 ] PHP      — Próximamente")
    click.echo("  [ 3 ] JavaScript — Próximamente")
    click.echo("  [ 4 ] Auto-detectar")
    lang_choice = click.prompt("Seleccione una opcion [Por defecto: 1]", default="1", type=click.Choice(['1', '2', '3', '4']), show_choices=False)

    if lang_choice == "1":
        lenguaje = "python"
    elif lang_choice == "2":
        click.echo("[Info] PHP - Próximamente. Usando Python por ahora.")
        lenguaje = "python"
    elif lang_choice == "3":
        click.echo("[Info] JavaScript - Próximamente. Usando Python por ahora.")
        lenguaje = "python"
    else:
        lenguaje = "auto"

    if limite < 10:
        click.echo("\n[Advertencia] Con menos de 10 commits el filtro IQR puede no ser representativo.")

    try:
        resultados = ejecutar_motor_analisis(
            repo=repo,
            limite=limite,
            salario=salario,
            horas_efectivas=horas,
            loc_por_hora=loc_por_hora,
            lenguaje=lenguaje
        )
        
        mostrar_reporte(resultados, salario, horas, loc_por_hora)
        
        c_esp_input = click.prompt("Presupuesto (C_esp) [Presiona Enter para omitir]", default="", show_default=False).strip()
        if c_esp_input:
            try:
                c_esp = float(c_esp_input)
                if c_esp <= 0:
                    click.echo("[Error] El presupuesto debe ser mayor que 0.")
                    mostrar_resumen_financiero(resultados)
                else:
                    mostrar_resumen_financiero(resultados, c_esp)
            except ValueError:
                click.echo("[Error] Presupuesto invalido (debe ser un numero).")
                mostrar_resumen_financiero(resultados)
        else:
            mostrar_resumen_financiero(resultados)

    except Exception as e:
        click.echo(click.style(f"\n[Error] {e}", fg="red"))

def es_local_path(entrada: str) -> bool:
    import os
    return os.path.exists(entrada)

cli.add_command(analyze)
