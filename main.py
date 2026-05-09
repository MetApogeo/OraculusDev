import requests
import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List

@dataclass
class ResultadoCommit:
    sha: str
    mensaje: str
    adiciones: int
    eliminaciones: int
    archivos: int

load_dotenv()

PAT_Github = os.getenv("GITHUB_TOKEN")
headers = {
    'Authorization': f'token {PAT_Github}',
    "Accept": "application/vnd.github.v3+json"
}
repo = "MetApogeo/Aprendiendo_Ruby_and_RubyOnRails"
url = f"https://api.github.com/repos/{repo}/commits"


def CalcularCommits() -> List[ResultadoCommit]:
    response = requests.get(url, headers=headers)
    lista_resultados = []

    if response.status_code == 200:
        commits = response.json()

        for c in commits[:5]:
            sha = c['sha']
            commit_url = f"{url}/{sha}"
            detail_response = requests.get(commit_url, headers=headers)

            if detail_response.status_code == 200:
                data = detail_response.json()
                stats = data.get('stats', {})

                obj_commit = ResultadoCommit(
                    sha = sha[:7],
                    mensaje = data['commit']['message'].splitlines()[0],
                    adiciones = stats.get('additions', 0),
                    eliminaciones = stats.get('deletions',0),
                    archivos = len(data.get('files', []))
                )

                lista_resultados.append(obj_commit)
                print(f"Procesado: {sha[:7]}")
        return lista_resultados
    else:
        print("Failed to fetch data:", response.status_code)
        return []

mis_commits = CalcularCommits()
