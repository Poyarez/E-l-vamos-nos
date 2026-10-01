"""Configurações globais: título, versão, caminhos e preferências do jogador."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from . import __version__

GAME_TITLE = "Crônicas de Primórdia"
GAME_SUBTITLE = "Um RPG de fantasia medieval para o terminal"
GAME_VERSION = __version__

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILENAME = "settings.json"


def save_dir() -> Path:
    """Pasta dos saves. Pode ser trocada pela variável de ambiente ``PRIMORDIA_SAVE_DIR``."""
    custom = os.environ.get("PRIMORDIA_SAVE_DIR")
    return Path(custom) if custom else PROJECT_ROOT / "saves"


@dataclass
class Settings:
    """Preferências do jogador, persistidas em ``saves/settings.json``."""

    color: bool = True          # cores ANSI
    unicode: bool = True        # molduras e símbolos Unicode (senão, ASCII puro)
    typewriter: bool = True     # narração letra a letra
    clear_screen: bool = True   # redesenhar a tela a cada passo
    autosave: bool = True       # salvar ao amanhecer e ao dormir
    timing: bool = True         # minijogo de reflexo para golpes e bloqueios perfeitos

    @classmethod
    def load(cls) -> "Settings":
        try:
            data = json.loads((save_dir() / SETTINGS_FILENAME).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls()
        if not isinstance(data, dict):
            return cls()
        known = {f.name for f in fields(cls)}
        return cls(**{key: bool(value) for key, value in data.items() if key in known})

    def save(self) -> None:
        directory = save_dir()
        directory.mkdir(parents=True, exist_ok=True)
        (directory / SETTINGS_FILENAME).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
