"""Comandos da exploração: registro, interpretação do que o jogador digita e as ações.

Cada comando é registrado com ``@command`` (nome, apelidos, ajuda e categoria) e a
tela de ajuda é gerada a partir desse registro. Novas mecânicas — combate, coleta,
ofícios — entram no jogo registrando novos comandos, sem tocar no laço principal.

Acentos e maiúsculas não importam: "INVENTÁRIO", "inventario" e "inv" são iguais.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from . import crafting, screens, shop, ui, world
from .config import Settings
from .data.items import SLOTS
from .data.recipes import RECIPES, STATIONS
from .data.skills import SKILLS
from .items import ItemStack, item_name
from .npcs import choose_npc, run_dialogue
from .save_system import SaveError
from .session import GameSession
from .utils import capitalize_first, normalize

Handler = Callable[[GameSession, List[str]], None]

MAX_STEPS = 20


@dataclass
class Command:
    name: str
    aliases: Tuple[str, ...]
    handler: Handler
    help: str
    usage: str
    category: str


COMMANDS: Dict[str, Command] = {}
_LOOKUP: Dict[str, Command] = {}
CATEGORIES = ("Exploração", "Combate e itens", "Ofícios", "Personagem", "Sistema")


def command(name: str, *aliases: str, help: str, usage: str = "", category: str = "Exploração"):
    """Registra uma função como comando do jogo."""
    def decorator(handler: Handler) -> Handler:
        entry = Command(name, aliases, handler, help, usage or name, category)
        for key in (name, *aliases):
            if key in _LOOKUP:
                raise ValueError(f"Apelido de comando repetido: {key!r}")
            _LOOKUP[key] = entry
        COMMANDS[name] = entry
        return handler
    return decorator


def dispatch(session: GameSession, raw: str) -> None:
    """Interpreta uma linha digitada e executa o comando correspondente."""
    words = normalize(raw).split()
    if not words:
        session.needs_redraw = True
        return
    head, args = words[0], words[1:]
    direction = world.parse_direction(head)
    if direction:
        session.walk(direction, _parse_steps(args))
        return
    if head.isdigit() and args and world.parse_direction(args[0]):   # "3 n"
        session.walk(world.parse_direction(args[0]) or "n", _parse_steps([head]))
        return
    entry = _LOOKUP.get(head)
    if entry is None:
        suggestion = difflib.get_close_matches(head, list(_LOOKUP), n=1, cutoff=0.6)
        hint = f" Você quis dizer '{_LOOKUP[suggestion[0]].name}'?" if suggestion else ""
        ui.echo(ui.style(f"  Comando desconhecido: '{head}'.{hint} Digite 'ajuda' para ver os comandos.", "gray"))
        return
    entry.handler(session, args)


def _parse_steps(args: List[str]) -> int:
    if args and args[0].isdigit():
        return max(1, min(MAX_STEPS, int(args[0])))
    return 1


def _full_screen(session: GameSession, render: Callable[[GameSession], None]) -> None:
    render(session)
    ui.pause()
    session.needs_redraw = True


def _print_messages(session: GameSession) -> None:
    for message in session.pop_messages():
        ui.echo_lines(ui.wrap(message, screens.screen_width() - 4, "  "))
    while session.level_ups:
        ui.echo_lines(screens.level_up_box(session.level_ups.pop(0), session.player))


# --------------------------------------------------------------------------- exploração

@command("olhar", "ol", "ver", "look", help="Descreve novamente o lugar onde você está.")
def cmd_look(session: GameSession, args: List[str]) -> None:
    session.needs_redraw = True


@command("examinar", "ex", "x", "investigar", "inspecionar", "vasculhar", "procurar", "abrir",
         help="Examina o lugar com atenção: detalhes, pistas, tesouros e segredos.")
def cmd_examine(session: GameSession, args: List[str]) -> None:
    ui.echo()
    for text in session.examine():
        ui.echo_lines(ui.wrap(ui.style(text, "italic"), screens.screen_width() - 4, "  "))
    _print_messages(session)


@command("mapa", "m", "map", help="Mostra o mapa completo da região, com coordenadas e locais conhecidos.")
def cmd_map(session: GameSession, args: List[str]) -> None:
    _full_screen(session, screens.map_screen)


@command("ir", "andar", "viajar", "go", usage="ir <direção> [passos] | ir <local>",
         help="Anda numa direção (ex.: 'ir norte 5') ou viaja até um local já descoberto (ex.: 'ir estalagem').")
def cmd_go(session: GameSession, args: List[str]) -> None:
    if not args:
        ui.echo(ui.style("  Para onde? Ex.: 'ir norte 3' ou 'ir estalagem'. Veja os locais no 'mapa'.", "gray"))
        return
    direction = world.parse_direction(args[0])
    if direction:
        session.walk(direction, _parse_steps(args[1:]))
        return
    target = find_known_landmark(session, " ".join(args))
    if target is None:
        ui.echo(ui.style(f"  Você não conhece nenhum local chamado '{' '.join(args)}' neste mapa.", "gray"))
        return
    session.travel_to(target)


def find_known_landmark(session: GameSession, query: str) -> Optional[world.Landmark]:
    """Procura, pelo nome, um local já descoberto no mapa atual."""
    key = normalize(query)
    known = [lm for lm in session.map.landmarks.values() if lm.id in session.state.discovered]
    exact = [lm for lm in known if normalize(lm.name) == key]
    if exact:
        return exact[0]
    partial = [lm for lm in known if key in normalize(lm.name)]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        ui.echo(ui.style("  Seja mais específico. Você quis dizer: "
                         + ", ".join(lm.name for lm in partial) + "?", "gray"))
    return None


@command("entrar", "enter", help="Atravessa uma entrada (cavernas, passagens secretas...).")
def cmd_enter(session: GameSession, args: List[str]) -> None:
    if not session.use_verb("entrar"):
        ui.echo(ui.style("  Não há onde entrar aqui.", "gray"))
        _print_messages(session)


@command("sair", "exit", help="Sai do lugar fechado em que você está (pela passagem deste ponto).")
def cmd_exit(session: GameSession, args: List[str]) -> None:
    if not session.use_verb("sair"):
        ui.echo(ui.style("  Não há saída aqui. (Para voltar ao menu principal, use 'menu'.)", "gray"))


@command("falar", "f", "conversar", "talk", usage="falar [nome]", help="Conversa com alguém que esteja aqui.")
def cmd_talk(session: GameSession, args: List[str]) -> None:
    candidates = session.npcs_here()
    if not candidates:
        ui.echo(ui.style("  Não há ninguém aqui com quem conversar.", "gray"))
        return
    npc = choose_npc(candidates, " ".join(args))
    if npc is None:
        ui.echo("  Com quem você quer falar?")
        choice = ui.choose([ui.style(c.name, c.color) + ui.style(f" — {c.title}", "gray") for c in candidates],
                           prompt="Falar com", cancel="Ninguém")
        if choice is None:
            return
        npc = candidates[choice]
    run_dialogue(session, npc)
    session.needs_redraw = True
    if session.pending_shop:
        session.pending_shop = False
        if npc.shop:
            shop.run(session, npc.shop)


@command("descansar", "dormir", "rest", "acampar",
         help="Descansa. Na estalagem, dorme até o amanhecer (e salva o jogo); fora dela, por uma hora.")
def cmd_rest(session: GameSession, args: List[str]) -> None:
    session.rest()


@command("esperar", "aguardar", "wait", usage="esperar [horas]", help="Deixa o tempo passar (1 a 24 horas).")
def cmd_wait(session: GameSession, args: List[str]) -> None:
    hours = int(args[0]) if args and args[0].isdigit() else 1
    session.wait(hours)


@command("hora", "tempo", "relogio", "clima", help="Mostra a hora, o clima e a fase da lua.")
def cmd_time(session: GameSession, args: List[str]) -> None:
    clock = session.clock
    ui.echo(f"  Dia {clock.day}, {clock.time_str} ({clock.period_name}). Clima: {clock.weather['name']}. "
            f"Lua: {clock.moon_phase}. Raio de visão: {session.vision_radius()}.")


# --------------------------------------------------------------------------- combate e itens

@command("cacar", "caca", "hunt", help="Procura uma presa na região atual (20 minutos). Bom para ganhar experiência.",
         category="Combate e itens")
def cmd_hunt(session: GameSession, args: List[str]) -> None:
    if not session.hunt():
        _print_messages(session)


@command("equipar", "eq", "vestir", "empunhar", "equip", usage="equipar [item]",
         help="Equipa uma arma, armadura ou joia da mochila (o que estava no lugar volta para a mochila).",
         category="Combate e itens")
def cmd_equip(session: GameSession, args: List[str]) -> None:
    player = session.player
    gear = [stack for stack in player.inventory if stack.data.get("slot")]
    stack = _choose_stack(gear, " ".join(args), "equipar", "Você não tem nada para equipar na mochila.")
    if stack is None:
        return
    before = (player.armor, player.max_hp, player.max_resource, player.inventory.capacity)
    name = stack.name()
    try:
        removed = player.equip(stack)
    except ValueError as error:
        ui.echo(ui.style(f"  {error}", "bright_red"))
        return
    ui.echo(f"  Você equipa {name}.")
    for old in removed:
        ui.echo(ui.style(f"  {old.name(colored=False)} volta para a mochila.", "gray"))
    _show_changes(session, before)
    session.dirty = True


@command("remover", "desequipar", "tirar", usage="remover [item]", help="Tira uma peça equipada e a guarda na mochila.",
         category="Combate e itens")
def cmd_unequip(session: GameSession, args: List[str]) -> None:
    player = session.player
    worn = list(player.equipment.items())
    if not worn:
        ui.echo(ui.style("  Você não está usando nada.", "gray"))
        return
    key = normalize(" ".join(args))
    matches = [(slot, stack) for slot, stack in worn
               if key and (key in normalize(stack.data["name"]) or key in normalize(SLOTS[slot]))]
    if len(matches) != 1:
        candidates = matches or worn
        labels = [f"{SLOTS[slot]}: {stack.name()}" for slot, stack in candidates]
        choice = ui.choose(labels, prompt="Remover", cancel="Cancelar")
        if choice is None:
            return
        matches = [candidates[choice]]
    slot, stack = matches[0]
    before = (player.armor, player.max_hp, player.max_resource, player.inventory.capacity)
    try:
        player.unequip(slot)
    except ValueError as error:
        ui.echo(ui.style(f"  {error}", "bright_red"))
        return
    ui.echo(f"  Você guarda {stack.name()} na mochila.")
    _show_changes(session, before)
    session.dirty = True


@command("usar", "u", "comer", "beber", "use", usage="usar [item]",
         help="Come, bebe ou usa um item: pão e água restauram vida e mana fora de combate; poções, a qualquer hora.",
         category="Combate e itens")
def cmd_use(session: GameSession, args: List[str]) -> None:
    usable = [stack for stack in session.player.inventory if stack.data.get("use")]
    stack = _choose_stack(usable, " ".join(args), "usar", "Você não tem nada para usar.")
    if stack is None:
        return
    if session.use_item(stack):
        session.needs_redraw = True        # a tela volta com a vida e os bônus atualizados, e a mensagem embaixo
    else:
        _print_messages(session)


@command("largar", "descartar", "jogar", "drop", usage="largar <item> [quantidade|tudo]",
         help="Joga fora itens da mochila para abrir espaço (itens de missão não podem ser largados).",
         category="Combate e itens")
def cmd_drop(session: GameSession, args: List[str]) -> None:
    quantity: Optional[int] = None          # sem número (ou "tudo"): a pilha inteira
    if args and (args[-1].isdigit() or args[-1] in ("tudo", "todos", "todas")):
        last = args.pop()
        if last.isdigit():
            quantity = int(last)
            if quantity <= 0:
                ui.echo(ui.style("  Quantidade inválida.", "gray"))
                return
    droppable = [stack for stack in session.player.inventory if stack.data["type"] != "missao"]
    stack = _choose_stack(droppable, " ".join(args), "largar", "Não há nada que você possa largar.")
    if stack is None:
        return
    amount = stack.quantity if quantity is None else min(quantity, stack.quantity)
    if stack.data.get("value", 0) >= 50 and not ui.confirm(f"Largar {stack.name()} x{amount} de verdade?", False):
        return
    name = stack.name()
    session.player.inventory.take(stack, amount)
    ui.echo(f"  Você larga {name} x{amount}.")
    session.dirty = True


@command("comerciar", "loja", "negociar", "comprar", "vender", help="Compra e vende com um mercador que esteja aqui.",
         category="Combate e itens")
def cmd_trade(session: GameSession, args: List[str]) -> None:
    merchants = [npc for npc in session.npcs_here() if npc.shop]
    if not merchants:
        ui.echo(ui.style("  Não há nenhum mercador aqui. (A Dona Graça atende no Mercado da Vila, de dia.)", "gray"))
        return
    shop.run(session, merchants[0].shop)


@command("bestiario", "monstros", "b", help="Criaturas que você já enfrentou: fraquezas, abates e saques.",
         category="Combate e itens")
def cmd_bestiary(session: GameSession, args: List[str]) -> None:
    _full_screen(session, screens.bestiary_screen)


def _choose_stack(stacks: List[ItemStack], query: str, verb: str, empty: str) -> Optional[ItemStack]:
    """Escolhe uma pilha da mochila pelo nome digitado (ou por um menu, se for ambíguo)."""
    if not stacks:
        ui.echo(ui.style(f"  {empty}", "gray"))
        return None
    key = normalize(query)
    if key:
        exact = [stack for stack in stacks if normalize(stack.data["name"]) == key]
        matches = exact[:1] or [stack for stack in stacks if key in normalize(stack.data["name"])]
        if not matches:
            ui.echo(ui.style(f"  Você não tem nada chamado '{query}' para {verb}.", "gray"))
            return None
        if len(matches) == 1:
            return matches[0]
        stacks = matches
    labels = [f"{stack.name()} x{stack.quantity}" for stack in stacks]
    choice = ui.choose(labels, prompt=capitalize_first(verb), cancel="Cancelar")
    return None if choice is None else stacks[choice]


def _show_changes(session: GameSession, before: Tuple[float, int, int, int]) -> None:
    player = session.player
    after = (player.armor, player.max_hp, player.max_resource, player.inventory.capacity)
    labels = ("Armadura", "Vida máxima", player.resource_data["name"] + " máxima", "Espaços na mochila")
    changes = []
    for label, old, new in zip(labels, before, after):
        if new != old:
            color = "bright_green" if new > old else "bright_red"
            changes.append(f"{label} {int(old)} {ui.sym('arrow')} " + ui.style(str(int(new)), color))
    if changes:
        ui.echo("  " + "   ".join(changes))


# --------------------------------------------------------------------------- ofícios

@command("minerar", "minera", "mine", usage="minerar [veio] [quantidade|tudo]",
         help="Minera no local (precisa de picareta). Sem quantidade, tenta tirar 5 minérios.", category="Ofícios")
def cmd_mine(session: GameSession, args: List[str]) -> None:
    _gather(session, args, ["mineracao"], "minerar")


@command("pescar", "pesca", "fish", usage="pescar [cardume] [quantidade|tudo]",
         help="Pesca no local (rede ou vara, e iscas para alguns peixes).", category="Ofícios")
def cmd_fish(session: GameSession, args: List[str]) -> None:
    _gather(session, args, ["pesca"], "pescar")


@command("colher", "colheita", "tosquiar", usage="colher [planta] [quantidade|tudo]",
         help="Colhe ervas (Alquimia), linho e lã (Alfaiataria) no local.", category="Ofícios")
def cmd_harvest(session: GameSession, args: List[str]) -> None:
    _gather(session, args, ["alquimia", "alfaiataria"], "colher")


@command("coletar", "extrair", "recolher", usage="coletar [recurso] [quantidade|tudo]",
         help="Coleta qualquer recurso do local (o mesmo que minerar, pescar ou colher).", category="Ofícios")
def cmd_gather(session: GameSession, args: List[str]) -> None:
    _gather(session, args, list(SKILLS), "coletar")


@command("forjar", "fundir", "ferraria", usage="forjar [item] [quantidade|tudo]",
         help="Metalurgia: funde barras na fornalha e forja armas e armaduras na bigorna.", category="Ofícios")
def cmd_smith(session: GameSession, args: List[str]) -> None:
    _craft(session, args, "metalurgia", "forjar")


@command("cozinhar", "assar", usage="cozinhar [prato] [quantidade|tudo]",
         help="Culinária: cozinha num fogo (estalagem ou fogueiras). Pratos especiais dão bônus.",
         category="Ofícios")
def cmd_cook(session: GameSession, args: List[str]) -> None:
    _craft(session, args, "culinaria", "cozinhar")


@command("costurar", "fiar", "tecer", usage="costurar [peça] [quantidade|tudo]",
         help="Alfaiataria: fia na roca e costura roupas, couro e bolsas (com agulha e linha).",
         category="Ofícios")
def cmd_sew(session: GameSession, args: List[str]) -> None:
    _craft(session, args, "alfaiataria", "costurar")


@command("preparar", "destilar", "misturar", usage="preparar [poção] [quantidade|tudo]",
         help="Alquimia: poções com o almofariz; elixires, óleos e frascos no caldeirão.", category="Ofícios")
def cmd_brew(session: GameSession, args: List[str]) -> None:
    _craft(session, args, "alquimia", "preparar")


@command("fabricar", "criar", "produzir", "fazer", usage="fabricar [item] [quantidade|tudo]",
         help="Produz qualquer receita disponível aqui (de qualquer perícia).", category="Ofícios")
def cmd_craft(session: GameSession, args: List[str]) -> None:
    _craft(session, args, None, "fabricar")


@command("receitas", "receita", "livro", usage="receitas [perícia]",
         help="Livro de ofício: onde coletar e tudo o que cada perícia sabe fazer.", category="Ofícios")
def cmd_recipes(session: GameSession, args: List[str]) -> None:
    key = normalize(" ".join(args))
    skills = list(SKILLS)
    matches = [skill_id for skill_id in skills if key and normalize(SKILLS[skill_id]["name"]).startswith(key)]
    if len(matches) == 1:
        skill_id = matches[0]
    else:
        labels = [f"{SKILLS[skill_id]['name']} " + ui.style(f"(nível {session.player.skills.level(skill_id)})", "gray")
                  for skill_id in skills]
        choice = ui.choose(labels, prompt="Perícia", cancel="Voltar")
        if choice is None:
            return
        skill_id = skills[choice]
    _full_screen(session, lambda current: screens.recipes_screen(current, skill_id))


def _split_quantity(args: List[str]) -> Tuple[List[str], Optional[int]]:
    """Separa a quantidade ("5", "tudo") do resto dos argumentos."""
    if args and (args[-1].isdigit() or args[-1] in ("tudo", "todos", "todas", "max")):
        last = args[-1]
        return args[:-1], int(last) if last.isdigit() else crafting.ALL
    return args, None


def _known_places(session: GameSession, wanted: Callable[[world.Landmark], bool]) -> List[str]:
    """Locais já descobertos (em qualquer mapa) que atendem ao critério."""
    return [landmark.name for map_id in world.map_ids() for landmark in world.get_map(map_id).landmarks.values()
            if landmark.id in session.state.discovered and wanted(landmark)]


def _gather(session: GameSession, args: List[str], skills: List[str], verb: str) -> None:
    args, quantity = _split_quantity(args)
    if quantity == 0:
        ui.echo(ui.style("  Quantidade inválida.", "gray"))
        return
    state = session.state
    landmark = session.map.landmark_at(*state.pos)
    spots = crafting.spots_at(landmark, state, skills)
    if not spots:
        places = _known_places(session, lambda lm: bool(crafting.spots_at(lm, state, skills)))
        hint = (f" Lugares que você conhece: {', '.join(places)}." if places else
                " Os locais com pontos de coleta mostram 'Coleta:' na descrição.")
        ui.echo_lines(ui.wrap(ui.style(f"Não há nada para {verb} aqui.{hint}", "gray"), screens.screen_width() - 4, "  "))
        return
    key = normalize(" ".join(args))
    if key:
        spots = [spot for spot in spots if key in normalize(spot.name)]
        if not spots:
            ui.echo(ui.style(f"  Não há '{' '.join(args)}' para {verb} aqui.", "gray"))
            return
    spot = spots[0]
    if len(spots) > 1:
        labels = []
        for candidate in spots:
            data = candidate.data
            label = f"{data['name']} " + ui.style(f"({SKILLS[data['skill']]['name']} {data['level']})", "gray")
            problem = crafting.gather_problem(session.player, state, candidate)
            labels.append(ui.truncate(label + (ui.style(f" — {problem}", "gray") if problem else ""),
                                      screens.screen_width() - 8))
        choice = ui.choose(labels, prompt=capitalize_first(verb), cancel="Cancelar")
        if choice is None:
            return
        spot = spots[choice]
    if session.gather(spot, quantity or crafting.DEFAULT_GATHER) is None:
        _print_messages(session)
    else:
        session.needs_redraw = True


def _craft(session: GameSession, args: List[str], skill: Optional[str], verb: str) -> None:
    args, quantity = _split_quantity(args)
    if quantity == 0:
        ui.echo(ui.style("  Quantidade inválida.", "gray"))
        return
    player, state = session.player, session.state
    landmark = session.map.landmark_at(*state.pos)
    here_stations = {station["id"] for station in landmark.stations} if landmark else set()
    known = [recipe_id for recipe_id in crafting.recipes_for(skill)
             if player.skills.level(RECIPES[recipe_id]["skill"]) >= RECIPES[recipe_id]["level"]]
    here = [recipe_id for recipe_id in known
            if not RECIPES[recipe_id].get("station") or RECIPES[recipe_id]["station"] in here_stations]
    key = normalize(" ".join(args))
    if key:
        named = [recipe_id for recipe_id in crafting.recipes_for(skill) if key in normalize(crafting.recipe_name(recipe_id))]
        exact = [recipe_id for recipe_id in named if normalize(crafting.recipe_name(recipe_id)) == key]
        named = exact or named
        if not named:
            ui.echo(ui.style(f"  Você não conhece nenhuma receita chamada '{' '.join(args)}'.", "gray"))
            return
        candidates = [recipe_id for recipe_id in named if recipe_id in here] or named[:1]
    else:
        candidates = here
    if not candidates:
        _explain_no_station(session, skill, verb, known)
        return
    recipe_id = candidates[0]
    if len(candidates) > 1:
        # o que dá para fazer agora vem primeiro (cada grupo continua em ordem de nível)
        candidates.sort(key=lambda candidate: crafting.max_craftable(player, candidate) == 0)
        recipe_id = _choose_recipe(session, candidates, skill, verb)
        if recipe_id is None:
            return
    problem = crafting.craft_problem(player, state, landmark, recipe_id)
    if problem:
        ui.echo_lines(ui.wrap(ui.style(problem, "gray"), screens.screen_width() - 4, "  "))
        return
    if quantity is None:
        most = crafting.max_craftable(player, recipe_id)
        quantity = 1 if most == 1 else _ask_count(most)
        if quantity is None:
            return
    if session.craft(recipe_id, quantity) is None:
        _print_messages(session)
    else:
        session.needs_redraw = True


def _choose_recipe(session: GameSession, candidates: List[str], skill: Optional[str], verb: str) -> Optional[str]:
    player = session.player
    labels = []
    for recipe_id in candidates:
        output_id, quantity = crafting.recipe_output(recipe_id)
        name = item_name(output_id) + (f" x{quantity}" if quantity > 1 else "")
        can = crafting.max_craftable(player, recipe_id)
        status = (ui.style(f"pode fazer {can}", "bright_green") if can else
                  ui.style(f"faltam: {crafting.missing_text(player, recipe_id)}", "gray"))
        labels.append(ui.truncate(f"{name} {ui.sym('arrow')} " + ui.style(crafting.ingredients_text(recipe_id), "gray")
                                  + f"  ({status})", screens.screen_width() - 8))
    if skill:
        upcoming = crafting.next_unlock(skill, player.skills.level(skill))
        if upcoming:
            ui.echo(ui.style(f"  Próximo, no nível {upcoming[0]} de {SKILLS[skill]['name']}: "
                             f"{', '.join(upcoming[1])}", "gray"))
    choice = ui.choose(labels, prompt=capitalize_first(verb), cancel="Cancelar")
    return None if choice is None else candidates[choice]


def _explain_no_station(session: GameSession, skill: Optional[str], verb: str, known: List[str]) -> None:
    needed = sorted({RECIPES[recipe_id]["station"] for recipe_id in known if RECIPES[recipe_id].get("station")})
    if not known:
        message = f"Você ainda não sabe {verb} nada."
    elif not needed:
        message = f"Não há nada para {verb} aqui."
    else:
        parts = []
        for station_id in needed:
            places = _known_places(session, lambda lm, sid=station_id: any(st["id"] == sid for st in lm.stations))
            where = f" ({', '.join(places)})" if places else ""
            parts.append(f"{STATIONS[station_id]['name']}{where}")
        message = f"Para {verb}, você precisa de: {'; '.join(parts)}."
    ui.echo_lines(ui.wrap(ui.style(message, "gray"), screens.screen_width() - 4, "  "))


def _ask_count(maximum: int) -> Optional[int]:
    raw = normalize(ui.ask("  Quantos? " + ui.style(f"(Enter = 1, 't' = todos os {maximum}, 0 cancela)", "gray")
                           + f" {ui.sym('arrow')} "))
    if not raw:
        return 1
    if raw in ("t", "tudo", "todos", "todas", "max"):
        return maximum
    if raw.isdigit() and int(raw) > 0:
        return min(int(raw), maximum)
    return None


# --------------------------------------------------------------------------- personagem

@command("ficha", "status", "st", "c", "personagem", help="Ficha do personagem: atributos e equipamento.",
         category="Personagem")
def cmd_sheet(session: GameSession, args: List[str]) -> None:
    _full_screen(session, screens.character_sheet)


@command("inventario", "inv", "i", "mochila", "bolsa", help="Itens da mochila e dinheiro.", category="Personagem")
def cmd_inventory(session: GameSession, args: List[str]) -> None:
    _full_screen(session, screens.inventory_screen)


@command("pericias", "skills", "p", "oficios", "profissoes",
         help="Perícias de coleta e produção (níveis 1 a 99).", category="Personagem")
def cmd_skills(session: GameSession, args: List[str]) -> None:
    _full_screen(session, screens.skills_screen)


@command("habilidades", "hab", "grimorio", "magias", "barra",
         help="Grimório da classe: habilidades, custos, recargas e elementos.", category="Personagem")
def cmd_abilities(session: GameSession, args: List[str]) -> None:
    _full_screen(session, screens.abilities_screen)


@command("diario", "d", "j", "pistas", "journal", help="Diário: pistas, segredos e locais descobertos.",
         category="Personagem")
def cmd_journal(session: GameSession, args: List[str]) -> None:
    _full_screen(session, screens.journal_screen)


# --------------------------------------------------------------------------- sistema

@command("salvar", "save", "gravar", help="Salva o jogo.", category="Sistema")
def cmd_save(session: GameSession, args: List[str]) -> None:
    try:
        path = session.save()
    except SaveError as error:
        ui.echo(ui.style(f"  {error}", "bright_red"))
        return
    ui.echo(ui.style(f"  {ui.sym('check')} Jogo salvo em {path}", "bright_green"))


@command("opcoes", "config", "configuracoes", help="Cores, símbolos, narração e salvamento automático.",
         category="Sistema")
def cmd_options(session: GameSession, args: List[str]) -> None:
    options_menu(session.settings)
    session.needs_redraw = True


@command("ajuda", "?", "help", "h", "comandos", help="Mostra esta lista de comandos.", category="Sistema")
def cmd_help(session: GameSession, args: List[str]) -> None:
    _full_screen(session, lambda _session: help_screen())


@command("menu", "quit", "q", help="Volta ao menu principal (pergunta se quer salvar).", category="Sistema")
def cmd_menu(session: GameSession, args: List[str]) -> None:
    if session.dirty and ui.confirm("Salvar antes de voltar ao menu?", default=True):
        cmd_save(session, [])
    session.running = False


# --------------------------------------------------------------------------- telas auxiliares

def help_screen() -> None:
    screens.section("COMO JOGAR")
    width = screens.screen_width() - 6
    ui.echo("  " + ui.style("Movimento", "bold bright_yellow"))
    ui.echo_lines(ui.wrap(
        "n, s, l, o (norte, sul, leste, oeste) e as diagonais ne, no, se, so. Acrescente um número para andar "
        "vários passos de uma vez: 'n 5'. A caminhada para sozinha quando algo interessante acontece.",
        width, "    "))
    ui.echo()
    for category in CATEGORIES:
        ui.echo("  " + ui.style(category, "bold bright_yellow"))
        for entry in COMMANDS.values():
            if entry.category != category:
                continue
            aliases = ui.style(" (" + ", ".join(entry.aliases) + ")", "gray") if entry.aliases else ""
            ui.echo(f"    {ui.style(entry.usage, 'bright_white bold')}{aliases}")
            ui.echo_lines(ui.wrap(entry.help, width - 4, "        "))
        ui.echo()
    ui.echo("  " + ui.style("Em combate", "bold bright_yellow"))
    ui.echo_lines(ui.wrap(
        "Use os números da barra de ações (1–9) para as habilidades, 'a' para atacar, 'd' para defender, 'i' para "
        "itens, 'x' para analisar e 'f' para fugir. Digite '?' durante a luta para ver tudo.", width, "    "))
    ui.echo()
    ui.echo_lines(ui.wrap(ui.style(
        "Dica: no mapa, '?' marca algo ainda não visitado e '!' marca pessoas — amarelo forte para quem você ainda "
        "não conhece. Examine os locais: muitos guardam pistas, e alguns, segredos.", "italic"), width, "  "))
    ui.echo()


def options_menu(settings: Settings) -> None:
    entries = [
        ("color", "Cores"),
        ("unicode", "Molduras e símbolos Unicode"),
        ("typewriter", "Narração letra a letra"),
        ("clear_screen", "Limpar a tela a cada passo"),
        ("autosave", "Salvamento automático (ao amanhecer e ao dormir)"),
        ("timing", "Golpes e bloqueios no tempo certo (reflexos)"),
    ]
    while True:
        screens.section("OPÇÕES")
        labels = []
        for key, label in entries:
            state = ui.style("LIGADO", "bright_green") if getattr(settings, key) else ui.style("desligado", "gray")
            labels.append(f"{label}: {state}")
        choice = ui.choose(labels, prompt="Alternar", cancel="Voltar")
        if choice is None:
            return
        key = entries[choice][0]
        setattr(settings, key, not getattr(settings, key))
        ui.configure(settings.color, settings.unicode, settings.typewriter, settings.clear_screen)
        try:
            settings.save()
        except OSError as error:
            ui.echo(ui.style(f"  Não foi possível gravar as opções: {error}", "bright_red"))
            ui.pause()
