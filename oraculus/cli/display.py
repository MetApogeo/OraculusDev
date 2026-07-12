from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Dict, Any

console = Console()

def mostrar_reporte(resultados: Dict[str, Any], salario: float, horas_efectivas: int, loc_por_hora: float):
    repo = resultados["repo"]
    es_local = resultados["es_local"]
    validos = resultados["commits_validos"]
    outliers = resultados["commits_outliers"]
    
    tipo_repo = "Local" if es_local else "Cache Local (Clonado)"
    
    console.print(Panel(
        f"[bold blue]Analisis de Repositorio ({tipo_repo})[/]\n[bold green]Ruta/Repo:[/] {repo}\n[bold]Parametros:[/] Salario: ${salario:.2f} | Horas/Mes: {horas_efectivas}h | LOC/Hora: {loc_por_hora}",
        title="[bold]OraculusDev: Analitica Financiera[/]",
        box=box.ASCII,
        border_style="blue"
    ))

    if not validos and not outliers:
        console.print("[yellow]No se encontraron commits para analizar.[/]")
        return

    if validos:
        table = Table(title="[bold green]=== COMMITS ESTANDAR ===[/]", box=box.ASCII, header_style="bold green")
        table.add_column("SHA", style="cyan", width=8)
        table.add_column("Mensaje", width=40)
        table.add_column("LOC (+/-)", justify="right")
        table.add_column("Tiempo Est.", justify="right", style="magenta")
        table.add_column("Costo Est.", justify="right", style="green")

        for c, t, costo in validos:
            loc_str = f"{c.additions + c.deletions} (+{c.additions}/-{c.deletions})"
            table.add_row(c.sha, c.mensaje, loc_str, f"{t:.2f}h", f"${costo:.2f}")
        
        console.print(table)

    if outliers:
        console.print("\n[bold red]=== ANOMALIAS DETECTADAS (Outliers) ===[/]")
        console.print("[dim]Commits de gran volumen que podrian sesgar las estimaciones normales.[/]")
        table_out = Table(box=box.ASCII, header_style="bold red")
        table_out.add_column("SHA", style="red", width=8)
        table_out.add_column("Mensaje", width=40)
        table_out.add_column("LOC (+/-)", justify="right")
        table_out.add_column("Tiempo Est.", justify="right", style="magenta")
        table_out.add_column("Costo Est.", justify="right", style="green")

        for c, t, costo in outliers:
            loc_str = f"{c.additions + c.deletions} (+{c.additions}/-{c.deletions})"
            table_out.add_row(c.sha, c.mensaje, loc_str, f"{t:.2f}h", f"${costo:.2f}")
        
        console.print(table_out)

def mostrar_resumen_financiero(resultados: Dict[str, Any], c_esp: float = None):
    costo_real = resultados["costo_real"]
    tiempo_total = resultados["tiempo_total"]
    
    panel_content = (
        f"[bold]Desarrollo Estandar:[/]  ${resultados['total_costo_normal']:.2f} (Tiempo: {resultados['total_tiempo_normal']:.2f}h)\n"
    )
    if resultados["commits_outliers"]:
        panel_content += (
            f"[bold]Desarrollo Anomalo:[/]   ${resultados['total_costo_outlier']:.2f} (Tiempo: {resultados['total_tiempo_outlier']:.2f}h)\n"
        )
    panel_content += f"[bold]Total (C_real):[/]       ${costo_real:.2f} (Tiempo Total: {tiempo_total:.2f}h)"
    
    if c_esp is not None:
        ief = costo_real / c_esp
        if ief < 0.8:
            semaforo = "[OK] Termino mas rapido de lo esperado"
            color = "green"
        elif ief <= 1.2:
            semaforo = "[OK] Rango aceptable (Dentro de lo esperado)"
            color = "yellow"
        else:
            semaforo = "[ALERTA] Presupuesto excedido"
            color = "red"
            
        panel_content += f"\n[bold]Presupuesto (C_esp):[/]  ${c_esp:.2f}"
        panel_content += f"\n---------------------------------------------\n[bold {color}]IEF: {ief:.2f}  {semaforo}[/]"

    console.print("\n", Panel(
        panel_content,
        title="[bold]Resumen Consolidado[/]",
        box=box.ASCII,
        border_style="green" if c_esp is None or IEF_color_helper(costo_real, c_esp) == "green" else "yellow" if IEF_color_helper(costo_real, c_esp) == "yellow" else "red"
    ))

def IEF_color_helper(c_real: float, c_esp: float) -> str:
    ief = c_real / c_esp
    if ief < 0.8:
        return "green"
    elif ief <= 1.2:
        return "yellow"
    return "red"
