from typing import Dict, Any, List
import subprocess
from oraculus.connectors.github_client import preparar_repositorio_analisis
from oraculus.core.metrics import CommitData, filtrar_outliers, realizar_calculos, medir_cc_codigo, calcular_delta_calidad
from oraculus.utils.config import obtener_github_token

def obtener_archivos_modificados(repo_path: str, sha: str) -> List[str]:
    cmd = ["git", "-c", "safe.directory=*", "show", "--pretty=format:", "--name-only", sha]
    res = subprocess.run(cmd, cwd=repo_path, capture_output=True, check=False)
    if res.returncode == 0:
        stdout_str = res.stdout.decode("utf-8", errors="ignore")
        return [line.strip() for line in stdout_str.splitlines() if line.strip()]
    return []

def obtener_contenido_revision(repo_path: str, revision: str, filepath: str) -> str:
    git_filepath = filepath.replace("\\", "/")
    cmd = ["git", "-c", "safe.directory=*", "show", f"{revision}:{git_filepath}"]
    res = subprocess.run(cmd, cwd=repo_path, capture_output=True, check=False)
    if res.returncode == 0:
        return res.stdout.decode("utf-8", errors="ignore")
    return ""

def analizar_calidad_commit(repo_cache_path: str, sha: str, lenguaje: str) -> str:
    if not repo_cache_path or lenguaje != "python":
        return "NEUTRAL"
        
    archivos = obtener_archivos_modificados(repo_cache_path, sha)
    py_files = [f for f in archivos if f.endswith(".py")]
    if not py_files:
        return "NEUTRAL"
        
    cc_antes_total = 0.0
    cc_despues_total = 0.0
    loc_antes_total = 0
    loc_despues_total = 0
    for filepath in py_files:
        code_before = obtener_contenido_revision(repo_cache_path, f"{sha}~1", filepath)
        code_after = obtener_contenido_revision(repo_cache_path, sha, filepath)
        
        cc_antes_total += medir_cc_codigo(code_before)
        cc_despues_total += medir_cc_codigo(code_after)
        loc_antes_total += len(code_before.splitlines())
        loc_despues_total += len(code_after.splitlines())
        
    cc_antes_avg = cc_antes_total / len(py_files)
    cc_despues_avg = cc_despues_total / len(py_files)
    return calcular_delta_calidad(cc_antes_avg, cc_despues_avg, loc_antes_total, loc_despues_total)

def ejecutar_motor_analisis(
    repo: str,
    limite: int,
    salario: float,
    horas_efectivas: int,
    loc_por_hora: float,
    lenguaje: str = "python"
) -> Dict[str, Any]:
    token = obtener_github_token()

    commits, repo_cache_path, es_repo_local = preparar_repositorio_analisis(repo, limite, token)

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

    # Auto-detección de lenguaje si es necesario
    if lenguaje == "auto" and repo_cache_path:
        todos_archivos = []
        for c in commits:
            todos_archivos.extend(obtener_archivos_modificados(repo_cache_path, c.sha))
        from oraculus.utils.data_helpers import detectar_lenguaje
        lenguaje = detectar_lenguaje(todos_archivos)

    validos, outliers = filtrar_outliers(commits)

    validos_procesados = []
    total_tiempo_normal = 0.0
    total_costo_normal = 0.0
    for c in validos:
        t, costo = realizar_calculos(c, salario, horas_efectivas, loc_por_hora)
        total_tiempo_normal += t
        total_costo_normal += costo
        calidad = analizar_calidad_commit(repo_cache_path, c.sha, lenguaje)
        validos_procesados.append((c, t, costo, calidad))

    outliers_procesados = []
    total_tiempo_outlier = 0.0
    total_costo_outlier = 0.0
    for c in outliers:
        t, costo = realizar_calculos(c, salario, horas_efectivas, loc_por_hora)
        total_tiempo_outlier += t
        total_costo_outlier += costo
        calidad = analizar_calidad_commit(repo_cache_path, c.sha, lenguaje)
        outliers_procesados.append((c, t, costo, calidad))

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
