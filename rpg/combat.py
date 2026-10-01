"""Combate por turnos: o motor de regras.

Inspirado em WoW Classic — Mana, Raiva e Energia, recargas por turno, pontos de combo,
armadura, críticos e esquivas — e em Sea of Stars — fraquezas elementares, **selos** que
enfraquecem ou cancelam golpes especiais e golpes no **tempo certo**.

O motor não lê o teclado nem desenha nada: a interface (``rpg.battle_ui``) escolhe as
ações e exibe o ``log``. Toda a aleatoriedade passa por ``rng``, o que torna as lutas
reprodutíveis nos testes.

Ordem de uma rodada: o herói age; depois, cada inimigo vivo age na ordem da lista. No
início do turno de cada combatente, efeitos periódicos (sangramento, veneno, cura
contínua) são aplicados; quem estiver atordoado, congelado ou apavorado perde a vez.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

from . import ui
from .items import apply_consumable, get_item

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

HIT_CHANCE = 0.95
SPELL_HIT_CHANCE = 0.96
MONSTER_HIT_CHANCE = 0.93
CRIT_MULTIPLIER = 2.0
SPELL_CRIT_MULTIPLIER = 1.5
MONSTER_CRIT_CHANCE = 0.05
MONSTER_CRIT_MULTIPLIER = 1.5
PERFECT_STRIKE = 1.25          # golpe no tempo certo
PERFECT_BLOCK = 0.5            # bloqueio no tempo certo
DEFEND_REDUCTION = -0.5
ENERGY_PER_TURN = 20
MAX_COMBO = 5
MAX_ENEMIES = 4
OFFHAND_FACTOR = 0.5
MAX_ROUNDS = 100

TIMING_PERFECT = "perfeito"

CC_KINDS = ("stun", "freeze", "fear")
PERIODIC_KINDS = ("dot", "hot")
CC_NAMES = {"stun": "Atordoamento", "freeze": "Congelamento", "fear": "Pavor"}

OUTCOME_VICTORY = "vitoria"
OUTCOME_DEFEAT = "derrota"
OUTCOME_FLED = "fuga"


# --------------------------------------------------------------------------- regras gerais

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


def armor_mitigation(armor: float, attacker_level: int) -> float:
    """Fração do dano físico absorvida pela armadura (fórmula do WoW Classic, até 75%)."""
    armor = max(0.0, armor)
    return min(0.75, armor / (armor + 400 + 85 * attacker_level))


def rage_factor(level: int) -> float:
    """Constante de conversão de dano em Raiva do WoW Classic."""
    return 0.0091107836 * level ** 2 + 3.225598133 * level + 4.2652911


# --------------------------------------------------------------------------- combatentes

@dataclass
class Effect:
    """Efeito temporário: dano/cura periódicos, escudos, bônus, penalidades e controle."""

    id: str
    name: str
    kind: str                  # dot | hot | shield | buff | debuff | stun | freeze | fear | stealth
    turns: int
    amount: float = 0.0        # por turno (dot/hot), absorção restante (shield) ou valor do modificador
    stat: str = ""             # buff/debuff: ap, armor, dodge, hit, damage_dealt, damage_taken, max_hp
    element: str = "fisico"
    fresh: bool = False        # aplicado no próprio turno do alvo: só começa a contar no próximo


@dataclass
class Charge:
    """Um golpe especial sendo concentrado, protegido por selos."""

    ability: Dict[str, Any]
    turns: int
    locks: List[str]
    broken: List[bool] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.broken:
            self.broken = [False] * len(self.locks)


class Combatant:
    is_hero = False

    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level
        self.effects: List[Effect] = []

    hp: int
    max_hp: int

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def find(self, effect_id: str) -> Optional[Effect]:
        return next((effect for effect in self.effects if effect.id == effect_id), None)

    def modifier(self, stat: str) -> float:
        return sum(effect.amount for effect in self.effects if effect.stat == stat)

    def incapacitation(self) -> Optional[Effect]:
        return next((effect for effect in self.effects if effect.kind in CC_KINDS), None)


class Hero(Combatant):
    """O herói em combate: um invólucro do ``Player`` que acrescenta recargas, combos e efeitos."""

    is_hero = True

    def __init__(self, player: Any) -> None:
        super().__init__(player.name, player.level)
        self.player = player
        self.data = player.class_data
        self.cooldowns: Dict[str, int] = {}    # habilidade -> rodada em que volta a ficar pronta
        self.combo = 0
        self.crit_next = False

    @property
    def hp(self) -> int:
        return self.player.hp

    @hp.setter
    def hp(self, value: float) -> None:
        self.player.hp = int(max(0, min(self.max_hp, round(value))))

    @property
    def max_hp(self) -> int:
        return self.player.max_hp + int(self.modifier("max_hp"))

    @property
    def resource(self) -> int:
        return self.player.resource

    @resource.setter
    def resource(self, value: float) -> None:
        self.player.resource = int(max(0, min(self.max_resource, round(value))))

    @property
    def max_resource(self) -> int:
        return self.player.max_resource

    @property
    def resource_id(self) -> str:
        return self.player.resource_id

    @property
    def armor(self) -> float:
        return self.player.armor + self.modifier("armor")

    @property
    def attack_power(self) -> float:
        base = sum(self.player.stat(stat) * factor for stat, factor in self.data["attack_power"].items())
        return base + self.modifier("ap")

    @property
    def spell_power(self) -> float:
        factors = self.data.get("spell_power") or {}
        if not factors:
            return 0.0
        return sum(self.player.stat(stat) * factor for stat, factor in factors.items()) + self.level * 1.5

    def talent(self, kind: str, key: Optional[str] = None) -> float:
        return self.player.talent_bonus(kind, key)

    @property
    def crit_chance(self) -> float:
        return 0.05 + self.player.stat("agilidade") / 2000 + self.talent("crit")

    @property
    def spell_crit_chance(self) -> float:
        return 0.05 + self.player.stat("intelecto") / 3000 + self.talent("spell_crit")

    @property
    def dodge(self) -> float:
        return min(0.75, 0.05 + self.player.stat("agilidade") / 2000 + self.modifier("dodge") + self.talent("dodge"))

    def damage_bonus(self, element: str, ability_id: Optional[str] = None) -> float:
        """Multiplicador de dano dos talentos para um elemento (e uma habilidade, se houver)."""
        bonus = self.talent("damage_pct", element)
        if ability_id:
            bonus += self.talent("ability_pct", ability_id)
        return 1 + bonus

    def gear(self, slot: str) -> Optional[Dict[str, Any]]:
        stack = self.player.equipment.get(slot)
        return stack.data if stack else None

    def weapon(self, slot: str = "arma") -> Optional[Dict[str, Any]]:
        data = self.gear(slot)
        return data if data and data.get("damage") else None

    @property
    def has_shield(self) -> bool:
        data = self.gear("secundaria")
        return bool(data and data.get("subtype") == "escudo")

    @property
    def has_dagger(self) -> bool:
        data = self.weapon("arma")
        return bool(data and data.get("subtype") == "adaga")

    def weapon_roll(self, rng: random.Random, offhand: bool = False) -> float:
        weapon = self.weapon("secundaria" if offhand else "arma")
        low, high = weapon["damage"] if weapon else (1, 3)
        return rng.uniform(low, high) + self.attack_power / 5

    def mana_regen(self) -> int:
        if self.resource_id != "mana":
            return 0
        return int(round((self.player.stat("espirito") * 0.2 + 2) * (1 + self.talent("mana_regen_pct"))))


class Monster(Combatant):
    """Uma criatura em combate (criada por ``rpg.monsters.create_monster``)."""

    def __init__(self, template_id: str, data: Dict[str, Any], level: int, max_hp: int,
                 damage: Tuple[float, float], armor: int) -> None:
        super().__init__(data["name"], level)
        self.template_id = template_id
        self.data = data
        self._max_hp = max_hp
        self._hp = max_hp
        self.damage = damage
        self.base_armor = armor
        self.dodge = data.get("dodge", 0.05)
        self.element = data.get("element", "fisico")
        self.weaknesses = tuple(data.get("weaknesses", ()))
        self.resistances = tuple(data.get("resistances", ()))
        self.immunities = tuple(data.get("immunities", ()))
        self.abilities: List[Dict[str, Any]] = list(data.get("abilities", []))
        self.elite = bool(data.get("elite"))
        self.boss = bool(data.get("boss"))
        self.attack_verb = data.get("attack", "ataca")
        self.cooldowns: Dict[str, int] = {}
        self.used_once: Set[str] = set()
        self.charging: Optional[Charge] = None

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: float) -> None:
        self._hp = int(max(0, min(self._max_hp, round(value))))

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def armor(self) -> float:
        return self.base_armor + self.modifier("armor")


# --------------------------------------------------------------------------- a batalha

class Battle:
    """Uma luta entre o herói e um grupo de criaturas.

    ``knowledge`` (por id de criatura) guarda o que já se sabe sobre fraquezas e
    resistências — normalmente o bestiário do jogador, atualizado durante a luta.
    ``summon`` cria reforços chamados pelas criaturas; ``block_prompt`` (opcional) é
    chamado antes de golpes especiais e devolve ``TIMING_PERFECT`` para um bloqueio perfeito.
    """

    def __init__(self, hero: Hero, enemies: List[Monster], rng: Optional[random.Random] = None,
                 knowledge: Optional[Dict[str, Set[str]]] = None, allow_flee: bool = True,
                 enemies_first: bool = False, hero_stealth: bool = False) -> None:
        self.hero = hero
        self.enemies = list(enemies)
        self.rng = rng or random.Random()
        self.knowledge: Dict[str, Set[str]] = knowledge if knowledge is not None else {}
        self.allow_flee = allow_flee
        self.round = 1
        self.log: List[str] = []
        self.outcome: Optional[str] = None
        self.defeated: List[Monster] = []
        self.actor: Optional[Combatant] = None
        self.summon: Optional[Callable[[str, int], Monster]] = None
        self.block_prompt: Optional[Callable[[str], Optional[str]]] = None
        self._enemies_first = enemies_first
        self._hits: Dict[int, bool] = {}
        if hero_stealth:
            hero.crit_next = True

    # ------------------------------------------------------------------ consultas

    def living_enemies(self) -> List[Monster]:
        return [enemy for enemy in self.enemies if enemy.alive]

    def known(self, monster: Monster) -> Set[str]:
        return self.knowledge.setdefault(monster.template_id, set())

    def ability_status(self, ability: Dict[str, Any], target: Optional[Monster] = None) -> Tuple[bool, str]:
        """A habilidade pode ser usada agora? Se não, por quê."""
        hero = self.hero
        name = ability["name"]
        ready = hero.cooldowns.get(ability["id"], 0)
        if ready > self.round:
            remaining = ready - self.round
            return False, f"{name} está em recarga ({remaining} {'turno' if remaining == 1 else 'turnos'})."
        cost = hero.player.ability_cost(ability)
        if hero.resource < cost:
            resource = hero.player.resource_data["name"]
            return False, f"{resource} insuficiente para {name} ({hero.resource}/{cost})."
        requires = ability.get("requires", {})
        if requires.get("first_round") and self.round != 1:
            return False, f"{name} só pode ser usada no primeiro turno da luta."
        if requires.get("shield") and not hero.has_shield:
            return False, f"{name} exige um escudo equipado."
        if requires.get("dagger") and not hero.has_dagger:
            return False, f"{name} exige uma adaga na mão principal."
        if requires.get("combo") and hero.combo < requires["combo"]:
            return False, f"{name} precisa de pontos de combo."
        if "target_below" in requires:
            limit = requires["target_below"]
            candidates = [target] if target else self.living_enemies()
            if not any(enemy.hp <= enemy.max_hp * limit for enemy in candidates):
                return False, f"{name} só funciona contra inimigos com menos de {int(limit * 100)}% de vida."
        return True, ""

    # ------------------------------------------------------------------ início

    def start(self) -> None:
        """Começa a luta. Numa emboscada, as criaturas agem antes do herói."""
        if self._enemies_first:
            self._say(ui.style("Emboscada! As criaturas atacam antes que você possa reagir.", "bright_red bold"))
            self._enemy_phase()
            if self._check_outcome():
                return
            self.round += 1
        self._prepare_hero_turn()

    # ------------------------------------------------------------------ ações do herói

    def attack(self, target_index: Optional[int] = None, timing: Optional[str] = None) -> bool:
        target = self._target(target_index)
        if target is None:
            return self._invalid("Alvo inválido.")
        hero = self.hero
        self._header("Ataque")
        bonus = hero.damage_bonus("fisico")
        dealt = self._hero_hit(target, hero.weapon_roll(self.rng) * bonus, "fisico", False, timing, "Seu golpe")
        self._rage_from_damage(dealt, dealing=True)
        self._weapon_coating(target, dealt)
        if hero.weapon("secundaria"):
            target = target if target.alive else self._target(None)
            if target is not None:
                offhand = (hero.weapon_roll(self.rng, offhand=True) * OFFHAND_FACTOR * bonus
                           * (1 + hero.talent("offhand_pct")))
                dealt = self._hero_hit(target, offhand, "fisico", False, timing, "Mão secundária")
                self._rage_from_damage(dealt, dealing=True)
                self._weapon_coating(target, dealt)
        self._finish_hero_action()
        return True

    def use_ability(self, ability_id: str, target_index: Optional[int] = None, timing: Optional[str] = None) -> bool:
        hero = self.hero
        ability = next((a for a in hero.player.abilities() if a["id"] == ability_id), None)
        if ability is None:
            return self._invalid("Você ainda não conhece essa habilidade.")
        mode = ability.get("target", "enemy")
        target = None
        if mode == "enemy":
            target = self._target(target_index)
            if target is None:
                return self._invalid("Alvo inválido.")
        usable, reason = self.ability_status(ability, target)
        if not usable:
            return self._invalid(reason)
        hero.resource -= hero.player.ability_cost(ability)
        cooldown = hero.player.ability_cooldown(ability)
        if cooldown:
            hero.cooldowns[ability["id"]] = self.round + cooldown + 1
        self._header(ability["name"])
        if mode == "self":
            targets: List[Combatant] = [hero]
        elif mode == "all_enemies":
            targets = list(self.living_enemies())
        else:
            targets = [target]
        self._hits = {}
        for spec in ability.get("effects", []):
            self._apply_spec(spec, ability, targets, timing)
        self._finish_hero_action()
        return True

    def defend(self) -> bool:
        hero = self.hero
        self._header("Defender")
        self._add_effect(hero, Effect("defesa", "Postura defensiva", "buff", 1, DEFEND_REDUCTION, "damage_taken"))
        if hero.resource_id == "raiva":
            hero.resource += 5
        self._say("Você se protege: o dano recebido cai pela metade até o seu próximo turno.")
        self._finish_hero_action()
        return True

    def use_item(self, item_id: str, target_index: Optional[int] = None, timing: Optional[str] = None) -> bool:
        """Usa um item: poções no herói; frascos de arremesso (``damage``) num inimigo."""
        hero = self.hero
        item = get_item(item_id)
        use = item.get("use")
        if not use:
            return self._invalid(f"{item['name']} não pode ser usado.")
        if not use.get("combat", True):
            return self._invalid(f"Não dá para usar {item['name']} no meio da luta!")
        if hero.player.inventory.count(item_id) == 0:
            return self._invalid(f"Você não tem {item['name']}.")
        if use.get("damage"):
            target = self._target(target_index)
            if target is None:
                return self._invalid("Alvo inválido.")
            self._header(item["name"])
            hero.player.inventory.remove(item_id, 1)
            self._say(f"{use.get('verb', 'Você arremessa')} em {target.name}!")
            amount = self.rng.uniform(*use["damage"])
            self._hits = {}
            self._hero_hit(target, amount, use.get("element", "fisico"), True, timing, item["name"])
            self._finish_hero_action()
            return True
        self._header(item["name"])
        self._say(apply_consumable(hero.player, item_id, self.rng, max_hp=hero.max_hp))
        self._finish_hero_action()
        return True

    def analyze(self, target_index: Optional[int] = None) -> bool:
        target = self._target(target_index)
        if target is None:
            return self._invalid("Alvo inválido.")
        self._header("Analisar")
        facts = self.known(target)
        facts.add("analisado")
        facts.update(f"fraco:{element}" for element in target.weaknesses)
        facts.update(f"resiste:{element}" for element in target.resistances)
        facts.update(f"imune:{element}" for element in target.immunities)
        self._say(f"Você estuda {target.name} com atenção. {target.data.get('description', '')}")
        for line in describe_knowledge(target, facts):
            self._say(line)
        specials = [a["name"] for a in target.abilities if not a.get("hp_below")]
        if specials:
            self._say("Habilidades: " + ", ".join(specials) + ".")
        self._finish_hero_action()
        return True

    def flee(self) -> bool:
        if not self.allow_flee:
            return self._invalid("Não há como fugir desta luta!")
        living = self.living_enemies()
        average = sum(enemy.level for enemy in living) / len(living)
        chance = 0.55 + 0.05 * (self.hero.level - average) + (0.2 if self.hero.resource_id == "energia" else 0.0)
        chance = max(0.15, min(0.95, chance))
        self._header("Fugir")
        if self.rng.random() < chance:
            self.outcome = OUTCOME_FLED
            self._say(ui.style("Você encontra uma brecha e escapa!", "bright_yellow"))
            return True
        self._say("Você tenta fugir, mas não encontra uma brecha!")
        self._finish_hero_action()
        return True

    # ------------------------------------------------------------------ resolução das habilidades

    def _apply_spec(self, spec: Dict[str, Any], ability: Dict[str, Any], targets: List[Combatant],
                    timing: Optional[str]) -> None:
        hero = self.hero
        kind = spec["type"]
        element = spec.get("element", ability.get("element", "fisico"))
        spell = element != "fisico"
        name = ability["name"]
        enemies = [t for t in targets if isinstance(t, Monster)]
        bonus = hero.damage_bonus(element, ability["id"])

        if kind == "damage":
            for target in enemies:
                for _ in range(spec.get("hits", 1)):
                    if not target.alive:
                        break
                    dealt = self._hero_hit(target, self._power(spec) * bonus, element, spell, timing, name)
                    self._hits[id(target)] = self._hits.get(id(target), False) or dealt is not None
                    if spec.get("scale") == "weapon":
                        self._weapon_coating(target, dealt)
        elif kind == "finisher":
            target = enemies[0]
            amount = sum(self._power(spec) for _ in range(hero.combo)) * bonus
            if self._hero_hit(target, amount, element, spell, timing, f"{name} ({hero.combo} combo)") is not None:
                hero.combo = 0
        elif kind == "execute":
            target = enemies[0]
            extra = hero.resource
            hero.resource = 0
            amount = (self.rng.uniform(*spec["base"]) + extra * spec.get("per_rage", 0)) * bonus
            self._hero_hit(target, amount, element, spell, timing, name)
        elif kind == "dot":
            for target in enemies:
                if target.alive and self._landed(target, spell, name):
                    amount = self._power(spec) * bonus * element_multiplier(element, target.weaknesses,
                                                                            target.resistances, target.immunities)
                    self._add_effect(target, Effect(spec["id"], spec["name"], "dot", spec["turns"], amount,
                                                    element=element))
                    self._say(f"{spec['name']}: {target.name} sofrerá dano por {spec['turns']} turnos.")
        elif kind == "debuff":
            for target in enemies:
                if target.alive and self._landed(target, spell, name):
                    self._add_effect(target, Effect(spec["id"], spec["name"], "debuff", spec["turns"],
                                                    spec["value"], spec["stat"]))
                    self._say(f"{spec['name']} em {target.name} por {spec['turns']} turnos.")
        elif kind in CC_KINDS:
            for target in enemies:
                if not (target.alive and self._landed(target, spell, name)):
                    continue
                if target.boss:
                    self._say(f"{target.name} é imune a esse efeito!")
                    continue
                label = spec.get("name", CC_NAMES[kind])
                self._add_effect(target, Effect(kind, label, kind, spec["turns"]))
                self._say(f"{label}: {target.name} perde {spec['turns']} {'turno' if spec['turns'] == 1 else 'turnos'}.")
        elif kind == "interrupt":
            for target in enemies:
                if not (target.alive and self._landed(target, spell, name)):
                    continue
                if target.charging:
                    interrupted = target.charging.ability["name"]
                    target.charging = None
                    self._say(ui.style(f"Você interrompe {interrupted}!", "bright_yellow bold"))
                    if not target.boss:
                        self._add_effect(target, Effect("stun", CC_NAMES["stun"], "stun", 1))
                else:
                    self._say(f"{target.name} não estava concentrando nada.")
        elif kind == "combo":
            if any(self._hits.values()):
                hero.combo = min(MAX_COMBO, hero.combo + spec.get("value", 1))
                self._say(f"Pontos de combo: {combo_display(hero.combo)}")
        elif kind == "heal":
            amount = self._power(spec) * (1 + hero.talent("heal_pct"))
            if self.rng.random() < hero.spell_crit_chance:
                amount *= SPELL_CRIT_MULTIPLIER
            if timing == TIMING_PERFECT:
                amount *= PERFECT_STRIKE
            healed = self._heal(hero, amount)
            perfect = " No tempo certo!" if timing == TIMING_PERFECT else ""
            self._say(ui.style(f"Você recupera {healed} de vida.{perfect}", "bright_green"))
        elif kind == "hot":
            amount = self._power(spec) * (1 + hero.talent("heal_pct"))
            self._add_effect(hero, Effect(spec["id"], spec["name"], "hot", spec["turns"], amount))
            self._say(f"{spec['name']}: você se cura a cada turno, por {spec['turns']} turnos.")
        elif kind == "shield":
            amount = self._power(spec) * (1 + hero.talent("shield_pct"))
            self._add_effect(hero, Effect(spec["id"], spec["name"], "shield", spec["turns"], amount))
            self._say(f"{spec['name']}: absorve até {int(amount)} de dano.")
        elif kind == "buff":
            self._add_effect(hero, Effect(spec["id"], spec["name"], "buff", spec["turns"], spec["value"], spec["stat"]))
            if spec["stat"] == "max_hp":
                hero.hp += spec["value"]
            turns = "até o fim da luta" if spec["turns"] >= 50 else f"por {spec['turns']} turnos"
            self._say(f"{spec['name']} ativo {turns}.")
        elif kind == "rage":
            hero.resource += spec["value"]
            self._say(f"+{spec['value']} de Raiva.")
        elif kind == "resource":
            before = hero.resource
            hero.resource += spec["value"]
            self._say(f"+{hero.resource - before} de {hero.player.resource_data['name']}.")
        elif kind == "stealth":
            self._add_effect(hero, Effect("furtividade", "Furtividade", "stealth", 1))
            hero.crit_next = True
            self._say("Você some nas sombras. Seu próximo golpe será crítico.")
        else:
            raise KeyError(f"Efeito de habilidade desconhecido: {kind!r}")

    def _power(self, spec: Dict[str, Any]) -> float:
        low, high = spec.get("base", (0, 0))
        value = self.rng.uniform(low, high)
        scale = spec.get("scale")
        if scale == "weapon":
            value += self.hero.weapon_roll(self.rng) * spec.get("weapon_mult", 1.0)
        elif scale == "ap":
            value += self.hero.attack_power * spec.get("coef", 0.0)
        elif scale == "sp":
            value += self.hero.spell_power * spec.get("coef", 0.0)
        return value

    def _roll_hit(self, target: Monster, spell: bool) -> bool:
        chance = (SPELL_HIT_CHANCE if spell else HIT_CHANCE) - 0.02 * max(0, target.level - self.hero.level)
        chance += self.hero.modifier("hit") + self.hero.talent("hit")
        if not spell:
            chance -= target.dodge
        return self.rng.random() < chance

    def _landed(self, target: Monster, spell: bool, name: str) -> bool:
        """Efeitos que acompanham um golpe só pegam se ele acertou; sozinhos, testam o acerto."""
        key = id(target)
        if key not in self._hits:
            self._hits[key] = self._roll_hit(target, spell)
            if not self._hits[key]:
                self._say(f"{name}: {target.name} {'resiste' if spell else 'se esquiva'}!")
        return self._hits[key]

    def _hero_hit(self, target: Monster, amount: float, element: str, spell: bool, timing: Optional[str],
                  label: str, proc: bool = False) -> Optional[int]:
        """Resolve um golpe do herói. Devolve o dano causado, ou ``None`` se errou.

        ``proc`` marca um dano extra que acompanha outro golpe (o veneno da arma): ele não
        testa acerto nem crítico.
        """
        hero = self.hero
        if not proc and not self._roll_hit(target, spell):
            self._say(f"{label}: {target.name} {'resiste' if spell else 'se esquiva'}!")
            return None
        crit = False
        if not proc:
            crit = hero.crit_next or self.rng.random() < (hero.spell_crit_chance if spell else hero.crit_chance)
            hero.crit_next = False
        if crit:
            amount *= SPELL_CRIT_MULTIPLIER if spell else CRIT_MULTIPLIER
        if timing == TIMING_PERFECT:
            amount *= PERFECT_STRIKE
        if element == "fisico":
            amount *= 1 - armor_mitigation(target.armor, hero.level)
        amount *= max(0.0, 1 + hero.modifier("damage_dealt"))
        multiplier = element_multiplier(element, target.weaknesses, target.resistances, target.immunities)
        amount *= multiplier
        dealt = self._damage(target, amount, direct=multiplier > 0)
        tags = []
        if timing == TIMING_PERFECT:
            tags.append(ui.style("No tempo certo!", "bright_cyan bold"))
        if crit:
            tags.append(ui.style("CRÍTICO!", "bright_yellow bold"))
        if multiplier > 1:
            tags.append(ui.style("Fraqueza!", "bright_green bold"))
        elif multiplier == 0:
            tags.append(ui.style("Imune!", "gray"))
        elif multiplier < 1:
            tags.append(ui.style("resistido", "gray"))
        suffix = (" " + " ".join(tags)) if tags else ""
        self._say(f"{label} atinge {target.name}: {ui.style(str(dealt), 'bright_white bold')} de dano.{suffix}")
        self._learn_from_hit(target, element, multiplier)
        if target.charging and multiplier > 0:
            self._break_lock(target, element)
        if not target.alive:
            self._on_enemy_death(target)
        return dealt

    def _weapon_coating(self, target: Monster, dealt: Optional[int]) -> None:
        """Veneno de arma: dano extra do elemento a cada golpe de arma que acerta."""
        buff = self.hero.player.coating
        if dealt is None or buff is None or not target.alive:
            return
        coating = buff["coating"]
        amount = self.rng.uniform(*coating["damage"]) * (1 + self.hero.talent("coating_pct"))
        self._hero_hit(target, amount, coating["element"], True, None, buff["name"], proc=True)

    def _break_lock(self, enemy: Monster, element: str) -> None:
        charge = enemy.charging
        if charge is None:
            return
        for index, lock in enumerate(charge.locks):
            if not charge.broken[index] and lock == element:
                charge.broken[index] = True
                self._say(ui.style(f"Selo de {ELEMENTS[element]['name']} rompido!", "bright_cyan bold"))
                break
        else:
            return
        if all(charge.broken):
            enemy.charging = None
            self._say(ui.style(f"Todos os selos rompidos! {enemy.name} perde a concentração.", "bright_cyan bold"))
            self._add_effect(enemy, Effect("stun", CC_NAMES["stun"], "stun", 1))

    def _rage_from_damage(self, amount: Optional[int], dealing: bool) -> None:
        hero = self.hero
        if not amount or hero.resource_id != "raiva":
            return
        factor = (9.0 if dealing else 2.5) * (1 + hero.talent("rage_pct"))
        hero.resource += factor * amount / rage_factor(hero.level)

    # ------------------------------------------------------------------ dano, cura e efeitos

    def _damage(self, target: Combatant, amount: float, direct: bool = True) -> int:
        amount = max(1, int(round(amount))) if amount > 0 else 0
        for effect in list(target.effects):
            if effect.kind != "shield" or amount <= 0:
                continue
            absorbed = min(int(effect.amount), amount)
            effect.amount -= absorbed
            amount -= absorbed
            if absorbed:
                self._say(f"{effect.name} absorve {absorbed} de dano.")
            if effect.amount < 1:
                target.effects.remove(effect)
                self._say(f"{effect.name} se desfaz.")
        target.hp = target.hp - amount
        if direct and amount > 0 and target.alive:
            for effect in list(target.effects):
                if effect.kind == "fear" or (effect.kind == "freeze" and self.rng.random() < 0.5):
                    target.effects.remove(effect)
                    who = "Você se recupera" if target.is_hero else f"{target.name} se recupera"
                    self._say(f"{who} do efeito de {effect.name.lower()}!")
        return amount

    def _heal(self, target: Combatant, amount: float) -> int:
        before = target.hp
        target.hp = target.hp + amount
        return target.hp - before

    def _add_effect(self, target: Combatant, effect: Effect) -> None:
        effect.fresh = target is self.actor
        existing = target.find(effect.id)
        if existing is not None:
            target.effects.remove(existing)
        target.effects.append(effect)

    def _learn(self, monster: Monster, fact: str) -> bool:
        facts = self.known(monster)
        if fact in facts:
            return False
        facts.add(fact)
        return True

    def _learn_from_hit(self, monster: Monster, element: str, multiplier: float) -> None:
        name = ELEMENTS[element]["name"]
        if multiplier > 1 and self._learn(monster, f"fraco:{element}"):
            self._say(ui.style(f"Fraqueza descoberta: {monster.name} é vulnerável a {name}!", "bright_green"))
        elif multiplier == 0 and self._learn(monster, f"imune:{element}"):
            self._say(ui.style(f"{monster.name} é imune a {name}.", "gray"))
        elif 0 < multiplier < 1 and self._learn(monster, f"resiste:{element}"):
            self._say(ui.style(f"{monster.name} resiste a {name}.", "gray"))

    def _on_enemy_death(self, enemy: Monster) -> None:
        if enemy in self.defeated:
            return
        enemy.charging = None
        self.defeated.append(enemy)
        self._say(ui.style(f"{enemy.name} tomba!", "bright_yellow bold"))

    # ------------------------------------------------------------------ turnos

    def _start_turn(self, unit: Combatant) -> bool:
        """Efeitos periódicos e controle. Devolve ``True`` se a unidade pode agir."""
        self.actor = unit
        for effect in list(unit.effects):
            if effect.kind not in PERIODIC_KINDS:
                continue
            if effect.kind == "dot":
                dealt = self._damage(unit, effect.amount, direct=False)
                who = "você sofre" if unit.is_hero else f"{unit.name} sofre"
                self._say(f"{effect.name}: {who} {dealt} de dano.")
            else:
                healed = self._heal(unit, effect.amount)
                self._say(ui.style(f"{effect.name}: você recupera {healed} de vida.", "bright_green"))
            effect.turns -= 1
            if effect.turns <= 0 and effect in unit.effects:
                unit.effects.remove(effect)
        if not unit.alive:
            if isinstance(unit, Monster):
                self._on_enemy_death(unit)
            return False
        control = unit.incapacitation()
        if control is not None:
            who = "Você perde" if unit.is_hero else f"{unit.name} perde"
            self._say(ui.style(f"{who} a vez ({control.name.lower()}).", "gray"))
            return False
        return True

    def _end_turn(self, unit: Combatant) -> None:
        for effect in list(unit.effects):
            if effect.kind in PERIODIC_KINDS:
                continue
            if effect.fresh:
                effect.fresh = False
                continue
            effect.turns -= 1
            if effect.turns <= 0:
                unit.effects.remove(effect)
                if effect.stat == "max_hp" and unit.is_hero:
                    unit.hp = min(unit.hp, unit.max_hp)
        self.actor = None

    def _prepare_hero_turn(self) -> None:
        """Avança até o herói poder agir (ou até a luta acabar)."""
        while self.outcome is None:
            if self.round > 1:
                self._regen_hero()
            can_act = self._start_turn(self.hero)
            if self._check_outcome():
                return
            if can_act:
                return
            self._end_turn(self.hero)
            self._enemy_phase()
            if self._check_outcome():
                return
            self.round += 1

    def _finish_hero_action(self) -> None:
        self._end_turn(self.hero)
        if self._check_outcome():
            return
        self._enemy_phase()
        if self._check_outcome():
            return
        self.round += 1
        self._prepare_hero_turn()

    def _regen_hero(self) -> None:
        hero = self.hero
        if hero.resource_id == "energia":
            hero.resource += ENERGY_PER_TURN
        else:
            hero.resource += hero.mana_regen()

    def _check_outcome(self) -> bool:
        if self.outcome:
            return True
        if not self.hero.alive:
            self.outcome = OUTCOME_DEFEAT
            self._say(ui.style("Você cai, sem forças...", "bright_red bold"))
            return True
        if not self.living_enemies():
            self.outcome = OUTCOME_VICTORY
            return True
        if self.round > MAX_ROUNDS:
            self.outcome = OUTCOME_FLED
            self._say("A luta se arrasta até que vocês se afastam, exaustos.")
            return True
        return False

    # ------------------------------------------------------------------ inimigos

    def _enemy_phase(self) -> None:
        for enemy in list(self.enemies):
            if self.outcome or not self.hero.alive:
                break
            if not enemy.alive:
                continue
            if self._start_turn(enemy) and enemy.alive:
                self._enemy_act(enemy)
            if enemy.alive:
                self._end_turn(enemy)
            self.actor = None
            if self._check_outcome():
                break

    def _enemy_act(self, enemy: Monster) -> None:
        charge = enemy.charging
        if charge is not None:
            charge.turns -= 1
            if charge.turns > 0:
                self._say(f"{enemy.name} continua concentrando {charge.ability['name']}... "
                          f"({charge.turns} {'turno' if charge.turns == 1 else 'turnos'})")
                return
            enemy.charging = None
            broken = sum(charge.broken)
            power = 1.0 - 0.75 * broken / len(charge.locks) if charge.locks else 1.0
            if broken:
                self._say(ui.style(f"Com {broken} {'selo rompido' if broken == 1 else 'selos rompidos'}, "
                                   f"{charge.ability['name']} sai enfraquecido!", "bright_cyan"))
            self._monster_ability(enemy, charge.ability, power)
            return
        for ability in enemy.abilities:
            limit = ability.get("hp_below")
            if limit and ability["id"] not in enemy.used_once and enemy.hp <= enemy.max_hp * limit:
                enemy.used_once.add(ability["id"])
                self._monster_ability(enemy, ability)
                return
        for ability in enemy.abilities:
            if ability.get("hp_below") or enemy.cooldowns.get(ability["id"], 0) > self.round:
                continue
            if self.rng.random() >= ability.get("chance", 0):
                continue
            enemy.cooldowns[ability["id"]] = self.round + ability.get("cooldown", 0) + 1
            if ability.get("charge"):
                enemy.charging = Charge(ability, ability["charge"], list(ability.get("locks", [])))
                self._say(ui.style(ability.get("announce") or f"{enemy.name} começa a concentrar {ability['name']}!",
                                   "bright_magenta bold"))
                if enemy.charging.locks:
                    locks = " ".join(f"[{element_label(lock)}]" for lock in enemy.charging.locks)
                    self._say(f"Selos {locks} — acerte esses elementos para enfraquecer ou cancelar "
                              f"{ability['name']} ({ability['charge']} {'turno' if ability['charge'] == 1 else 'turnos'}).")
                return
            self._monster_ability(enemy, ability)
            return
        self._monster_attack(enemy)

    def _monster_attack(self, enemy: Monster, multiplier: float = 1.0, element: Optional[str] = None,
                        label: Optional[str] = None, blockable: bool = False) -> Optional[int]:
        hero = self.hero
        element = element or enemy.element
        if hero.find("furtividade"):
            self._say(f"{enemy.name} procura você nas sombras, mas não encontra ninguém.")
            return None
        chance = MONSTER_HIT_CHANCE + 0.02 * max(0, enemy.level - hero.level) + enemy.modifier("hit") - hero.dodge
        if self.rng.random() >= chance:
            self._say(f"{label or enemy.name}: você se esquiva!")
            return None
        amount = self.rng.uniform(*enemy.damage) * multiplier * max(0.0, 1 + enemy.modifier("damage_dealt"))
        crit = self.rng.random() < MONSTER_CRIT_CHANCE
        if crit:
            amount *= MONSTER_CRIT_MULTIPLIER
        if element == "fisico":
            amount *= 1 - armor_mitigation(hero.armor, enemy.level)
        amount *= max(0.0, 1 + hero.modifier("damage_taken"))
        blocked = False
        if blockable and self.block_prompt is not None:
            if self.block_prompt(f"{enemy.name}: {label}!") == TIMING_PERFECT:
                amount *= PERFECT_BLOCK
                blocked = True
        dealt = self._damage(hero, amount, direct=True)
        what = f"{label}: você sofre" if label else f"{enemy.name} {enemy.attack_verb} você:"
        extras = (" (crítico!)" if crit else "") + (" Bloqueio perfeito!" if blocked else "")
        self._say(ui.style(f"{what} {dealt} de dano.{extras}", "red"))
        self._rage_from_damage(dealt, dealing=False)
        return dealt

    def _monster_ability(self, enemy: Monster, ability: Dict[str, Any], power: float = 1.0) -> None:
        name = ability["name"]
        if ability.get("summon"):
            self._say(ui.style(ability.get("text") or f"{enemy.name} usa {name}!", "bright_magenta"))
            for template_id in ability["summon"]:
                if self.summon is not None and len(self.living_enemies()) < MAX_ENEMIES:
                    minion = self.summon(template_id, max(1, enemy.level - 1))
                    self.enemies.append(minion)
                    self._say(f"{minion.name} (nível {minion.level}) entra na luta!")
            return
        self._say(ui.style(f"{enemy.name} usa {name}!", "bright_magenta"))
        landed = True
        if ability.get("damage"):
            landed = self._monster_attack(enemy, ability["damage"] * power, ability.get("element"), name,
                                          blockable=True) is not None
        full = power >= 0.999
        hero = self.hero
        for spec in ability.get("effects", []):
            kind = spec["type"]
            if kind == "heal_self":
                healed = self._heal(enemy, enemy.max_hp * spec["value"] * power)
                self._say(f"{enemy.name} recupera {healed} de vida.")
            elif kind == "buff_self":
                if full:
                    self._add_effect(enemy, Effect(spec["id"], spec["name"], "buff", spec["turns"], spec["value"],
                                                   spec["stat"]))
                    self._say(f"{spec['name']}: {enemy.name} ganha força por {spec['turns']} turnos.")
            elif not (landed and full and hero.alive):
                continue
            elif kind == "dot":
                per_turn = sum(enemy.damage) / 2 * spec["power"]
                self._add_effect(hero, Effect(spec["id"], spec["name"], "dot", spec["turns"], per_turn,
                                              element=spec.get("element", "fisico")))
                self._say(f"{spec['name']}: você sofrerá dano por {spec['turns']} turnos.")
            elif kind in CC_KINDS:
                label = spec.get("name", CC_NAMES[kind])
                self._add_effect(hero, Effect(kind, label, kind, spec["turns"]))
                self._say(ui.style(f"{label}! Você perderá {spec['turns']} "
                                   f"{'turno' if spec['turns'] == 1 else 'turnos'}.", "bright_red"))
            elif kind == "debuff":
                self._add_effect(hero, Effect(spec["id"], spec["name"], "debuff", spec["turns"], spec["value"],
                                              spec["stat"]))
                self._say(f"{spec['name']}: você fica sob efeito por {spec['turns']} turnos.")
            elif kind == "drain_mana":
                if hero.resource_id == "mana":
                    drained = min(hero.resource, int(hero.max_resource * spec["value"]))
                    hero.resource -= drained
                    self._say(f"Você perde {drained} de mana.")
            else:
                raise KeyError(f"Efeito de monstro desconhecido: {kind!r}")

    # ------------------------------------------------------------------ utilidades

    def _target(self, index: Optional[int]) -> Optional[Monster]:
        if index is None:
            living = self.living_enemies()
            return living[0] if living else None
        if 0 <= index < len(self.enemies) and self.enemies[index].alive:
            return self.enemies[index]
        return None

    def _invalid(self, message: str) -> bool:
        self._say(ui.style(message, "gray"))
        return False

    def _header(self, label: str) -> None:
        self._say(ui.style(f"{ui.sym('arrow')} {label}", "bold"))

    def _say(self, text: str) -> None:
        self.log.append(text)


# --------------------------------------------------------------------------- textos

def combo_display(points: int) -> str:
    filled, empty = ("●", "○") if ui.display.unicode else ("*", "-")
    return ui.style(filled * points, "bright_yellow") + ui.style(empty * (MAX_COMBO - points), "gray")


def describe_knowledge(monster: Monster, facts: Set[str]) -> List[str]:
    """Fraquezas, resistências e imunidades conhecidas (``?`` para o que ainda não se sabe)."""
    analyzed = "analisado" in facts

    def listing(prefix: str, elements: Iterable[str]) -> str:
        known = [element_label(e) for e in elements if f"{prefix}:{e}" in facts]
        if analyzed:
            return ", ".join(known) if known else "nenhuma"
        return ", ".join(known + ["?"])

    return [f"Fraquezas: {listing('fraco', monster.weaknesses)} {ui.sym('dot')} "
            f"Resistências: {listing('resiste', monster.resistances + monster.immunities)}"]
