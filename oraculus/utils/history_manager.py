import json
import os
import webbrowser
from datetime import datetime

def cargar_historial() -> list:
    reports_dir = os.path.join(os.getcwd(), "oraculus_reports")
    index_path = os.path.join(reports_dir, "index.json")
    if not os.path.exists(index_path):
        return []
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def registrar_reporte(repo: str, ief, riesgo: str, c_real: float, c_esp, archivo: str, costo_deuda: float) -> None:
    reports_dir = os.path.join(os.getcwd(), "oraculus_reports")
    os.makedirs(reports_dir, exist_ok=True)
    index_path = os.path.join(reports_dir, "index.json")
    
    historial = cargar_historial()
    
    nuevo_id = 1
    if historial:
        nuevo_id = max(item.get("id", 0) for item in historial) + 1
        
    now = datetime.now()
    nueva_entrada = {
        "id": nuevo_id,
        "repo": repo,
        "ief": round(ief, 2) if ief is not None else None,
        "riesgo": riesgo,
        "c_real": round(c_real, 2),
        "c_esp": round(c_esp, 2) if c_esp is not None else None,
        "costo_deuda": round(costo_deuda, 2),
        "fecha": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M"),
        "archivo": archivo
    }
    
    historial.append(nueva_entrada)
    
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def abrir_reporte(numero: int) -> None:
    historial = cargar_historial()
    for item in historial:
        if item.get("id") == numero:
            archivo = item.get("archivo")
            if archivo:
                reports_dir = os.path.join(os.getcwd(), "oraculus_reports")
                filepath = os.path.abspath(os.path.join(reports_dir, archivo))
                if os.path.exists(filepath):
                    import click
                    click.echo(f"[Info] Abriendo reporte en el navegador: {filepath}")
                    webbrowser.open(filepath)
                    return
                else:
                    raise FileNotFoundError(f"El archivo de reporte '{archivo}' no existe en {reports_dir}.")
    raise ValueError(f"No se encontró ningún reporte con ID #{numero}.")

def eliminar_reporte_fisico(archivo: str) -> None:
    if not archivo:
        return
    reports_dir = os.path.join(os.getcwd(), "oraculus_reports")
    filepath = os.path.abspath(os.path.join(reports_dir, archivo))
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

def limpiar_historial_por_completo() -> None:
    historial = cargar_historial()
    for item in historial:
        eliminar_reporte_fisico(item.get("archivo"))
    reports_dir = os.path.join(os.getcwd(), "oraculus_reports")
    index_path = os.path.join(reports_dir, "index.json")
    if os.path.exists(index_path):
        try:
            os.remove(index_path)
        except Exception:
            pass

def conservar_ultimos_n_reportes(n: int) -> None:
    historial = cargar_historial()
    if len(historial) <= n:
        return
    
    # Reportes a eliminar
    a_eliminar = historial[:-n]
    a_conservar = historial[-n:]
    
    for item in a_eliminar:
        eliminar_reporte_fisico(item.get("archivo"))
        
    reports_dir = os.path.join(os.getcwd(), "oraculus_reports")
    index_path = os.path.join(reports_dir, "index.json")
    
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(a_conservar, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
