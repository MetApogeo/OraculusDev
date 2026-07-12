from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Dict, Any

console = Console()

class CyberpunkColors:
    LOGO = "color(129)"       # Morado Eléctrico / Violeta Intenso
    TEXTO_P = "color(141)"    # Lavanda / Violeta Claro (para textos secundarios)
    NEON_CYAN = "color(51)"   # Cian Neón (para headers, variables y SHAs)
    NEON_GREEN = "color(82)"  # Verde Neón (para rangos [OK], éxitos y ganancias)
    NEON_RED = "color(196)"   # Rojo Neón (para alertas de presupuesto excedido o [CRITICAL])

def mostrar_banner():
    MORADO = '\033[38;5;129m'
    ROSA_NEON = '\033[38;5;201m'
    CIAN_NEON = '\033[38;5;51m'
    LAVANDA = '\033[38;5;141m'
    RESET = '\033[0m'

    banner = fr"""
{MORADO}                  .++++++++++++                                                                                                                                        
{MORADO}              ++++++++++++++++++++=                                                                                                                                   
{MORADO}           +++++     +    =+++    +++++                                                                                                                                
{MORADO}         ++++      +         +++     ++++                                                                                                                              
{MORADO}       +*++       -            ++.     ++++                                                                                                                            
{MORADO}      *++          +++++++++:   +++      +++                                                                                                                           
{MORADO}     **+      ++++++++=    -++++ -++      +++              {CIAN_NEON}%@@@@@      @@@@@@@@         @@@@         @@@@@@     @@@     @@@   @@@         -@@+     @@@     @@@@@@      
{ROSA_NEON}    +++    =+++ ++=            :++:++      +++           {CIAN_NEON}@@@@@@@@@@-   @@@@@@@@@@+     @@@@@@      @@@@@@@@@@   @@@     @@@   @@@         -@@+     @@@   @@@@+%@@@@    
{ROSA_NEON}   *++   +++. =+=   ++++++++++   -+++. +    +++          {CIAN_NEON}@@@     @@@   @@@     @@@    #@@  @@+    @@@     @@@   @@@     @@@   @@@         -@@+     @@@  @@@     %@@    
{ROSA_NEON}  :**  +++   *+   +++        +++   +++   +.  ++         {CIAN_NEON}-@@.     @@@   @@@     @@@    @@@  @@@    @@@           @@@     @@@   @@@         -@@+     @@@   @@@@%         
{ROSA_NEON}  *** *+=   ++.  **-          =++  :++     + +++        {CIAN_NEON}-@@.     @@@   @@@@@@@@@@    *@@    @@#   @@@           @@@     @@@   @@@         -@@+     @@@     @@@@@@@+    
{ROSA_NEON}  *****     **  +*+            +++  ++      ++++        {CIAN_NEON}-@@.     @@@   @@@   @@@     @@@@@@@@@@   @@@     :**   @@@     @@@   @@@         -@@=     @@@          @@@-   
{ROSA_NEON}  ****      **  +++            +++  ++     :++++         {CIAN_NEON}@@@     @@@   @@@   -@@@   %@@@@@@@@@@#  @@@     @@@   @@@     @@@   @@@          @@@     @@@  @@@     =@@+ 
{MORADO}  ****      *+  +**            ++-  ++    ++++++          {CIAN_NEON}@@@@@@@@@    @@@    @@@#  @@@      @@@   @@@@@@@@@     @@@@@@@@@    @@@@@@@@@@   +@@@@@@@@@    @@@@@@@@@@    
{MORADO}  **+ ++    +++  +++          +++  ++   .++. ++=             {LAVANDA}#%*                                      +%#           #%*                       .%%+          =%%-       
{MORADO}   *+   +=  ++++  =+++-    -+++-  ++   +++  =++                                                                                                                        
{MORADO}   ***     + ++++    ++++++++    ++ ++++    ++=                                                                                                                        
{MORADO}    ***      .++ ++=          =++++++      +++                         
{MORADO}     ***      :++  +++++++++++++++        +++                        
{MORADO}      ***-      ++=     -++:    =       +++=                        
{MORADO}        *++.     +++           +      -+++                                                                                                                             
{MORADO}         -++++     +++       +      ++++                                                                                                                               
{MORADO}            +++++:   ++++  +=   =+++++                                                                                                                                 
{MORADO}               +++++++++++++++++++=                                                                                                                                    
{MORADO}                    .=++++++=                                                                                                                                          

{RESET}"""
    print(banner)

def format_calidad(calidad: str) -> str:
    if calidad == "OPTIMIZACION":
        return "[cyan]Optimizacion[/cyan]"
    elif calidad == "FEATURE_LIMPIA":
        return "[green]Feature Limpia[/green]"
    elif calidad == "DEUDA_TECNICA":
        return "[red]Deuda Tecnica[/red]"
    else:
        return "[dim]Neutral[/dim]"

def mostrar_reporte(resultados: Dict[str, Any], salario: float, horas_efectivas: int, loc_por_hora: float):
    c = CyberpunkColors
    repo = resultados["repo"]
    es_local = resultados["es_local"]
    validos = resultados["commits_validos"]
    outliers = resultados["commits_outliers"]
    
    tipo_repo = "Local" if es_local else "Cache Local (Clonado)"
    
    console.print(Panel(
        f"[bold {c.LOGO}]Analisis de Repositorio ({tipo_repo})[/bold {c.LOGO}]\n[bold {c.NEON_CYAN}]Ruta/Repo:[/] {repo}\n[bold {c.TEXTO_P}]Parametros:[/] Salario: ${salario:.2f} | Horas/Mes: {horas_efectivas}h | LOC/Hora: {loc_por_hora}",
        title=f"[bold {c.NEON_CYAN}]OraculusDev: Analitica Financiera[/bold {c.NEON_CYAN}]",
        box=box.ASCII,
        border_style=c.LOGO
    ))

    if not validos and not outliers:
        console.print(f"[yellow]No se encontraron commits para analizar.[/]")
        return

    if validos:
        table = Table(
            title=f"[bold {c.NEON_GREEN}]=== COMMITS ESTANDAR ===[/bold {c.NEON_GREEN}]",
            box=box.ASCII,
            header_style=f"bold {c.NEON_CYAN}",
            border_style=c.TEXTO_P
        )
        table.add_column("SHA", style=c.NEON_CYAN, width=8)
        table.add_column("Mensaje", width=35, style=c.TEXTO_P)
        table.add_column("LOC (+/-)", justify="right")
        table.add_column("Tiempo Est.", justify="right", style="magenta")
        table.add_column("Costo Est.", justify="right", style=c.NEON_GREEN)
        table.add_column("Calidad", justify="center")

        for commit_item, t, costo, calidad in validos:
            loc_str = f"{commit_item.additions + commit_item.deletions} (+{commit_item.additions}/-{commit_item.deletions})"
            table.add_row(commit_item.sha, commit_item.mensaje, loc_str, f"{t:.2f}h", f"${costo:.2f}", format_calidad(calidad))
        
        console.print(table)

    if outliers:
        console.print(f"\n[bold {c.NEON_RED}]=== ANOMALIAS DETECTADAS (Outliers) ===[/bold {c.NEON_RED}]")
        console.print(f"[{c.TEXTO_P}][dim]Commits de gran volumen que podrian sesgar las estimaciones normales.[/][/{c.TEXTO_P}]")
        
        table_out = Table(
            box=box.ASCII,
            header_style=f"bold {c.NEON_RED}",
            border_style=c.LOGO
        )
        table_out.add_column("SHA", style=c.NEON_RED, width=8)
        table_out.add_column("Mensaje", width=35, style=c.TEXTO_P)
        table_out.add_column("LOC (+/-)", justify="right")
        table_out.add_column("Tiempo Est.", justify="right", style="magenta")
        table_out.add_column("Costo Est.", justify="right", style=c.NEON_GREEN)
        table_out.add_column("Calidad", justify="center")

        for commit_item, t, costo, calidad in outliers:
            loc_str = f"{commit_item.additions + commit_item.deletions} (+{commit_item.additions}/-{commit_item.deletions})"
            table_out.add_row(commit_item.sha, commit_item.mensaje, loc_str, f"{t:.2f}h", f"${costo:.2f}", format_calidad(calidad))
        
        console.print(table_out)

def mostrar_resumen_financiero(resultados: Dict[str, Any], c_esp: float = None):
    c = CyberpunkColors
    costo_real = resultados["costo_real"]
    tiempo_total = resultados["tiempo_total"]
    
    # 1. Analizar Deuda Técnica Detectada
    commits_deuda = []
    for item in resultados["commits_validos"]:
        if item[3] == "DEUDA_TECNICA":
            commits_deuda.append(item)
    for item in resultados["commits_outliers"]:
        if item[3] == "DEUDA_TECNICA":
            commits_deuda.append(item)
            
    if commits_deuda:
        from oraculus.core.metrics import estimar_costo_deuda
        costo_actual_deuda = sum(item[2] for item in commits_deuda)
        costo_futuro_deuda = estimar_costo_deuda(commits_deuda)
        
        debt_panel_content = (
            f"[bold {c.NEON_RED}]Commits con deuda:[/]     {len(commits_deuda)}\n"
            f"[bold {c.NEON_RED}]Costo actual:[/]          ${costo_actual_deuda:.2f}\n"
            f"[bold {c.NEON_RED}]Costo futuro est.:[/]     ${costo_futuro_deuda:.2f}  (factor 3x)"
        )
        console.print("\n", Panel(
            debt_panel_content,
            title=f"[bold {c.NEON_RED}]=== DEUDA TECNICA DETECTADA ===[/bold {c.NEON_RED}]",
            box=box.ASCII,
            border_style=c.NEON_RED
        ))
    
    # 2. Resumen Consolidado Principal
    panel_content = (
        f"[bold {c.TEXTO_P}]Desarrollo Estandar:[/]  ${resultados['total_costo_normal']:.2f} (Tiempo: {resultados['total_tiempo_normal']:.2f}h)\n"
    )
    if resultados["commits_outliers"]:
        panel_content += (
            f"[bold {c.NEON_RED}]Desarrollo Anomalo:[/]   ${resultados['total_costo_outlier']:.2f} (Tiempo: {resultados['total_tiempo_outlier']:.2f}h)\n"
        )
    panel_content += f"[bold {c.NEON_CYAN}]Total (C_real):[/bold {c.NEON_CYAN}]       ${costo_real:.2f} (Tiempo Total: {tiempo_total:.2f}h)"
    
    border_style = c.LOGO
    
    if c_esp is not None:
        ief = costo_real / c_esp
        if ief < 0.8:
            semaforo = "[OK] Termino mas rapido de lo esperado"
            color = c.NEON_GREEN
            border_style = c.NEON_GREEN
        elif ief <= 1.2:
            semaforo = "[OK] Rango aceptable (Dentro de lo esperado)"
            color = c.NEON_GREEN
            border_style = c.TEXTO_P
        else:
            semaforo = "[ALERTA] Presupuesto excedido"
            color = c.NEON_RED
            border_style = c.NEON_RED
            
        panel_content += f"\n[bold {c.NEON_CYAN}]Presupuesto (C_esp):[/]  ${c_esp:.2f}"
        panel_content += f"\n---------------------------------------------\n[bold {color}]IEF: {ief:.2f}  {semaforo}[/]"

    console.print("\n", Panel(
        panel_content,
        title=f"[bold {c.NEON_CYAN}]Resumen Consolidado[/bold {c.NEON_CYAN}]",
        box=box.ASCII,
        border_style=border_style
    ))
