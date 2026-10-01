#!/usr/bin/env python3
"""Crônicas de Primórdia — um RPG de fantasia medieval para o terminal.

Como jogar:   python main.py
Opções:       python main.py --sem-cor --ascii --sem-animacao

Este arquivo cuida do menu principal e do laço principal do jogo (Main Game Loop):
desenhar a tela, ler um comando, executá-lo e atualizar o mundo, até o jogador sair.
As regras ficam no pacote ``rpg``.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rpg import battle_ui, character_creation, commands, save_system, screens, ui
from rpg.config import GAME_TITLE, GAME_VERSION, Settings
from rpg.save_system import SaveError, SaveInfo
from rpg.session import GameSession
from rpg.state import GameState
from rpg.utils import format_duration


def parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="main.py", description=f"{GAME_TITLE} — RPG de fantasia para o terminal.")
    parser.add_argument("--sem-cor", action="store_true", help="desliga as cores ANSI")
    parser.add_argument("--ascii", action="store_true", help="usa apenas caracteres ASCII nas molduras e símbolos")
    parser.add_argument("--sem-animacao", action="store_true", help="desliga a narração letra a letra")
    parser.add_argument("--version", action="version", version=f"{GAME_TITLE} {GAME_VERSION}")
    return parser.parse_args(argv)


def apply_display(settings: Settings, args: argparse.Namespace) -> None:
    ui.configure(color=settings.color and not args.sem_cor,
                 unicode=settings.unicode and not args.ascii,
                 typewriter=settings.typewriter and not args.sem_animacao,
                 clear_screen=settings.clear_screen)


# --------------------------------------------------------------------------- laço principal

def game_loop(session: GameSession) -> None:
    """Main Game Loop: desenha, lê um comando, executa e atualiza o mundo."""
    while session.running:
        if session.needs_redraw:
            screens.render_location(session)
            session.needs_redraw = False
        else:
            screens.show_messages(session)
        try:
            raw = ui.ask("\n  " + ui.style(f"[{session.clock.time_str}]", "gray") + " "
                         + ui.style("O que você faz?", "bold") + f" {ui.sym('arrow')} ")
        except KeyboardInterrupt:
            ui.echo()
            commands.cmd_menu(session, [])   # Ctrl+C volta ao menu (oferecendo salvar)
            continue
        commands.dispatch(session, raw)
        session.update_quests()
        if session.pending_battle is not None and session.running:
            battle_ui.run(session)
            session.update_quests()
        if session.pending_autosave and session.running:
            autosave(session)
    session.sync_play_time()


def autosave(session: GameSession) -> None:
    try:
        session.save()
    except SaveError as error:
        session.notify(ui.style(f"Falha no salvamento automático: {error}", "bright_red"))
        session.pending_autosave = False
        return
    session.notify(ui.style(f"{ui.sym('check')} Progresso salvo automaticamente.", "green"))


# --------------------------------------------------------------------------- partidas

def new_game(settings: Settings) -> None:
    player = character_creation.create_character()
    if player is None:
        return
    state = GameState.new(player)
    state.add_journal("convocacao", "O cartaz de convocação",
                      "O cartaz que trouxe você ao vale pede que os aventureiros procurem a Anciã Ysolde, na "
                      "Vila de Primórdia.")
    character_creation.play_intro(player)
    session = GameSession(state, settings)
    session.begin(new_game=True)
    try:
        session.save()
    except SaveError as error:
        session.notify(ui.style(f"Atenção: {error}", "bright_red"))
    game_loop(session)


def continue_game(path: Path, settings: Settings) -> None:
    try:
        state = save_system.load_game(path)
    except SaveError as error:
        ui.echo(ui.style(f"  {error}", "bright_red"))
        ui.pause()
        return
    session = GameSession(state, settings)
    session.begin()
    session.notify(ui.style(f"Que bom ver você de volta, {state.player.name}!", "bright_yellow"))
    game_loop(session)


def describe_save(info: SaveInfo) -> str:
    if info.damaged:
        return ui.style(f"{info.name} (arquivo danificado)", "bright_red")
    try:
        when = datetime.fromisoformat(info.saved_at).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        when = "?"
    details = (f" {ui.sym('dot')} Dia {info.day} {ui.sym('dot')} {info.location} {ui.sym('dot')} "
               f"{format_duration(info.play_seconds)} {ui.sym('dot')} salvo em {when}")
    return ui.style(info.name, "bold") + f" — {info.class_name} nível {info.level}" + ui.style(details, "gray")


def load_menu(settings: Settings) -> None:
    while True:
        screens.section("CARREGAR JOGO")
        saves = save_system.list_saves()
        if not saves:
            ui.echo("  Nenhum jogo salvo ainda. Que tal começar uma nova aventura?")
            ui.echo()
            ui.pause()
            return
        choice = ui.choose([describe_save(info) for info in saves], prompt="Escolha um save", cancel="Voltar")
        if choice is None:
            return
        info = saves[choice]
        ui.echo()
        action = ui.choose(["Jogar", ui.style("Apagar este save", "bright_red")], prompt="Ação", cancel="Voltar")
        if action == 0:
            continue_game(info.path, settings)
            return
        if action == 1 and ui.confirm(f"Apagar para sempre o save de {info.name}?", default=False):
            save_system.delete_save(info.path)


# --------------------------------------------------------------------------- menu principal

def main_menu(settings: Settings) -> None:
    while True:
        screens.title_screen()
        saves = [info for info in save_system.list_saves() if not info.damaged]
        options, actions = [], []
        if saves:
            latest = saves[0]
            options.append(ui.style("Continuar", "bright_green bold")
                           + ui.style(f"  ({latest.name}, nível {latest.level}, Dia {latest.day})", "gray"))
            actions.append("continuar")
        options += ["Novo jogo", "Carregar jogo", "Opções", "Como jogar", "Sair"]
        actions += ["novo", "carregar", "opcoes", "ajuda", "sair"]
        action = actions[ui.choose(options) or 0]
        if action == "continuar":
            continue_game(saves[0].path, settings)
        elif action == "novo":
            new_game(settings)
        elif action == "carregar":
            load_menu(settings)
        elif action == "opcoes":
            commands.options_menu(settings)
        elif action == "ajuda":
            commands.help_screen()
            ui.pause()
        else:
            ui.echo(ui.style("\n  Até a próxima aventura!\n", "bright_yellow"))
            return


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    settings = Settings.load()
    ui.init_terminal()
    apply_display(settings, args)
    try:
        main_menu(settings)
    except (KeyboardInterrupt, ui.InputClosed):
        ui.echo(ui.style("\n  Até a próxima aventura!", "bright_yellow"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
