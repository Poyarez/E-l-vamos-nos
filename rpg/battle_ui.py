"""Interface de combate: encontro, tela da luta, barra de ações, reflexos e resultados.

Comandos durante a luta: os números da barra de ações (``1``–``9``, opcionalmente seguidos
do número do alvo, como ``1 2``), ``a`` atacar, ``d`` defender, ``i`` itens, ``x`` analisar,
``f`` fugir e ``?`` ajuda. Também dá para digitar o nome da habilidade.
"""

from __future__ import annotations

from typing import List, Optional

from . import screens, ui
from .combat import (CC_KINDS, OUTCOME_DEFEAT, OUTCOME_FLED, OUTCOME_VICTORY, Battle, Hero, Monster,
                     combo_display, describe_knowledge, element_label)
from .data.monsters import FAMILIES
from .items import get_item, item_name
from .monsters import con_color, create_monster
from .session import BattleReport, BattleRequest, GameSession
from .utils import format_money, normalize

#: Habilidades com estes efeitos usam o minijogo de "golpe no tempo certo".
TIMED_EFFECTS = {"damage", "finisher", "execute", "heal"}

COMBAT_HELP = [
    "Números (1–9): habilidades da barra de ações. Acrescente o alvo: '1 2' usa a habilidade 1 no inimigo 2.",
    "a: atacar com a arma   d: defender (metade do dano até o próximo turno)   i: usar um item (poções e frascos)",
    "x: analisar um inimigo (revela fraquezas e resistências, e o bestiário lembra para sempre)",
    "f: fugir (impossível contra chefes)",
    "Selos: quando uma criatura concentra um golpe especial, acerte-a com os elementos indicados para "
    "enfraquecê-lo — ou cancelá-lo de vez, se romper todos.",
    "Reflexos: com a opção ligada, aperte Enter logo que surgir o sinal para golpes e bloqueios perfeitos.",
]


def run(session: GameSession) -> None:
    """Conduz o encontro pendente da sessão, do aviso inicial à tela de resultados."""
    request = session.pending_battle
    if request is None:
        return
    enemies = [create_monster(template_id, level, session.rng) for template_id, level in request.monsters]
    for enemy in enemies:
        session.state.bestiary_entry(enemy.template_id)
    choice = _encounter_screen(session, request, enemies)
    if choice == "recuar":
        session.pending_battle = None
        session.retreat(request)
        session.notify("Você recua em silêncio. Talvez seja melhor se preparar antes.")
        return
    if choice == "deixar":
        session.pending_battle = None
        session.encounter_grace = 2
        session.needs_redraw = True
        return
    enemies_first = request.ambush
    if choice == "evitar":
        if session.avoid(request):
            session.pending_battle = None
            session.needs_redraw = True
            session.notify("Você se afasta devagar e escapa sem chamar atenção.")
            return
        ui.echo(ui.style("  Não deu! As criaturas percebem você e atacam primeiro.", "bright_red"))
        ui.pause()
        enemies_first = True
    battle = _fight(session, request, enemies, enemies_first, stealth=choice == "emboscar")
    report = session.finish_battle(battle, request)
    _results(session, battle, report)


# --------------------------------------------------------------------------- encontro

def _enemy_label(enemy: Monster, player_level: int) -> str:
    level = ui.style(f"nível {enemy.level}", con_color(player_level, enemy.level))
    extras = [FAMILIES.get(enemy.data.get("family", ""), "")]
    if enemy.elite:
        extras.append(ui.style("elite", "bright_yellow"))
    return f"{ui.style(enemy.name, 'bold')} ({level}) " + ui.style(" · ".join(e for e in extras if e), "gray")


def _encounter_screen(session: GameSession, request: BattleRequest, enemies: List[Monster]) -> str:
    ui.clear()
    width = screens.screen_width()
    player = session.player
    if request.intro:
        intro = request.intro
    elif len(enemies) == 1:
        intro = f"{enemies[0].name} aparece no seu caminho!"
    else:
        intro = "Criaturas cercam você!"
    lines = ui.wrap(ui.style(intro, "italic"), width - 4) + [""]
    lines += [f"{ui.sym('bullet')} {_enemy_label(enemy, player.level)}" for enemy in enemies]
    color = "bright_red" if request.boss else "red"
    title = ui.style(f"{ui.sym('sword')} {'CHEFE' if request.boss else 'ENCONTRO'} {ui.sym('sword')}",
                     color + " bold")
    ui.echo_lines(ui.box(lines, width, title=title, double=True, color=color))
    ui.echo()
    if request.ambush:
        ui.echo(ui.style("  Emboscada! Não há tempo para pensar.", "bright_red bold"))
        ui.pause("Pressione Enter para lutar...")
        return "lutar"
    if request.kind == "fixo":
        options, keys = ["Lutar", "Recuar"], ["lutar", "recuar"]
    elif request.kind == "caca":
        options, keys = ["Atacar", "Deixar para lá"], ["lutar", "deixar"]
    else:
        options, keys = ["Lutar", "Tentar evitar a luta"], ["lutar", "evitar"]
    if player.resource_id == "energia" and request.kind != "fixo":
        options.append("Emboscar (o primeiro golpe sai das sombras: crítico garantido)")
        keys.append("emboscar")
    choice = ui.choose(options, prompt="O que você faz")
    return keys[choice if choice is not None else 0]


# --------------------------------------------------------------------------- a luta

def _fight(session: GameSession, request: BattleRequest, enemies: List[Monster], enemies_first: bool,
           stealth: bool) -> Battle:
    battle = Battle(Hero(session.player), enemies, rng=session.rng, knowledge=session.state.knowledge(),
                    allow_flee=not request.boss, enemies_first=enemies_first, hero_stealth=stealth)
    battle.summon = lambda template_id, level: create_monster(template_id, level, session.rng)
    timing = session.settings.timing and ui.display.interactive
    shown = [0]
    if timing:
        battle.block_prompt = lambda text: _block(battle, shown, text, session)
    if stealth:
        battle.log.append("Você surge das sombras: o primeiro golpe será crítico.")
    battle.start()
    turn_start = 0
    while battle.outcome is None:
        _render(battle, battle.log[turn_start:])
        shown[0] = turn_start = len(battle.log)
        try:
            raw = ui.ask("\n  " + ui.style(f"Rodada {battle.round}", "gray") + " "
                         + ui.style("Sua ação", "bold") + f" {ui.sym('arrow')} ")
        except KeyboardInterrupt:
            battle.log.append(ui.style("Para sair da luta, tente fugir (f).", "gray"))
            continue
        _handle(battle, session, raw, timing)
    _render(battle, battle.log[turn_start:])
    ui.pause()
    return battle


def _block(battle: Battle, shown: List[int], text: str, session: GameSession) -> Optional[str]:
    """Mostra o que aconteceu até agora e abre o minijogo de bloqueio."""
    for line in battle.log[shown[0]:]:
        ui.echo_lines(ui.wrap(line, screens.screen_width() - 4, "  "))
    shown[0] = len(battle.log)
    return ui.timed_press(ui.style(f"{text} Defenda-se!", "bright_red bold"), session.rng)


def _effects_text(unit) -> str:
    parts = []
    for effect in unit.effects:
        if effect.kind == "shield":
            parts.append(ui.style(f"{effect.name} ({int(effect.amount)})", "bright_cyan"))
        elif effect.kind == "stealth":
            parts.append(ui.style("Furtividade", "magenta"))
        else:
            color = "bright_red" if effect.kind in CC_KINDS or effect.kind in ("dot", "debuff") else "bright_green"
            turns = "" if effect.turns >= 50 else f" ({effect.turns})"
            parts.append(ui.style(f"{effect.name}{turns}", color))
    if unit.is_hero:      # comidas, elixires e venenos de arma valem a luta inteira
        parts.extend(ui.style(buff["name"], "cyan") for buff in unit.player.buffs)
    return " ".join(parts)


def _render(battle: Battle, lines: List[str]) -> None:
    ui.clear()
    width = screens.screen_width()
    inner = width - 4
    hero = battle.hero
    bar_width = 12 if inner >= 76 else 8
    rows = []
    for index, enemy in enumerate(battle.enemies, 1):
        tag = ui.style(f"[{index}]", "bright_yellow")
        if not enemy.alive:
            rows.append(ui.style(f"[{index}] {enemy.name} — fora de combate", "gray"))
            continue
        level = ui.style(f"nv {enemy.level}", con_color(hero.level, enemy.level))
        ratio_color = "bright_red" if enemy.hp <= enemy.max_hp * 0.2 else "red"
        rows.append(f"{tag} {ui.style(enemy.name, 'bold')} {level}  {ui.bar(enemy.hp, enemy.max_hp, bar_width, ratio_color)}"
                    f" {enemy.hp}/{enemy.max_hp}  {_effects_text(enemy)}")
        rows.append("    " + describe_knowledge(enemy, battle.known(enemy))[0])
        if enemy.charging:
            charge = enemy.charging
            locks = " ".join(
                ui.style(f"[{'✓' if ui.display.unicode else 'x'}]", "gray") if broken else f"[{element_label(lock)}]"
                for lock, broken in zip(charge.locks, charge.broken))
            rows.append("    " + ui.style(f"CONCENTRANDO {charge.ability['name'].upper()} ({charge.turns})",
                                          "bright_magenta bold") + f"  Selos: {locks}")
    rows.append(ui.style(ui.sym("h") * inner, "gray"))
    resource = screens.resource_bar(hero.player, bar_width)
    rows.append(f"{ui.style(hero.name, 'bold')} {ui.style(f'nv {hero.level}', hero.player.color)}   "
                f"{screens.hp_bar(hero.player, bar_width)}   {resource}")
    extras = []
    if hero.resource_id == "energia":
        extras.append(f"Combo: {combo_display(hero.combo)}")
    effects = _effects_text(hero)
    if effects:
        extras.append(f"Efeitos: {effects}")
    if hero.crit_next:
        extras.append(ui.style("próximo golpe: crítico", "bright_yellow"))
    if extras:
        rows.append("   ".join(extras))
    title = ui.style(f"{ui.sym('sword')} COMBATE {ui.sym('dot')} Rodada {battle.round}", "bold")
    ui.echo_lines(ui.box(rows, width, title=title, double=True, color="red"))
    for line in lines:
        ui.echo_lines(ui.wrap(line, width - 4, "  "))
    if battle.outcome is None:
        ui.echo()
        ui.echo_lines(_action_bar(battle, width))


def _action_bar(battle: Battle, width: int) -> List[str]:
    hero = battle.hero
    resource = hero.player.resource_data
    entries = []
    for slot, ability in enumerate(hero.player.abilities(), 1):
        usable, _reason = battle.ability_status(ability)
        cost = f" {ability['cost']} {resource['name']}" if ability.get("cost") else ""
        ready = hero.cooldowns.get(ability["id"], 0) - battle.round
        status = f" (recarga {ready})" if ready > 0 else ""
        label = f"[{slot}] {ability['name']}{cost}{status}"
        entries.append(ui.style(label, "bright_white") if usable else ui.style(label, "gray"))
    potions = sum(stack.quantity for stack in hero.player.inventory
                  if stack.data.get("use", {}).get("combat", True) and stack.data.get("use"))
    basics = ["[a] atacar", "[d] defender", f"[i] itens ({potions})", "[x] analisar",
              "[f] fugir" if battle.allow_flee else ui.style("[f] fugir", "gray"), "[?] ajuda"]
    rows: List[str] = []
    current = "  "
    for entry in entries + [ui.style(b, "cyan") for b in basics]:
        if ui.visible_len(current) + ui.visible_len(entry) + 3 > width and current.strip():
            rows.append(current.rstrip())
            current = "  "
        current += entry + "   "
    rows.append(current.rstrip())
    return rows


# --------------------------------------------------------------------------- comandos

def _handle(battle: Battle, session: GameSession, raw: str, timing: bool) -> None:
    words = normalize(raw).split()
    if not words:
        return
    head, args = words[0], words[1:]
    abilities = battle.hero.player.abilities()
    if head.isdigit():
        slot = int(head)
        if 1 <= slot <= len(abilities):
            _use_ability(battle, session, abilities[slot - 1], args, timing)
        else:
            battle.log.append(ui.style("Não há habilidade nesse espaço da barra.", "gray"))
        return
    if head in ("a", "atacar", "ataque", "atk"):
        target = _pick_target(battle, args)
        if target is not None:
            battle.attack(target, _strike_timing(session, "Ataque", timing))
    elif head in ("d", "defender", "defesa", "bloquear"):
        battle.defend()
    elif head in ("i", "item", "itens", "usar", "pocao", "beber", "arremessar", "jogar"):
        _use_item(battle, session, args, timing)
    elif head in ("x", "analisar", "examinar"):
        target = _pick_target(battle, args)
        if target is not None:
            battle.analyze(target)
    elif head in ("f", "fugir", "correr"):
        battle.flee()
    elif head in ("?", "ajuda", "h"):
        battle.log.extend(ui.style(line, "gray") for line in COMBAT_HELP)
    else:
        typed = " ".join(words)
        matches = [a for a in abilities if normalize(a["name"]).startswith(typed)]
        if len(matches) == 1:
            _use_ability(battle, session, matches[0], [], timing)
        else:
            battle.log.append(ui.style("Ação desconhecida. Use os números da barra, a, d, i, x, f ou ?.", "gray"))


def _pick_target(battle: Battle, args: List[str]) -> Optional[int]:
    """Índice do alvo: o número digitado, o único inimigo vivo ou a escolha do jogador."""
    living = [index for index, enemy in enumerate(battle.enemies) if enemy.alive]
    if args and args[0].isdigit():
        index = int(args[0]) - 1
        if index in living:
            return index
        battle.log.append(ui.style("Esse alvo não está disponível.", "gray"))
        return None
    if len(living) == 1:
        return living[0]
    labels = [f"{battle.enemies[i].name} ({battle.enemies[i].hp}/{battle.enemies[i].max_hp})" for i in living]
    choice = ui.choose(labels, prompt="Alvo", cancel="Cancelar")
    return None if choice is None else living[choice]


def _strike_timing(session: GameSession, label: str, enabled: bool) -> Optional[str]:
    if not enabled:
        return None
    return ui.timed_press(ui.style(f"{label}! Aperte Enter no sinal...", "bright_yellow"), session.rng)


def _use_ability(battle: Battle, session: GameSession, ability: dict, args: List[str], timing: bool) -> None:
    target: Optional[int] = None
    if ability.get("target", "enemy") == "enemy":
        target = _pick_target(battle, args)
        if target is None:
            return
    usable, reason = battle.ability_status(ability, battle.enemies[target] if target is not None else None)
    if not usable:
        battle.log.append(ui.style(reason, "gray"))
        return
    timed = any(effect["type"] in TIMED_EFFECTS for effect in ability.get("effects", []))
    quality = _strike_timing(session, ability["name"], timing and timed)
    battle.use_ability(ability["id"], target, quality)


def _use_item(battle: Battle, session: GameSession, args: List[str], timing: bool) -> None:
    inventory = battle.hero.player.inventory
    usable = [stack for stack in inventory if stack.data.get("use") and stack.data["use"].get("combat", True)]
    if not usable:
        battle.log.append(ui.style("Você não tem nenhum item que sirva em combate.", "gray"))
        return
    chosen = None
    if args:
        typed = " ".join(args)
        matches = [stack for stack in usable if typed in normalize(stack.data["name"])]
        if len(matches) == 1:
            chosen = matches[0]
    if chosen is None:
        labels = [f"{stack.name()} x{stack.quantity}" + ui.style(f"  {stack.data['description']}", "gray")
                  for stack in usable]
        choice = ui.choose([ui.truncate(label, screens.screen_width() - 8) for label in labels],
                           prompt="Usar", cancel="Cancelar")
        if choice is None:
            return
        chosen = usable[choice]
    if chosen.data["use"].get("damage"):          # frasco de arremesso: escolhe o alvo e mira
        target = _pick_target(battle, [])
        if target is None:
            return
        quality = _strike_timing(session, f"Arremesso de {chosen.data['name']}", timing)
        battle.use_item(chosen.item_id, target, quality)
        return
    battle.use_item(chosen.item_id)


# --------------------------------------------------------------------------- resultados

def _results(session: GameSession, battle: Battle, report: BattleReport) -> None:
    width = min(screens.screen_width(), 90)
    lines: List[str] = []
    if report.outcome == OUTCOME_VICTORY:
        title = ui.style("VITÓRIA!", "bright_yellow bold")
        color = "bright_yellow"
        if report.text:
            lines += ui.wrap(ui.style(report.text, "italic"), width - 4) + [""]
        lines.append(ui.style(f"+{report.xp} XP", "bright_magenta bold"))
        if report.items:
            loot = ", ".join(f"{item_name(item_id)} x{quantity}" for item_id, quantity in report.items)
            lines += ui.wrap("Saque: " + loot, width - 4)
        if report.copper:
            lines.append("Moedas: " + ui.style(format_money(report.copper), "bright_yellow"))
        if report.lost_items:
            lost = ", ".join(f"{get_item(item_id)['name']} x{quantity}" for item_id, quantity in report.lost_items)
            lines += ui.wrap(ui.style(f"Mochila cheia! Ficou para trás: {lost}.", "red"), width - 4)
        if not report.items and not report.copper:
            lines.append(ui.style("As criaturas não deixaram nada de valor.", "gray"))
    elif report.outcome == OUTCOME_DEFEAT:
        title = ui.style("DERROTA", "bright_red bold")
        color = "bright_red"
        lines += ui.wrap(ui.style(
            "Tudo escurece. Horas depois, você desperta num banco da Capela da Aurora, com curativos limpos e "
            "cheiro de incenso. \"Um caçador trouxe você nos ombros\", diz a Irmã Celeste. \"A Aurora ainda não "
            "quer você ao lado dela.\"", "italic"), width - 4)
        if report.copper_lost:
            lines.append("")
            lines.append(ui.style(f"Na confusão, você perdeu {format_money(report.copper_lost)}.", "red"))
    elif report.outcome == OUTCOME_FLED:
        title = ui.style("FUGA", "bright_yellow bold")
        color = "yellow"
        lines.append("Você escapa e recupera o fôlego longe do perigo.")
    else:
        return
    ui.clear()
    ui.echo_lines(ui.box(lines, width, title=title, double=True, color=color))
    screens.show_messages(session)
    ui.echo()
    ui.pause()
