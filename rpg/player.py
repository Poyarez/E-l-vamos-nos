"""O herói: aparência, classe, atributos, experiência (curva do WoW Classic), equipamento,
perícias, talentos e bônus temporários (comidas, elixires e venenos de arma)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any, Dict, List, Mapping, Optional

from .data.appearance import ALIGNMENTS, ARMOR_COLORS, FEATURES, GENDERS, HAIR_COLORS, HAIR_STYLES
from .data.classes import CLASSES, RESOURCES, STATS, TALENT_START_LEVEL
from .data.items import ITEMS, STARTING_COPPER, STARTING_ITEMS, SUBTYPES
from . import talents as talent_rules
from .items import DEFAULT_BAG_SLOTS, Inventory, ItemStack, get_item
from .skills import SkillSet
from .utils import capitalize_first

MAX_LEVEL = 60
BALD_STYLES = {"cabeca_raspada"}


def xp_to_next_level(level: int) -> int:
    """XP para ir de ``level`` a ``level + 1``: a fórmula do WoW Classic, arredondada a centenas.

    ``(8 × nível + dif(nível)) × (45 + 5 × nível)`` — 400 XP no nível 1, 7.600 no nível 10.
    """
    if level >= MAX_LEVEL:
        return 0
    if level <= 28:
        diff = 0
    elif level == 29:
        diff = 1
    elif level == 30:
        diff = 3
    elif level == 31:
        diff = 6
    else:
        diff = 5 * (level - 30)
    raw = (8 * level + diff) * (45 + 5 * level)
    return int(raw / 100 + 0.5) * 100


@dataclass
class Appearance:
    gender: str
    hair_style: str
    hair_color: str
    feature: str
    armor_color: str

    def validate(self) -> None:
        for value, options in ((self.gender, GENDERS), (self.hair_style, HAIR_STYLES),
                               (self.hair_color, HAIR_COLORS), (self.feature, FEATURES),
                               (self.armor_color, ARMOR_COLORS)):
            if value not in options:
                raise ValueError(f"Opção de aparência desconhecida: {value!r}")

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Appearance":
        appearance = cls(**{f.name: str(data[f.name]) for f in fields(cls)})
        appearance.validate()
        return appearance


@dataclass
class LevelUp:
    """O que mudou ao subir de nível (para a tela de comemoração)."""

    level: int
    stat_gains: Dict[str, int]
    hp_gain: int
    resource_gain: int
    new_abilities: List[str]
    talent_point: bool


class Player:
    def __init__(self, name: str, class_id: str, appearance: Appearance, alignment: str, level: int = 1,
                 xp: int = 0, hp: Optional[int] = None, resource: Optional[int] = None, copper: int = 0,
                 inventory: Optional[Inventory] = None, equipment: Optional[Dict[str, ItemStack]] = None,
                 skills: Optional[SkillSet] = None, buffs: Optional[List[Dict[str, Any]]] = None,
                 talents: Optional[Mapping[str, int]] = None) -> None:
        if class_id not in CLASSES:
            raise ValueError(f"Classe desconhecida: {class_id!r}")
        if alignment not in ALIGNMENTS:
            raise ValueError(f"Alinhamento desconhecido: {alignment!r}")
        appearance.validate()
        self.name = name
        self.class_id = class_id
        self.appearance = appearance
        self.alignment = alignment
        self.level = max(1, min(MAX_LEVEL, level))
        self.xp = max(0, xp)
        self.copper = max(0, copper)
        self.inventory = inventory or Inventory()
        self.equipment: Dict[str, ItemStack] = dict(equipment or {})
        self.skills = skills or SkillSet()
        self.buffs: List[Dict[str, Any]] = [dict(buff) for buff in (buffs or [])]
        catalog = talent_rules.all_talents(class_id)
        self.talents: Dict[str, int] = {talent_id: min(int(ranks), catalog[talent_id][1]["ranks"])
                                        for talent_id, ranks in (talents or {}).items()
                                        if talent_id in catalog and int(ranks) > 0}
        self._sync_capacity()
        self.hp = self.max_hp if hp is None else max(0, min(hp, self.max_hp))
        default_resource = self.max_resource if self.resource_data["starts_full"] else 0
        self.resource = default_resource if resource is None else max(0, min(resource, self.max_resource))

    @classmethod
    def create(cls, name: str, class_id: str, appearance: Appearance, alignment: str) -> "Player":
        """Novo herói com o equipamento e os itens iniciais da classe."""
        player = cls(name, class_id, appearance, alignment, copper=STARTING_COPPER)
        class_data = CLASSES[class_id]
        for slot, item_id in class_data["starting_equipment"].items():
            dye = appearance.armor_color if get_item(item_id).get("dyeable") else None
            player.equipment[slot] = ItemStack(item_id, 1, dye)
        for item_id, quantity in STARTING_ITEMS + class_data["starting_items"]:
            player.inventory.add(item_id, quantity)
        player.restore()
        return player

    # ------------------------------------------------------------------ classe e recurso

    @property
    def class_data(self) -> Dict[str, Any]:
        return CLASSES[self.class_id]

    @property
    def class_name(self) -> str:
        return self.class_data["names"][self.appearance.gender]

    @property
    def color(self) -> str:
        return self.class_data["color"]

    @property
    def resource_id(self) -> str:
        return self.class_data["resource"]

    @property
    def resource_data(self) -> Dict[str, Any]:
        return RESOURCES[self.resource_id]

    # ------------------------------------------------------------------ atributos

    def base_stat(self, stat: str) -> int:
        data = self.class_data
        return int(data["base_stats"][stat] + data["growth"][stat] * (self.level - 1))

    def gear_bonus(self, stat: str) -> int:
        return sum(stack.data.get("stats", {}).get(stat, 0) for stack in self.equipment.values())

    def buff_bonus(self, stat: str) -> int:
        return sum(buff.get("stats", {}).get(stat, 0) for buff in self.buffs)

    def talent_bonus(self, kind: str, key: Optional[str] = None) -> float:
        return talent_rules.bonus(self.class_id, self.talents, kind, key)

    def stat(self, stat: str) -> int:
        return (self.base_stat(stat) + self.gear_bonus(stat) + self.buff_bonus(stat)
                + int(self.talent_bonus("stat", stat)))

    def stats(self) -> Dict[str, int]:
        return {stat: self.stat(stat) for stat in STATS}

    @property
    def max_hp(self) -> int:
        data = self.class_data
        base = data["base_hp"] + data["hp_per_level"] * (self.level - 1) + self.stat("vigor") * 2
        return int(round(base * (1 + self.talent_bonus("max_hp_pct"))))

    @property
    def max_resource(self) -> int:
        fixed = self.resource_data["max"]
        if fixed:
            return fixed
        data = self.class_data
        base = data["base_mana"] + data["mana_per_level"] * (self.level - 1) + self.stat("intelecto") * 3
        return int(round(base * (1 + self.talent_bonus("max_resource_pct"))))

    @property
    def armor(self) -> int:
        base = sum(stack.data.get("armor", 0) for stack in self.equipment.values()) + self.stat("agilidade") * 2
        return int(round(base * (1 + self.talent_bonus("armor_pct"))))

    @property
    def xp_needed(self) -> int:
        return xp_to_next_level(self.level)

    @property
    def talent_points(self) -> int:
        """Pontos de talento ainda livres."""
        return talent_rules.points_total(self.level) - talent_rules.points_spent(self.talents)

    def learn_talent(self, talent_id: str) -> None:
        """Gasta um ponto num talento. Levanta ``ValueError`` se não der."""
        talent_rules.learn(self.class_id, self.level, self.talents, talent_id)
        self.clamp_vitals()

    def reset_talents(self) -> int:
        """Esquece todos os talentos e devolve quantos pontos voltaram."""
        refunded = talent_rules.points_spent(self.talents)
        self.talents = {}
        self.clamp_vitals()
        return refunded

    def abilities(self, include_locked: bool = False) -> List[Dict[str, Any]]:
        """Habilidades conhecidas (as de talento só depois de aprender o talento)."""
        granted = set(talent_rules.granted_abilities(self.class_id, self.talents))
        known = []
        for ability in self.class_data["abilities"]:
            if ability.get("talent"):
                if include_locked or ability["id"] in granted:
                    known.append(ability)
            elif include_locked or ability["level"] <= self.level:
                known.append(ability)
        return known

    def ability_cost(self, ability: Mapping[str, Any]) -> int:
        reduction = self.talent_bonus("cost", ability["id"])
        return max(0, int(ability.get("cost", 0) - reduction))

    def ability_cooldown(self, ability: Mapping[str, Any]) -> int:
        reduction = self.talent_bonus("cooldown", ability["id"])
        return max(0, int(ability.get("cooldown", 0) - reduction))

    # ------------------------------------------------------------------ progressão

    def gain_xp(self, amount: int) -> List[LevelUp]:
        """Soma experiência e devolve os níveis conquistados (pode ser mais de um)."""
        if self.level >= MAX_LEVEL or amount <= 0:
            return []
        self.xp += amount
        level_ups = []
        while self.level < MAX_LEVEL and self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            before_stats, before_hp, before_res = self.stats(), self.max_hp, self.max_resource
            self.level += 1
            level_ups.append(LevelUp(
                level=self.level,
                stat_gains={stat: self.stat(stat) - value for stat, value in before_stats.items()},
                hp_gain=self.max_hp - before_hp,
                resource_gain=self.max_resource - before_res,
                new_abilities=[a["name"] for a in self.class_data["abilities"]
                               if a["level"] == self.level and not a.get("talent")],
                talent_point=self.level >= TALENT_START_LEVEL,
            ))
            self.restore()
        if self.level >= MAX_LEVEL:
            self.xp = 0
        return level_ups

    def restore(self) -> None:
        """Vida cheia; recurso no estado de descanso (Raiva zera, Mana e Energia enchem)."""
        self.hp = self.max_hp
        self.resource = self.max_resource if self.resource_data["starts_full"] else 0

    def clamp_vitals(self) -> None:
        """Ajusta vida e recurso aos máximos atuais (depois de trocar equipamento ou de uma luta)."""
        self.hp = max(0, min(self.hp, self.max_hp))
        self.resource = max(0, min(self.resource, self.max_resource))

    def regenerate(self, minutes: int) -> None:
        """Recuperação natural fora de combate, guiada pelo Espírito. A Raiva esfria; a Energia volta."""
        if minutes <= 0:
            return
        spirit = self.stat("espirito")
        if self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + max(1, round(self.max_hp * (0.004 + spirit / 25000) * minutes)))
        if self.resource_id == "mana":
            rate = (0.005 + spirit / 20000) * (1 + self.talent_bonus("mana_regen_pct"))
            gain = max(1, round(self.max_resource * rate * minutes))
            self.resource = min(self.max_resource, self.resource + gain)
        elif self.resource_id == "energia":
            self.resource = self.max_resource
        else:
            self.resource = max(0, self.resource - 2 * minutes)

    # ------------------------------------------------------------------ bônus temporários

    def add_buff(self, spec: Mapping[str, Any], now: int) -> Dict[str, Any]:
        """Aplica um bônus de comida, elixir ou veneno de arma. Um por grupo: o novo substitui o antigo."""
        buff = {"id": spec["id"], "name": spec["name"], "group": spec.get("group", spec["id"]),
                "stats": dict(spec.get("stats", {})), "vision": int(spec.get("vision", 0)),
                "coating": dict(spec["coating"]) if spec.get("coating") else None,
                "expires": int(now + spec["minutes"])}
        self.buffs = [old for old in self.buffs if old["group"] != buff["group"]] + [buff]
        return buff

    def expire_buffs(self, now: int) -> List[Dict[str, Any]]:
        """Remove os bônus vencidos e devolve quais foram."""
        expired = [buff for buff in self.buffs if buff["expires"] <= now]
        if expired:
            self.buffs = [buff for buff in self.buffs if buff["expires"] > now]
            self.clamp_vitals()
        return expired

    @property
    def vision_bonus(self) -> int:
        return sum(buff.get("vision", 0) for buff in self.buffs)

    @property
    def coating(self) -> Optional[Dict[str, Any]]:
        """O veneno (ou óleo) aplicado na arma, se houver."""
        return next((buff for buff in self.buffs if buff.get("coating")), None)

    # ------------------------------------------------------------------ equipamento

    @property
    def bag_slots(self) -> int:
        bag = self.equipment.get("bolsa")
        return bag.data.get("bag_slots", 0) if bag else 0

    def _sync_capacity(self) -> None:
        self.inventory.capacity = DEFAULT_BAG_SLOTS + self.bag_slots

    def equip_problem(self, item_id: str) -> Optional[str]:
        """Por que este item não pode ser equipado agora (``None`` se pode)."""
        data = get_item(item_id)
        slot = data.get("slot")
        if not slot:
            return f"{data['name']} não é um equipamento."
        skills = self.class_data["proficiencies"]
        subtype = data.get("subtype")
        if data["type"] == "arma" and subtype not in skills["weapons"]:
            return f"Sua classe não sabe usar armas do tipo {SUBTYPES[subtype].lower()}."
        if data["type"] == "escudo" and not skills["shield"]:
            return "Sua classe não sabe usar escudos."
        if data["type"] == "armadura" and subtype and subtype not in skills["armor"]:
            return f"Sua classe não pode vestir armadura de {SUBTYPES[subtype].lower()}."
        if slot == "secundaria" and data["type"] == "arma" and not skills["dual_wield"]:
            return "Sua classe não sabe lutar com duas armas."
        main = self.equipment.get("arma")
        if slot == "secundaria" and main is not None and main.data.get("two_handed"):
            return f"{main.data['name']} exige as duas mãos."
        return None

    def equip(self, stack: ItemStack) -> List[ItemStack]:
        """Equipa uma pilha da mochila e devolve o que saiu do lugar. Levanta ``ValueError`` se não der."""
        problem = self.equip_problem(stack.item_id)
        if problem:
            raise ValueError(problem)
        item_id, dye, data = stack.item_id, stack.dye, stack.data
        slot = data["slot"]
        slots = [slot] + (["secundaria"] if data.get("two_handed") else [])
        displaced = [name for name in slots if name in self.equipment]
        used_after = self.inventory.used_slots - (1 if stack.quantity == 1 else 0) + len(displaced)
        capacity_after = DEFAULT_BAG_SLOTS + (data.get("bag_slots", 0) if slot == "bolsa" else self.bag_slots)
        if used_after > capacity_after:
            if slot == "bolsa":
                raise ValueError("Essa bolsa é menor que a sua: esvazie um pouco a mochila antes de trocar.")
            raise ValueError("Não há espaço na mochila para guardar o que você está usando.")
        self.inventory.take(stack)
        removed = [self.equipment.pop(name) for name in displaced]
        self.equipment[slot] = ItemStack(item_id, 1, dye)
        self._sync_capacity()
        for old in removed:
            self.inventory.add(old.item_id, 1, old.dye)
        self.clamp_vitals()
        return removed

    def unequip(self, slot: str) -> ItemStack:
        if slot not in self.equipment:
            raise ValueError("Não há nada equipado aí.")
        capacity_after = DEFAULT_BAG_SLOTS + (0 if slot == "bolsa" else self.bag_slots)
        if self.inventory.used_slots + 1 > capacity_after:
            if slot == "bolsa":
                raise ValueError(f"Sem a bolsa, a mochila só tem {DEFAULT_BAG_SLOTS} espaços: esvazie um pouco antes.")
            raise ValueError("Sua mochila está cheia.")
        stack = self.equipment.pop(slot)
        self._sync_capacity()
        self.inventory.add(stack.item_id, 1, stack.dye)
        self.clamp_vitals()
        return stack

    # ------------------------------------------------------------------ texto

    @property
    def forms(self) -> Dict[str, str]:
        """Palavras usadas nos diálogos: ``{nome}``, ``{tratamento}``, ``{Bem_vindo}``..."""
        base = dict(GENDERS[self.appearance.gender]["forms"])
        base["classe"] = self.class_name.lower()
        for key, value in list(base.items()):
            base[capitalize_first(key)] = capitalize_first(value)
        base["nome"] = self.name
        return base

    def portrait(self) -> str:
        """Descrição em texto da aparência do personagem."""
        look = self.appearance
        hair = HAIR_STYLES[look.hair_style]["description"]
        if look.hair_style not in BALD_STYLES:
            hair += ", de um tom " + HAIR_COLORS[look.hair_color]["adjective"]
        parts = [f"Diante do espelho d'água, você se vê: {hair}."]
        feature = FEATURES[look.feature]["description"]
        if feature:
            parts.append(feature)
        parts.append(f"Seu equipamento foi tingido em um tom {ARMOR_COLORS[look.armor_color]['description']}.")
        parts.append(GENDERS[look.gender]["description"])
        return " ".join(parts)

    # ------------------------------------------------------------------ persistência

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "class": self.class_id,
            "appearance": self.appearance.to_dict(),
            "alignment": self.alignment,
            "level": self.level,
            "xp": self.xp,
            "hp": self.hp,
            "resource": self.resource,
            "copper": self.copper,
            "inventory": self.inventory.to_dict(),
            "equipment": {slot: stack.to_dict() for slot, stack in self.equipment.items()},
            "skills": self.skills.to_dict(),
            "buffs": [dict(buff) for buff in self.buffs],
            "talents": dict(self.talents),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Player":
        equipment = {slot: ItemStack.from_dict(entry) for slot, entry in data.get("equipment", {}).items()
                     if entry.get("id") in ITEMS}
        return cls(
            name=str(data["name"]),
            class_id=str(data["class"]),
            appearance=Appearance.from_dict(data["appearance"]),
            alignment=str(data["alignment"]),
            level=int(data.get("level", 1)),
            xp=int(data.get("xp", 0)),
            hp=data.get("hp"),
            resource=data.get("resource"),
            copper=int(data.get("copper", 0)),
            inventory=Inventory.from_dict(data.get("inventory")),
            equipment=equipment,
            skills=SkillSet.from_dict(data.get("skills")),
            buffs=[buff for buff in data.get("buffs", [])
                   if isinstance(buff, dict) and {"id", "name", "group", "expires"} <= set(buff)],
            talents=data.get("talents"),
        )
