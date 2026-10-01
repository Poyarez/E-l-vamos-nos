"""Criação de personagem: nome, gênero, classe, aparência, cor da armadura e alinhamento.

O jogador pode seguir passo a passo ou sortear tudo, e sempre termina numa tela de
resumo onde dá para revisar e alterar qualquer escolha antes de começar.
"""

from __future__ import annotations

import random
import re
from typing import Any, Dict, Mapping, Optional

from . import screens, ui
from .data.appearance import ALIGNMENTS, ARMOR_COLORS, FEATURES, GENDERS, HAIR_COLORS, HAIR_STYLES
from .data.classes import CLASSES
from .player import BALD_STYLES, Appearance, Player
from .utils import capitalize_first

NAME_MIN, NAME_MAX = 2, 16
_NAME_RE = re.compile(r"^[^\W\d_]+(?:[ '\-][^\W\d_]+)*$")

RANDOM_NAMES = {
    "masculino": ["Tristão", "Bento", "Afonso", "Martim", "Gonçalo", "Vasco", "Rodrigo", "Aldric", "Teodoro", "Iago"],
    "feminino": ["Leonor", "Inês", "Beatriz", "Brites", "Mécia", "Aldonça", "Isolda", "Branca", "Violante", "Elvira"],
    "nao_binario": ["Ariel", "Lior", "Sael", "Rian", "Noá", "Darian", "Elis", "Kai", "Sasha", "Alexis"],
}


def validate_name(raw: str) -> Optional[str]:
    """Devolve o nome normalizado, ou ``None`` se for inválido."""
    name = " ".join(raw.split())
    if not (NAME_MIN <= len(name) <= NAME_MAX) or not _NAME_RE.match(name):
        return None
    return capitalize_first(name)


def random_draft(rng: Optional[random.Random] = None) -> Dict[str, str]:
    rng = rng or random.Random()
    gender = rng.choice(list(GENDERS))
    return {
        "name": rng.choice(RANDOM_NAMES[gender]),
        "gender": gender,
        "class_id": rng.choice(list(CLASSES)),
        "hair_style": rng.choice(list(HAIR_STYLES)),
        "hair_color": rng.choice(list(HAIR_COLORS)),
        "feature": rng.choice(list(FEATURES)),
        "armor_color": rng.choice(list(ARMOR_COLORS)),
        "alignment": rng.choice(list(ALIGNMENTS)),
    }


def build_player(draft: Mapping[str, str]) -> Player:
    appearance = Appearance(draft["gender"], draft["hair_style"], draft["hair_color"], draft["feature"],
                            draft["armor_color"])
    return Player.create(draft["name"], draft["class_id"], appearance, draft["alignment"])


# --------------------------------------------------------------------------- passos

def _step_header(step: int, total: int, title: str) -> None:
    screens.section(f"CRIAÇÃO DE PERSONAGEM  {ui.sym('dot')}  {step}/{total}  {ui.sym('dot')}  {title}")


def ask_name(current: str = "") -> str:
    _step_header(1, 7, "NOME")
    ui.narrate("Toda lenda começa com um nome. Qual é o seu?")
    ui.echo(ui.style(f"  ({NAME_MIN} a {NAME_MAX} letras; espaços, hífens e apóstrofos são permitidos"
                     + (f"; Enter mantém \"{current}\"" if current else "") + ")", "gray"))
    while True:
        raw = ui.ask(f"  {ui.style('Nome', 'bold')} {ui.sym('arrow')} ")
        if not raw and current:
            return current
        name = validate_name(raw)
        if name:
            return name
        ui.echo(ui.style("  Nome inválido. Use só letras (com ou sem acento), espaços, hífens e apóstrofos.",
                         "bright_red"))


def _pick(step: int, title: str, question: str, options: Mapping[str, Mapping[str, Any]],
          color_key: Optional[str] = None, detail_key: Optional[str] = "description") -> str:
    _step_header(step, 7, title)
    ui.narrate(question)
    ui.echo()
    keys = list(options)
    labels = [ui.style(options[k]["name"], options[k][color_key]) if color_key else options[k]["name"] for k in keys]
    details = [capitalize_first(options[k].get(detail_key, "")) for k in keys] if detail_key else None
    choice = ui.choose(labels, details=details)
    return keys[choice if choice is not None else 0]


def ask_gender() -> str:
    return _pick(2, "GÊNERO", "Como você se apresenta ao mundo?", GENDERS)


def ask_class(gender: str) -> str:
    while True:
        _step_header(3, 7, "CLASSE")
        ui.narrate("Que caminho de batalha você trilha? (Escolha para ver os detalhes.)")
        ui.echo()
        keys = list(CLASSES)
        labels = [ui.style(f"{CLASSES[k]['names'][gender]:<12}", CLASSES[k]["color"] + " bold")
                  + ui.style(f"{CLASSES[k]['role']}", "gray") for k in keys]
        details = [CLASSES[k]["tagline"] for k in keys]
        class_id = keys[ui.choose(labels, details=details) or 0]
        ui.clear()
        ui.echo_lines(screens.class_card(class_id, gender))
        ui.echo()
        if ui.confirm(f"Seguir o caminho de {CLASSES[class_id]['names'][gender]}?", default=True):
            return class_id


def ask_hair() -> Dict[str, str]:
    style = _pick(4, "CABELO", "Como é o seu cabelo?", HAIR_STYLES)
    if style in BALD_STYLES:
        return {"hair_style": style, "hair_color": "negro"}
    color = _pick(4, "COR DO CABELO", "E a cor?", HAIR_COLORS, color_key="color", detail_key=None)
    return {"hair_style": style, "hair_color": color}


def ask_feature() -> str:
    return _pick(5, "TRAÇO MARCANTE", "Algum traço que as pessoas notem à primeira vista?", FEATURES)


def ask_armor_color() -> str:
    return _pick(6, "COR DA ARMADURA", "De que cor é o equipamento que você trouxe de casa?", ARMOR_COLORS,
                 color_key="color")


def ask_alignment() -> str:
    return _pick(7, "ALINHAMENTO", "No fundo do coração, o que guia suas escolhas?", ALIGNMENTS)


# --------------------------------------------------------------------------- resumo

def show_summary(draft: Mapping[str, str]) -> None:
    preview = build_player(draft)
    screens.section("SEU PERSONAGEM")
    width = screens.screen_width() - 4
    ui.echo("  " + ui.style(preview.name, "bold") + "  " + ui.style(preview.class_name, preview.color + " bold")
            + ui.style(f"  {ui.sym('dot')}  {CLASSES[draft['class_id']]['role']}", "gray"))
    ui.echo()
    ui.echo_lines(ui.wrap(ui.style(preview.portrait(), "italic"), width, "  "))
    ui.echo()
    hair = HAIR_STYLES[draft["hair_style"]]["name"]
    if draft["hair_style"] not in BALD_STYLES:
        hair += ", " + ui.style(HAIR_COLORS[draft["hair_color"]]["name"].lower(), HAIR_COLORS[draft["hair_color"]]["color"])
    armor = ARMOR_COLORS[draft["armor_color"]]
    rows = [
        ("Gênero", GENDERS[draft["gender"]]["name"]),
        ("Cabelo", hair),
        ("Traço marcante", FEATURES[draft["feature"]]["name"]),
        ("Cor da armadura", ui.style(armor["name"], armor["color"] + " bold")),
        ("Alinhamento", ALIGNMENTS[draft["alignment"]]["name"] + ui.style(
            " — " + ALIGNMENTS[draft["alignment"]]["description"], "gray")),
        ("Vida / " + preview.resource_data["name"], f"{preview.max_hp} / {preview.max_resource}"),
    ]
    for label, value in rows:
        ui.echo_lines(ui.labeled(ui.style(f"{label}:", "bold"), value, 18, width))
    ui.echo()


def create_character() -> Optional[Player]:
    """Conduz a criação completa. Devolve ``None`` se o jogador desistir."""
    screens.section("CRIAÇÃO DE PERSONAGEM")
    ui.narrate("Antes de pisar no Vale de Primórdia, diga ao mundo quem você é.")
    ui.echo()
    mode = ui.choose(["Criar passo a passo", "Sortear um personagem (dá para ajustar depois)"],
                     cancel="Voltar ao menu")
    if mode is None:
        return None
    if mode == 1:
        draft = random_draft()
    else:
        draft = {"name": ask_name()}
        draft["gender"] = ask_gender()
        draft["class_id"] = ask_class(draft["gender"])
        draft.update(ask_hair())
        draft["feature"] = ask_feature()
        draft["armor_color"] = ask_armor_color()
        draft["alignment"] = ask_alignment()

    while True:
        show_summary(draft)
        choice = ui.choose([
            ui.style("Confirmar e começar a aventura", "bright_green bold"),
            "Mudar o nome", "Mudar o gênero", "Mudar a classe", "Mudar o cabelo",
            "Mudar o traço marcante", "Mudar a cor da armadura", "Mudar o alinhamento", "Sortear tudo de novo",
        ], prompt="O que deseja fazer", cancel="Desistir e voltar ao menu")
        if choice is None:
            if ui.confirm("Descartar este personagem?", default=False):
                return None
        elif choice == 0:
            return build_player(draft)
        elif choice == 1:
            draft["name"] = ask_name(draft["name"])
        elif choice == 2:
            draft["gender"] = ask_gender()
        elif choice == 3:
            draft["class_id"] = ask_class(draft["gender"])
        elif choice == 4:
            draft.update(ask_hair())
        elif choice == 5:
            draft["feature"] = ask_feature()
        elif choice == 6:
            draft["armor_color"] = ask_armor_color()
        elif choice == 7:
            draft["alignment"] = ask_alignment()
        else:
            draft = random_draft()


# --------------------------------------------------------------------------- introdução

def play_intro(player: Player) -> None:
    forms = player.forms
    screens.section("PRÓLOGO")
    paragraphs = [
        ("O cartaz pregado no quadro de avisos de Alvorada era curto: \"PROCURAM-SE AVENTUREIROS. O VALE DE "
         "PRIMÓRDIA PEDE AJUDA. RECOMPENSA EM OURO.\" Quase ninguém parou para ler. Você parou."),
        ("Foram três dias sacolejando na carroça de um mercador de especiarias, por estradas cada vez mais "
         "estreitas, até que as montanhas se abriram e revelaram o vale: campos dourados, um rio de prata "
         "serpenteando até um lago que espelha o céu e, ao longe, a nordeste, ruínas brancas onde — dizem — uma "
         "luz violeta dança nas noites sem lua."),
        (f"O mercador puxa as rédeas na entrada da vila. \"Daqui em diante é com você, {forms['tratamento']}. Que "
         "a Aurora ilumine seu caminho.\" Ele hesita, olhando para as montanhas, e acrescenta mais baixo: \"E que "
         "a Lua guarde seus passos.\""),
        (f"A carroça se afasta. {player.name} ajeita o equipamento, respira o ar frio que desce das montanhas e "
         "dá o primeiro passo."),
    ]
    for paragraph in paragraphs:
        ui.narrate(paragraph)
        ui.echo()
    ui.echo(ui.pad(ui.style("E lá vamos nós.", "bold bright_yellow"), screens.screen_width(), "center"))
    ui.echo()
    tips = [
        f"{ui.style('n s l o', 'bright_white bold')} (e {ui.style('ne no se so', 'bright_white bold')}) para "
        f"andar; 'n 5' anda cinco passos.",
        f"{ui.style('mapa', 'bright_white bold')} mostra a região; {ui.style('ir <local>', 'bright_white bold')} "
        "viaja até um lugar conhecido.",
        f"{ui.style('falar', 'bright_white bold')} com as pessoas (marcadas com !) e "
        f"{ui.style('examinar', 'bright_white bold')} os lugares em busca de pistas.",
        f"{ui.style('ajuda', 'bright_white bold')} lista todos os comandos. Primeiro objetivo: encontrar a "
        "Anciã Ysolde, na vila.",
    ]
    width = min(screens.screen_width(), 90)
    ui.echo_lines(ui.box([row for tip in tips for row in ui.wrap(tip, width - 4)], width, title="Dicas",
                         color="cyan"))
    ui.pause("Pressione Enter para começar...")
