"""Perícias de coleta e produção com a curva de experiência clássica do OSRS (níveis 1 a 99).

A experiência total para o nível ``L`` é::

    floor( 1/4 * soma_{n=1}^{L-1} floor(n + 300 * 2^(n/7)) )

o que dá 83 XP para o nível 2 e 13.034.431 XP para o nível 99.
"""

from __future__ import annotations

import bisect
import math
from typing import Dict, List, Mapping, Optional, Tuple

from .data.skills import SKILLS

MAX_SKILL_LEVEL = 99
MAX_SKILL_XP = 200_000_000


def _build_xp_table() -> List[int]:
    table = [0, 0]   # índice = nível; o nível 1 começa com 0 XP
    points = 0
    for level in range(1, MAX_SKILL_LEVEL):
        points += math.floor(level + 300 * 2 ** (level / 7))
        table.append(points // 4)
    return table


#: ``XP_TABLE[nível]`` = experiência total necessária para alcançar o nível (1..99).
XP_TABLE: List[int] = _build_xp_table()


def xp_for_level(level: int) -> int:
    level = max(1, min(MAX_SKILL_LEVEL, level))
    return XP_TABLE[level]


def level_for_xp(xp: int) -> int:
    return max(1, min(MAX_SKILL_LEVEL, bisect.bisect_right(XP_TABLE, xp) - 1))


def level_progress(xp: int) -> Tuple[int, int, int]:
    """Devolve (nível, XP dentro do nível, XP que o nível exige). No 99, a barra fica cheia."""
    level = level_for_xp(xp)
    if level >= MAX_SKILL_LEVEL:
        return level, 1, 1
    start = XP_TABLE[level]
    return level, xp - start, XP_TABLE[level + 1] - start


class SkillSet:
    """A experiência acumulada em cada perícia."""

    def __init__(self, xp: Optional[Mapping[str, int]] = None) -> None:
        self.xp: Dict[str, int] = {skill_id: 0 for skill_id in SKILLS}
        for skill_id, amount in (xp or {}).items():
            if skill_id in self.xp:   # perícias removidas de versões antigas são ignoradas
                self.xp[skill_id] = max(0, min(MAX_SKILL_XP, int(amount)))

    def level(self, skill_id: str) -> int:
        return level_for_xp(self.xp[skill_id])

    def add_xp(self, skill_id: str, amount: int) -> int:
        """Soma experiência e devolve quantos níveis foram ganhos."""
        before = self.level(skill_id)
        self.xp[skill_id] = min(MAX_SKILL_XP, self.xp[skill_id] + max(0, int(amount)))
        return self.level(skill_id) - before

    def total_level(self) -> int:
        return sum(self.level(skill_id) for skill_id in self.xp)

    def to_dict(self) -> Dict[str, int]:
        return dict(self.xp)

    @classmethod
    def from_dict(cls, data: Optional[Mapping[str, int]]) -> "SkillSet":
        return cls(data)
