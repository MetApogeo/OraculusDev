# data_helpers.py
# Utilidades de datos compartidas (v0.1)

def formatear_loc(additions: int, deletions: int) -> str:
    return f"+{additions}/-{deletions}"

ARCHIVOS_IGNORADOS = {
    "package-lock.json",
    "composer.lock",
    "yarn.lock",
    "Pipfile.lock",
    "poetry.lock",
}

CARPETAS_IGNORADAS = {
    "vendor/",
    "node_modules/",
    "dist/",
    "build/",
    ".oraculus_cache/",
}

def es_archivo_ignorado(filepath: str) -> bool:
    # Normalizar separadores de ruta
    filepath = filepath.replace("\\", "/")
    
    # Manejar renombrados en git log ("a => b")
    if " => " in filepath:
        filepath = filepath.split(" => ")[-1]
        filepath = filepath.replace("}", "").strip()

    nombre = filepath.split("/")[-1]
    
    if nombre in ARCHIVOS_IGNORADOS:
        return True
        
    if nombre.endswith(".min.js") or nombre.endswith(".min.css"):
        return True
        
    for carpeta in CARPETAS_IGNORADAS:
        if filepath.startswith(carpeta) or f"/{carpeta}" in filepath:
            return True
            
    return False

def detectar_lenguaje(archivos: list) -> str:
    # Obtener extensiones de los archivos modificados
    extensiones = [f.split(".")[-1] for f in archivos if "." in f]
    if "py" in extensiones:
        return "python"
    # PHP, JS próximamente
    return "python"  # fallback seguro por ahora

def commits_a_dataframe(commits_validos: list, commits_outliers: list) -> "pd.DataFrame":
    import pandas as pd
    data = []
    for c_item, t, costo, calidad in commits_validos:
        data.append({
            "sha": c_item.sha,
            "mensaje": c_item.mensaje,
            "loc": c_item.additions + c_item.deletions,
            "tiempo": t,
            "costo": costo,
            "calidad": calidad,
            "tipo": "Estandar"
        })
    for c_item, t, costo, calidad in commits_outliers:
        data.append({
            "sha": c_item.sha,
            "mensaje": c_item.mensaje,
            "loc": c_item.additions + c_item.deletions,
            "tiempo": t,
            "costo": costo,
            "calidad": calidad,
            "tipo": "Outlier"
        })
    return pd.DataFrame(data)

def resumen_a_series(resultados: dict) -> "pd.Series":
    import pandas as pd
    return pd.Series({
        "costo_real": resultados.get("costo_real", 0.0),
        "tiempo_total": resultados.get("tiempo_total", 0.0),
        "total_costo_normal": resultados.get("total_costo_normal", 0.0),
        "total_tiempo_normal": resultados.get("total_tiempo_normal", 0.0),
        "total_costo_outlier": resultados.get("total_costo_outlier", 0.0),
        "total_tiempo_outlier": resultados.get("total_tiempo_outlier", 0.0),
    })
