"""
PRECAUCIÓN:
    Actualmente esta herramienta hace un API REST a Github con un Formula de N+1
    Por lo que se debe mantener el limite de commits en 5 y no abusar de ello
    No solo por los tokens de la API sino porque el sistema se saturará

Posibles refactorizaciones:
    1. Github GraphQL API:
        GraphQL permite enviar una nota a GitHub diciendo: 
        "Dame los últimos 20 commits y de cada uno dime sus adiciones, 
        eliminaciones y mensaje". 
        
        GitHub responde todo en un solo paquete JSON.
    2. Clonado Local(El ideal):
        El usuario tenga el repositorio descargado en su computadora. 
        En lugar de preguntarle a los servidores de GitHub en 
        California cada vez que necesitas un dato, se pregunta a 
        la carpeta .git que ya tiene en su disco duro.
        
        Usando una librería como GitPython o simplemente 
        comandos de consola desde Python
"""

import requests
import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List



@dataclass
class CommitData:
    sha: str
    mensaje: str
    additions: int
    deletions: int

def obtener_commits(repo_path, token):
    url = f"https://api.github.com/repos/{repo_path}/commits"
    headers = {
        'Authorization': f'token {token}',
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200: return []

    lista_objetos = []
    for c in response.json()[:5]:
        sha = c['sha']
        res = requests.get(f"{url}/{sha}", headers=headers).json()

        lista_objetos.append(CommitData(
            sha=sha[:7],
            mensaje = res['commit']['message'].splitlines()[0],
            additions = res.get('stats', {}).get('additions'),
            deletions=res.get('stats', {}).get('deletions',0)
        ))
    return lista_objetos

def realizar_calculos(commit: CommitData, salario: float, horas_mes: int):
    costo_hora = salario / horas_mes
    loc_commit = commit.additions + commit.deletions

    t_horas = loc_commit /60
    costo_monetario = costo_hora * t_horas

    return t_horas, costo_monetario

def ejecutar_cli():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    repo = input("Introduce el repo (usuario/repo): ")
    salario = float(input("Salario mensual: "))
    horas_efectivas = int(input("Horas efectivas al mes: "))

    print(f"\n--- Analizando {repo} ---\n")

    commits = obtener_commits(repo, token)

    for c in commits:
        tiempo, costo = realizar_calculos(c, salario, horas_efectivas)

        print(f"Commit: {c.sha} | LOC: {c.additions + c.deletions}")
        print(f"> Tiempo: {tiempo:.2f}h | Costo: ${costo:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    ejecutar_cli()


