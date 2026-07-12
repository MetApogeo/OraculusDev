from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CommitData:
    sha: str
    mensaje: str
    additions: int = 0
    deletions: int = 0

def aplicar_tope(loc: int, loc_por_hora: float) -> int:
    tope = int(8 * loc_por_hora)
    return min(loc, tope)

def realizar_calculos(commit: CommitData, salario: float, horas_mes: int, loc_por_hora: float = 60.0) -> Tuple[float, float]:
    costo_hora = salario / horas_mes
    loc_commit = commit.additions + commit.deletions

    loc_limpio = aplicar_tope(loc_commit, loc_por_hora)

    t_horas = loc_limpio / loc_por_hora
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

def medir_cc_codigo(code: str) -> float:
    from radon.complexity import cc_visit
    if not code.strip():
        return 0.0
    try:
        blocks = cc_visit(code)
        if not blocks:
            return 0.0
        return sum(b.complexity for b in blocks) / len(blocks)
    except Exception:
        return 0.0

def calcular_delta_calidad(cc_antes: float, cc_despues: float, 
                           loc_antes: int, loc_despues: int) -> str:
    if loc_antes == 0:
        return "FEATURE_LIMPIA"
        
    delta_cc = cc_despues - cc_antes
    delta_loc = loc_despues - loc_antes
    
    if delta_loc < 0 and delta_cc < 0:
        return "OPTIMIZACION"
    elif delta_loc > 0 and delta_cc <= 0:
        return "FEATURE_LIMPIA"
    elif delta_loc > 0 and delta_cc > 0:
        return "DEUDA_TECNICA"
    else:
        return "NEUTRAL"

def estimar_costo_deuda(commits_deuda: list) -> float:
    # La deuda técnica típicamente cuesta 3x su costo original en mantenimiento futuro.
    # commits_deuda es una lista de tuplas (commit_data, tiempo_est, costo_est, calidad)
    return sum(item[2] for item in commits_deuda) * 3.0
