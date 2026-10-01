"""Mapas em arte ASCII: o minimapa ao redor do herói e o mapa completo da zona.

Tiles nunca vistos ficam em branco (névoa de guerra); tiles lembrados, mas fora do
alcance da visão atual, aparecem esmaecidos — à noite, o mundo encolhe ao seu redor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from . import ui
from .npcs import NPC, npc_positions

if TYPE_CHECKING:
    from .session import GameSession

Coord = Tuple[int, int]

MARKERS = [
    ("@", "bright_white bold", "você"),
    ("!", "bright_yellow bold", "pessoa"),
    ("*", "bright_magenta bold", "local conhecido"),
    ("?", "bright_white", "algo a explorar"),
]


def _glyph(session: "GameSession", x: int, y: int, people: Dict[Coord, List[NPC]]) -> str:
    state, game_map = session.state, session.map
    if (x, y) == state.pos:
        return ui.style("@", "bright_white bold")
    if (x, y) not in state.explored_on(state.map_id):
        return " "
    if (x, y) in people:
        new_face = any(npc.id not in state.met for npc in people[(x, y)])
        return ui.style("!", "bright_yellow bold" if new_face else "yellow")
    landmark = game_map.landmark_at(x, y)
    if landmark and landmark.id in state.discovered:
        return ui.style("*", "bright_magenta bold")
    if landmark and not landmark.hidden:
        return ui.style("?", "bright_white")
    terrain = game_map.terrain_at(x, y)
    color = terrain.color if (x, y) in session.visible else terrain.color + " dim"
    return ui.style(game_map.char_at(x, y), color)


def minimap(session: "GameSession", half_width: int = 8, half_height: int = 5) -> List[str]:
    """Janela ao redor do herói, com moldura. Cada tile ocupa duas colunas (fica mais "quadrado")."""
    game_map = session.map
    people = npc_positions(session.state, session.state.map_id)
    cx, cy = session.state.pos
    rows = []
    for y in range(cy - half_height, cy + half_height + 1):
        cells = [_glyph(session, x, y, people) if game_map.in_bounds(x, y) else " "
                 for x in range(cx - half_width, cx + half_width + 1)]
        rows.append(" ".join(cells))
    inner = (2 * half_width + 1) * 2 - 1
    return ui.box(rows, inner + 4, title=ui.style(f"{ui.sym('up')} N", "bold"))


def minimap_width(half_width: int = 8) -> int:
    return (2 * half_width + 1) * 2 - 1 + 4


def full_map(session: "GameSession", double: bool) -> List[str]:
    """O mapa inteiro com réguas de coordenadas a cada 10 tiles."""
    game_map = session.map
    people = npc_positions(session.state, session.state.map_id)
    cell = 2 if double else 1
    ruler = [" "] * (game_map.width * cell)
    for x in range(0, game_map.width, 10):
        for offset, digit in enumerate(str(x)):
            if x * cell + offset < len(ruler):
                ruler[x * cell + offset] = digit
    rows = ["    " + ui.style("".join(ruler).rstrip(), "gray")]
    for y in range(game_map.height):
        cells = [_glyph(session, x, y, people) for x in range(game_map.width)]
        rows.append(ui.style(f"{y:>3} ", "gray") + (" " if double else "").join(cells))
    return rows


def legend(session: "GameSession") -> List[str]:
    """Legenda com os terrenos já vistos neste mapa e os marcadores."""
    game_map, state = session.map, session.state
    explored = state.explored_on(state.map_id)
    seen_chars = {game_map.char_at(x, y) for x, y in explored}
    entries = [f"{ui.style(char, color)} {label}" for char, color, label in MARKERS]
    for char, terrain in game_map.legend.items():
        if char in seen_chars:
            entries.append(f"{ui.style(char, terrain.color)} {terrain.name}")
    return entries
