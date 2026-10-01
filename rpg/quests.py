"""Missões e o quadro de avisos.

**Missões** (``rpg.data.quests``) têm etapas em ordem. Cada etapa tem um objetivo
(``goal``): um bloco de condições de ``rpg.conditions`` (flags, itens, locais, perícias...)
e/ou ``kill`` — derrotar ``count`` criaturas de ``monsters`` depois que a etapa começou.
Uma missão começa por um efeito de diálogo (``start_quest``) ou sozinha, quando as
condições de ``start`` ficam verdadeiras. A cada ação do jogador, ``update`` avança as
etapas cumpridas e, ao fim, entrega as recompensas.

**Quadro de avisos** (``BOUNTIES``): todo dia, o quadro da Praça do Poço oferece três
tarefas — caçadas e encomendas para as perícias — sorteadas entre as que combinam com o
nível do herói (``min_level``/``max_level``) e com a história (``if``). Aceite com
``avisos``, cumpra e volte ao quadro para receber; cada tarefa só pode ser feita uma vez
por dia.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple

from . import ui
from .conditions import as_list, conditions_met, item_pairs
from .data.monsters import MONSTERS
from .data.quests import BOUNTIES, QUESTS
from .items import get_item, item_name
from .player import MAX_LEVEL
from .utils import format_money, stable_hash

if TYPE_CHECKING:
    from .session import GameSession
    from .state import GameState

BOARD_LANDMARK = "praca_poco"
BOARD_SIZE = 3
MAX_ACTIVE_BOUNTIES = 3
CATEGORIES = {"principal": "Missão principal", "secundaria": "Missão secundária"}


# --------------------------------------------------------------------------- missões

def get_quest(quest_id: str) -> Dict[str, Any]:
    try:
        return QUESTS[quest_id]
    except KeyError:
        raise KeyError(f"Missão desconhecida: {quest_id!r}") from None


def entry(state: "GameState", quest_id: str) -> Optional[Dict[str, Any]]:
    return state.quests.get(quest_id)


def is_active(state: "GameState", quest_id: str) -> bool:
    found = entry(state, quest_id)
    return bool(found) and not found["done"]


def is_done(state: "GameState", quest_id: str) -> bool:
    found = entry(state, quest_id)
    return bool(found) and found["done"]


def active(state: "GameState") -> List[str]:
    order = list(QUESTS)
    ids = [quest_id for quest_id, data in state.quests.items() if not data["done"] and quest_id in QUESTS]
    return sorted(ids, key=lambda quest_id: (QUESTS[quest_id]["category"] != "principal", order.index(quest_id)))


def completed(state: "GameState") -> List[str]:
    return [quest_id for quest_id, data in state.quests.items() if data["done"] and quest_id in QUESTS]


def start(state: "GameState", quest_id: str) -> bool:
    """Começa a missão (se ainda não começou). Devolve ``True`` se começou agora."""
    get_quest(quest_id)
    if quest_id in state.quests:
        return False
    state.quests[quest_id] = {"stage": 0, "kills": 0, "done": False, "day": state.clock.day}
    return True


def current_stage(quest_id: str, data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    stages = get_quest(quest_id)["stages"]
    return stages[data["stage"]] if data["stage"] < len(stages) else None


def _goal_met(goal: Mapping[str, Any], state: "GameState", kills: int) -> bool:
    conditions = {key: value for key, value in goal.items() if key != "kill"}
    if not conditions_met(conditions, state):
        return False
    hunt = goal.get("kill")
    return not hunt or kills >= hunt["count"]


def goal_items(goal: Mapping[str, Any]) -> List[Tuple[str, int]]:
    """Os itens que um objetivo pede (também dentro de ``any``, nas entregas com plano B)."""
    if "item" in goal:
        return item_pairs(goal["item"])
    for block in goal.get("any", []):
        if "item" in block:
            return item_pairs(block["item"])
    return []


def progress_text(state: "GameState", quest_id: str) -> str:
    """O progresso visível da etapa atual: "Lobos Cinzentos: 3/6" ou "Pele de Lobo: 2/5"."""
    data = entry(state, quest_id)
    stage = current_stage(quest_id, data) if data else None
    if stage is None:
        return ""
    parts = []
    hunt = stage["goal"].get("kill")
    if hunt:
        names = " ou ".join(MONSTERS[monster]["name"] for monster in hunt["monsters"])
        parts.append(f"{names}: {min(data['kills'], hunt['count'])}/{hunt['count']}")
    pairs = goal_items(stage["goal"])
    for item_id, quantity in pairs:
        if quantity > 1 or len(pairs) > 1:
            have = min(state.player.inventory.count(item_id), quantity)
            parts.append(f"{get_item(item_id)['name']}: {have}/{quantity}")
    return " · ".join(parts)


def record_kill(state: "GameState", template_id: str) -> None:
    """Conta uma criatura derrotada para as missões e tarefas que pedem caçadas."""
    for quest_id, data in state.quests.items():
        if data["done"] or quest_id not in QUESTS:
            continue
        stage = current_stage(quest_id, data)
        hunt = stage and stage["goal"].get("kill")
        if hunt and template_id in hunt["monsters"]:
            data["kills"] += 1
    board = state.bounties
    for bounty_id, data in board.get("active", {}).items():
        bounty = BOUNTIES.get(bounty_id)
        hunt = bounty and bounty["goal"].get("kill")
        if hunt and template_id in hunt["monsters"]:
            data["kills"] += 1


def update(session: "GameSession") -> None:
    """Começa as missões automáticas e avança as etapas cumpridas (com recompensas no fim)."""
    state = session.state
    for quest_id, quest in QUESTS.items():
        if quest_id not in state.quests and quest.get("start") and conditions_met(quest["start"], state):
            session.start_quest(quest_id)
    for quest_id in list(state.quests):
        data = state.quests[quest_id]
        if data["done"] or quest_id not in QUESTS:
            continue
        quest = QUESTS[quest_id]
        while not data["done"]:
            stage = current_stage(quest_id, data)
            if stage is None or not _goal_met(stage["goal"], state, data["kills"]):
                break
            last = data["stage"] + 1 >= len(quest["stages"])
            if last and not state.player.inventory.room_for(reward_items(quest_id, state.player.class_id)):
                if quest_id not in session.reward_warnings:   # avisa uma vez, e espera haver espaço
                    session.reward_warnings.add(quest_id)
                    session.notify(ui.style(f"Sua mochila está cheia: abra espaço para receber a recompensa de "
                                            f"\"{quest['name']}\".", "red"))
                break
            for item_id, quantity in item_pairs(stage.get("take_item")):
                state.player.inventory.remove(item_id, quantity)
            data["stage"] += 1
            data["kills"] = 0
            if last:
                data["done"] = True
                _complete(session, quest_id)
            else:
                following = quest["stages"][data["stage"]]
                session.notify(ui.style(f"{ui.sym('star')} Missão atualizada — {quest['name']}: ", "bright_cyan bold")
                               + following["text"])


def _complete(session: "GameSession", quest_id: str) -> None:
    quest = get_quest(quest_id)
    rewards = quest.get("rewards", {})
    session.notify(ui.style(f"{ui.sym('star')} Missão concluída: {quest['name']}!", "bright_yellow bold"))
    if quest.get("ending"):
        session.notify(ui.style(quest["ending"], "italic"))
    for flag in as_list(rewards.get("set_flag", [])):
        session.state.flags[flag] = True
    for item_id, quantity in reward_items(quest_id, session.player.class_id):
        session.give_item(item_id, quantity)
    if rewards.get("copper"):
        session.give_copper(int(rewards["copper"]))
    if rewards.get("xp"):
        session.notify(ui.style(f"+{rewards['xp']} XP", "bright_magenta"))
        session.gain_xp(int(rewards["xp"]), "missão")
    journal = rewards.get("journal")
    if journal:
        session.add_journal(journal["id"], journal["title"], journal["text"], "missão")


def reward_items(quest_id: str, class_id: Optional[str] = None) -> List[Tuple[str, int]]:
    """Itens da recompensa: os de todos mais os da classe do herói (``class_items``)."""
    rewards = get_quest(quest_id).get("rewards", {})
    pairs = item_pairs(rewards.get("items"))
    if class_id:
        pairs += item_pairs(rewards.get("class_items", {}).get(class_id))
    return pairs


def quest_reward_text(quest_id: str, class_id: Optional[str] = None) -> str:
    rewards = get_quest(quest_id).get("rewards", {})
    parts = []
    if rewards.get("xp"):
        parts.append(f"{rewards['xp']} XP")
    if rewards.get("copper"):
        parts.append(format_money(int(rewards["copper"])))
    parts += [item_name(item_id, colored=False) + (f" x{quantity}" if quantity > 1 else "")
              for item_id, quantity in reward_items(quest_id, class_id)]
    if rewards.get("class_items") and not class_id:
        parts.append("um item para a sua classe")
    return ", ".join(parts)


# --------------------------------------------------------------------------- quadro de avisos

def _board(state: "GameState") -> Dict[str, Any]:
    """O quadro do dia (renova as ofertas quando o dia muda; as tarefas aceitas continuam)."""
    board = state.bounties
    if board.get("day") != state.clock.day:
        level = state.player.level
        pool = sorted(bounty_id for bounty_id, bounty in BOUNTIES.items()
                      if bounty.get("min_level", 1) <= level <= bounty.get("max_level", MAX_LEVEL)
                      and conditions_met(bounty.get("if"), state))
        pool.sort(key=lambda bounty_id: stable_hash(state.clock.seed, state.clock.day, bounty_id))
        board["day"] = state.clock.day
        board["offers"] = pool[:BOARD_SIZE]
        board["done"] = []
        board.setdefault("active", {})
    return board


def offers(state: "GameState") -> List[str]:
    return list(_board(state)["offers"])


def active_bounties(state: "GameState") -> List[str]:
    return [bounty_id for bounty_id in _board(state).get("active", {}) if bounty_id in BOUNTIES]


def bounty_status(state: "GameState", bounty_id: str) -> str:
    """"aceita", "pronta" (pode entregar), "feita" (hoje) ou "livre"."""
    board = _board(state)
    if bounty_id in board["done"]:
        return "feita"
    if bounty_id in board.get("active", {}):
        return "pronta" if bounty_ready(state, bounty_id) else "aceita"
    return "livre"


def bounty_ready(state: "GameState", bounty_id: str) -> bool:
    goal = BOUNTIES[bounty_id]["goal"]
    data = _board(state)["active"].get(bounty_id, {"kills": 0})
    hunt = goal.get("kill")
    if hunt and data["kills"] < hunt["count"]:
        return False
    return all(state.player.inventory.count(item_id) >= quantity
               for item_id, quantity in item_pairs(goal.get("deliver")))


def bounty_progress(state: "GameState", bounty_id: str) -> str:
    goal = BOUNTIES[bounty_id]["goal"]
    data = _board(state)["active"].get(bounty_id, {"kills": 0})
    parts = []
    hunt = goal.get("kill")
    if hunt:
        parts.append(f"{min(data['kills'], hunt['count'])}/{hunt['count']}")
    for item_id, quantity in item_pairs(goal.get("deliver")):
        parts.append(f"{get_item(item_id)['name']} {min(state.player.inventory.count(item_id), quantity)}/{quantity}")
    return " · ".join(parts)


def accept_bounty(state: "GameState", bounty_id: str) -> Optional[str]:
    """Aceita uma tarefa do quadro; devolve o motivo se não der."""
    board = _board(state)
    if bounty_id not in board["offers"]:
        return "Essa tarefa não está no quadro hoje."
    status = bounty_status(state, bounty_id)
    if status == "feita":
        return "Você já cumpriu essa tarefa hoje. Volte amanhã."
    if status != "livre":
        return "Você já aceitou essa tarefa."
    if len(board["active"]) >= MAX_ACTIVE_BOUNTIES:
        return f"Você já tem {MAX_ACTIVE_BOUNTIES} tarefas aceitas. Entregue alguma antes."
    board["active"][bounty_id] = {"kills": 0}
    return None


def abandon_bounty(state: "GameState", bounty_id: str) -> bool:
    """Desiste de uma tarefa aceita (sem recompensa; se ainda estiver no quadro, pode ser aceita de novo)."""
    board = _board(state)
    return board.get("active", {}).pop(bounty_id, None) is not None


def turn_in_bounty(session: "GameSession", bounty_id: str) -> bool:
    state = session.state
    board = _board(state)
    if bounty_id not in board.get("active", {}) or not bounty_ready(state, bounty_id):
        return False
    bounty = BOUNTIES[bounty_id]
    for item_id, quantity in item_pairs(bounty["goal"].get("deliver")):
        state.player.inventory.remove(item_id, quantity)
    del board["active"][bounty_id]
    if bounty_id in board["offers"]:
        board["done"].append(bounty_id)
    state.stats["tarefas"] = state.stats.get("tarefas", 0) + 1
    reward = bounty["reward"]
    session.notify(ui.style(f"{ui.sym('check')} Tarefa cumprida: {bounty['name']}", "bright_green bold"))
    if reward.get("copper"):
        session.give_copper(int(reward["copper"]))
    for item_id, quantity in item_pairs(reward.get("items")):
        session.give_item(item_id, quantity)
    if reward.get("xp"):
        session.notify(ui.style(f"+{reward['xp']} XP", "bright_magenta"))
        session.gain_xp(int(reward["xp"]), "tarefa")
    return True


def bounty_reward_text(bounty_id: str) -> str:
    reward = BOUNTIES[bounty_id]["reward"]
    parts = [f"{reward['xp']} XP"] if reward.get("xp") else []
    if reward.get("copper"):
        parts.append(format_money(int(reward["copper"])))
    parts += [item_name(item_id, colored=False) + (f" x{quantity}" if quantity > 1 else "")
              for item_id, quantity in item_pairs(reward.get("items"))]
    return ", ".join(parts)


def describe_goal(goal: Mapping[str, Any]) -> Tuple[str, ...]:
    """Partes legíveis de um objetivo de tarefa (para o quadro)."""
    parts = []
    hunt = goal.get("kill")
    if hunt:
        names = " ou ".join(MONSTERS[monster]["name"] for monster in hunt["monsters"])
        parts.append(f"derrotar {hunt['count']}: {names}")
    for item_id, quantity in item_pairs(goal.get("deliver")):
        parts.append(f"entregar {quantity} {get_item(item_id)['name']}")
    return tuple(parts)
