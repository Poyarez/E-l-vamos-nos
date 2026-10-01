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
from .conditions import as_list, conditions_met, item_pairs
from .data.npcs import NPCS
from .utils import format_money, normalize

if TYPE_CHECKING:  # evita importação circular em tempo de execução
    from .player import Player
    from .session import GameSession
    from .state import GameState

Coord = Tuple[int, int]

EFFECT_KEYS = {"set_flag", "journal", "xp", "give_item", "take_item", "give_copper", "take_copper", "restore",
               "open_shop", "start_quest", "reset_talents"}

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
    shop: Optional[str] = None       # loja aberta pelo comando 'comerciar'

    def location(self, period: str, state: Optional["GameState"] = None) -> Optional[Tuple[str, Coord]]:
        """Mapa e coordenadas do NPC neste período do dia (``None`` = fora de cena).

        Regras com ``if`` só valem quando as condições batem (NPCs ocultos, que aparecem
        depois de algum acontecimento ou só em certas noites); sem ``state``, são ignoradas.
        Uma regra pode levar o NPC a outro mapa com ``"map"``.
        """
        for rule in self.schedule:
            if "periods" in rule and period not in rule["periods"]:
                continue
            if rule.get("if") and (state is None or not conditions_met(rule["if"], state)):
                continue
            return rule.get("map", self.map_id), (rule["x"], rule["y"])
        return None

    def position(self, period: str, state: Optional["GameState"] = None,
                 map_id: Optional[str] = None) -> Optional[Coord]:
        """Coordenadas do NPC (só se ele estiver no mapa ``map_id``, quando informado)."""
        found = self.location(period, state)
        if found is None or (map_id is not None and found[0] != map_id):
            return None
        return found[1]


_cache: Dict[str, NPC] = {}


def get_npc(npc_id: str) -> NPC:
    """Fábrica de NPCs (com cache)."""
    if npc_id not in _cache:
        data = NPCS[npc_id]
        _cache[npc_id] = NPC(npc_id, data["name"], data["short"], data["title"], data["color"],
                             data["description"], data["map"], list(data.get("schedule", [])),
                             dict(data["dialogue"]), data.get("shop"))
    return _cache[npc_id]


def all_npcs() -> List[NPC]:
    return [get_npc(npc_id) for npc_id in NPCS]


def npcs_at(state: "GameState", map_id: str, x: int, y: int) -> List[NPC]:
    period = state.clock.period
    return [npc for npc in all_npcs() if npc.position(period, state, map_id) == (x, y)]


def npc_positions(state: "GameState", map_id: str) -> Dict[Coord, List[NPC]]:
    positions: Dict[Coord, List[NPC]] = {}
    period = state.clock.period
    for npc in all_npcs():
        pos = npc.position(period, state, map_id)
        if pos is not None:
            positions.setdefault(pos, []).append(npc)
    return positions


# --------------------------------------------------------------------------- condições e efeitos

def apply_effects(effects: Optional[Mapping[str, Any]], session: "GameSession") -> None:
    if not effects:
        return
    unknown = set(effects) - EFFECT_KEYS
    if unknown:
        raise KeyError(f"Efeito de diálogo desconhecido: {sorted(unknown)}")
    for flag in as_list(effects.get("set_flag", [])):
        session.state.flags[flag] = True
    for entry in as_list(effects.get("journal", [])):
        session.add_journal(entry["id"], entry["title"], entry["text"])
    for item_id, quantity in item_pairs(effects.get("give_item")):
        session.give_item(item_id, quantity)
    for item_id, quantity in item_pairs(effects.get("take_item")):
        session.player.inventory.remove(item_id, quantity)
    if "give_copper" in effects:
        session.give_copper(int(effects["give_copper"]))
    if "take_copper" in effects:
        amount = min(session.player.copper, int(effects["take_copper"]))
        session.player.copper -= amount
        session.notify(ui.style(f"Você paga {format_money(amount)}.", "gray"))
    if effects.get("reset_talents"):
        refunded = session.player.reset_talents()
        points = "1 ponto volta" if refunded == 1 else f"{refunded} pontos voltam"
        session.notify(ui.style(f"Seus talentos foram esquecidos: {points} para você gastar de novo.",
                                "bright_cyan"))
    if "start_quest" in effects:
        session.start_quest(effects["start_quest"])
    if "xp" in effects:
        session.notify(ui.style(f"{ui.sym('star')} Conhecimento adquirido! (+{effects['xp']} XP)", "bright_magenta"))
        session.gain_xp(int(effects["xp"]), "conhecimento")
    if effects.get("restore"):
        session.player.restore()
        session.notify(ui.style("Sua vida e seu vigor foram restaurados.", "bright_green"))
    if effects.get("open_shop"):
        session.pending_shop = True


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
