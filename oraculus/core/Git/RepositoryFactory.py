import os

# Interfaces
from oraculus.core.git.IBaseRepository import IBaseRepository

# Implementaciones
from oraculus.core.git.LocalGitRepository import LocalGitRepository
from oraculus.core.git.GithubRepository import GithubRepository

class RepositoryFactory:

    @staticmethod
    def crear(raw_repo:str, limit:int = 10, token:str|None = None)-> IBaseRepository:

        if os.path.exists(raw_repo):
            return LocalGitRepository(raw_repo, limit)

        return GithubRepository(raw_repo, limit, token)
