import os
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def cargar_logo_svg() -> str:
    # Ruta relativa al directorio docs/src/oraculus svg.svg
    ruta = Path(__file__).parent.parent.parent / "docs" / "src" / "oraculus svg.svg"
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        try:
            ruta_cwd = Path.cwd() / "docs" / "src" / "oraculus svg.svg"
            with open(ruta_cwd, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""

def obtener_nombre_repositorio_git(repo: str) -> str:
    import subprocess
    import os
    
    if os.path.isdir(repo) or repo in (".", "./", ".\\"):
        # Intentamos obtener la URL remota de git
        try:
            cmd = ["git", "-c", "safe.directory=*", "config", "--get", "remote.origin.url"]
            res = subprocess.run(cmd, cwd=os.path.abspath(repo), capture_output=True, text=True, check=True)
            url = res.stdout.strip()
            if url:
                # Limpiar la URL para obtener usuario/repo
                if url.endswith(".git"):
                    url = url[:-4]
                if "github.com/" in url:
                    url = url.split("github.com/")[-1]
                elif "github.com:" in url:
                    url = url.split("github.com:")[-1]
                return url
        except Exception:
            pass
        # Fallback si no hay git remote: usar el nombre del directorio
        return os.path.basename(os.path.abspath(repo))
    return repo

def generar_grafica_costos(df) -> str:
    import plotly.express as px
    import plotly.io as pio
    if df.empty:
        return "<p style='color: #8A8A8A; text-align: center; padding: 50px 0;'>Sin datos de commits para graficar.</p>"
    
    # Invertimos el orden para que los commits más nuevos aparezcan arriba en la barra horizontal
    df_sorted = df.iloc[::-1].copy()
    
    # Mapear colores cyberpunk
    color_map = {
        "OPTIMIZACION": "#00E6FF",
        "FEATURE_LIMPIA": "#00FF66",
        "DEUDA_TECNICA": "#FF1493",
        "NEUTRAL": "#8A8A8A"
    }
    
    # Crear gráfica
    fig = px.bar(
        df_sorted,
        x="costo",
        y="sha",
        color="calidad",
        orientation="h",
        hover_data=["mensaje", "loc", "tiempo"],
        color_discrete_map=color_map,
        title="Costo de Desarrollo por Commit (USD)",
        labels={"costo": "Costo (USD)", "sha": "Commit SHA", "calidad": "Calidad"}
    )
    
    # Ajustar estilos Cyberpunk
    fig.update_layout(
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#1A1A1A",
        font_color="#FFFFFF",
        title_font_size=16,
        xaxis=dict(showgrid=True, gridcolor="#333333"),
        yaxis=dict(showgrid=False, type='category'),
        margin=dict(l=80, r=20, t=50, b=50),
        height=380
    )
    
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

def generar_grafica_calidad(df) -> str:
    import plotly.express as px
    import plotly.io as pio
    if df.empty:
        return "<p style='color: #8A8A8A; text-align: center; padding: 50px 0;'>Sin datos de calidad para graficar.</p>"
    
    counts = df["calidad"].value_counts().reset_index()
    counts.columns = ["calidad", "cantidad"]
    
    color_map = {
        "OPTIMIZACION": "#00E6FF",
        "FEATURE_LIMPIA": "#00FF66",
        "DEUDA_TECNICA": "#FF1493",
        "NEUTRAL": "#8A8A8A"
    }
    
    fig = px.pie(
        counts,
        values="cantidad",
        names="calidad",
        color="calidad",
        color_discrete_map=color_map,
        title="Distribución de Calidad del Código"
    )
    
    fig.update_layout(
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#1A1A1A",
        font_color="#FFFFFF",
        title_font_size=16,
        margin=dict(l=40, r=40, t=50, b=40),
        height=380
    )
    
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def generar_reporte_html(resultados: dict, repo: str, c_esp: float = None) -> str:
    from oraculus.utils.data_helpers import commits_a_dataframe, resumen_a_series
    
    # 1. Obtener DataFrames y Series
    df = commits_a_dataframe(resultados.get("commits_validos", []), resultados.get("commits_outliers", []))
    resumen = resumen_a_series(resultados)
    
    # 2. Obtener Logo SVG y Nombre del repositorio
    logo_svg = cargar_logo_svg()
    logo_html = ""
    if logo_svg:
        logo_html = '<div class="logo-svg-container">' + logo_svg + '</div>'
    
    repo_name = obtener_nombre_repositorio_git(repo)
    
    # 3. Gráficos Plotly
    grafica_costos = generar_grafica_costos(df)
    grafica_calidad = generar_grafica_calidad(df)
    
    # 4. Formatear IEF
    ief_card_html = ""
    if c_esp is not None and c_esp > 0:
        costo_real = resultados.get("costo_real", 0.0)
        ief = costo_real / c_esp
        if ief < 0.8:
            color_ief = "#00FF66"
            status_ief = "Terminó más rápido de lo esperado"
        elif ief <= 1.2:
            color_ief = "#00E6FF"
            status_ief = "Rango aceptable"
        else:
            color_ief = "#FF1493"
            status_ief = "Presupuesto excedido"
            
        ief_card_html = f"""
        <div class="card accent" style="border-color: {color_ief}; box-shadow: 0 0 8px {color_ief}4D;">
            <h3>Índice IEF</h3>
            <div class="value" style="color: {color_ief};">{ief:.2f}</div>
            <div class="subtitle">{status_ief}</div>
        </div>
        """
        
    # 5. Formatear Tarjeta de Riesgo de Negocio
    riesgo = resultados.get("riesgo")
    riesgo_card_html = ""
    riesgo_panel_html = ""
    if riesgo and riesgo["nivel"] != "BAJO":
        nivel = riesgo["nivel"]
        retraso = riesgo["retraso_estimado"]
        costo_mitigar = riesgo["costo_mitigar_hoy"]
        costo_ignorar = riesgo["costo_ignorar"]
        perdida_eficiencia = riesgo["perdida_eficiencia"]
        
        if nivel == "CRITICO":
            class_riesgo = "critico"
            color_riesgo = "#FF1493"
        elif nivel == "ALTO":
            class_riesgo = "alto"
            color_riesgo = "#FFA500"
        elif nivel == "MODERADO":
            class_riesgo = "moderado"
            color_riesgo = "#FFFF00"
        else:
            class_riesgo = "bajo"
            color_riesgo = "#00FF66"
            
        riesgo_card_html = f"""
        <div class="card accent" style="border-color: {color_riesgo}; box-shadow: 0 0 8px {color_riesgo}4D;">
            <h3>Riesgo de Negocio</h3>
            <div class="value" style="color: {color_riesgo};">{nivel}</div>
            <div class="subtitle">Retraso est.: +{retraso}%</div>
        </div>
        """
        
        riesgo_panel_html = f"""
        <div class="panel" style="border-color: {color_riesgo}; box-shadow: 0 0 10px {color_riesgo}22;">
            <h2>EVALUACIÓN DE RIESGO DE NEGOCIO</h2>
            <div class="badge-risk {class_riesgo}">RIESGO {nivel}</div>
            <p><strong>[! RIESGO DE BLOQUEO]</strong> Probabilidad de retraso en próximos entregables: <strong>+{retraso}%</strong></p>
            <h3>COSTO DE OPORTUNIDAD</h3>
            <p>Mitigar deuda hoy: <strong class="highlight-green">${costo_mitigar:.2f}</strong></p>
            <p>Ignorar un sprint más: <strong class="highlight-red">${costo_ignorar:.2f}</strong></p>
            <p>Pérdida neta de eficiencia: <strong class="highlight-red">{perdida_eficiencia:.0f}%</strong></p>
            <h3>RECOMENDACIÓN PARA EL PM:</h3>
            <p style="color: {color_riesgo}; font-weight: bold;">Detener nuevas features y priorizar refactorización antes del siguiente sprint.</p>
        </div>
        """
        
    # 6. Tabla de Commits
    tabla_rows = ""
    for _, row in df.iterrows():
        calidad_badge = f'<span class="badge {row["calidad"].lower().replace("_", "-")}">{row["calidad"].replace("_", " ")}</span>'
        tabla_rows += f"""
        <tr>
            <td><code>{row["sha"]}</code></td>
            <td>{row["mensaje"]}</td>
            <td>{row["loc"]}</td>
            <td>{row["tiempo"]:.2f}h</td>
            <td>${row["costo"]:.2f}</td>
            <td>{calidad_badge}</td>
        </tr>
        """
        
    # 7. Tarjeta Deuda Técnica (factor 3x)
    deuda_panel_html = ""
    commits_deuda_df = df[df["calidad"] == "DEUDA_TECNICA"]
    if not commits_deuda_df.empty:
        costo_actual_deuda = commits_deuda_df["costo"].sum()
        costo_futuro_deuda = costo_actual_deuda * 3.0
        deuda_panel_html = f"""
        <div class="panel" style="border-color: #FF1493;">
            <h2>DEUDA TÉCNICA DETECTADA</h2>
            <p>Se identificaron <strong>{len(commits_deuda_df)}</strong> commits que incrementan la complejidad ciclomática del código.</p>
            <p>Costo de desarrollo actual: <strong class="highlight-cyan">${costo_actual_deuda:.2f}</strong></p>
            <p>Costo futuro estimado de mantenimiento: <strong class="highlight-red">${costo_futuro_deuda:.2f}</strong> (factor multiplicador 3x)</p>
        </div>
        """

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte Financiero de Código - Oraculus</title>
    <style>
        body {{
            background-color: #121212;
            color: #FFFFFF;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #AA00FF;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header-logo-title {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .logo-svg-container {{
            width: 50px;
            height: 50px;
        }}
        .logo-svg-container svg {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        header h1 {{
            margin: 0;
            color: #00E6FF;
            font-size: 28px;
            text-shadow: 0 0 10px rgba(0, 230, 255, 0.5);
        }}
        header .metadata {{
            text-align: right;
            color: #8A8A8A;
        }}
        .grid-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background-color: #1A1A1A;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .card.accent {{
            border-color: #AA00FF;
            box-shadow: 0 0 8px rgba(170, 0, 255, 0.3);
        }}
        .card h3 {{
            margin: 0 0 10px 0;
            font-size: 12px;
            color: #8A8A8A;
            text-transform: uppercase;
        }}
        .card .value {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .card .subtitle {{
            font-size: 12px;
            color: #8A8A8A;
        }}
        .grid-charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        @media (max-width: 900px) {{
            .grid-charts {{
                grid-template-columns: 1fr;
            }}
        }}
        .chart-box {{
            background-color: #1A1A1A;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        }}
        .panel {{
            background-color: #1A1A1A;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .panel h2 {{
            margin-top: 0;
            color: #00E6FF;
            font-size: 18px;
            border-bottom: 1px solid #333333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .panel h3 {{
            color: #FFFFFF;
            font-size: 15px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #222222;
        }}
        th {{
            background-color: #151515;
            color: #00E6FF;
        }}
        tr:hover {{
            background-color: #222222;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            white-space: nowrap;
        }}
        .badge.neutral {{ background-color: #333333; color: #CCCCCC; }}
        .badge.optimizacion {{ background-color: #004D61; color: #00E6FF; border: 1px solid #00E6FF; }}
        .badge.feature-limpia {{ background-color: #004D1B; color: #00FF66; border: 1px solid #00FF66; }}
        .badge.deuda-tecnica {{ background-color: #4D0025; color: #FF1493; border: 1px solid #FF1493; }}
        
        .badge-risk {{
            font-size: 16px;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 6px;
            display: inline-block;
            margin-bottom: 15px;
        }}
        .badge-risk.critico {{ background-color: #4D0000; color: #FF1493; border: 2px solid #FF1493; }}
        .badge-risk.alto {{ background-color: #4D2600; color: #FFA500; border: 2px solid #FFA500; }}
        .badge-risk.moderado {{ background-color: #4D4D00; color: #FFFF00; border: 2px solid #FFFF00; }}
        .badge-risk.bajo {{ background-color: #004D1B; color: #00FF66; border: 2px solid #00FF66; }}

        .highlight-red {{ color: #FF1493; }}
        .highlight-green {{ color: #00FF66; }}
        .highlight-cyan {{ color: #00E6FF; }}
        
        footer {{
            text-align: center;
            color: #555555;
            font-size: 12px;
            margin-top: 50px;
            border-top: 1px solid #222222;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-logo-title">
                {logo_html}
                <h1>ORACULUS</h1>
            </div>
            <div class="metadata">
                <div>Repositorio: <strong>{repo_name}</strong></div>
                <div>Generado: <strong>{fecha_reporte}</strong></div>
            </div>
        </header>

        <section class="grid-cards">
            <div class="card">
                <h3>Costo Real (C_real)</h3>
                <div class="value" style="color: #00E6FF;">${resumen["costo_real"]:.2f}</div>
                <div class="subtitle">Esfuerzo invertido</div>
            </div>
            <div class="card">
                <h3>Presupuesto</h3>
                <div class="value" style="color: #FFFFFF;">{"N/D" if c_esp is None else f"${c_esp:.2f}"}</div>
                <div class="subtitle">Presupuesto asignado</div>
            </div>
            {ief_card_html}
            {riesgo_card_html}
        </section>

        <section class="grid-charts">
            <div class="chart-box">
                {grafica_costos}
            </div>
            <div class="chart-box">
                {grafica_calidad}
            </div>
        </section>

        {riesgo_panel_html}
        {deuda_panel_html}

        <section class="panel">
            <h2>HISTORIAL DE COMMITS ANALIZADOS</h2>
            <table>
                <thead>
                    <tr>
                        <th>SHA</th>
                        <th>Mensaje</th>
                        <th>LOC</th>
                        <th>Tiempo Est.</th>
                        <th>Costo Est.</th>
                        <th>Calidad</th>
                    </tr>
                </thead>
                <tbody>
                    {tabla_rows}
                </tbody>
            </table>
        </section>

        <footer>
            Oraculus Financial Telemetry System &copy; {datetime.now().year} - MetApogeo
        </footer>
    </div>
</body>
</html>
"""
    return html

def guardar_reporte(html: str, repo: str) -> str:
    import os
    
    # Si el repo es un directorio local, resolvemos su nombre de carpeta absoluto
    if os.path.isdir(repo) or repo in (".", "./", ".\\"):
        repo_name = os.path.basename(os.path.abspath(repo))
    else:
        # Si es remoto (ej: MetApogeo/OraculusDev), limpiamos barras
        repo_name = repo.replace("/", "_").replace("\\", "_").replace(":", "_")
        
    reports_dir = os.path.join(os.getcwd(), "oraculus_reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    fecha = datetime.now().strftime("%Y-%m-%d")
    filename = f"{repo_name}_{fecha}.html"
    filepath = os.path.abspath(os.path.join(reports_dir, filename))
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
        
    return filepath
