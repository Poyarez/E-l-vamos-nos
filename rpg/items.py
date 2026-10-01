"""Itens: fábrica a partir de ``rpg.data.items``, pilhas, mochila, consumíveis e descrições."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Mapping, Optional, Tuple

from . import ui
from .data.appearance import ARMOR_COLORS
from .data.classes import STATS
from .data.items import ITEM_TYPES, ITEMS, QUALITIES, SLOTS, SUBTYPES
from .utils import format_duration

if TYPE_CHECKING:
    from .player import Player

DEFAULT_BAG_SLOTS = 16


def get_item(item_id: str) -> Dict[str, Any]:
    try:
        return ITEMS[item_id]
    except KeyError:
        raise KeyError(f"Item desconhecido: {item_id!r}") from None


def item_name(item_id: str, dye: Optional[str] = None, colored: bool = True) -> str:
    """Nome do item na cor da sua qualidade, com a tinta (se houver): "Manto (Azul real)"."""
    item = get_item(item_id)
    name = item["name"]
    if dye in ARMOR_COLORS:
        name += f" ({ARMOR_COLORS[dye]['name']})"
    return ui.style(name, QUALITIES[item["quality"]]["color"]) if colored else name


@dataclass
class ItemStack:
    """Uma pilha de itens iguais (mesmo id e mesma tinta)."""

    item_id: str
    quantity: int = 1
    dye: Optional[str] = None

    @property
    def data(self) -> Dict[str, Any]:
        return get_item(self.item_id)

    def name(self, colored: bool = True) -> str:
        return item_name(self.item_id, self.dye, colored)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"id": self.item_id, "qty": self.quantity}
        if self.dye:
            data["dye"] = self.dye
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ItemStack":
        return cls(str(data["id"]), max(1, int(data.get("qty", 1))), data.get("dye"))


def is_quest_item(item_id: str) -> bool:
    """Itens de missão vão num bolso à parte: não ocupam espaço e nunca ficam para trás."""
    return get_item(item_id)["type"] == "missao"


class Inventory:
    """Mochila com número limitado de espaços; itens empilháveis dividem um espaço.

    Itens de missão não contam (ver ``is_quest_item``): uma mochila cheia nunca pode
    travar a história.
    """

    def __init__(self, capacity: int = DEFAULT_BAG_SLOTS, stacks: Optional[List[ItemStack]] = None) -> None:
        self.capacity = capacity
        self.stacks: List[ItemStack] = list(stacks or [])

    def __iter__(self) -> Iterator[ItemStack]:
        return iter(self.stacks)

    def __len__(self) -> int:
        return len(self.stacks)

    @property
    def used_slots(self) -> int:
        return sum(1 for stack in self.stacks if not is_quest_item(stack.item_id))

    @property
    def free_slots(self) -> int:
        return self.capacity - self.used_slots

    def count(self, item_id: str) -> int:
        return sum(stack.quantity for stack in self.stacks if stack.item_id == item_id)

    def add(self, item_id: str, quantity: int = 1, dye: Optional[str] = None) -> int:
        """Guarda itens e devolve quantos NÃO couberam (0 = tudo guardado)."""
        max_stack = get_item(item_id).get("stack", 1)
        remaining = quantity
        for stack in self.stacks:
            if remaining <= 0:
                break
            if stack.item_id == item_id and stack.dye == dye and stack.quantity < max_stack:
                moved = min(max_stack - stack.quantity, remaining)
                stack.quantity += moved
                remaining -= moved
        while remaining > 0 and (self.free_slots > 0 or is_quest_item(item_id)):
            moved = min(max_stack, remaining)
            self.stacks.append(ItemStack(item_id, moved, dye))
            remaining -= moved
        return remaining

    def room_for(self, pairs: List[Tuple[str, int]]) -> bool:
        """Cabem todos estes itens? (simula sem mexer na mochila)"""
        trial = Inventory(self.capacity, [ItemStack(s.item_id, s.quantity, s.dye) for s in self.stacks])
        return all(trial.add(item_id, quantity) == 0 for item_id, quantity in pairs)

    def take(self, stack: ItemStack, quantity: int = 1) -> None:
        """Retira unidades de uma pilha específica (preservando a tinta das demais)."""
        stack.quantity -= quantity
        if stack.quantity <= 0:
            self.stacks.remove(stack)

    def find(self, item_id: str) -> Optional[ItemStack]:
        return next((stack for stack in self.stacks if stack.item_id == item_id), None)

    def remove(self, item_id: str, quantity: int = 1) -> bool:
        """Remove itens (das últimas pilhas para as primeiras). Falha se não houver o bastante."""
        if self.count(item_id) < quantity:
            return False
        for stack in reversed(list(self.stacks)):
            if quantity <= 0:
                break
            if stack.item_id != item_id:
                continue
            taken = min(stack.quantity, quantity)
            stack.quantity -= taken
            quantity -= taken
            if stack.quantity == 0:
                self.stacks.remove(stack)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"capacity": self.capacity, "items": [stack.to_dict() for stack in self.stacks]}

    @classmethod
    def from_dict(cls, data: Optional[Mapping[str, Any]]) -> "Inventory":
        data = data or {}
        stacks = [ItemStack.from_dict(entry) for entry in data.get("items", []) if entry.get("id") in ITEMS]
        return cls(int(data.get("capacity", DEFAULT_BAG_SLOTS)), stacks)


# --------------------------------------------------------------------------- uso e descrição

ELEMENT_NAMES = {"fisico": "Físico", "fogo": "Fogo", "gelo": "Gelo", "arcano": "Arcano", "sagrado": "Sagrado",
                 "sombra": "Sombra", "natureza": "Natureza"}


def buff_summary(spec: Mapping[str, Any]) -> str:
    """"+3 VIG +3 ESP", "+1 de visão", "+3–5 de dano de Natureza nos golpes da arma"."""
    parts = [f"+{value} {STATS[stat]['short']}" for stat, value in spec.get("stats", {}).items()]
    if spec.get("vision"):
        parts.append(f"+{spec['vision']} de visão")
    coating = spec.get("coating")
    if coating:
        low, high = coating["damage"]
        parts.append(f"+{low}–{high} de dano de {ELEMENT_NAMES[coating['element']]} nos golpes da arma")
    return " ".join(parts)


def apply_consumable(player: "Player", item_id: str, rng: Optional[random.Random] = None,
                     max_hp: Optional[int] = None, now: Optional[int] = None) -> str:
    """Consome uma unidade do item e aplica o efeito. Devolve a mensagem para o jogador.

    ``now`` (minutos do relógio do jogo) é preciso para os bônus temporários.
    """
    rng = rng or random.Random()
    item = get_item(item_id)
    use = item["use"]
    player.inventory.remove(item_id, 1)
    parts = [use.get("verb") or f"Você usa {item['name']}."]
    buff = use.get("buff")
    if buff and now is not None:
        player.add_buff(buff, now)
        parts.append(f"{buff['name']}: {buff_summary(buff)} por {format_duration(buff['minutes'] * 60)}.")
    cap = max_hp if max_hp is not None else player.max_hp
    heal = (rng.randint(*use["heal"]) if "heal" in use else 0) + round(cap * use.get("heal_pct", 0) / 100)
    if heal:
        before = player.hp
        player.hp = min(cap, player.hp + heal)
        if player.hp > before:
            parts.append(f"+{player.hp - before} de vida.")
    if player.resource_id == "mana":
        mana = (rng.randint(*use["mana"]) if "mana" in use else 0)
        mana += round(player.max_resource * use.get("mana_pct", 0) / 100)
        if mana:
            before = player.resource
            player.resource = min(player.max_resource, player.resource + mana)
            parts.append(f"+{player.resource - before} de mana.")
    return " ".join(parts)


def item_summary(item_id: str) -> str:
    """Resumo técnico: "Cabeça · Couro · Armadura 24 · +2 AGI +1 VIG"."""
    item = get_item(item_id)
    parts = []
    if item.get("slot"):
        parts.append(SLOTS[item["slot"]])
    if item.get("subtype"):
        parts.append(SUBTYPES[item["subtype"]] + (" (duas mãos)" if item.get("two_handed") else ""))
    elif not item.get("slot"):
        parts.append(ITEM_TYPES.get(item["type"], item["type"]))
    if item.get("tool"):
        parts.append(item["tool"].capitalize() + (f" (+{item['power']:.0%})" if item.get("power") else ""))
    if item.get("bag_slots"):
        parts.append(f"+{item['bag_slots']} espaços")
    if item.get("damage"):
        parts.append(f"Dano {item['damage'][0]}–{item['damage'][1]}")
    if item.get("armor"):
        parts.append(f"Armadura {item['armor']}")
    stats = item.get("stats", {})
    if stats:
        parts.append(" ".join(f"+{value} {STATS[stat]['short']}" for stat, value in stats.items()))
    return " · ".join(parts)
