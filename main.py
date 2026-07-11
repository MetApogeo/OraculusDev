"""
PRECAUCIÓN:
    Actualmente esta herramienta hace un API REST a Github con un Formula de N+1
    Por lo que se debe mantener el limite de commits en 5 y no abusar de ello
    No solo por los tokens de la API sino porque el sistema se saturará

Posibles refactorizaciones:
    1. Github GraphQL API:
        GraphQL permite enviar una nota a GitHub diciendo: 
        "Dame los últimos 20 commits y de cada uno dime sus adiciones, 
        eliminaciones y mensaje". 
        
        GitHub responde todo en un solo paquete JSON.
    2. Clonado Local(El ideal):
        El usuario tenga el repositorio descargado en su computadora. 
        En lugar de preguntarle a los servidores de GitHub en 
        California cada vez que necesitas un dato, se pregunta a 
        la carpeta .git que ya tiene en su disco duro.
        
        Usando una librería como GitPython o simplemente 
        comandos de consola desde Python
"""

import requests
import os
import subprocess
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List



@dataclass
class CommitData:
    sha: str
    mensaje: str
    additions: int = 0
    deletions: int = 0

def es_local(entrada: str) -> bool:
    return os.path.exists(entrada)

def obtener_commits_api(repo_path, token):
    if not token:
        print("[Advertencia] GITHUB_TOKEN no está configurado en el archivo .env. Podrías experimentar límites de tasa (rate limiting).")

    url = f"https://api.github.com/repos/{repo_path}/commits"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise RuntimeError(f"Error de conexión al conectar con GitHub: {e}")

    if response.status_code == 401:
        raise RuntimeError("Error 401: El token de GitHub proporcionado no es válido o ha expirado.")
    elif response.status_code == 404:
        raise RuntimeError(f"Error 404: No se encontró el repositorio '{repo_path}'. Verifica que el nombre sea correcto y que el repositorio sea público (o que tu token tenga acceso si es privado).")
    elif response.status_code == 403:
        rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
        if rate_limit_remaining == "0":
            raise RuntimeError("Error 403: Se ha alcanzado el límite de tasa (rate limit) de la API de GitHub. Intenta de nuevo más tarde o configura un GITHUB_TOKEN válido.")
        else:
            raise RuntimeError("Error 403: Acceso prohibido al repositorio.")
    elif response.status_code != 200:
        raise RuntimeError(f"Error al obtener commits de GitHub (Código {response.status_code}): {response.text}")

    commits_json = response.json()
    if not commits_json:
        return []

    lista_objetos = []
    # Limitar a los primeros 5 commits como precaución de N+1
    for c in commits_json[:5]:
        sha = c['sha']
        try:
            res_detail = requests.get(f"{url}/{sha}", headers=headers, timeout=10)
            if res_detail.status_code != 200:
                print(f"[Advertencia] No se pudieron obtener detalles para el commit {sha[:7]}. Código: {res_detail.status_code}")
                continue
            res = res_detail.json()
        except requests.RequestException as e:
            print(f"[Advertencia] Error de conexión al obtener detalles para el commit {sha[:7]}: {e}")
            continue

        stats = res.get('stats') or {}
        lista_objetos.append(CommitData(
            sha=sha[:7],
            mensaje=res['commit']['message'].splitlines()[0],
            additions=stats.get('additions', 0),
            deletions=stats.get('deletions', 0)
        ))
    return lista_objetos

def obtener_commits_local(repo_path: str, limit: int = 10) -> List[CommitData]:
    if not os.path.exists(repo_path):
        raise RuntimeError(f"La ruta local '{repo_path}' no existe.")

    cmd = ["git", "log", f"-n", str(limit), "--numstat", "--pretty=format:COMMIT:%h|%s"]
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
    except FileNotFoundError:
        raise RuntimeError("No se encontró el comando 'git' en el sistema. Asegúrate de tener Git instalado y configurado en tu PATH.")

    if result.returncode != 0:
        error_msg = result.stderr.strip()
        raise RuntimeError(f"Error de Git al obtener los commits: {error_msg}")

    output = result.stdout
    if not output.strip():
        return []

    lista_objetos = []
    current_commit = None

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("COMMIT:"):
            parts = line[7:].split("|", 1)
            sha = parts[0]
            mensaje = parts[1] if len(parts) > 1 else ""
            current_commit = CommitData(
                sha=sha,
                mensaje=mensaje,
                additions=0,
                deletions=0
            )
            lista_objetos.append(current_commit)
        elif current_commit is not None:
            # Línea de estadísticas de --numstat: "additions deletions filename"
            parts = line.split(None, 2)
            if len(parts) >= 2:
                add_str, del_str = parts[0], parts[1]
                add_val = int(add_str) if add_str.isdigit() else 0
                del_val = int(del_str) if del_str.isdigit() else 0
                current_commit.additions += add_val
                current_commit.deletions += del_val

    return lista_objetos

def realizar_calculos(commit: CommitData, salario: float, horas_mes: int, loc_por_hora: float = 60.0):
    costo_hora = salario / horas_mes
    loc_commit = commit.additions + commit.deletions

    t_horas = loc_commit / loc_por_hora
    costo_monetario = costo_hora * t_horas

    return t_horas, costo_monetario

def filtrar_outliers(commits: list[CommitData]):
    locs = [c.additions + c.deletions for c in commits]
    locs_ordenados = sorted(locs)

    q1 = locs_ordenados[len(locs_ordenados) // 4]
    q3 = locs_ordenados[(len(locs_ordenados) * 3) // 4]
    iqr = q3 - q1
    l_sup = q3 + (1.5 * iqr)

    validos = [c for c in commits if (c.additions + c.deletions) <= l_sup]
    outliers = [c for c in commits if (c.additions + c.deletions) > l_sup]

    return validos, outliers

def ejecutar_cli():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    try:
        repo = input("Introduce el repo (usuario/repo o ruta local) [Por defecto: .]: ").strip()
        if not repo:
            repo = "."

        limite_input = input("Número de commits a analizar [Por defecto: 10]: ").strip()
        limite = int(limite_input) if limite_input else 10
        if limite < 1:
            print("[Error] El número de commits debe ser al menos 1.")
            return

        if limite < 10:
            print("\n[Advertencia] Con menos de 10 commits el filtro IQR puede no ser representativo.")

        salario_input = input("Salario mensual: ").strip()
        salario = float(salario_input) if salario_input else 0.0

        horas_input = input("Horas efectivas al mes: ").strip()
        horas_efectivas = int(horas_input) if horas_input else 160

        loc_por_hora_input = input("Líneas de código (LOC) promedio por hora [Por defecto: 60]: ").strip()
        loc_por_hora = float(loc_por_hora_input) if loc_por_hora_input else 60.0

        if es_local(repo):
            print(f"\n--- Analizando repositorio local en: {os.path.abspath(repo)} ---\n")
            commits = obtener_commits_local(repo, limit=limite)
        else:
            print(f"\n--- Analizando repositorio remoto en GitHub: {repo} ---\n")
            if limite > 5:
                print("[Nota] El análisis remoto vía API REST está limitado a un máximo de 5 commits para prevenir límites de tasa.")
                limite = 5
            commits = obtener_commits_api(repo, token)

        if not commits:
            print("No se encontraron commits o el historial está vacío.")
            return

        # Filtrar outliers
        validos, outliers = filtrar_outliers(commits)

        print("=== COMMITS ESTÁNDAR ===")
        total_tiempo_normal = 0.0
        total_costo_normal = 0.0
        for c in validos:
            tiempo, costo = realizar_calculos(c, salario, horas_efectivas, loc_por_hora)
            total_tiempo_normal += tiempo
            total_costo_normal += costo
            print(f"Commit: {c.sha} | LOC: {c.additions + c.deletions} (+{c.additions}/-{c.deletions})")
            print(f"  > Mensaje: {c.mensaje}")
            print(f"  > Tiempo estimado: {tiempo:.2f}h | Costo: ${costo:.2f}")
            print("-" * 40)

        total_tiempo_outlier = 0.0
        total_costo_outlier = 0.0
        if outliers:
            print("\n=== ANOMALÍAS DETECTADAS (Outliers) ===")
            print("Commits cuyo volumen de código excede el límite estadístico (IQR) y podrían desviar las estimaciones.")
            for c in outliers:
                tiempo, costo = realizar_calculos(c, salario, horas_efectivas, loc_por_hora)
                total_tiempo_outlier += tiempo
                total_costo_outlier += costo
                print(f"Commit: {c.sha} [OUTLIER] | LOC: {c.additions + c.deletions} (+{c.additions}/-{c.deletions})")
                print(f"  > Mensaje: {c.mensaje}")
                print(f"  > Tiempo estimado: {tiempo:.2f}h | Costo: ${costo:.2f}")
                print("-" * 40)

        print("\n=== RESUMEN FINANCIERO ===")
        print(f"Desarrollo Estándar:  Tiempo: {total_tiempo_normal:.2f}h | Costo Estimado: ${total_costo_normal:.2f}")
        if outliers:
            print(f"Desarrollo Anómalo:   Tiempo: {total_tiempo_outlier:.2f}h | Costo Estimado: ${total_costo_outlier:.2f}")
            print(f"Total Acumulado:      Tiempo: {total_tiempo_normal + total_tiempo_outlier:.2f}h | Costo Total: ${total_costo_normal + total_costo_outlier:.2f}")
        else:
            print("No se detectaron anomalías en la muestra de commits analizada.")

    except ValueError as e:
        print(f"\n[Error] Entrada no válida. Asegúrate de introducir números correctos para salario, horas y LOC/hora. Detalle: {e}")
    except RuntimeError as e:
        print(f"\n[Error] {e}")
    except Exception as e:
        print(f"\n[Error inesperado] {e}")

if __name__ == "__main__":
    ejecutar_cli()


