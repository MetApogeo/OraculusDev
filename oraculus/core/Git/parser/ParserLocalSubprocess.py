from oraculus.core.git.parser.ICommitParser import ICommitParser
from oraculus.core.metrics import CommitData
from oraculus.utils.data_helpers import es_archivo_ignorado

from typing import List


class ParserLocalSubprocess(ICommitParser):

    PREFIX_COMMIT = "COMMIT:"
    PREFIX_LEN = len(PREFIX_COMMIT)

    NUMSTAT_MAX_SPLIT = 2
    NUMSTAT_REQUIRED_FIELDS = 3

    def parse_to_commit_data_list(self, commits_output:str)-> List[CommitData]:
        commit_data_list:List[CommitData] = []
        current_commit = None

        for line in commits_output.splitlines():
            line = line.strip()
            if not line: continue

            if line.startswith(self.PREFIX_COMMIT):
                contenido_commit = line[self.PREFIX_LEN:]

                parts = contenido_commit.split("|", maxsplit=1)
                sha = parts[0]
                mensaje = parts[1] if len(parts) > 1 else ""

                if mensaje.startswith('Merge'):
                    current_commit = None
                    continue

                current_commit = CommitData(sha, mensaje, additions=0, deletions=0)
                commit_data_list.append(current_commit)

            elif current_commit is not None:
                parts = line.split(None, self.NUMSTAT_MAX_SPLIT)

                if len(parts) >= self.NUMSTAT_REQUIRED_FIELDS:
                    add_str, del_str, filepath = parts[0], parts[1], parts[2]
                    if not es_archivo_ignorado(filepath):
                        add_val = int(add_str) if add_str.isdigit() else 0
                        del_val = int(del_str) if del_str.isdigit() else 0
                        current_commit.additions += add_val
                        current_commit.deletions += del_val

        return commit_data_list
