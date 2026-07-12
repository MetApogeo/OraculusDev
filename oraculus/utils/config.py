import os
from dotenv import load_dotenv

def cargar_entorno(ruta_repo=None):
    load_dotenv()
    if ruta_repo and os.path.isdir(ruta_repo):
        env_path = os.path.join(ruta_repo, ".env")
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path)

def obtener_github_token() -> str:
    return os.getenv("GITHUB_TOKEN", "")
