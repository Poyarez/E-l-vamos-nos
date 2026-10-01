"""NPCs: fábrica a partir de ``rpg.data.npcs``, agenda diária e o motor de diálogos.

O motor é dirigido por dados: condições (``if``) escondem falas e opções, e efeitos
(``effects``) ativam flags, anotam pistas no diário e concedem recompensas. As
missões das próximas etapas reutilizam exatamente esse mecanismo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence, Tuple

from . import ui
from .data.appearance import ALIGNMENTS
from .data.npcs import NPCS
from .utils import normalize

if TYPE_CHECKING:  # evita importação circular em tempo de execução
    from .player import Player
    from .session import GameSession
    from .state import GameState

Coord = Tuple[int, int]

CONDITION_KEYS = {"flag", "not_flag", "journal", "discovered", "class", "moral", "law", "period", "night",
                  "met", "min_level"}
EFFECT_KEYS = {"set_flag", "journal", "xp", "give_item", "give_copper", "restore"}

_NARRATION_RE = re.compile(r"\*(.+?)\*")


@dataclass
class NPC:
    id: str
    name: str
    short: str
    title: str
    color: str
    description: str
    map_id: str
    schedule: List[Dict[str, Any]] = field(default_factory=list)
    dialogue: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def position(self, period: str) -> Optional[Coord]:
        """Onde o NPC está neste período do dia (``None`` = fora do mapa)."""
        for rule in self.schedule:
            if "periods" not in rule or period in rule["periods"]:
                return (rule["x"], rule["y"])
        return None


_cache: Dict[str, NPC] = {}


def get_npc(npc_id: str) -> NPC:
    """Fábrica de NPCs (com cache)."""
    if npc_id not in _cache:
        data = NPCS[npc_id]
        _cache[npc_id] = NPC(npc_id, data["name"], data["short"], data["title"], data["color"],
                             data["description"], data["map"], list(data.get("schedule", [])),
                             dict(data["dialogue"]))
    return _cache[npc_id]


def all_npcs() -> List[NPC]:
    return [get_npc(npc_id) for npc_id in NPCS]


def npcs_at(state: "GameState", map_id: str, x: int, y: int) -> List[NPC]:
    period = state.clock.period
    return [npc for npc in all_npcs() if npc.map_id == map_id and npc.position(period) == (x, y)]


def npc_positions(state: "GameState", map_id: str) -> Dict[Coord, List[NPC]]:
    positions: Dict[Coord, List[NPC]] = {}
    period = state.clock.period
    for npc in all_npcs():
        pos = npc.position(period) if npc.map_id == map_id else None
        if pos is not None:
            positions.setdefault(pos, []).append(npc)
    return positions


# --------------------------------------------------------------------------- condições e efeitos

def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, (list, tuple)) else [value]


def conditions_met(conditions: Optional[Mapping[str, Any]], state: "GameState", met: bool = False) -> bool:
    """Avalia um bloco ``if``. ``met`` indica se o herói já conhecia o NPC antes desta conversa."""
    if not conditions:
        return True
    player = state.player
    alignment = ALIGNMENTS[player.alignment]
    for key, value in conditions.items():
        if key == "flag":
            ok = all(state.has_flag(flag) for flag in _as_list(value))
        elif key == "not_flag":
            ok = not any(state.has_flag(flag) for flag in _as_list(value))
        elif key == "journal":
            known = {entry.id for entry in state.journal}
            ok = all(entry_id in known for entry_id in _as_list(value))
        elif key == "discovered":
            ok = all(landmark in state.discovered for landmark in _as_list(value))
        elif key == "class":
            ok = player.class_id in _as_list(value)
        elif key == "moral":
            ok = alignment["moral"] in _as_list(value)
        elif key == "law":
            ok = alignment["law"] in _as_list(value)
        elif key == "period":
            ok = state.clock.period in _as_list(value)
        elif key == "night":
            ok = state.clock.is_night == bool(value)
        elif key == "met":
            ok = met == bool(value)
        elif key == "min_level":
            ok = player.level >= int(value)
        else:
            raise KeyError(f"Condição de diálogo desconhecida: {key!r}")
        if not ok:
            return False
    return True


def apply_effects(effects: Optional[Mapping[str, Any]], session: "GameSession") -> None:
    if not effects:
        return
    unknown = set(effects) - EFFECT_KEYS
    if unknown:
        raise KeyError(f"Efeito de diálogo desconhecido: {sorted(unknown)}")
    for flag in _as_list(effects.get("set_flag", [])):
        session.state.flags[flag] = True
    for entry in _as_list(effects.get("journal", [])):
        session.add_journal(entry["id"], entry["title"], entry["text"])
    if "give_item" in effects:
        item_id, quantity = effects["give_item"]
        session.give_item(item_id, quantity)
    if "give_copper" in effects:
        session.give_copper(int(effects["give_copper"]))
    if "xp" in effects:
        session.notify(ui.style(f"{ui.sym('star')} Conhecimento adquirido! (+{effects['xp']} XP)", "bright_magenta"))
        session.gain_xp(int(effects["xp"]), "conhecimento")
    if effects.get("restore"):
        session.player.restore()
        session.notify(ui.style("Sua vida e seu vigor foram restaurados.", "bright_green"))


# --------------------------------------------------------------------------- texto

class _Forms(dict):
    """Dicionário de marcadores que mantém intactos os marcadores desconhecidos."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def format_text(text: str, player: "Player") -> str:
    return text.format_map(_Forms(player.forms))


def node_lines(node: Mapping[str, Any], state: "GameState", met: bool) -> List[str]:
    lines = []
    for entry in node.get("text", []):
        if isinstance(entry, str):
            lines.append(entry)
        elif conditions_met(entry.get("if"), state, met):
            lines.append(entry["text"])
    return lines


def node_options(node: Mapping[str, Any], state: "GameState", met: bool) -> List[Dict[str, Any]]:
    return [option for option in node.get("options", []) if conditions_met(option.get("if"), state, met)]


def render_line(npc: NPC, text: str, player: "Player", width: int) -> List[str]:
    """Falas vêm precedidas pelo nome do NPC; trechos entre *asteriscos* viram narração própria."""
    rows: List[str] = []
    prefix = f"{npc.short} {ui.sym('arrow')} "
    for index, segment in enumerate(_NARRATION_RE.split(format_text(text, player).strip())):
        segment = segment.strip()
        if not segment:
            continue
        if index % 2:   # os grupos capturados (posições ímpares) são narração
            rows.extend(ui.wrap(ui.style(segment, "gray italic"), width, "  "))
            continue
        speech = ui.wrap(segment, width - len(prefix) - 2)
        rows.append("  " + ui.style(prefix, npc.color + " bold") + speech[0])
        rows.extend("  " + " " * len(prefix) + row for row in speech[1:])
    return rows


def _header(npc: NPC) -> None:
    width = min(ui.term_width(), 100)
    title = ui.style(npc.name, npc.color + " bold") + ui.style(f" {ui.sym('dot')} {npc.title}", "gray")
    ui.echo_lines(ui.box(ui.wrap(ui.style(npc.description, "italic"), width - 4), width, title=title))
    ui.echo()


def run_dialogue(session: "GameSession", npc: NPC) -> None:
    """Conduz uma conversa completa com ``npc``."""
    state = session.state
    met_before = npc.id in state.met
    state.met.add(npc.id)
    session.dirty = True
    width = min(ui.term_width(), 100) - 2
    shown = set()
    node_id: Optional[str] = "inicio"
    ui.clear()
    _header(npc)
    while node_id is not None:
        node = npc.dialogue[node_id]
        if node_id not in shown:
            shown.add(node_id)
            for line in node_lines(node, state, met_before):
                ui.echo_lines(render_line(npc, line, state.player, width))
                ui.echo()
            apply_effects(node.get("effects"), session)
            state.flags[f"visto:{npc.id}:{node_id}"] = True
            messages = session.pop_messages()
            for message in messages:
                ui.echo_lines(ui.wrap(message, width, "  "))
            if messages:
                ui.echo()
        if "options" not in node:
            next_id = node.get("next")
            if next_id is None:
                ui.pause()
            node_id = next_id
            continue
        options = node_options(node, state, met_before)
        if not options:
            ui.pause()
            break
        labels = []
        for option in options:
            seen = option["next"] is not None and state.has_flag(f"visto:{npc.id}:{option['next']}")
            labels.append(ui.style(option["text"], "gray") if seen else option["text"])
        choice = ui.choose(labels, prompt="Responder")
        option = options[choice if choice is not None else -1]
        apply_effects(option.get("effects"), session)
        node_id = option["next"]
        if node_id is not None:
            ui.clear()
            _header(npc)


def choose_npc(candidates: Sequence[NPC], name_hint: str) -> Optional[NPC]:
    """Escolhe com quem falar: pelo nome digitado ou, se houver só um, automaticamente."""
    if name_hint:
        key = normalize(name_hint)
        matches = [npc for npc in candidates
                   if key in normalize(npc.name) or normalize(npc.short).startswith(key)]
        return matches[0] if len(matches) == 1 else None
    if len(candidates) == 1:
        return candidates[0]
    return None
