"""Condições declarativas usadas pelos dados do jogo (diálogos, encontros, passagens...).

Um bloco de condições é um dicionário em que todas as chaves precisam ser verdadeiras:

* ``flag`` / ``not_flag`` — marcos de história ativos ou não;
* ``journal`` — anotações presentes no diário;
* ``discovered`` — locais já visitados;
* ``class``, ``moral``, ``law`` — classe e eixos do alinhamento do herói;
* ``period``, ``night`` — hora do dia;
* ``min_level`` — nível mínimo do herói;
* ``item`` — ter um item na mochila: ``"barra_bronze"`` ou ``["rabo_rato", 5]``;
* ``skill`` — níveis mínimos de perícia: ``{"mineracao": 15}``;
* ``met`` — (só em diálogos) se o herói já conhecia o NPC antes da conversa.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Tuple

from .data.appearance import ALIGNMENTS

if TYPE_CHECKING:
    from .state import GameState

CONDITION_KEYS = {"flag", "not_flag", "journal", "discovered", "class", "moral", "law", "period", "night",
                  "met", "min_level", "item", "skill"}


def as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, (list, tuple)) else [value]


def item_requirement(value: Any) -> Tuple[str, int]:
    """``"pao"`` ou ``["pao", 3]`` -> ``("pao", 3)``."""
    if isinstance(value, (list, tuple)):
        return str(value[0]), int(value[1])
    return str(value), 1


def item_pairs(value: Any) -> List[Tuple[str, int]]:
    """``["pao", 2]`` ou ``[["pao", 2], ["agua", 1]]`` -> lista de pares (vazia sem valor)."""
    if not value:
        return []
    if isinstance(value[0], (list, tuple)):
        return [item_requirement(entry) for entry in value]
    return [item_requirement(value)]


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
        elif key == "item":
            item_id, quantity = item_requirement(value)
            ok = player.inventory.count(item_id) >= quantity
        elif key == "skill":
            ok = all(player.skills.level(skill_id) >= int(level) for skill_id, level in value.items())
        else:
            raise KeyError(f"Condição desconhecida: {key!r}")
        if not ok:
            return False
    return True
