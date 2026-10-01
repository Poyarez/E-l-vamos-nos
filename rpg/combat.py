"""Combate: escolas de dano (elementos) e a regra de fraquezas/resistências.

Inspirado em WoW Classic (escolas de magia) e em Sea of Stars (explorar fraquezas
elementares é a chave de cada luta). Hoje estes dados já aparecem no grimório das
classes; o motor de combate por turnos é construído sobre eles na próxima etapa.
"""

from __future__ import annotations

from typing import Iterable

from . import ui

ELEMENTS = {
    "fisico": {"name": "Físico", "color": "white"},
    "fogo": {"name": "Fogo", "color": "bright_red"},
    "gelo": {"name": "Gelo", "color": "bright_cyan"},
    "arcano": {"name": "Arcano", "color": "bright_magenta"},
    "sagrado": {"name": "Sagrado", "color": "bright_yellow"},
    "sombra": {"name": "Sombra", "color": "magenta"},
    "natureza": {"name": "Natureza", "color": "bright_green"},
}

WEAKNESS_MULTIPLIER = 1.5
RESISTANCE_MULTIPLIER = 0.5


def element_multiplier(element: str, weaknesses: Iterable[str] = (), resistances: Iterable[str] = (),
                       immunities: Iterable[str] = ()) -> float:
    """Multiplicador de dano de um elemento contra um alvo.

    Imunidade anula o dano; fraqueza e resistência ao mesmo elemento se cancelam.
    """
    if element not in ELEMENTS:
        raise KeyError(f"Elemento desconhecido: {element!r}")
    if element in set(immunities):
        return 0.0
    weak = element in set(weaknesses)
    resistant = element in set(resistances)
    if weak and not resistant:
        return WEAKNESS_MULTIPLIER
    if resistant and not weak:
        return RESISTANCE_MULTIPLIER
    return 1.0


def element_label(element: str) -> str:
    data = ELEMENTS[element]
    return ui.style(data["name"], data["color"])
