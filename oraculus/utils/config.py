import os
from dotenv import load_dotenv
import shutil
import subprocess

def cargar_entorno(ruta_repo=None):
    load_dotenv()
    if ruta_repo and os.path.isdir(ruta_repo):
        env_path = os.path.join(ruta_repo, ".env")
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path)

def obtener_github_token() -> str:
    return os.getenv("GITHUB_TOKEN", "")


def preparar_directorio_cache(nombre_destino:str) -> str:

    directorio_cache = os.path.join(os.getcwd(), ".oraculus_cache")

    os.makedirs(directorio_cache, exist_ok=True)
    ruta_final = os.path.join(directorio_cache, nombre_destino)

    # Vefificar existencia, eliminar en su caso
    if os.path.exists(ruta_final):
        try:
            shutil.rmtree(ruta_final)
        except Exception:
            subprocess.run(['rmdir', '/s', '/q', ruta_final], shell=True)

    return ruta_final
