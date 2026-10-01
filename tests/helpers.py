"""Utilidades compartilhadas pelos testes."""

from __future__ import annotations

import os
import tempfile
import unittest

from rpg.character_creation import build_player
from rpg.config import Settings
from rpg.session import GameSession
from rpg.state import GameState

DRAFT = {
    "name": "Teste", "gender": "feminino", "class_id": "guerreiro", "hair_style": "trancas_guerreiras",
    "hair_color": "ruivo", "feature": "cicatriz", "armor_color": "azul_real", "alignment": "neutro_bom",
}


def make_session(**overrides: str) -> GameSession:
    player = build_player({**DRAFT, **overrides})
    state = GameState.new(player, seed=42)
    session = GameSession(state, Settings(autosave=True))
    session.begin(new_game=True)
    return session


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
