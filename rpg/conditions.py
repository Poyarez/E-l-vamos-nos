"""Condições declarativas usadas pelos dados do jogo (diálogos, encontros, passagens...).

Um bloco de condições é um dicionário em que todas as chaves precisam ser verdadeiras:

* ``flag`` / ``not_flag`` — marcos de história ativos ou não;
* ``journal`` — anotações presentes no diário;
* ``discovered`` — locais já visitados;
* ``class``, ``moral``, ``law`` — classe e eixos do alinhamento do herói;
* ``period``, ``night`` — hora do dia;
* ``min_level`` — nível mínimo do herói;
* ``met`` — (só em diálogos) se o herói já conhecia o NPC antes da conversa.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Mapping, Optional

from .data.appearance import ALIGNMENTS

if TYPE_CHECKING:
    from .state import GameState

CONDITION_KEYS = {"flag", "not_flag", "journal", "discovered", "class", "moral", "law", "period", "night",
                  "met", "min_level"}


def as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, (list, tuple)) else [value]


def conditions_met(conditions: Optional[Mapping[str, Any]], state: "GameState", met: bool = False) -> bool:
    """Avalia um bloco ``if``. ``met`` indica se o herói já conhecia o NPC (diálogos)."""
    if not conditions:
        return True
    player = state.player
    alignment = ALIGNMENTS[player.alignment]
    for key, value in conditions.items():
        if key == "flag":
            ok = all(state.has_flag(flag) for flag in as_list(value))
        elif key == "not_flag":
            ok = not any(state.has_flag(flag) for flag in as_list(value))
        elif key == "journal":
            known = {entry.id for entry in state.journal}
            ok = all(entry_id in known for entry_id in as_list(value))
        elif key == "discovered":
            ok = all(landmark in state.discovered for landmark in as_list(value))
        elif key == "class":
            ok = player.class_id in as_list(value)
        elif key == "moral":
            ok = alignment["moral"] in as_list(value)
        elif key == "law":
            ok = alignment["law"] in as_list(value)
        elif key == "period":
            ok = state.clock.period in as_list(value)
        elif key == "night":
            ok = state.clock.is_night == bool(value)
        elif key == "met":
            ok = met == bool(value)
        elif key == "min_level":
            ok = player.level >= int(value)
        else:
            raise KeyError(f"Condição desconhecida: {key!r}")
        if not ok:
            return False
    return True
