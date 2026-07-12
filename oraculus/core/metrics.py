from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CommitData:
    sha: str
    mensaje: str
    additions: int = 0
    deletions: int = 0

def realizar_calculos(commit: CommitData, salario: float, horas_mes: int, loc_por_hora: float = 60.0) -> Tuple[float, float]:
    costo_hora = salario / horas_mes
    loc_commit = commit.additions + commit.deletions

    t_horas = loc_commit / loc_por_hora
    costo_monetario = costo_hora * t_horas

    return t_horas, costo_monetario

def filtrar_outliers(commits: List[CommitData]) -> Tuple[List[CommitData], List[CommitData]]:
    if not commits:
        return [], []
    locs = [c.additions + c.deletions for c in commits]
    locs_ordenados = sorted(locs)

    q1 = locs_ordenados[len(locs_ordenados) // 4]
    q3 = locs_ordenados[(len(locs_ordenados) * 3) // 4]
    iqr = q3 - q1
    l_sup = q3 + (1.5 * iqr)

    validos = [c for c in commits if (c.additions + c.deletions) <= l_sup]
    outliers = [c for c in commits if (c.additions + c.deletions) > l_sup]

    return validos, outliers
