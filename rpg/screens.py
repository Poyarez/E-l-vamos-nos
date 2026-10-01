"""Telas do jogo: título, exploração (HUD + minimapa + descrição), ficha, mochila, perícias,
grimório, mapa completo, diário e comemoração de nível."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from . import mapview, ui, world
from .combat import element_label
from .config import GAME_SUBTITLE, GAME_VERSION
from .data.appearance import ALIGNMENTS
from .data.classes import CLASSES, RESOURCES, STATS, TALENT_START_LEVEL
from .data.items import ITEM_TYPES, SLOTS
from .player import LevelUp, Player
from .skills import SKILLS, level_progress
from .utils import format_duration, format_money

if TYPE_CHECKING:
    from .session import GameSession, LocationView

LOGO = [
    r" ____   ____   ___  __  __   ___   ____   ____   ___     _    ",
    r"|  _ \ |  _ \ |_ _||  \/  | / _ \ |  _ \ |  _ \ |_ _|   / \   ",
    r"| |_) || |_) | | | | |\/| || | | || |_) || | | | | |   / _ \  ",
    r"|  __/ |  _ <  | | | |  | || |_| ||  _ < | |_| | | |  / ___ \ ",
    r"|_|    |_| \_\|___||_|  |_| \___/ |_| \_\|____/ |___|/_/   \_\ ",
]


def screen_width() -> int:
    return min(ui.term_width(), 110)


def thousands(number: int) -> str:
    """12345 -> '12.345' (separador brasileiro)."""
    return f"{number:,}".replace(",", ".")


def title_screen() -> None:
    width = screen_width()
    ui.clear()
    ui.echo()
    ui.echo(ui.pad(ui.style("C  R  Ô  N  I  C  A  S     D  E", "gray"), width, "center"))
    for row, color in zip(LOGO, ("bright_yellow", "bright_yellow", "yellow", "yellow", "red")):
        ui.echo(ui.pad(ui.style(row, color + " bold"), width, "center"))
    ui.echo()
    ornament = f"{ui.sym('h') * 8} {ui.sym('moon')} {ui.sym('star')} {ui.sym('sun')} {ui.sym('h') * 8}"
    ui.echo(ui.pad(ui.style(ornament, "gray"), width, "center"))
    ui.echo(ui.pad(ui.style(GAME_SUBTITLE, "italic"), width, "center"))
    ui.echo(ui.pad(ui.style(f"versão {GAME_VERSION}", "gray"), width, "center"))
    ui.echo()


def section(title: str) -> None:
    """Cabeçalho de tela: limpa e desenha uma faixa com o título."""
    width = screen_width()
    ui.clear()
    ui.echo_lines(ui.box([ui.style(title, "bold bright_yellow")], width, double=True, color="yellow"))
    ui.echo()


# --------------------------------------------------------------------------- HUD

def _two_sided(left: str, right: str, width: int) -> str:
    gap = width - ui.visible_len(left) - ui.visible_len(right)
    if gap < 2:
        return ui.truncate(left, width)
    return left + " " * gap + right


def resource_bar(player: Player, width: int) -> str:
    data = player.resource_data
    return (ui.style(data["name"], data["color"]) + " " + ui.bar(player.resource, player.max_resource, width,
                                                                   data["color"])
            + f" {player.resource}/{player.max_resource}")


def hp_bar(player: Player, width: int) -> str:
    ratio = player.hp / max(1, player.max_hp)
    color = "bright_green" if ratio > 0.5 else "bright_yellow" if ratio > 0.25 else "bright_red"
    return ui.style("Vida", color) + " " + ui.bar(player.hp, player.max_hp, width, color) + f" {player.hp}/{player.max_hp}"


def xp_bar(player: Player, width: int) -> str:
    if not player.xp_needed:
        return ui.style("XP", "bright_magenta") + " " + ui.style("nível máximo", "bright_magenta")
    return (ui.style("XP", "bright_magenta") + " " + ui.bar(player.xp, player.xp_needed, width, "bright_magenta")
            + f" {player.xp}/{player.xp_needed}")


def hud(session: "GameSession", width: int) -> List[str]:
    player, clock, state = session.player, session.clock, session.state
    inner = width - 4
    bar_width = 10 if inner >= 76 else 6
    name = ui.style(player.name, "bold") + ui.style(f" {ui.sym('dot')} ", "gray") + ui.style(
        f"{player.class_name} nível {player.level}", player.color)
    line1 = _two_sided(name, ui.style(format_money(player.copper), "bright_yellow"), inner)
    line2 = "   ".join((hp_bar(player, bar_width), resource_bar(player, bar_width), xp_bar(player, bar_width)))
    icon = ui.style(ui.sym("moon"), "bright_white") if clock.is_night else ui.style(ui.sym("sun"), "bright_yellow")
    when = f"{icon} Dia {clock.day} {ui.sym('dot')} {clock.period_name} {clock.time_str}"
    if session.map.outdoor:
        when += f" {ui.sym('dot')} {clock.weather['name']}"
        if clock.is_night:
            when += f" {ui.sym('dot')} {clock.moon_phase}"
    where = ui.style(f"{session.map.name} ({state.x}, {state.y})", "gray")
    line3 = _two_sided(when, where, inner)
    return ui.box([line1, line2, line3], width, double=True, color="yellow")


# --------------------------------------------------------------------------- exploração

def location_panel(view: "LocationView", width: int) -> List[str]:
    rows = [ui.style(f"{ui.sym('diamond')} {view.title.upper()}", "bold bright_yellow"),
            ui.style("  " + view.subtitle, "gray"), ""]
    for paragraph in view.paragraphs:
        rows.extend(ui.wrap(paragraph, width))
        rows.append("")
    for npc in view.npcs:
        rows.extend(ui.wrap(f"{ui.style('!', 'bright_yellow bold')} Aqui: {ui.style(npc.name, npc.color + ' bold')} "
                            f"{ui.style('— ' + npc.title, 'gray')}", width))
    if view.npcs:
        rows.append(ui.style("  (use 'falar' para conversar)", "gray"))
    if view.resources:
        rows.extend(ui.wrap(ui.style("Coleta: ", "bright_green") + f" {ui.sym('dot')} ".join(view.resources), width))
    for passage in view.passages:
        rows.extend(ui.wrap(ui.style("Passagem: ", "bright_cyan") + passage, width))
    if view.can_rest:
        rows.extend(ui.wrap(ui.style("Descanso: ", "bright_blue") + "dá para dormir aqui ('descansar').", width))
    exits = f" {ui.sym('dot')} ".join(view.exits) if view.exits else "nenhum"
    rows.extend(ui.wrap(ui.style("Caminhos: ", "bold") + exits, width))
    return rows


def render_location(session: "GameSession") -> None:
    width = screen_width()
    ui.clear()
    ui.echo_lines(hud(session, width))
    view = session.describe()
    map_rows = mapview.minimap(session)
    map_width = mapview.minimap_width()
    markers = ui.style("@ você  ! pessoa  * local  ? novo", "gray")
    if width >= map_width + 42:
        panel = location_panel(view, width - map_width - 3)
        ui.echo_lines(ui.side_by_side(map_rows + [" " + markers], panel, map_width, gap=2))
    else:
        ui.echo_lines(map_rows)
        ui.echo(" " + markers)
        ui.echo()
        ui.echo_lines(location_panel(view, width - 2))
    show_messages(session)


def show_messages(session: "GameSession") -> None:
    messages = session.pop_messages()
    if messages:
        ui.echo()
        for message in messages:
            ui.echo_lines(ui.wrap(message, screen_width() - 4, "  "))
    while session.level_ups:
        ui.echo()
        ui.echo_lines(level_up_box(session.level_ups.pop(0), session.player))


def level_up_box(level_up: LevelUp, player: Player) -> List[str]:
    gains = [f"{STATS[stat]['short']} +{value}" for stat, value in level_up.stat_gains.items() if value]
    lines = [ui.style(f"Vida máxima +{level_up.hp_gain}", "bright_green")]
    if level_up.resource_gain:
        lines[0] += "   " + ui.style(f"{player.resource_data['name']} máxima +{level_up.resource_gain}",
                                     player.resource_data["color"])
    if gains:
        lines.append("   ".join(gains))
    for name in level_up.new_abilities:
        lines.append(ui.style(f"{ui.sym('star')} Nova habilidade: {name}", "bright_cyan"))
    if level_up.talent_point:
        lines.append(ui.style(f"{ui.sym('star')} Você ganhou um ponto de talento!", "bright_magenta"))
    title = ui.style(f"{ui.sym('up')} NÍVEL {level_up.level}! ", "bold bright_yellow")
    return ui.box(lines, min(screen_width(), 70), title=title, double=True, color="bright_yellow")


# --------------------------------------------------------------------------- ficha

def character_sheet(session: "GameSession") -> None:
    player, state = session.player, session.state
    section("FICHA DO PERSONAGEM")
    width = screen_width() - 4
    alignment = ALIGNMENTS[player.alignment]["name"]
    ui.echo("  " + ui.style(player.name, "bold") + "  " + ui.style(player.class_name, player.color + " bold")
            + ui.style(f"  {ui.sym('dot')}  nível {player.level}  {ui.sym('dot')}  {alignment}", "gray"))
    ui.echo_lines(ui.wrap(ui.style(player.portrait(), "italic"), width, "  "))
    ui.echo()

    left = [ui.style("ATRIBUTOS", "bold")]
    for stat, data in STATS.items():
        bonus = player.gear_bonus(stat)
        extra = ui.style(f" (+{bonus})", "bright_green") if bonus else ""
        left.append(f"{data['name']:<10} {player.stat(stat):>3}{extra}")
    left += ["", hp_bar(player, 10), resource_bar(player, 10), xp_bar(player, 10), "",
             f"Armadura   {player.armor:>3}"]

    right = [ui.style("EQUIPAMENTO", "bold")]
    for slot, label in SLOTS.items():
        stack = player.equipment.get(slot)
        right.append(f"{label + ':':<16}" + (stack.name() if stack else ui.style("—", "gray")))

    if screen_width() >= 92:
        ui.echo_lines(ui.side_by_side(["  " + row for row in left], right, 36))
    else:
        ui.echo_lines("  " + row for row in left)
        ui.echo()
        ui.echo_lines("  " + ui.truncate(row, screen_width() - 4) for row in right)
    ui.echo()
    trees = f" {ui.sym('dot')} ".join(tree["name"] for tree in player.class_data["talent_trees"])
    points = (f"{player.talent_points} disponível(is)" if player.level >= TALENT_START_LEVEL
              else f"a partir do nível {TALENT_START_LEVEL}")
    ui.echo(f"  {ui.style('Talentos:', 'bold')} {trees}  " + ui.style(f"({points})", "gray"))
    ui.echo(f"  {ui.style('Bolsa:', 'bold')} {ui.style(format_money(player.copper), 'bright_yellow')}")
    total_landmarks = sum(len(world.get_map(map_id).landmarks) for map_id in world.map_ids())
    session.sync_play_time()
    ui.echo(f"  {ui.style('Jornada:', 'bold')} Dia {state.clock.day}, "
            f"{len(state.discovered)}/{total_landmarks} locais descobertos, "
            f"{state.stats.get('passos', 0)} passos, {format_duration(state.play_seconds)} de jogo.")
    ui.echo()


def inventory_screen(session: "GameSession") -> None:
    player = session.player
    inventory = player.inventory
    section(f"MOCHILA  ({len(inventory)}/{inventory.capacity} espaços)")
    width = screen_width() - 10
    if not len(inventory):
        ui.echo("  Sua mochila está vazia.")
    for number, stack in enumerate(inventory, 1):
        quantity = ui.style(f" x{stack.quantity}", "bright_white") if stack.quantity > 1 else ""
        kind = ITEM_TYPES.get(stack.data["type"], stack.data["type"])
        ui.echo(f"  {ui.style(f'{number:>2}.', 'gray')} {stack.name()}{quantity}  " + ui.style(f"[{kind}]", "gray"))
        ui.echo_lines(ui.wrap(ui.style(stack.data["description"], "yellow italic"), width, "      "))
    ui.echo()
    ui.echo(f"  {ui.style('Bolsa:', 'bold')} {ui.style(format_money(player.copper), 'bright_yellow')}"
            + ui.style("   (o = ouro, p = prata, c = cobre)", "gray"))
    ui.echo()


def skills_screen(session: "GameSession") -> None:
    skills = session.player.skills
    section(f"PERÍCIAS DE COLETA E PRODUÇÃO  {ui.sym('dot')}  nível total {skills.total_level()}")
    width = screen_width()
    bar_width = 20 if width >= 90 else 12
    for skill_id, data in SKILLS.items():
        xp = skills.xp[skill_id]
        level, into, needed = level_progress(xp)
        name = ui.style(f"{data['name']:<12}", data["color"] + " bold")
        kind = ui.style(f"{data['kind']:<9}", "gray")
        remaining = ui.style(f"faltam {thousands(needed - into)} XP", "gray") if level < 99 else ""
        ui.echo(f"  {name} {kind} {ui.style(f'{level:>2}', 'bold')}/99  "
                f"{ui.bar(into, needed, bar_width, data['color'])}  {thousands(xp)} XP  {remaining}")
        ui.echo_lines(ui.wrap(ui.style(data["description"], "gray"), width - 8, "      "))
    ui.echo()
    ui.echo_lines(ui.wrap(ui.style(
        "As perícias evoluem de forma independente do nível de combate, de 1 a 99, com a curva clássica de "
        "experiência: 83 XP para o nível 2... e 13.034.431 XP para o 99.", "italic"), width - 4, "  "))
    ui.echo()


def abilities_screen(session: "GameSession") -> None:
    player = session.player
    section(f"GRIMÓRIO DE {player.class_name.upper()}")
    resource = player.resource_data
    width = screen_width() - 8
    ui.echo_lines(ui.wrap(ui.style(f"{resource['name']}: ", resource["color"] + " bold") + resource["description"],
                          width, "  "))
    ui.echo()
    known = player.abilities()
    for ability in player.abilities(include_locked=True):
        unlocked = ability in known
        slot = known.index(ability) + 1 if unlocked else None
        tag = ui.style(f"[{slot}]", "bright_yellow") if slot else ui.style(f"nv {ability['level']:>2}", "gray")
        cost = f"{ability['cost']} {resource['name']}" if ability["cost"] else "sem custo"
        cooldown = f"recarga {ability['cooldown']} turnos" if ability["cooldown"] else "sem recarga"
        name = ui.style(ability["name"], "bold") if unlocked else ui.style(ability["name"], "gray")
        ui.echo(f"  {tag} {name}  " + ui.style(f"({ability['kind']} {ui.sym('dot')} ", "gray")
                + element_label(ability["element"]) + ui.style(f" {ui.sym('dot')} {cost} {ui.sym('dot')} {cooldown})", "gray"))
        ui.echo_lines(ui.wrap(ui.style(ability["description"], "italic" if unlocked else "gray"), width, "        "))
    ui.echo()
    ui.echo_lines(ui.wrap(ui.style(
        "Os números entre colchetes são a sua barra de ações. Novas habilidades são aprendidas ao subir de nível.",
        "gray"), width, "  "))
    ui.echo()


def map_screen(session: "GameSession") -> None:
    game_map, state = session.map, session.state
    explored = state.explored_on(state.map_id)
    percent = 100 * len([t for t in explored if game_map.passable(*t)]) // max(1, game_map.passable_tiles)
    section(f"{game_map.name.upper()}  {ui.sym('dot')}  {percent}% explorado")
    double = ui.term_width() >= game_map.width * 2 + 8
    ui.echo_lines(mapview.full_map(session, double))
    ui.echo()
    entries = mapview.legend(session)
    columns = 4 if ui.term_width() >= 100 else 3
    for start in range(0, len(entries), columns):
        ui.echo("  " + "".join(ui.pad(entry, 24) for entry in entries[start:start + columns]))
    known = [lm for lm in game_map.landmarks.values() if lm.id in state.discovered]
    if known:
        ui.echo()
        ui.echo("  " + ui.style("Locais conhecidos (use 'ir <nome>' para viajar):", "bold"))
        names = [f"{lm.name} ({lm.x},{lm.y})" for lm in sorted(known, key=lambda lm: (lm.y, lm.x))]
        ui.echo_lines(ui.wrap(f" {ui.sym('dot')} ".join(names), screen_width() - 6, "    "))
    ui.echo()


def journal_screen(session: "GameSession") -> None:
    state = session.state
    section("DIÁRIO DE VIAGEM")
    width = screen_width() - 8
    entries = sorted(state.journal, key=lambda entry: entry.day)
    if not entries:
        ui.echo_lines(ui.wrap("Nenhuma pista anotada ainda. Converse com os moradores e examine os lugares que "
                              "visitar: o que for importante será registrado aqui.", width, "  "))
    for entry in entries:
        color = "bright_magenta" if entry.category == "segredo" else "bright_cyan"
        label = "Segredo" if entry.category == "segredo" else "Pista"
        ui.echo(f"  {ui.style(ui.sym('star') + ' ' + entry.title, color + ' bold')}  "
                + ui.style(f"({label}, dia {entry.day})", "gray"))
        ui.echo_lines(ui.wrap(entry.text, width, "     "))
        ui.echo()
    ui.echo("  " + ui.style("Locais descobertos por região:", "bold"))
    for map_id in world.map_ids():
        game_map = world.get_map(map_id)
        groups: Dict[str, List[str]] = {}
        for landmark in game_map.landmarks.values():
            region = game_map.region_at(landmark.x, landmark.y)
            name = region.name if region else game_map.name
            groups.setdefault(name, [])
            if landmark.id in state.discovered:
                groups[name].append(landmark.name)
        total = len(game_map.landmarks)
        found = sum(len(names) for names in groups.values())
        if not found:
            continue
        ui.echo(f"  {ui.style(game_map.name, 'bright_yellow')} " + ui.style(f"({found}/{total})", "gray"))
        for name, landmarks in groups.items():
            if landmarks:
                ui.echo_lines(ui.wrap(ui.style(name + ": ", "magenta") + ", ".join(landmarks), width, "    "))
    ui.echo()


# --------------------------------------------------------------------------- criação

def class_card(class_id: str, gender: str) -> List[str]:
    data: Dict[str, Any] = CLASSES[class_id]
    resource = RESOURCES[data["resource"]]
    width = min(screen_width(), 100)
    inner = width - 4
    stars = ui.style(ui.sym("star") * data["difficulty"], "bright_yellow") + ui.style(
        ui.sym("star_off") * (3 - data["difficulty"]), "gray")
    dot = f" {ui.sym('dot')} "
    starting = [a for a in data["abilities"] if a["level"] == 1]
    lines = [
        ui.style(data["tagline"], "italic"),
        "",
        data["description"],
        "",
        f"{ui.style('Função:', 'bold')} {data['role']}{dot}{ui.style('Dificuldade:', 'bold')} {stars}",
        f"{ui.style('Recurso:', 'bold')} {ui.style(resource['name'], resource['color'] + ' bold')}{dot}"
        f"{resource['description']}",
        f"{ui.style('Armadura:', 'bold')} {data['armor']}",
        f"{ui.style('Armas:', 'bold')} {data['weapons']}",
        ui.style("Atributos: ", "bold") + dot.join(
            f"{STATS[stat]['short']} {value}" for stat, value in data["base_stats"].items()),
        ui.style("Habilidades iniciais: ", "bold") + ", ".join(
            f"{a['name']} ({element_label(a['element'])})" for a in starting),
        ui.style("Árvores de talento: ", "bold") + f" {ui.sym('dot')} ".join(
            tree["name"] for tree in data["talent_trees"]),
        ui.style("Estilo de jogo: ", "bold") + data["playstyle"],
    ]
    wrapped = [row for line in lines for row in (ui.wrap(line, inner) if line else [""])]
    title = ui.style(data["names"][gender].upper(), data["color"] + " bold")
    return ui.box(wrapped, width, title=title, color=data["color"])
