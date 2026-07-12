import os
import requests
import subprocess
import shutil
from typing import List
from oraculus.core.metrics import CommitData
from oraculus.utils.data_helpers import es_archivo_ignorado
from oraculus.utils.i18n import t

def es_local(entrada: str) -> bool:
    return os.path.exists(entrada)

def obtener_commits_api(repo_path: str, token: str) -> List[CommitData]:
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

        mensaje = res['commit']['message'].splitlines()[0]
        if mensaje.startswith("Merge"):
            continue

        additions_limpias = 0
        deletions_limpias = 0
        for file_entry in res.get('files', []):
            filename = file_entry.get('filename', '')
            if not es_archivo_ignorado(filename):
                additions_limpias += file_entry.get('additions', 0)
                deletions_limpias += file_entry.get('deletions', 0)

        lista_objetos.append(CommitData(
            sha=sha[:7],
            mensaje=mensaje,
            additions=additions_limpias,
            deletions=deletions_limpias
        ))
    return lista_objetos

def obtener_commits_local(repo_path: str, limit: int = 10) -> List[CommitData]:
    if not os.path.exists(repo_path):
        raise RuntimeError(f"La ruta local '{repo_path}' no existe.")

    cmd = ["git", "-c", "safe.directory=*", "log", f"-n", str(limit), "--numstat", "--pretty=format:COMMIT:%h|%s"]
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            check=False
        )
    except FileNotFoundError:
        raise RuntimeError("No se encontró el comando 'git' en el sistema. Asegúrate de tener Git instalado y configurado en tu PATH.")

    output = result.stdout.decode("utf-8", errors="ignore")
    stderr = result.stderr.decode("utf-8", errors="ignore")

    if result.returncode != 0:
        raise RuntimeError(f"Error de Git al obtener los commits: {stderr.strip()}")
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
            if mensaje.startswith("Merge"):
                current_commit = None
                continue
            current_commit = CommitData(
                sha=sha,
                mensaje=mensaje,
                additions=0,
                deletions=0
            )
            lista_objetos.append(current_commit)
        elif current_commit is not None:
            parts = line.split(None, 2)
            if len(parts) >= 3:
                add_str, del_str, filepath = parts[0], parts[1], parts[2]
                if not es_archivo_ignorado(filepath):
                    add_val = int(add_str) if add_str.isdigit() else 0
                    del_val = int(del_str) if del_str.isdigit() else 0
                    current_commit.additions += add_val
                    current_commit.deletions += del_val

    return lista_objetos

def clonar_y_obtener_commits(repo_remoto: str, limit: int, token: str = None) -> List[CommitData]:
    if "github.com" not in repo_remoto and not repo_remoto.startswith("http"):
        if token:
            url = f"https://{token}@github.com/{repo_remoto}.git"
        else:
            url = f"https://github.com/{repo_remoto}.git"
        repo_name = repo_remoto.replace("/", "_")
    else:
        url = repo_remoto
        repo_name = repo_remoto.split("/")[-1].replace(".git", "")
        if token and "github.com" in url and "@github.com" not in url:
            url = url.replace("https://github.com", f"https://{token}@github.com")

    cache_dir = os.path.join(os.getcwd(), ".oraculus_cache")
    os.makedirs(cache_dir, exist_ok=True)
    dest_path = os.path.join(cache_dir, repo_name)

    if os.path.exists(dest_path):
        import shutil
        try:
            shutil.rmtree(dest_path)
        except Exception:
            subprocess.run(["rmdir", "/s", "/q", dest_path], shell=True)

    print(f"[Info] Clonando repositorio remoto {repo_remoto} en caché local (.oraculus_cache)...")
    clone_cmd = ["git", "clone", "--depth", str(limit), "--quiet", url, dest_path]
    try:
        result = subprocess.run(clone_cmd, capture_output=True, check=False)
        if result.returncode != 0:
            clean_error = result.stderr.decode("utf-8", errors="ignore").strip()
            if token:
                clean_error = clean_error.replace(token, "******")
            raise RuntimeError(f"Error al clonar el repositorio: {clean_error}")
    except FileNotFoundError:
        raise RuntimeError("No se encontró el comando 'git' en el sistema. Asegúrate de tener Git instalado y en tu PATH.")

    return obtener_commits_local(dest_path, limit)

def clonar_local_a_cache(ruta_local: str) -> str:
    import shutil
    abs_path = os.path.abspath(ruta_local)
    dir_name = "local_copy_" + os.path.basename(abs_path)
    cache_dir = os.path.join(os.getcwd(), ".oraculus_cache")
    os.makedirs(cache_dir, exist_ok=True)
    dest_path = os.path.join(cache_dir, dir_name)
    
    if os.path.exists(dest_path):
        try:
            shutil.rmtree(dest_path)
        except Exception:
            subprocess.run(["rmdir", "/s", "/q", dest_path], shell=True)
            
    print(t('cli', 'info_clonando_local').format(ruta=ruta_local))
    cmd = ["git", "clone", "--quiet", abs_path, dest_path]
    try:
        result = subprocess.run(cmd, capture_output=True, check=False)
        if result.returncode != 0:
            stderr_str = result.stderr.decode("utf-8", errors="ignore").strip()
            raise RuntimeError(f"Error al clonar el repositorio local a cache: {stderr_str}")
    except FileNotFoundError:
        raise RuntimeError("No se encontro el comando 'git' en el sistema. Asegurarse de tener Git instalado y en tu PATH.")
    return dest_path

def preparar_repositorio_analisis(repo: str, limite: int, token: str = None):
    if es_local(repo):
        try:
            cache_path = clonar_local_a_cache(repo)
            commits = obtener_commits_local(cache_path, limite)
            return commits, cache_path, True
        except Exception as e:
            print(t('cli', 'advertencia_error_clone').format(error=e))
            commits = obtener_commits_local(repo, limite)
            return commits, repo, True
    else:
        if "github.com" not in repo and not repo.startswith("http"):
            repo_name = repo.replace("/", "_")
        else:
            repo_name = repo.split("/")[-1].replace(".git", "")
        
        cache_dir = os.path.join(os.getcwd(), ".oraculus_cache")
        cache_path = os.path.join(cache_dir, repo_name)
        
        try:
            commits = clonar_y_obtener_commits(repo, limite, token)
            return commits, cache_path, False
        except Exception as clone_err:
            print(t('cli', 'info_clone_api_fallback').format(error=clone_err))
            limite_api = 5 if limite > 5 else limite
            try:
                commits = obtener_commits_api(repo, token)[:limite_api]
            except Exception as api_err:
                print(t('cli', 'error_api_github').format(error=api_err))
                commits = []
            return commits, None, False

