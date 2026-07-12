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
@click.option('--python', is_flag=True, help='Activa el análisis de calidad para Python.')
@click.option('--php', is_flag=True, help='Activa el análisis de calidad para PHP (Próximamente).')
@click.option('--js', is_flag=True, help='Activa el análisis de calidad para JavaScript (Próximamente).')
def analyze(repo, limite, salario, horas, loc_por_hora, python, php, js):
    """Analiza los costos de desarrollo de un repositorio y calcula el IEF."""
    mostrar_banner()
    cargar_entorno(repo if es_local_path(repo) else None)

    if salario is None:
        salario = click.prompt("Salario mensual promedio (USD)", type=float)

    lenguaje = None
    if python:
        lenguaje = "python"
    elif php:
        click.echo("[Info] PHP - Próximamente. Usando Python por ahora.")
        lenguaje = "python"
    elif js:
        click.echo("[Info] JavaScript - Próximamente. Usando Python por ahora.")
        lenguaje = "python"
    else:
        if click.confirm("¿Desea realizar el analisis de calidad de codigo?", default=True):
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
        else:
            lenguaje = "skip"

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
        
        c_esp = None
        c_esp_input = click.prompt("Presupuesto (C_esp) [Presiona Enter para omitir]", default="", show_default=False).strip()
        if c_esp_input:
            try:
                val = float(c_esp_input)
                if val <= 0:
                    click.echo("[Error] El presupuesto debe ser mayor que 0.")
                    mostrar_resumen_financiero(resultados)
                else:
                    c_esp = val
                    mostrar_resumen_financiero(resultados, c_esp)
            except ValueError:
                click.echo("[Error] Presupuesto invalido (debe ser un numero).")
                mostrar_resumen_financiero(resultados)
        else:
            mostrar_resumen_financiero(resultados)

        # Generar Reporte HTML
        if click.confirm("\n¿Desea generar un reporte HTML?", default=True):
            from oraculus.core.reporter import generar_reporte_html, guardar_reporte
            import webbrowser
            import os
            
            resultados["c_esp"] = c_esp
            resultados["ief"] = (resultados["costo_real"] / c_esp) if c_esp else None
            
            html = generar_reporte_html(resultados, repo, c_esp)
            ruta = guardar_reporte(html, repo, resultados)
            ruta_abs = os.path.abspath(ruta)
            click.echo(f"[Info] Reporte generado en: oraculus_reports/{os.path.basename(ruta_abs)}")
            click.echo("[Info] Abriendo en el navegador...")
            webbrowser.open(ruta_abs)

    except Exception as e:
        click.echo(click.style(f"\n[Error] {e}", fg="red"))

def es_local_path(entrada: str) -> bool:
    import os
    return os.path.exists(entrada)

def limpiar_unicode_consola(texto: str) -> str:
    import sys
    try:
        encoding = sys.stdout.encoding or "utf-8"
        texto.encode(encoding)
        return texto
    except Exception:
        return (
            texto.replace("→", "->")
                 .replace("↑", "^")
                 .replace("↓", "v")
                 .replace("©", "(c)")
        )

@click.command("history")
@click.option("--open", "abrir", type=int, default=None, help="Número del reporte a abrir")
def history(abrir):
    """Muestra el historial de análisis generados."""
    from oraculus.utils.history_manager import cargar_historial, abrir_reporte
    
    if abrir is not None:
        try:
            abrir_reporte(abrir)
        except Exception as e:
            click.echo(click.style(f"[Error] {e}", fg="red"))
        return

    historial = cargar_historial()
    if not historial:
        click.echo("[Info] No hay análisis guardados aún.")
        return

    from rich.table import Table
    from rich.console import Console
    from rich.panel import Panel
    from rich import box
    from oraculus.cli.display import CyberpunkColors

    console = Console()
    c = CyberpunkColors

    table = Table(
        title=f"[bold {c.LOGO}]=== HISTORIAL DE ANÁLISIS ===[/]",
        box=box.ASCII,
        border_style=c.LOGO
    )
    table.add_column("#", style=c.NEON_CYAN, justify="center")
    table.add_column("Repositorio", style=c.TEXTO_P, width=25)
    table.add_column("IEF", justify="right")
    table.add_column("Riesgo", justify="center")
    table.add_column("Fecha", justify="center", style=c.NEON_CYAN)

    for item in historial:
        riesgo_val = item["riesgo"]
        if riesgo_val == "CRITICO":
            style_r = f"bold {c.NEON_RED}"
        elif riesgo_val == "ALTO":
            style_r = "bold color(208)"
        elif riesgo_val == "MODERADO":
            style_r = "bold color(226)"
        else:
            style_r = f"bold {c.NEON_GREEN}"
            
        ief_val = item["ief"]
        ief_str = f"{ief_val:.2f}" if ief_val is not None else "N/D"
        
        fecha_val = item["fecha"]
        fecha_str = fecha_val[5:] if len(fecha_val) >= 10 else fecha_val
        
        table.add_row(
            str(item["id"]),
            item["repo"],
            ief_str,
            f"[{style_r}]{riesgo_val}[/]",
            fecha_str
        )

    console.print(table)
    click.echo(f"Ejecuta: oraculus history --open <#> para abrir un reporte\n")

    # Tendencia del último repositorio analizado
    ultimo_repo = historial[-1]["repo"]
    repo_entries = [item for item in historial if item["repo"] == ultimo_repo]
    if len(repo_entries) > 1:
        # Calcular tendencias de IEF
        iefs = [item["ief"] for item in repo_entries]
        valid_iefs = [v for v in iefs if v is not None]
        ief_trend_str = " → ".join([f"{v:.2f}" if v is not None else "N/D" for v in iefs])
        
        if len(valid_iefs) >= 2:
            first_ief = valid_iefs[0]
            last_ief = valid_iefs[-1]
            if last_ief > first_ief:
                ief_msg = " [bold color(196)][↑ Deteriorando][/]"
            elif last_ief < first_ief:
                ief_msg = f" [bold {c.NEON_GREEN}][↓ Mejorando][/]"
            else:
                ief_msg = f" [bold {c.TEXTO_P}][= Estable][/]"
        else:
            ief_msg = ""
            
        # Calcular tendencias de Deuda
        deudas = [item.get("costo_deuda", 0.0) for item in repo_entries]
        deuda_trend_str = " → ".join([f"${v:.0f}" for v in deudas])
        
        first_deuda = deudas[0]
        last_deuda = deudas[-1]
        if last_deuda > first_deuda:
            deuda_msg = " [bold color(196)][↑ Acumulando][/]"
        elif last_deuda < first_deuda:
            deuda_msg = f" [bold {c.NEON_GREEN}][↓ Reduciendo][/]"
        else:
            deuda_msg = f" [bold {c.TEXTO_P}][= Estable][/]"
            
        trend_content = (
            f"  [bold {c.NEON_CYAN}]IEF:[/]   {ief_trend_str}{ief_msg}\n"
            f"  [bold {c.NEON_CYAN}]Deuda:[/] {deuda_trend_str}{deuda_msg}"
        )
        
        trend_content = limpiar_unicode_consola(trend_content)
        trend_title = limpiar_unicode_consola(f"[bold {c.NEON_CYAN}]=== TENDENCIA: {ultimo_repo} ===[/bold {c.NEON_CYAN}]")
        
        console.print(Panel(
            trend_content,
            title=trend_title,
            box=box.ASCII,
            border_style=c.NEON_CYAN,
            width=60
        ))

cli.add_command(analyze)
cli.add_command(history)
