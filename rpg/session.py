"""Sessão de jogo: as regras da exploração.

Movimento, visão (névoa de guerra), descobertas com experiência, passagem do tempo,
passagens entre mapas, segredos, descanso, viagem rápida, a ponte com o combate
(encontros aleatórios por região, encontros fixos, caçadas, recompensas e derrota) e com
os ofícios (coleta, produção, bônus temporários e níveis de perícia).

Os comandos (``rpg.commands``) chamam estes métodos; as telas (``rpg.screens`` e
``rpg.battle_ui``) desenham o resultado. Quando uma luta deve começar, a sessão apenas
registra ``pending_battle`` — quem conduz a batalha é a interface.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from . import crafting, monsters, quests, save_system, ui, world
from .combat import OUTCOME_DEFEAT, OUTCOME_VICTORY, Battle
from .conditions import conditions_met, item_pairs
from .config import Settings
from .data.gathering import GATHER_VERBS
from .data.recipes import STATIONS
from .items import ItemStack, apply_consumable, item_name
from .npcs import NPC, npcs_at
from .player import LevelUp
from .skills import SKILLS
from .state import GameState
from .utils import format_money, stable_choice, stable_hash

Coord = Tuple[int, int]

PERIOD_MESSAGES = {
    "madrugada": "A madrugada avança, fria e silenciosa.",
    "amanhecer": "O céu clareia a leste: está amanhecendo.",
    "manha": "O sol já vai alto. É manhã.",
    "tarde": "O sol passa do meio do céu. É tarde.",
    "entardecer": "O sol se põe atrás das montanhas, tingindo o vale de laranja.",
    "noite": "A noite cai sobre o vale.",
}

BLOCKED_TEXT = {
    "agua": "As águas são fundas e rápidas demais para atravessar aqui.",
    "montanha": "Paredões de rocha bloqueiam o caminho.",
    "cachoeira": "A cachoeira despenca sobre o penhasco; não há como seguir por aí.",
    "parede_gruta": "Rocha maciça bloqueia o caminho.",
    "lago_subterraneo": "A água negra do lago subterrâneo é funda e gelada demais.",
    "porta_selada": "A porta de pedra não se move nem um milímetro.",
    "fogo_violeta": "As chamas violetas não esquentam nada — e é justamente por isso que você não chega perto.",
}

# eventos que interrompem uma caminhada de vários passos
EVENT_DISCOVERY = "descoberta"
EVENT_NPC = "npc"
EVENT_PASSAGE = "passagem"
EVENT_COMBAT = "combate"

RESPAWN = ("vale_primordia", 31, 12)       # Capela da Aurora
SAFE_TERRAINS = {"estrada": 0.4, "ponte": 0.4}
ENCOUNTER_GRACE = 4                        # passos sem encontros depois de uma luta
AMBUSH_CHANCE = 0.12


@dataclass
class LocationView:
    """Tudo o que a tela de exploração precisa mostrar sobre o lugar atual."""

    title: str
    subtitle: str
    paragraphs: List[str]
    npcs: List[NPC] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    exits: List[str] = field(default_factory=list)
    passages: List[str] = field(default_factory=list)
    can_rest: bool = False
    danger: Optional[Tuple[int, int]] = None
    stations: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)   # comandos de ofício úteis aqui (minerar, forjar...)
    board: str = ""                                    # resumo do quadro de avisos (na Praça do Poço)


@dataclass
class BattleRequest:
    """Uma luta prestes a começar (conduzida por ``rpg.battle_ui``)."""

    monsters: List[Tuple[str, int]]
    kind: str                                   # "aleatorio" | "caca" | "fixo"
    intro: str = ""
    boss: bool = False
    ambush: bool = False                        # as criaturas atacam primeiro
    landmark_id: Optional[str] = None
    encounter: Optional[Dict[str, Any]] = None  # dados do encontro fixo


@dataclass
class BattleReport:
    """O que a luta rendeu (ou custou)."""

    outcome: str
    xp: int = 0
    items: List[Tuple[str, int]] = field(default_factory=list)
    lost_items: List[Tuple[str, int]] = field(default_factory=list)
    copper: int = 0
    copper_lost: int = 0
    text: str = ""


class GameSession:
    def __init__(self, state: GameState, settings: Settings, rng: Optional[random.Random] = None) -> None:
        self.state = state
        self.settings = settings
        self.rng = rng or random.Random()
        self.messages: List[str] = []
        self.level_ups: List[LevelUp] = []
        self.visible: Set[Coord] = set()
        self.events: Set[str] = set()
        self.needs_redraw = True
        self.running = True
        self.dirty = False
        self.pending_autosave = False
        self.pending_battle: Optional[BattleRequest] = None
        self.pending_shop = False
        self.encounter_grace = 0
        self.previous: Optional[Tuple[str, int, int]] = None
        self.suppressed: Set[str] = set()       # encontros fixos recusados (até o herói se afastar)
        self.reward_warnings: Set[str] = set()  # missões esperando espaço na mochila (já avisadas)
        self._timer = time.monotonic()
        self._region_id: Optional[str] = None

    # ------------------------------------------------------------------ atalhos

    @property
    def map(self) -> world.GameMap:
        return world.get_map(self.state.map_id)

    @property
    def player(self):
        return self.state.player

    @property
    def clock(self):
        return self.state.clock

    def notify(self, text: str) -> None:
        self.messages.append(text)

    def pop_messages(self) -> List[str]:
        messages, self.messages = self.messages, []
        return messages

    # ------------------------------------------------------------------ início

    def begin(self, new_game: bool = False) -> None:
        """Prepara a sessão. Num jogo novo, o lugar de partida já conta como conhecido."""
        if new_game:
            region = self.map.region_at(*self.state.pos)
            if region:
                self.state.regions.add(region.id)
            landmark = self.map.landmark_at(*self.state.pos)
            if landmark:
                self.state.discovered.add(landmark.id)
        self.update_vision()
        region = self.map.region_at(*self.state.pos)
        self._region_id = region.id if region else None
        self.needs_redraw = True

    # ------------------------------------------------------------------ tempo

    def advance_time(self, minutes: int) -> None:
        change = self.clock.advance(minutes)
        self.player.regenerate(minutes)
        for buff in self.player.expire_buffs(self.clock.minutes):
            self.notify(ui.style(f"O efeito de {buff['name']} terminou.", "gray"))
        if change.dawns:
            self.notify(ui.style(f"{ui.sym('sun')} Amanhece o Dia {self.clock.day}. "
                                 f"Clima: {self.clock.weather['name']}.", "bright_yellow"))
            if self.settings.autosave:
                self.pending_autosave = True
        elif change.period_changed and self.map.outdoor:
            self.notify(ui.style(PERIOD_MESSAGES[change.period_changed], "gray italic"))
        self.dirty = True

    def wait(self, hours: int) -> None:
        hours = max(1, min(24, hours))
        self.advance_time(hours * 60)
        self.update_vision()
        self.notify(f"Você espera {hours} {'hora' if hours == 1 else 'horas'}. "
                    f"Agora são {self.clock.time_str} ({self.clock.period_name}).")
        self.needs_redraw = True

    def rest(self) -> None:
        landmark = self.map.landmark_at(*self.state.pos)
        player = self.player
        self.needs_redraw = True
        if landmark and landmark.rest:
            if 7 <= self.clock.hour < 17:
                self.advance_time(120)
                self.notify("Ainda é dia claro. Você tira um cochilo de duas horas num quarto da estalagem.")
            else:
                self.advance_time(self.clock.minutes_until(7))
                self.notify(f"Você dorme profundamente num quarto quente da estalagem e acorda com energia "
                            f"renovada às {self.clock.time_str} do Dia {self.clock.day}.")
                if self.settings.autosave:
                    self.pending_autosave = True
            player.restore()
            self.update_vision()
            return
        encounters = self._region_encounters()
        if encounters and not landmark and self.rng.random() < min(0.5, 3 * self._encounter_chance(encounters)):
            group = monsters.pick_group(encounters, self.state, self.rng, self.map.outdoor)
            if group:
                self.advance_time(20)
                self.pending_battle = BattleRequest(group, "aleatorio", ambush=True,
                                                    intro="Você mal fecha os olhos e algo salta sobre você!")
                return
        self.advance_time(60)
        player.restore()
        self.update_vision()
        self.notify("Você encontra um canto abrigado e descansa por uma hora.")

    def sync_play_time(self) -> None:
        now = time.monotonic()
        self.state.play_seconds += now - self._timer
        self._timer = now

    # ------------------------------------------------------------------ progressão e itens

    def gain_xp(self, amount: int, reason: str = "") -> None:
        if amount <= 0:
            return
        for level_up in self.player.gain_xp(amount):
            self.level_ups.append(level_up)
            self.notify(ui.style(f"{ui.sym('up')} NÍVEL {level_up.level}! Você se sente mais forte.",
                                 "bright_yellow bold"))
        self.dirty = True

    def start_quest(self, quest_id: str) -> None:
        if quests.start(self.state, quest_id):
            quest = quests.get_quest(quest_id)
            self.notify(ui.style(f"{ui.sym('star')} Nova missão: {quest['name']}", "bright_yellow bold"))
            self.notify(quest["stages"][0]["text"])
            self.dirty = True

    def update_quests(self) -> None:
        """Avança as missões (chamado depois de cada ação do jogador)."""
        quests.update(self)

    def add_journal(self, entry_id: str, title: str, text: str, category: str = "pista") -> None:
        if self.state.add_journal(entry_id, title, text, category):
            self.notify(ui.style(f"{ui.sym('star')} Diário atualizado: {title}", "bright_cyan"))
            self.dirty = True

    def give_item(self, item_id: str, quantity: int = 1) -> int:
        """Guarda itens na mochila; devolve quantos ficaram para trás por falta de espaço."""
        leftover = self.player.inventory.add(item_id, quantity)
        received = quantity - leftover
        if received:
            self.notify(f"Recebido: {item_name(item_id)} x{received}")
        if leftover:
            self.notify(ui.style(f"Sua mochila está cheia: {item_name(item_id, colored=False)} x{leftover} "
                                 "ficou para trás.", "red"))
        self.dirty = True
        return leftover

    def give_copper(self, amount: int) -> None:
        self.player.copper += amount
        self.notify(f"Recebido: {ui.style(format_money(amount), 'bright_yellow')}")
        self.dirty = True

    def use_item(self, stack: ItemStack) -> bool:
        """Usa um consumível fora de combate (comer, beber, poções, elixires, venenos de arma)."""
        use = stack.data.get("use")
        if not use:
            self.notify(f"Não há como usar {stack.name()}.")
            return False
        if use.get("combat_only"):
            self.notify(f"{stack.name()} só serve no meio de uma luta: arremesse-o num inimigo.")
            return False
        self.notify(apply_consumable(self.player, stack.item_id, self.rng, now=self.clock.minutes))
        self.advance_time(use.get("minutes", 1))
        return True

    # ------------------------------------------------------------------ ofícios

    def gather(self, spot: crafting.Spot, quantity: int) -> Optional[crafting.GatherReport]:
        """Coleta num ponto do local atual (minerar, pescar, colher)."""
        problem = crafting.gather_problem(self.player, self.state, spot)
        if problem:
            self.notify(problem)
            return None
        report = crafting.gather(self.player, self.state, spot, quantity, self.rng)
        self.advance_time(report.minutes)
        refill = crafting.minutes_to_refill(self.state, spot)
        lines = [ui.style(spot.data.get("verb", ""), "italic")] if spot.data.get("verb") else []
        if report.items:
            got = ", ".join(f"{item_name(item_id)} x{quantity}" for item_id, quantity in report.items.items())
            lines.append(f"Em {report.minutes} min, você consegue: {got} "
                         + ui.style(f"(+{report.xp} XP de {crafting.skill_name(report.skill)})", "bright_magenta"))
        else:
            lines.append(f"Você passa {report.minutes} min tentando, mas não consegue nada desta vez.")
        for rare_id in report.rare:
            lines.append(ui.style(f"{ui.sym('star')} Achado raro: {item_name(rare_id, colored=False)}!",
                                  "bright_yellow bold"))
        stops = {
            "esgotado": f"{spot.name} se esgotou. Volta a render aos poucos (cerca de {refill} min para o próximo).",
            "isca": "Suas iscas acabaram.",
            "mochila": "Sua mochila está cheia.",
            "cansaco": "Depois de horas de trabalho, seus braços pedem uma pausa.",
        }
        if report.stopped in stops:
            lines.append(ui.style(stops[report.stopped], "gray"))
        for line in lines:
            self.notify(line)
        self._skill_level_ups(report.level_ups)
        self.dirty = True
        return report

    def craft(self, recipe_id: str, quantity: int) -> Optional[crafting.CraftReport]:
        """Produz itens de uma receita no local atual (forjar, cozinhar, costurar, preparar)."""
        landmark = self.map.landmark_at(*self.state.pos)
        problem = crafting.craft_problem(self.player, self.state, landmark, recipe_id)
        if problem:
            self.notify(problem)
            return None
        report = crafting.craft(self.player, self.state, landmark, recipe_id, quantity, self.rng)
        self.advance_time(report.minutes)
        output_id, output_qty = crafting.recipe_output(recipe_id)
        skill = crafting.RECIPES[recipe_id]["skill"]
        if report.fuel:
            self.notify(ui.style(f"Você acende o fogo com {item_name(report.fuel, colored=False).lower()}.", "italic"))
        if report.made:
            self.notify(f"Você faz {item_name(output_id)} x{report.made * output_qty} em {report.minutes} min "
                        + ui.style(f"(+{report.xp} XP de {crafting.skill_name(skill)})", "bright_magenta"))
        if report.burnt:
            self.notify(ui.style(f"Você deixou queimar {report.burnt}: virou {item_name('comida_queimada', colored=False)}.",
                                 "red"))
        if report.failed:
            self.notify(ui.style(f"{report.failed} se perdeu: o material impuro se esfarelou na fornalha.", "red"))
        if report.stopped == "mochila":
            self.notify(ui.style("Sua mochila está cheia: não há onde guardar o que você fez.", "red"))
        self._skill_level_ups(report.level_ups)
        self.dirty = True
        return report

    def _skill_level_ups(self, level_ups: List[Tuple[str, int]]) -> None:
        for skill_id, level in level_ups:
            unlocked = crafting.unlocks(skill_id, level)
            extra = f" Novo: {', '.join(unlocked)}." if unlocked else ""
            self.notify(ui.style(f"{ui.sym('up')} {crafting.skill_name(skill_id)} subiu para o nível {level}!{extra}",
                                 "bright_yellow bold"))

    # ------------------------------------------------------------------ visão

    def vision_radius(self) -> int:
        game_map = self.map
        if game_map.outdoor:
            if self.clock.is_night:
                radius = 1
            elif self.clock.is_twilight:
                radius = 2
            else:
                radius = 3
            radius += self.clock.weather["vision"]
        else:
            radius = game_map.light
        radius += game_map.terrain_at(*self.state.pos).vision + self.player.vision_bonus
        return max(1, radius)

    def update_vision(self) -> None:
        self.visible = set(self.map.tiles_in_radius(self.state.x, self.state.y, self.vision_radius()))
        self.state.explored_on(self.state.map_id).update(self.visible)

    def reveal(self, radius: int) -> None:
        tiles = self.map.tiles_in_radius(self.state.x, self.state.y, radius)
        self.state.explored_on(self.state.map_id).update(tiles)

    # ------------------------------------------------------------------ movimento

    def step(self, dx: int, dy: int) -> bool:
        """Tenta dar um passo. Devolve ``True`` se o herói se moveu (inclusive para outro mapa)."""
        x, y = self.state.pos
        direction = next(key for key, (ddx, ddy, _n) in world.DIRECTIONS.items() if (ddx, ddy) == (dx, dy))
        for portal in self.map.portals_at(x, y):
            if portal.direction == direction and portal.is_known(self.state.flags):
                return self.use_portal(portal)
        nx, ny = x + dx, y + dy
        if not self.map.in_bounds(nx, ny):
            self.notify("Não há caminho nessa direção.")
            return False
        if not self.map.can_step(x, y, dx, dy):
            target = self.map.terrain_at(nx, ny)
            if target.passable:
                self.notify("Não dá para cortar caminho nessa diagonal: siga pelos lados.")
            else:
                self.notify(BLOCKED_TEXT.get(target.id, "Não é possível seguir nessa direção."))
            return False
        self.previous = (self.state.map_id, x, y)
        self.state.x, self.state.y = nx, ny
        self.state.stats["passos"] = self.state.stats.get("passos", 0) + 1
        self.advance_time(self.map.terrain_at(nx, ny).cost)
        self.arrive()
        self._check_encounters()
        return True

    def arrive(self) -> None:
        """Chegou a um tile: atualiza a visão e registra descobertas e encontros."""
        self.update_vision()
        x, y = self.state.pos
        game_map = self.map
        region = game_map.region_at(x, y)
        if region and region.id not in self.state.regions:
            self.state.regions.add(region.id)
            xp_text = f" (+{region.xp} XP)" if region.xp else ""
            self.notify(ui.style(f"{ui.sym('diamond')} Nova área: {region.name}{xp_text}", "bright_magenta bold"))
            if region.intro:
                self.notify(ui.style(region.intro, "italic"))
            self.gain_xp(region.xp, "exploração")
            self.events.add(EVENT_DISCOVERY)
        elif region and region.id != self._region_id:
            self.notify(ui.style(f"Você entra em: {region.name}", "magenta"))
        self._region_id = region.id if region else None
        landmark = game_map.landmark_at(x, y)
        if landmark and landmark.id not in self.state.discovered:
            self.state.discovered.add(landmark.id)
            xp_text = f" (+{landmark.xp} XP)" if landmark.xp else ""
            self.notify(ui.style(f"{ui.sym('star')} Local descoberto: {landmark.name}{xp_text}", "bright_yellow bold"))
            self.gain_xp(landmark.xp, "exploração")
            if landmark.reveal:
                self.reveal(landmark.reveal)
                self.notify(ui.style("Do alto, você memoriza o terreno ao redor: seu mapa foi ampliado.", "bright_cyan"))
            self.events.add(EVENT_DISCOVERY)
        if npcs_at(self.state, self.state.map_id, x, y):
            self.events.add(EVENT_NPC)
        if any(p.is_known(self.state.flags) for p in game_map.portals_at(x, y)):
            self.events.add(EVENT_PASSAGE)
        self.dirty = True

    def walk(self, direction: str, steps: int = 1) -> int:
        """Anda até ``steps`` passos; para antes se algo interessante acontecer."""
        dx, dy, _name = world.DIRECTIONS[direction]
        moved = 0
        self.events.clear()
        start_map = self.state.map_id
        for _ in range(max(1, steps)):
            if not self.step(dx, dy):
                break
            moved += 1
            if self.events or self.state.map_id != start_map:
                break
        if 1 < steps and 0 < moved < steps and self.events - {EVENT_COMBAT}:
            self.notify(ui.style(f"Você interrompe a caminhada após {moved} "
                                 f"{'passo' if moved == 1 else 'passos'}.", "gray"))
        self.needs_redraw = True
        return moved

    def travel_to(self, landmark: world.Landmark) -> bool:
        """Viagem rápida até um local já descoberto, só por caminhos conhecidos."""
        explored = self.state.explored_on(self.state.map_id)
        path = self.map.find_path(self.state.pos, landmark.pos, allowed=lambda x, y: (x, y) in explored)
        if path is None:
            self.notify("Você não conhece um caminho até lá. Explore mais o mapa.")
            return False
        if not path:
            self.notify("Você já está aqui.")
            return False
        start_minutes = self.clock.minutes
        self.events.clear()
        steps = 0
        for nx, ny in path:
            x, y = self.state.pos
            if not self.step(nx - x, ny - y):
                break
            steps += 1
            if self.pending_battle:
                break
            if EVENT_DISCOVERY in self.events and self.state.pos != landmark.pos:
                self.notify(ui.style("Algo novo chama sua atenção no caminho, e você para.", "gray"))
                break
        elapsed = self.clock.minutes - start_minutes
        self.notify(ui.style(f"Viagem: {steps} {'passo' if steps == 1 else 'passos'}, "
                             f"{elapsed // 60}h{elapsed % 60:02d}min de caminhada.", "gray"))
        self.needs_redraw = True
        return self.state.pos == landmark.pos

    def use_portal(self, portal: world.Portal) -> bool:
        if portal.is_locked(self.state.flags, self.player.level):
            self.notify(ui.style(portal.locked_text or "A passagem está bloqueada.", "italic"))
            return False
        if portal.target is None:
            self.notify("Esse caminho ainda não leva a lugar nenhum.")
            return False
        if portal.travel_text:
            self.notify(ui.style(portal.travel_text, "italic"))
        map_id, x, y = portal.target
        self.previous = None
        self.state.map_id, self.state.x, self.state.y = map_id, x, y
        self.advance_time(10)
        self.arrive()
        self.events.add(EVENT_PASSAGE)
        self.encounter_grace = max(self.encounter_grace, 2)
        self.needs_redraw = True
        return True

    def use_verb(self, verb: str) -> bool:
        """``entrar``/``sair``/``navegar``: atravessa a passagem deste tile que aceita o verbo."""
        for portal in self.map.portals_at(*self.state.pos):
            if portal.verb == verb and portal.is_known(self.state.flags):
                self.use_portal(portal)
                return True
        return False

    # ------------------------------------------------------------------ encontros

    def _region_encounters(self) -> Optional[Dict[str, Any]]:
        region = self.map.region_at(*self.state.pos)
        return region.encounters if region else None

    def _encounter_chance(self, encounters: Dict[str, Any]) -> float:
        chance = monsters.encounter_chance(encounters, self.state, self.map.outdoor)
        return chance * SAFE_TERRAINS.get(self.map.terrain_at(*self.state.pos).id, 1.0)

    def _check_encounters(self) -> None:
        if self.pending_battle or self._check_fixed_encounter():
            return
        if self.encounter_grace > 0:
            self.encounter_grace -= 1
            return
        encounters = self._region_encounters()
        if not encounters or self.map.landmark_at(*self.state.pos):
            return
        if self.rng.random() >= self._encounter_chance(encounters):
            return
        group = monsters.pick_group(encounters, self.state, self.rng, self.map.outdoor)
        if group:
            ambush_chance = AMBUSH_CHANCE / 2 if self.player.resource_id == "energia" else AMBUSH_CHANCE
            self.pending_battle = BattleRequest(group, "aleatorio", ambush=self.rng.random() < ambush_chance)
            self.events.add(EVENT_COMBAT)

    def _check_fixed_encounter(self) -> bool:
        x, y = self.state.pos
        for landmark in self.map.landmarks.values():
            encounter = landmark.encounter
            if not encounter or self.state.has_flag(encounter["flag"]):
                continue
            if not conditions_met(encounter.get("if"), self.state):
                continue
            near = max(abs(landmark.x - x), abs(landmark.y - y)) <= encounter.get("radius", 0)
            if not near:
                self.suppressed.discard(landmark.id)
                continue
            if landmark.id in self.suppressed:
                continue
            self.pending_battle = BattleRequest(
                [(template_id, level) for template_id, level in encounter["monsters"]], "fixo",
                intro=encounter.get("intro", ""), boss=encounter.get("boss", False),
                landmark_id=landmark.id, encounter=encounter)
            self.events.add(EVENT_COMBAT)
            return True
        return False

    def hunt(self) -> bool:
        """Procura uma presa na região atual (gasta tempo; luta garantida se houver criaturas)."""
        encounters = self._region_encounters()
        if not encounters:
            self.notify("Não há nada para caçar por aqui.")
            return False
        self.advance_time(20)
        group = monsters.pick_group(encounters, self.state, self.rng, self.map.outdoor)
        if not group:
            self.notify("Você procura por um bom tempo, mas nenhuma criatura aparece a esta hora.")
            self.needs_redraw = True
            return False
        self.pending_battle = BattleRequest(group, "caca",
                                            intro="Depois de algum tempo seguindo rastros, você encontra sua presa.")
        return True

    def danger(self) -> Optional[Tuple[int, int]]:
        return monsters.danger_range(self._region_encounters(), self.state, self.map.outdoor)

    def retreat(self, request: BattleRequest) -> None:
        """Recua de um encontro fixo para o passo anterior; ele só volta quando o herói se afastar."""
        if request.landmark_id:
            self.suppressed.add(request.landmark_id)
        if self.previous and self.previous[0] == self.state.map_id:
            self.state.x, self.state.y = self.previous[1], self.previous[2]
            self.update_vision()
        self.needs_redraw = True

    def avoid(self, request: BattleRequest) -> bool:
        """Tenta escapar de um encontro aleatório sem lutar."""
        levels = [level for _template, level in request.monsters]
        chance = 0.45 + 0.05 * (self.player.level - sum(levels) / len(levels))
        if self.player.resource_id == "energia":
            chance += 0.3
        if self.map.outdoor and self.clock.is_night:
            chance += 0.1
        if self.rng.random() < max(0.1, min(0.95, chance)):
            self.encounter_grace = ENCOUNTER_GRACE
            return True
        return False

    # ------------------------------------------------------------------ fim de luta

    def finish_battle(self, battle: Battle, request: BattleRequest) -> BattleReport:
        """Aplica o resultado de uma luta: experiência, saque, bestiário, marcos e derrota."""
        player, state = self.player, self.state
        self.pending_battle = None
        self.encounter_grace = ENCOUNTER_GRACE
        state.learn(battle.knowledge)
        for enemy in battle.enemies:
            state.bestiary_entry(enemy.template_id)
        player.clamp_vitals()
        if player.resource_id != "mana":
            player.resource = 0 if player.resource_id == "raiva" else player.max_resource
        report = BattleReport(battle.outcome or "")
        self.needs_redraw = True
        self.dirty = True
        if battle.outcome == OUTCOME_VICTORY:
            state.stats["vitorias"] = state.stats.get("vitorias", 0) + 1
            level = player.level
            for enemy in battle.defeated:
                report.xp += monsters.kill_xp(level, enemy.level, enemy.elite)
                loot, copper = monsters.roll_loot(enemy, self.rng)
                report.copper += copper
                for item_id, quantity in loot:
                    leftover = player.inventory.add(item_id, quantity)
                    if quantity - leftover:
                        report.items.append((item_id, quantity - leftover))
                    if leftover:
                        report.lost_items.append((item_id, leftover))
                state.record_kill(enemy.template_id, [item_id for item_id, _q in loot])
                quests.record_kill(state, enemy.template_id)
            player.copper += report.copper
            encounter = request.encounter or {}
            if encounter.get("flag"):
                state.flags[encounter["flag"]] = True
                report.text = encounter.get("victory", "")
                for item_id, quantity in item_pairs(encounter.get("items")):
                    leftover = player.inventory.add(item_id, quantity)
                    if quantity - leftover:
                        report.items.append((item_id, quantity - leftover))
                    if leftover:
                        report.lost_items.append((item_id, leftover))
                journal = encounter.get("journal")
                if journal:
                    self.add_journal(journal["id"], journal["title"], journal["text"], "segredo")
            self.gain_xp(report.xp, "combate")
        elif battle.outcome == OUTCOME_DEFEAT:
            report.copper_lost = self.respawn()
        else:
            if request.landmark_id:
                self.retreat(request)
        return report

    def respawn(self) -> int:
        """Depois de uma derrota, o herói desperta na Capela da Aurora. Devolve o cobre perdido."""
        player, state = self.player, self.state
        lost = player.copper // 10
        player.copper -= lost
        state.stats["derrotas"] = state.stats.get("derrotas", 0) + 1
        state.map_id, state.x, state.y = RESPAWN
        self.previous = None
        self.suppressed.clear()
        self.advance_time(240)
        player.hp = max(1, player.max_hp // 2)
        player.resource = player.max_resource // 2 if player.resource_data["starts_full"] else 0
        region = self.map.region_at(*state.pos)
        self._region_id = region.id if region else None
        self.update_vision()
        return lost

    # ------------------------------------------------------------------ interação

    def examine(self) -> List[str]:
        """Examina o lugar atual. Pode revelar segredos ou recompensas."""
        landmark = self.map.landmark_at(*self.state.pos)
        state = self.state
        self.advance_time(5)
        if landmark is None:
            terrain = self.map.terrain_at(*state.pos)
            return [f"Você examina os arredores ({terrain.name.lower()}) com atenção, mas não encontra nada "
                    "fora do comum."]
        secret = landmark.secret
        hidden = bool(secret) and not state.has_flag(secret["flag"])
        skilled = hidden and all(self.player.skills.level(skill_id) >= level
                                 for skill_id, level in secret.get("skill", {}).items())
        allowed = hidden and conditions_met(secret.get("if"), state)
        if hidden and skilled and allowed:
            state.flags[secret["flag"]] = True
            self.notify(ui.style(f"{ui.sym('star')} Segredo descoberto! (+{secret.get('xp', 0)} XP)",
                                 "bright_magenta bold"))
            self.gain_xp(secret.get("xp", 0), "segredo")
            journal = secret.get("journal")
            if journal:
                self.add_journal(secret["flag"], journal["title"], journal["text"], "segredo")
            return [secret["text"]]
        chest = landmark.chest
        if chest and not state.has_flag(chest["flag"]):
            return self._open_chest(landmark, chest)
        loot = landmark.loot
        if loot and not state.has_flag(loot["flag"]):
            state.flags[loot["flag"]] = True
            self.notify(ui.style(f"{ui.sym('star')} Tesouro encontrado! (+{loot.get('xp', 0)} XP)",
                                 "bright_yellow bold"))
            for item_id, quantity in loot.get("items", []):
                self.give_item(item_id, quantity)
            if loot.get("copper"):
                self.give_copper(loot["copper"])
            self.gain_xp(loot.get("xp", 0), "tesouro")
            return [loot["text"]]
        texts = [landmark.examine or landmark.description]
        if hidden and secret.get("hint"):
            needs = ""
            if not skilled:
                needs = " (" + ", ".join(f"{crafting.skill_name(skill_id)} {level}"
                                         for skill_id, level in secret["skill"].items()) + ")"
            texts.append(ui.style(secret["hint"] + needs, "gray"))
        return texts

    def _open_chest(self, landmark: world.Landmark, chest: Dict[str, Any]) -> List[str]:
        """Baú trancado: abre com a chave certa, ou um ladino experiente arromba."""
        state, player = self.state, self.player
        key = chest.get("key")
        how = None
        if "if" in chest and conditions_met(chest["if"], state):
            how = chest.get("opens", "O fecho cede sozinho, como se reconhecesse você.")
        elif key and player.inventory.count(key):
            if chest.get("consume_key", True):
                player.inventory.remove(key, 1)
            how = f"Você usa {item_name(key, colored=False)} na fechadura. Clique."
        elif chest.get("pick") and player.class_id == "ladino" and player.level >= chest["pick"]:
            self.advance_time(10)
            how = "Você trabalha a fechadura com uma gazua improvisada e, depois de alguns minutos, ela cede."
        if how is None:
            hints = [f"falta {item_name(key, colored=False)}"] if key else []
            if chest.get("pick"):
                hints.append(f"um ladino de nível {chest['pick']} conseguiria arrombar")
            return [landmark.examine or landmark.description,
                    ui.style(chest.get("locked", "Está trancado.") + (f" ({'; '.join(hints)})" if hints else ""),
                             "gray")]
        state.flags[chest["flag"]] = True
        self.notify(ui.style(f"{ui.sym('star')} Baú aberto! (+{chest.get('xp', 0)} XP)", "bright_yellow bold"))
        for item_id, quantity in chest.get("items", []):
            self.give_item(item_id, quantity)
        if chest.get("copper"):
            self.give_copper(chest["copper"])
        self.gain_xp(chest.get("xp", 0), "tesouro")
        return [how, chest["text"]]

    def npcs_here(self) -> List[NPC]:
        return npcs_at(self.state, self.state.map_id, *self.state.pos)

    def save(self) -> Path:
        self.sync_play_time()
        path = save_system.save_game(self.state)
        self.dirty = False
        self.pending_autosave = False
        return path

    # ------------------------------------------------------------------ descrição

    def describe(self) -> LocationView:
        state, game_map, clock = self.state, self.map, self.clock
        x, y = state.pos
        terrain = game_map.terrain_at(x, y)
        region = game_map.region_at(x, y)
        landmark = game_map.landmark_at(x, y)
        night = game_map.outdoor and clock.is_night
        region_name = region.name if region else game_map.name

        if landmark:
            title, subtitle = landmark.name, f"{region_name} {ui.sym('dot')} ({x}, {y})"
            paragraphs = [landmark.night if night and landmark.night else landmark.description]
        else:
            title, subtitle = region_name, f"{terrain.name} {ui.sym('dot')} ({x}, {y})"
            pool = terrain.night if night else terrain.day
            paragraphs = [stable_choice(pool, game_map.id, x, y)]

        ambient = (region.night if night else region.day) if region else ()
        if ambient and stable_hash(game_map.id, x, y, clock.day, "ambiente") % 2 == 0:
            paragraphs.append(stable_choice(ambient, game_map.id, x, y, clock.day))

        if game_map.outdoor:
            weather_id = clock.weather_id()
            if weather_id in ("chuva", "neblina", "tempestade") or stable_hash(x, y, clock.day) % 3 == 0:
                lines = clock.weather["night" if clock.is_night else "day"]
                paragraphs.append(ui.style(stable_choice(lines, clock.day, x, y), "cyan"))

        senses = self._senses()
        if senses:
            paragraphs.append(ui.style(" ".join(senses), "gray"))

        exits = [key.upper() for key, (dx, dy, _n) in world.DIRECTIONS.items() if game_map.can_step(x, y, dx, dy)]
        passages = []
        for portal in game_map.portals_at(x, y):
            if not portal.is_known(state.flags):
                continue
            how = f"'{portal.verb}'" if portal.verb else world.DIRECTIONS[portal.direction][2]
            lock = ""
            if portal.is_locked(state.flags, self.player.level):
                lock = f" (nível {portal.min_level}+)" if self.player.level < portal.min_level else " (bloqueado)"
            passages.append(f"{portal.label} {ui.sym('arrow')} {how}{lock}")
            if portal.direction and portal.direction.upper() not in exits:
                exits.append(portal.direction.upper())
        resources, stations, actions = [], [], []
        for spot in crafting.spots_at(landmark, state):
            data = spot.data
            actions.append(GATHER_VERBS[data["skill"]])
            label = f"{data['name']} ({SKILLS[data['skill']]['name']} {data['level']})"
            if not crafting.node_open(spot, state):
                label += " " + ui.style("[fechado agora]", "gray")
            elif crafting.node_left(state, spot) <= 0:
                label += " " + ui.style("[esgotado]", "gray")
            resources.append(label)
        for station in landmark.stations if landmark else ():
            actions.append(STATIONS[station["id"]]["verb"])
            name = station.get("name", crafting.station_name(station["id"]))
            open_now = crafting.station_at(landmark, station["id"], state)[0] is not None
            stations.append(name if open_now else name + " " + ui.style("[fechada]", "gray"))
        board = ""
        if landmark and landmark.id == quests.BOARD_LANDMARK:
            free = sum(1 for bounty_id in quests.offers(state) if quests.bounty_status(state, bounty_id) == "livre")
            ready = sum(1 for bounty_id in quests.active_bounties(state) if quests.bounty_ready(state, bounty_id))
            board = f"{free} {'tarefa nova' if free == 1 else 'tarefas novas'} hoje"
            if ready:
                board += f", {ready} pronta{'s' if ready > 1 else ''} para entregar"
            board += " ('avisos')."
        return LocationView(title, subtitle, paragraphs, self.npcs_here(), resources, exits, passages,
                            bool(landmark and landmark.rest), self.danger(), stations,
                            list(dict.fromkeys(actions)), board)

    def _senses(self) -> List[str]:
        """Dicas sobre locais próximos: pistas dos não descobertos e direções dos conhecidos."""
        game_map, state = self.map, self.state
        hints, nearby = [], []
        for landmark in game_map.landmarks.values():
            if landmark.pos == state.pos:
                continue
            distance = max(abs(landmark.x - state.x), abs(landmark.y - state.y))
            direction = world.direction_between(state.pos, landmark.pos)
            if direction is None:
                continue
            direction_name = world.DIRECTIONS[direction][2].lower()
            if landmark.id in state.discovered:
                if distance <= 3:
                    nearby.append((distance, f"{landmark.name} ({direction.upper()})"))
            elif landmark.hint and not landmark.hidden and distance <= 6:
                hints.append(landmark.hint.format(direcao=direction_name))
        texts = hints[:2]
        if nearby:
            nearby.sort()
            texts.append("Por perto: " + ", ".join(name for _d, name in nearby[:4]) + ".")
        return texts
