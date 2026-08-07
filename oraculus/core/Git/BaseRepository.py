from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Tuple, List
from oraculus.core.metrics import CommitData
import subprocess

class BaseRepository(ABC):

    def __init__(self, ruta_repo:str, limit:int = 10):
        self.ruta_repo = ruta_repo
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

    def _ejecutar_clonacion(self, cmd:list[str], mensaje_inicial:str, callback_resultado:Callable[[subprocess.CompletedProcess], None]|None = None) -> None:
        print(mensaje_inicial)
        try:
            result = subprocess.run(cmd, capture_output=True, check=False)
            if callable(callback_resultado): callback_resultado(result)

        except FileNotFoundError:
            raise RuntimeError("No se encontró el comando 'git' en el sistema. Asegurarse de tener Git instalado y en tu PATH")

    @abstractmethod
    def _validar(self) -> None:
        pass
