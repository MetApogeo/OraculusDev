from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Dict, Any
from oraculus.utils.i18n import t

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
        return f"[cyan]{t('cli', 'optimizacion')}[/cyan]"
    elif calidad == "FEATURE_LIMPIA":
        return f"[green]{t('cli', 'feature_limpia')}[/green]"
    elif calidad == "DEUDA_TECNICA":
        return f"[red]{t('cli', 'deuda_tecnica')}[/red]"
    else:
        return f"[dim]{t('cli', 'neutral')}[/dim]"

def mostrar_reporte(resultados: Dict[str, Any], salario: float, horas_efectivas: int, loc_por_hora: float):
    c = CyberpunkColors
    repo = resultados["repo"]
    es_local = resultados["es_local"]
    validos = resultados["commits_validos"]
    outliers = resultados["commits_outliers"]
    
    tipo_repo = t('cli', 'local') if es_local else t('cli', 'cache_local')
    analisis_repo_str = t('cli', 'analisis_repo').format(tipo_repo=tipo_repo)
    params_str = t('cli', 'salario_mes').format(salario=salario, horas=horas_efectivas, loc=loc_por_hora)
    
    console.print(Panel(
        f"[bold {c.LOGO}]{analisis_repo_str}[/bold {c.LOGO}]\n[bold {c.NEON_CYAN}]{t('cli', 'ruta_repo')}[/] {repo}\n[bold {c.TEXTO_P}]{t('cli', 'parametros')}[/] {params_str}",
        title="OraculusDev: Analitica Financiera",
        box=box.ASCII,
        border_style=c.LOGO
    ))

    if not validos and not outliers:
        console.print(f"[yellow]{t('cli', 'no_commits')}[/]")
        return

    if validos:
        table = Table(
            title=f"[bold {c.NEON_GREEN}]{t('cli', 'commits_estandar')}[/bold {c.NEON_GREEN}]",
            box=box.ASCII,
            header_style=f"bold {c.NEON_CYAN}",
            border_style=c.TEXTO_P
        )
        table.add_column(t('report', 'col_sha'), style=c.NEON_CYAN, width=8)
        table.add_column(t('report', 'col_mensaje'), width=35, style=c.TEXTO_P)
        table.add_column(t('report', 'col_loc'), justify="right")
        table.add_column(t('report', 'col_tiempo'), justify="right", style="magenta")
        table.add_column(t('report', 'col_costo'), justify="right", style=c.NEON_GREEN)
        table.add_column(t('report', 'col_calidad'), justify="center")

        for commit_item, t_val, costo, calidad in validos:
            loc_str = f"{commit_item.additions + commit_item.deletions} (+{commit_item.additions}/-{commit_item.deletions})"
            table.add_row(commit_item.sha, commit_item.mensaje, loc_str, f"{t_val:.2f}h", f"${costo:.2f}", format_calidad(calidad))
        
        console.print(table)

    if outliers:
        console.print(f"\n[bold {c.NEON_RED}]{t('cli', 'anomalias_detectadas')}[/bold {c.NEON_RED}]")
        console.print(f"[{c.TEXTO_P}][dim]{t('cli', 'outliers_desc')}[/dim][/{c.TEXTO_P}]")
        
        table_out = Table(
            box=box.ASCII,
            header_style=f"bold {c.NEON_RED}",
            border_style=c.LOGO
        )
        table_out.add_column(t('report', 'col_sha'), style=c.NEON_RED, width=8)
        table_out.add_column(t('report', 'col_mensaje'), width=35, style=c.TEXTO_P)
        table_out.add_column(t('report', 'col_loc'), justify="right")
        table_out.add_column(t('report', 'col_tiempo'), justify="right", style="magenta")
        table_out.add_column(t('report', 'col_costo'), justify="right", style=c.NEON_GREEN)
        table_out.add_column(t('report', 'col_calidad'), justify="center")

        for commit_item, t_val, costo, calidad in outliers:
            loc_str = f"{commit_item.additions + commit_item.deletions} (+{commit_item.additions}/-{commit_item.deletions})"
            table_out.add_row(commit_item.sha, commit_item.mensaje, loc_str, f"{t_val:.2f}h", f"${costo:.2f}", format_calidad(calidad))
        
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
            f"[bold {c.NEON_RED}]{t('cli', 'commits_con_deuda')}[/]     {len(commits_deuda)}\n"
            f"[bold {c.NEON_RED}]{t('cli', 'costo_actual')}[/]          ${costo_actual_deuda:.2f}\n"
            f"[bold {c.NEON_RED}]{t('cli', 'costo_futuro_est')}[/]     ${costo_futuro_deuda:.2f}  {t('cli', 'factor_3x')}"
        )
        console.print("\n", Panel(
            debt_panel_content,
            title=f"[bold {c.NEON_RED}]{t('cli', 'deuda_detectada')}[/bold {c.NEON_RED}]",
            box=box.ASCII,
            border_style=c.NEON_RED
        ))
    
    # 2. Evaluar Riesgo de Negocio
    riesgo = resultados.get("riesgo")
    if riesgo and riesgo["nivel"] != "BAJO":
        nivel = riesgo["nivel"]
        retraso = riesgo["retraso_estimado"]
        costo_mitigar = riesgo["costo_mitigar_hoy"]
        costo_ignorar = riesgo["costo_ignorar"]
        perdida_eficiencia = riesgo["perdida_eficiencia"]
        
        if nivel == "CRITICO":
            color_nivel = c.NEON_RED
        elif nivel == "ALTO":
            color_nivel = "color(208)"
        elif nivel == "MODERADO":
            color_nivel = "color(226)"
        else:
            color_nivel = c.NEON_GREEN
            
        risk_panel_content = (
            f"  [bold {c.TEXTO_P}]{t('cli', 'nivel_riesgo')}[/]      [bold {color_nivel}][{nivel}][/bold {color_nivel}]\n\n"
            f"  [bold {color_nivel}]{t('cli', 'riesgo_bloqueo')}[/bold {color_nivel}]\n"
            f"  {t('cli', 'probabilidad_retraso')} [bold {color_nivel}]+{retraso}%[/bold {color_nivel}]\n\n"
            f"  [bold {c.NEON_CYAN}]{t('cli', 'costo_oportunidad')}[/bold {c.NEON_CYAN}]\n"
            f"  {t('cli', 'mitigar_deuda_hoy')}     [bold {c.NEON_GREEN}]${costo_mitigar:.2f}[/bold {c.NEON_GREEN}]\n"
            f"  {t('cli', 'ignorar_sprint_mas')} [bold {c.NEON_RED}]${costo_ignorar:.2f}[/bold {c.NEON_RED}]\n"
            f"  {t('cli', 'perdida_neta')}          [bold {c.NEON_RED}]{perdida_eficiencia:.0f}%[/bold {c.NEON_RED}]\n\n"
            f"  [bold {c.NEON_CYAN}]{t('cli', 'recomendacion_pm')}[/bold {c.NEON_CYAN}]\n"
            f"  {t('cli', 'detener_features')}"
        )
        
        console.print("\n", Panel(
            risk_panel_content,
            title=f"[bold {color_nivel}]{t('report', 'risk_assessment')}[/bold {color_nivel}]",
            box=box.ASCII,
            border_style=color_nivel
        ))
    
    # 3. Resumen Consolidado Principal
    panel_content = (
        f"[bold {c.TEXTO_P}]{t('cli', 'desarrollo_estandar')}[/]  ${resultados['total_costo_normal']:.2f} (Tiempo: {resultados['total_tiempo_normal']:.2f}h)\n"
    )
    if resultados["commits_outliers"]:
        panel_content += (
            f"[bold {c.NEON_RED}]{t('cli', 'desarrollo_anomalo')}[/]   ${resultados['total_costo_outlier']:.2f} (Tiempo: {resultados['total_tiempo_outlier']:.2f}h)\n"
        )
    panel_content += f"[bold {c.NEON_CYAN}]{t('cli', 'total_c_real')}[/bold {c.NEON_CYAN}]       ${costo_real:.2f} (Tiempo Total: {tiempo_total:.2f}h)"
    
    border_style = c.LOGO
    
    if c_esp is not None:
        ief = costo_real / c_esp
        if ief < 0.8:
            semaforo = t('cli', 'sef_ok_fast')
            color = c.NEON_GREEN
            border_style = c.NEON_GREEN
        elif ief <= 1.2:
            semaforo = t('cli', 'sef_ok_range')
            color = c.NEON_GREEN
            border_style = c.TEXTO_P
        else:
            semaforo = t('cli', 'sef_exceeded')
            color = c.NEON_RED
            border_style = c.NEON_RED
            
        panel_content += f"\n[bold {c.NEON_CYAN}]{t('cli', 'presupuesto_c_esp')}[/]  ${c_esp:.2f}"
        panel_content += f"\n---------------------------------------------\n[bold {color}]IEF: {ief:.2f}  {semaforo}[/]"
 
    console.print("\n", Panel(
        panel_content,
        title=f"[bold {c.NEON_CYAN}]{t('cli', 'resumen_consolidado')}[/bold {c.NEON_CYAN}]",
        box=box.ASCII,
        border_style=border_style
    ))
