from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List
from oraculus.core.metrics import CommitData
import subprocess

class IBaseRepository(ABC):

    def __init__(self, raw_repo:str, limit:int = 10):
        self.raw_repo = raw_repo.strip()
        self.ruta_repo_cache:str | None = None
        self.limit = limit

        self._validar()

    @abstractmethod
    def obtener_commits(self) -> List[CommitData]:
        pass
    
    @abstractmethod
    def _preparar_repositorio(self) -> str:
        pass

    @abstractmethod
    def _clonar_repositorio(self) -> None:
        pass

    @abstractmethod
    def _validar(self) -> None:
        pass

    def _ejecutar_clonacion(self, cmd:list[str], mensaje_inicial:str, callback_resultado:Callable[[subprocess.CompletedProcess], None]|None = None) -> None:
        print(mensaje_inicial)
        try:
            result = subprocess.run(cmd, capture_output=True, check=False)
            if callable(callback_resultado): callback_resultado(result)

        except FileNotFoundError:
            raise RuntimeError("No se encontró el comando 'git' en el sistema. Asegurarse de tener Git instalado y en tu PATH")

    def _commits_desde_carpeta(self) -> List[CommitData]:
        cmd = ["git", "-c", "safe.directory=*", "log", f"-n", str(self.limit), "--numstat", "--pretty=format:COMMIT:%h|%s"]

        try:
            result = subprocess.run(cmd, cwd=self.ruta_repo_cache, capture_output=True, check=False)
        except FileNotFoundError:
            #TODO: Cambiar por implementación multilenguaje
            raise RuntimeError("No se encontró el comando 'git' en el sistema. Asegurese de tener Git instalado y configurado en el PATH")

        output = result.stdout.decode("utf-8", errors="ignore")
        salida_error = result.stderr.decode("utf-8", errors="ignore")

        if result.returncode != 0:
            raise RuntimeError(f"Error de Git al obtener los commits: {salida_error.strip()}")

        if not output.strip():
            return []