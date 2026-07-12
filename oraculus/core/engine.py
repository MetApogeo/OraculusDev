from typing import Dict, Any, List
from oraculus.connectors.github_client import es_local, obtener_commits_local, obtener_commits_api, clonar_y_obtener_commits
from oraculus.core.metrics import CommitData, filtrar_outliers, realizar_calculos
from oraculus.utils.config import obtener_github_token

def ejecutar_motor_analisis(repo: str, limite: int, salario: float, horas_efectivas: int, loc_por_hora: float) -> Dict[str, Any]:
    token = obtener_github_token()

    if es_local(repo):
        es_repo_local = True
        commits = obtener_commits_local(repo, limit=limite)
    else:
        es_repo_local = False
        try:
            commits = clonar_y_obtener_commits(repo, limit=limite, token=token)
        except Exception as clone_err:
            print(f"[Info] Clonado local no disponible ({clone_err}). Reintentando via GitHub API...")
            limite_api = 5 if limite > 5 else limite
            commits = obtener_commits_api(repo, token)[:limite_api]

    if not commits:
        return {
            "repo": repo,
            "es_local": es_repo_local,
            "commits_validos": [],
            "commits_outliers": [],
            "costo_real": 0.0,
            "tiempo_total": 0.0,
            "total_costo_normal": 0.0,
            "total_tiempo_normal": 0.0,
            "total_costo_outlier": 0.0,
            "total_tiempo_outlier": 0.0
        }

    validos, outliers = filtrar_outliers(commits)

    validos_procesados = []
    total_tiempo_normal = 0.0
    total_costo_normal = 0.0
    for c in validos:
        t, costo = realizar_calculos(c, salario, horas_efectivas, loc_por_hora)
        total_tiempo_normal += t
        total_costo_normal += costo
        validos_procesados.append((c, t, costo))

    outliers_procesados = []
    total_tiempo_outlier = 0.0
    total_costo_outlier = 0.0
    for c in outliers:
        t, costo = realizar_calculos(c, salario, horas_efectivas, loc_por_hora)
        total_tiempo_outlier += t
        total_costo_outlier += costo
        outliers_procesados.append((c, t, costo))

    costo_real = total_costo_normal + total_costo_outlier
    tiempo_total = total_tiempo_normal + total_tiempo_outlier

    return {
        "repo": repo,
        "es_local": es_repo_local,
        "commits_validos": validos_procesados,
        "commits_outliers": outliers_procesados,
        "costo_real": costo_real,
        "tiempo_total": tiempo_total,
        "total_costo_normal": total_costo_normal,
        "total_tiempo_normal": total_tiempo_normal,
        "total_costo_outlier": total_costo_outlier,
        "total_tiempo_outlier": total_tiempo_outlier
    }
