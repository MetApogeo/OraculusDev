import click
from oraculus.utils.config import cargar_entorno
from oraculus.core.engine import ejecutar_motor_analisis
from oraculus.cli.display import mostrar_reporte, mostrar_resumen_financiero, mostrar_banner
from oraculus.utils.i18n import t, inicializar_i18n

inicializar_i18n()

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
        salario = click.prompt(t('cli', 'input_salario').rstrip(': '), type=float)

    lenguaje = None
    if python:
        lenguaje = "python"
    elif php:
        click.echo(t('cli', 'info_php_proximamente'))
        lenguaje = "python"
    elif js:
        click.echo(t('cli', 'info_js_proximamente'))
        lenguaje = "python"
    else:
        if click.confirm(t('cli', 'confirm_calidad'), default=True):
            click.echo("\n" + t('cli', 'lang_select_titulo'))
            click.echo(t('cli', 'lang_option_python'))
            click.echo(t('cli', 'lang_option_php'))
            click.echo(t('cli', 'lang_option_js'))
            click.echo(t('cli', 'lang_option_auto'))
            lang_choice = click.prompt(t('cli', 'lang_prompt'), default="1", type=click.Choice(['1', '2', '3', '4']), show_choices=False)

            if lang_choice == "1":
                lenguaje = "python"
            elif lang_choice == "2":
                click.echo(t('cli', 'info_php_proximamente'))
                lenguaje = "python"
            elif lang_choice == "3":
                click.echo(t('cli', 'info_js_proximamente'))
                lenguaje = "python"
            else:
                lenguaje = "auto"
        else:
            lenguaje = "skip"

    if limite < 10:
        click.echo("\n" + t('cli', 'advertencia_limite'))

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
        c_esp_input = click.prompt(t('cli', 'input_presupuesto').rstrip(': '), default="", show_default=False).strip()
        if c_esp_input:
            try:
                val = float(c_esp_input)
                if val <= 0:
                    click.echo(t('cli', 'error_presupuesto_positivo'))
                    mostrar_resumen_financiero(resultados)
                else:
                    c_esp = val
                    mostrar_resumen_financiero(resultados, c_esp)
            except ValueError:
                click.echo(t('cli', 'error_presupuesto_invalido'))
                mostrar_resumen_financiero(resultados)
        else:
            mostrar_resumen_financiero(resultados)

        # Generar Reporte HTML
        if click.confirm("\n" + t('cli', 'confirm_html'), default=True):
            from oraculus.core.reporter import generar_reporte_html, guardar_reporte
            import webbrowser
            import os
            
            resultados["c_esp"] = c_esp
            resultados["ief"] = (resultados["costo_real"] / c_esp) if c_esp else None
            
            html = generar_reporte_html(resultados, repo, c_esp)
            ruta = guardar_reporte(html, repo, resultados)
            ruta_abs = os.path.abspath(ruta)
            click.echo(t('cli', 'report_generated').format(filename=os.path.basename(ruta_abs)))
            click.echo(t('cli', 'opening_browser'))
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
@click.option("--compare", type=(int, int), default=None, help="Comparación lado a lado de dos análisis específicos (ej. --compare 1 3)")
@click.option("--stats", is_flag=True, help="Estadísticas globales del historial de análisis")
@click.option("--clean", is_flag=True, help="Eliminar reportes antiguos de forma interactiva")
def history(abrir, compare, stats, clean):
    """Muestra el historial de análisis generados."""
    from oraculus.utils.history_manager import cargar_historial, abrir_reporte
    
    if abrir is not None:
        try:
            abrir_reporte(abrir)
        except Exception as e:
            click.echo(click.style(f"[Error] {e}", fg="red"))
        return

    if clean:
        historial = cargar_historial()
        if not historial:
            click.echo(t('cli', 'no_history'))
            return
            
        click.echo("\n" + t('cli', 'menu_limpieza'))
        click.echo(t('cli', 'analisis_actuales').format(cantidad=len(historial)))
        click.echo(t('cli', 'opcion_eliminar_todo'))
        click.echo(t('cli', 'opcion_conservar_3'))
        click.echo(t('cli', 'opcion_cancelar'))
        
        opcion = click.prompt(t('cli', 'seleccione_opcion'), type=int, default=3)
        if opcion == 1:
            if click.confirm(t('cli', 'confirm_eliminar_todo'), default=False):
                from oraculus.utils.history_manager import limpiar_historial_por_completo
                limpiar_historial_por_completo()
                click.echo(click.style(t('cli', 'limpieza_completa'), fg="green"))
            else:
                click.echo(t('cli', 'operacion_cancelada'))
        elif opcion == 2:
            if click.confirm(t('cli', 'confirm_conservar_3'), default=True):
                from oraculus.utils.history_manager import conservar_ultimos_n_reportes
                conservar_ultimos_n_reportes(3)
                click.echo(click.style(t('cli', 'limpieza_3'), fg="green"))
            else:
                click.echo(t('cli', 'operacion_cancelada'))
        else:
            click.echo(t('cli', 'operacion_cancelada'))
        return

    if stats:
        historial = cargar_historial()
        if not historial:
            click.echo(t('cli', 'no_history'))
            return
            
        ief_vals = [item["ief"] for item in historial if item["ief"] is not None]
        prom_ief_str = f"{sum(ief_vals)/len(ief_vals):.2f}" if ief_vals else "N/D"
        
        if ief_vals:
            peor_entry = max(historial, key=lambda x: x["ief"] if x["ief"] is not None else -999999)
            mejor_entry = min(historial, key=lambda x: x["ief"] if x["ief"] is not None else 999999)
            peor_str = f"#{peor_entry['id']} (IEF {peor_entry['ief']:.2f})"
            mejor_str = f"#{mejor_entry['id']} (IEF {mejor_entry['ief']:.2f})"
        else:
            peor_str = "N/D"
            mejor_str = "N/D"
            
        deuda_acum = sum(item.get("costo_deuda", 0.0) for item in historial)
        
        from rich.panel import Panel
        from rich import box
        from rich.console import Console
        from oraculus.cli.display import CyberpunkColors
        
        console = Console()
        c = CyberpunkColors
        
        stats_content = (
            f"  [bold {c.NEON_CYAN}]Promedio IEF:[/]    {prom_ief_str}\n"
            f"  [bold {c.NEON_CYAN}]{t('cli', 'peor_analisis')}[/]   {peor_str}\n"
            f"  [bold {c.NEON_CYAN}]{t('cli', 'mejor_analisis')}[/]  {mejor_str}\n"
            f"  [bold {c.NEON_CYAN}]{t('cli', 'deuda_acumulada')}[/] ${deuda_acum:.2f}"
        )
        
        stats_content = limpiar_unicode_consola(stats_content)
        console.print(Panel(
            stats_content,
            title=limpiar_unicode_consola(f"[bold {c.NEON_CYAN}]{t('cli', 'stats_title')}[/bold {c.NEON_CYAN}]"),
            box=box.ASCII,
            border_style=c.NEON_CYAN,
            width=55
        ))
        return

    if compare is not None:
        id1, id2 = compare
        historial = cargar_historial()
        
        entry1 = next((item for item in historial if item.get("id") == id1), None)
        entry2 = next((item for item in historial if item.get("id") == id2), None)
        
        if not entry1:
            click.echo(click.style(t('cli', 'error_no_report').format(id=id1), fg="red"))
            return
        if not entry2:
            click.echo(click.style(t('cli', 'error_no_report').format(id=id2), fg="red"))
            return
            
        ief1 = entry1.get("ief")
        ief2 = entry2.get("ief")
        ief1_str = f"{ief1:.2f}" if ief1 is not None else "N/D"
        ief2_str = f"{ief2:.2f}" if ief2 is not None else "N/D"
        
        riesgo1 = entry1.get("riesgo", "BAJO")
        riesgo2 = entry2.get("riesgo", "BAJO")
        
        c_real1 = entry1.get("c_real", 0.0)
        c_real2 = entry2.get("c_real", 0.0)
        
        deuda1 = entry1.get("costo_deuda", 0.0)
        deuda2 = entry2.get("costo_deuda", 0.0)
        
        from oraculus.cli.display import CyberpunkColors
        c = CyberpunkColors
        
        if ief1 is not None and ief2 is not None:
            if ief2 > ief1:
                trend_ief = f"[bold color(196)]{t('cli', 'comparar_tendencia_ief_deteriorando')}[/]"
            elif ief2 < ief1:
                trend_ief = f"[bold {c.NEON_GREEN}]{t('cli', 'comparar_tendencia_ief_mejorando')}[/]"
            else:
                trend_ief = f"[bold {c.TEXTO_P}]{t('cli', 'comparar_tendencia_ief_estable')}[/]"
        else:
            trend_ief = ""
            
        if deuda2 > deuda1:
            trend_deuda = f"[bold color(196)]{t('cli', 'comparar_tendencia_deuda_acumulando')}[/]"
        elif deuda2 < deuda1:
            trend_deuda = f"[bold {c.NEON_GREEN}]{t('cli', 'comparar_tendencia_deuda_reduciendo')}[/]"
        else:
            trend_deuda = f"[bold {c.TEXTO_P}]{t('cli', 'comparar_tendencia_deuda_estable')}[/]"
            
        if trend_ief:
            trend_msg = f"{trend_ief} | {trend_deuda}"
        else:
            trend_msg = trend_deuda
            
        from rich.table import Table
        from rich.console import Console
        from rich import box
        
        console = Console()
        table = Table(
            title=f"[bold {c.LOGO}]{t('cli', 'comparacion_title')}[/]",
            box=box.ASCII,
            border_style=c.LOGO
        )
        table.add_column(t('cli', 'metrica'), style=c.NEON_CYAN)
        table.add_column(t('cli', 'analisis_num').format(id=id1), justify="center")
        table.add_column(t('cli', 'analisis_num').format(id=id2), justify="center")
        
        def get_style_r(riesgo_val):
            if riesgo_val == "CRITICO":
                return f"bold {c.NEON_RED}"
            elif riesgo_val == "ALTO":
                return "bold color(208)"
            elif riesgo_val == "MODERADO":
                return "bold color(226)"
            return f"bold {c.NEON_GREEN}"
            
        table.add_row("IEF", ief1_str, ief2_str)
        table.add_row("Riesgo", f"[{get_style_r(riesgo1)}]{riesgo1}[/]", f"[{get_style_r(riesgo2)}]{riesgo2}[/]")
        table.add_row("Costo real", f"${c_real1:.2f}", f"${c_real2:.2f}")
        table.add_row("Deuda detectada", f"${deuda1:.2f}", f"${deuda2:.2f}")
        
        console.print(table)
        
        trend_msg_cleaned = limpiar_unicode_consola(f"  [bold {c.NEON_CYAN}]{t('cli', 'tendencia')}[/] {trend_msg}")
        console.print(trend_msg_cleaned)
        return

    historial = cargar_historial()
    if not historial:
        click.echo(t('cli', 'no_history'))
        return

    from rich.table import Table
    from rich.console import Console
    from rich.panel import Panel
    from rich import box
    from oraculus.cli.display import CyberpunkColors

    console = Console()
    c = CyberpunkColors

    table = Table(
        title=f"[bold {c.LOGO}]{t('cli', 'historial_titulo')}[/]",
        box=box.ASCII,
        border_style=c.LOGO
    )
    table.add_column("#", style=c.NEON_CYAN, justify="center")
    table.add_column(t('cli', 'col_repositorio'), style=c.TEXTO_P, width=25)
    table.add_column("IEF", justify="right")
    table.add_column(t('report', 'risk_title'), justify="center")
    table.add_column(t('cli', 'col_fecha'), justify="center", style=c.NEON_CYAN)

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
    click.echo(t('cli', 'ejecuta_history_open') + "\n")

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
                ief_msg = f" [bold color(196)]{t('cli', 'comparar_tendencia_ief_deteriorando')}[/]"
            elif last_ief < first_ief:
                ief_msg = f" [bold {c.NEON_GREEN}]{t('cli', 'comparar_tendencia_ief_mejorando')}[/]"
            else:
                ief_msg = f" [bold {c.TEXTO_P}]{t('cli', 'comparar_tendencia_ief_estable')}[/]"
        else:
            ief_msg = ""
            
        # Calcular tendencias de Deuda
        deudas = [item.get("costo_deuda", 0.0) for item in repo_entries]
        deuda_trend_str = " → ".join([f"${v:.0f}" for v in deudas])
        
        first_deuda = deudas[0]
        last_deuda = deudas[-1]
        if last_deuda > first_deuda:
            deuda_msg = f" [bold color(196)]{t('cli', 'comparar_tendencia_deuda_acumulando')}[/]"
        elif last_deuda < first_deuda:
            deuda_msg = f" [bold {c.NEON_GREEN}]{t('cli', 'comparar_tendencia_deuda_reduciendo')}[/]"
        else:
            deuda_msg = f" [bold {c.TEXTO_P}]{t('cli', 'comparar_tendencia_deuda_estable')}[/]"
            
        trend_content = (
            f"  [bold {c.NEON_CYAN}]IEF:[/]   {ief_trend_str}{ief_msg}\n"
            f"  [bold {c.NEON_CYAN}]Deuda:[/] {deuda_trend_str}{deuda_msg}"
        )
        
        trend_content = limpiar_unicode_consola(trend_content)
        trend_title = limpiar_unicode_consola(f"[bold {c.NEON_CYAN}]=== {t('cli', 'tendencia').rstrip(':')} {ultimo_repo} ===[/bold {c.NEON_CYAN}]")
        
        console.print(Panel(
            trend_content,
            title=trend_title,
            box=box.ASCII,
            border_style=c.NEON_CYAN,
            width=60
        ))

cli.add_command(analyze)
cli.add_command(history)


@click.group(name="config")
def config_group():
    """Configurar preferencias de Oraculus (idioma, etc.)."""
    pass


@config_group.command(name="lang")
@click.argument("idioma", type=click.Choice(["es", "en", "fr"], case_sensitive=False))
def config_lang(idioma: str):
    """Cambia el idioma de la interfaz. Idiomas disponibles: es, en, fr."""
    from oraculus.utils.i18n import cambiar_idioma_configurado
    try:
        cambiar_idioma_configurado(idioma)
        # Usar t() DESPUÉS de cambiar el idioma para el mensaje en el nuevo idioma
        click.echo(t('cli', 'config_success').format(lang=idioma))
    except Exception as e:
        click.echo(click.style(f"[Error] {e}", fg="red"))


cli.add_command(config_group)
