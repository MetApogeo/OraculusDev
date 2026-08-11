# Interfaces
from oraculus.core.git.IBaseRepository import IBaseRepository

# Implementaciones
from oraculus.core.git.parser.ParserLocalSubprocess import ParserLocalSubprocess
from oraculus.core.metrics import CommitData
# Utilidades
import subprocess
from pathlib import Path
from oraculus.utils.config import preparar_directorio_cache
from oraculus.utils.i18n import t
from typing import List

class LocalGitRepository(IBaseRepository):

    def __init__(self, raw_repo: str, limit: int = 10):
        super().__init__(raw_repo=raw_repo, parser=ParserLocalSubprocess(), limit=limit)
        self.ruta_absoluta = Path(self.raw_repo).absolute()

    @property
    def es_origen_local(self):
        return True
    
    def obtener_commits(self)-> List[CommitData]:
        try:
            self._preparar_repositorio()
        except RuntimeError as e:
            print(f"[Advertencia] No se pudo crear el caché seguro: {e}")
            print("[Advertencia] Se operará sobre el repositorio original.")

            self.ruta_repo_cache = self.ruta_absoluta

        commits_crudo:str = super()._commits_desde_carpeta()
        commit_data_list:List[CommitData] = self.parser.parse_to_commit_data_list(commits_crudo)

        return commit_data_list

    def _preparar_repositorio(self):
        # Preparar carpeta
        carpeta_destino = "local_copy_" + self.ruta_absoluta.name
        self.ruta_repo_cache = preparar_directorio_cache(carpeta_destino)

        # Ejecutar proceso de clonado
        self._clonar_repositorio();

    def _clonar_repositorio(self):
        # Definimos los parámetros para el clonado
        cmd = ['git', 'clone', '--quiet', self.ruta_absoluta, self.ruta_repo_cache]
        mensaje_cmd = t('cli', 'info_clonado_local').format(ruta=self.raw_repo)

        def manejar_resultado(result:subprocess.CompletedProcess):
            if result.returncode != 0:
                error_limpio = result.stderr.decode('utf-8', errors="ignore").strip()
                #TODO: Cambiar el error hardcodeado por su implementación multilenguaje
                raise RuntimeError(f"Error al clonar el repositorio local a cache: {error_limpio}")

        # Clonamos el repositorio
        super()._ejecutar_clonacion(cmd, mensaje_cmd, manejar_resultado)


    def _validar(self):
        ruta = Path(self.raw_repo)

        # Comprobar que la ruta exista en el disco
        if not ruta.exists():
            #TODO: Cambiar los value errors por su traducción local
            raise ValueError(f"La ruta local '{ruta}' no existe.")

        # Comprobar que sea un directorio
        if not ruta.is_dir():
            #TODO: Cambiar los value errors por su traducción local
            raise ValueError(f"La ruta '{ruta}' no es un directorio")

        # Buscar el elemento .git dentro del directorio
        git_path = ruta / ".git"

        if not git_path.exists():
            #TODO: Cambiar los value errors por su traducción local
            raise ValueError(f"La ruta '{ruta}' no es un repositorio Git válido (falta el directorio .git).")

        # Buscar la ubicación real del directorio Git

        # Caso si el directorio Git es directamente .git/
        if git_path.is_dir():
            git_dir = git_path

        # Caso en donde .git es un archivo de texto (worktree/submódulo)
        elif git_path.is_file():
            try:
                contenido = git_path.read_text(encoding='utf-8').strip()
            except Exception as e:
                raise ValueError(f"No se pudo validar el archivo .git en '{ruta}': {e}") from e

            if not contenido.startswith("gitdir:"): raise ValueError(f"El archivo .git en '{ruta}' no es un puntero válido")

            gitdir_value = contenido.split("gitdir:", 1)[1].strip()

            if not gitdir_value: raise ValueError(f"El archivo .git en ruta '{ruta}' no contiene una ruta válida")

            git_dir = Path(gitdir_value)

            if not git_dir.is_absolute(): 
                git_dir = (ruta / git_dir).resolve()

            if not git_dir.is_dir(): raise ValueError(f"El puntero de .git en '{ruta}' apunta a una ruta inexistente")

        else: 
            # Caso borde: .git existe pero no es ni archivo ni directorio
            raise ValueError(f"El elemento '.git' en '{ruta}' no es un directorio ni un archivo válido")

        # Validar la estructura interna mínima del repo (Ahora que ya sabemos que si es un directorio git valido en la mayoria de casos)
        tiene_head = (git_dir / "HEAD").is_file()
        tiene_objects = (git_dir / "objects").is_dir()
        tiene_refs = (git_dir / "refs").is_dir()

        if not (tiene_head and tiene_objects and tiene_refs): 
            raise ValueError(f"La carpeta '{ruta}' contiene un .git pero está corrupto o incompleto")