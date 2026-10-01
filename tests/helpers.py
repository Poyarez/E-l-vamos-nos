"""Utilidades compartilhadas pelos testes."""

from __future__ import annotations

import contextlib
import io
import os
import random
import tempfile
import unittest

from typing import Optional

from rpg import ui
from rpg.character_creation import build_player
from rpg.config import Settings
from rpg.session import GameSession
from rpg.state import GameState
from rpg.time_system import MINUTES_PER_DAY

DRAFT = {
    "name": "Teste", "gender": "feminino", "class_id": "guerreiro", "hair_style": "trancas_guerreiras",
    "hair_color": "ruivo", "feature": "cicatriz", "armor_color": "azul_real", "alignment": "neutro_bom",
}


class FixedRandom(random.Random):
    """Gerador "viciado": ``random()`` sempre devolve o mesmo valor.

    Com 0.5, todo golpe acerta, nada é crítico e as criaturas só usam habilidades com
    chance acima de 50% — o que deixa as lutas totalmente previsíveis.
    """

    def __init__(self, value: float = 0.5) -> None:
        super().__init__(0)
        self.value = value

    def random(self) -> float:
        return self.value


def make_session(rng: Optional[random.Random] = None, **overrides: str) -> GameSession:
    player = build_player({**DRAFT, **overrides})
    state = GameState.new(player, seed=42)
    session = GameSession(state, Settings(autosave=True), rng=rng or random.Random(0))
    session.begin(new_game=True)
    return session


def place(session: GameSession, x: int, y: int, map_id: Optional[str] = None) -> None:
    """Teleporta o herói (para testar um ponto específico do mapa)."""
    if map_id:
        session.state.map_id = map_id
    session.state.x, session.state.y = x, y
    session.arrive()


def set_hour(session: GameSession, hour: int) -> None:
    clock = session.clock
    clock.minutes = (clock.day - 1) * MINUTES_PER_DAY + hour * 60


class QuietTestCase(unittest.TestCase):
    """Silencia a saída de texto e permite simular o que o jogador digita."""

    def setUp(self) -> None:
        super().setUp()
        self._stdout = contextlib.redirect_stdout(io.StringIO())
        self.output = self._stdout.__enter__()
        self._old_input = ui.input_func

    def tearDown(self) -> None:
        ui.input_func = self._old_input
        self._stdout.__exit__(None, None, None)
        super().tearDown()

    def type_in(self, *answers: str) -> None:
        queue = iter(answers)
        ui.input_func = lambda _prompt: next(queue)


class TempSaveDirMixin(unittest.TestCase):
    """Redireciona os saves para uma pasta temporária durante o teste."""

    def setUp(self) -> None:
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self._old = os.environ.get("PRIMORDIA_SAVE_DIR")
        os.environ["PRIMORDIA_SAVE_DIR"] = self._tmp.name

    def tearDown(self) -> None:
        if self._old is None:
            os.environ.pop("PRIMORDIA_SAVE_DIR", None)
        else:
            os.environ["PRIMORDIA_SAVE_DIR"] = self._old
        self._tmp.cleanup()
        super().tearDown()
