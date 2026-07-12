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
