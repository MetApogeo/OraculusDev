from typing import List, Any

# Core
from oraculus.core.git.parser.ICommitParser import ICommitParser
from oraculus.core.metrics import CommitData
from oraculus.utils.data_helpers import es_archivo_ignorado

class ParserGithubApi(ICommitParser):

    SHORT_SHA_LENGTH = 7

    def parse_to_commit_data_list(self, commit_list:List[dict[str, Any]]) -> List[CommitData]:

        commit_data_list:List[CommitData] = []

        for detalle_sha in commit_list:
            mensaje:str = detalle_sha['commit']['message'].splitlines()[0]

            if mensaje.startswith('Merge'):
                continue

            additions_limpias = 0
            deletions_limpias = 0

            for file_entry in detalle_sha.get('files', []):
                filename = file_entry.get('filename', '')
                if not es_archivo_ignorado(filename):
                    additions_limpias += file_entry.get('additions', 0)
                    deletions_limpias += file_entry.get('deletions', 0)

            short_sha:str = detalle_sha['sha'][:self.SHORT_SHA_LENGTH]

            commit_data_list.append(CommitData(short_sha, mensaje, additions_limpias, deletions_limpias))

        return commit_data_list