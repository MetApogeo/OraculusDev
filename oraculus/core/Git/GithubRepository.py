import re
import subprocess
import requests
from typing import List, Callable, Any
#Utilidades
from oraculus.utils.config import preparar_directorio_cache
from oraculus.core.metrics import CommitData
from oraculus.utils.i18n import t
# Interfaces
from oraculus.core.git.IBaseRepository import IBaseRepository

class GithubRepository(IBaseRepository):

    _valid_url_regex = re.compile(
        r"^(?:https://)?github\.com/"
        r"(?P<owner>[a-zA-Z0-9][a-zA-Z0-9-]{0,38})/"
        r"(?P<repository>[a-zA-Z0-9_.-]{1,100})"
        r"(?:\.git)?$"
    )

    _valid_identificador_regex = re.compile(
        r"^(?P<owner>[a-zA-Z0-9][a-zA-Z0-9-]{0,38})/(?P<repository>[a-zA-Z0-9_.-]{1,100})$"
    )

    msg_error_status:dict[int, Callable[[Any, requests.Response], str]] = {
        401: lambda self, r: "Error 401: El token de Github proporcionado no es válido o ha expirado.",
        404: lambda self, r: f"Error 404: No se encontró el repositorio '{self.usuario}/{self.repositorio}'. Verifica que el nombre sea correcto y que el repositorio sea público (o que tu token tenga acceso si es privado).",
        403: lambda self, r: (
            "Error 403: Se ha alcanzado el límite de tasa (rate limit) de la API de GitHub. Intenta de nuevo más tarde o configura un GITHUB_TOKEN válido." 
            if r.headers.get("X-RateLimit-Remaining") == "0"
            else "Error 403: Acceso prohibido al repositorio."
        )
    }

    def __init__(self, raw_repo:str, limit:int = 10, token:str|None = None):
        super().__init__(raw_repo=raw_repo, limit=limit)

        self.token:str|None = token

        info_repo = self._obtener_info_identificador()
        self.usuario = info_repo["owner"]
        self.repositorio = info_repo["repository"].removesuffix(".git")

        self.url_remote_repository = self._construir_url()

    def obtener_commits(self):
        estrategia_obtencion_commits = None
        try: 
            self._preparar_repositorio()
            estrategia_obtencion_commits = super()._commits_desde_carpeta
        except Exception as clone_error:
            print(t('cli', 'info_clone_api_fallback').format(error=clone_error))
            self.limit = 5
            estrategia_obtencion_commits = self._commits_desde_api

        commits:List[CommitData] = estrategia_obtencion_commits()


    def _preparar_repositorio(self):
        carpeta_destino = f"{self.usuario}_{self.repositorio}"
        self.ruta_repo_cache = preparar_directorio_cache(carpeta_destino)

        self._clonar_repositorio()

    def _clonar_repositorio(self):
        # Parámetros de clonado 
        cmd = ["git", "clone", "--depth", str(self.limit), "--quiet", self.url_remote_repository, self.ruta_repo_cache]
        mensaje_cmd = f"[Info] Clonando repositorio remoto {self.usuario}/{self.repositorio}"

        def manejar_resultado(result:subprocess.CompletedProcess):
            if result.returncode != 0:
                error_limpio = result.stderr.decode('utf-8', errors='ignore').strip()
                if self.token:
                    error_limpio = error_limpio.replace(self.token, '******')
                raise RuntimeError(f"Error al clonar el repositorio: {error_limpio}")

        super()._ejecutar_clonacion(cmd, mensaje_cmd, manejar_resultado)

    def _validar(self):
        #TODO: Colocar mensaje de error correcto
        if not self._es_repo_remoto(self.raw_repo): raise ValueError("El repositorio ingresado no es un identificador de repositorio de Github válido")


    def _es_repo_remoto(self, repo:str) -> bool:
        return self._es_url(repo) or self._es_identificador(repo)

    def _es_url(self, repo:str) -> bool:
        return bool(self._valid_url_regex.match(repo))

    def _es_identificador(self, repo:str) -> bool:
        return bool(self._valid_identificador_regex.match(repo))

    def _obtener_info_identificador(self) -> dict[str, str]:
        repo = self.raw_repo
        match = self._valid_identificador_regex.match(repo) or self._valid_url_regex.match(repo)

        return match.groupdict()

    def _construir_url(self):
        url_token:str = ""
        at:str = ""

        if self.token:
            url_token = self.token
            at = "@"

        return f"https://{url_token}{at}github.com/{self.usuario}/{self.repositorio}.git"

    def _commits_desde_api(self) -> List[CommitData]:
        url:str = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/commits"
        headers:dict[str, str] = { "Accept": "application/vnd.github.v3+json" }

        if self.token is None:
            print("[Advertencia] GITHUB_TOKEN no esta configurado en el archivo .env. Podrías experimentar límites de tasa (Rate Limiting).")
        else:
            headers["Authorization"] = f"token {self.token}"

        try:
            response = requests.get(url, headers=headers, params={"per_page": self.limit}, timeout=10)
        except requests.RequestException as e:
            raise RuntimeError(f"Error de conexión al conectar con Github: {e}")

        if response.status_code != 200:
            msg_error:str = f"Error al obtener commits de GitHub (Código {response.status_code}): {response.text}"

            if response.status_code in self.msg_error_status:
                msg_error = self.msg_error_status[response.status_code](response)

            raise RuntimeError(msg_error)

        commits_json = response.json()

        if not commits_json: 
            return []
