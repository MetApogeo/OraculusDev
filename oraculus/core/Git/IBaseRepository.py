from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List, Type
from oraculus.core.metrics import CommitData
import subprocess

from oraculus.core.git.parser.ICommitParser import ICommitParser
from oraculus.core.git.parser.ParserLocalSubprocess import ParserLocalSubprocess

class IBaseRepository(ABC):

    def __init__(self, raw_repo:str, parser:ICommitParser, limit:int = 10):
        self.raw_repo = raw_repo.strip()
        self.ruta_repo_cache:str | None = None
        self.limit = limit
        self.parser:ICommitParser = parser

        self._validar()

    @property
    @abstractmethod
    def es_origen_local(self)-> bool:
        pass

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

    def _commits_desde_carpeta(self) -> str:
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
            return ""

        return output