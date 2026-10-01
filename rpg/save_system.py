"""Salvamento e carregamento em JSON.

* Um arquivo por personagem: ``saves/<nome>-<id>.json`` (legível e fácil de copiar).
* Escrita atômica (arquivo temporário + ``os.replace``) e cópia de segurança ``.bak``:
  uma queda de energia no meio do salvamento nunca leva a progressão embora.
* Cada save registra ``version``; ``migrate`` atualiza saves antigos quando o formato mudar.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, MutableMapping

from . import world
from .config import GAME_VERSION, SETTINGS_FILENAME, save_dir
from .state import GameState
from .utils import slugify

SAVE_VERSION = 1

#: versão -> função que converte um save dessa versão para a seguinte.
MIGRATIONS: Dict[int, Callable[[MutableMapping[str, Any]], None]] = {}


class SaveError(Exception):
    """Falha ao ler ou gravar um save (mensagem pronta para o jogador)."""


@dataclass
class SaveInfo:
    path: Path
    name: str
    class_name: str
    level: int
    day: int
    location: str
    saved_at: str
    play_seconds: float
    damaged: bool = False


def location_name(state: GameState) -> str:
    game_map = world.get_map(state.map_id)
    landmark = game_map.landmark_at(state.x, state.y)
    if landmark and landmark.id in state.discovered:
        return landmark.name
    region = game_map.region_at(state.x, state.y)
    return region.name if region else game_map.name


def save_path(state: GameState) -> Path:
    return save_dir() / f"{slugify(state.player.name)}-{state.save_id}.json"


def save_game(state: GameState) -> Path:
    """Grava a partida e devolve o caminho do arquivo."""
    path = save_path(state)
    payload = {
        "version": SAVE_VERSION,
        "game_version": GAME_VERSION,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "name": state.player.name,
            "class": state.player.class_name,
            "level": state.player.level,
            "day": state.clock.day,
            "location": location_name(state),
            "play_seconds": round(state.play_seconds, 1),
        },
        "state": state.to_dict(),
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        if path.exists():
            shutil.copy2(path, path.with_suffix(".bak"))
        os.replace(temp, path)
    except OSError as error:
        raise SaveError(f"Não foi possível salvar em {path}: {error}") from error
    return path


def migrate(data: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    version = int(data.get("version", 1))
    if version > SAVE_VERSION:
        raise SaveError("Este save foi criado por uma versão mais nova do jogo.")
    while version < SAVE_VERSION:
        MIGRATIONS[version](data)
        version += 1
        data["version"] = version
    return data


def _read(path: Path) -> GameState:
    data = migrate(json.loads(path.read_text(encoding="utf-8")))
    return GameState.from_dict(data["state"])


def load_game(path: Path) -> GameState:
    """Carrega um save; se estiver danificado, tenta a cópia de segurança."""
    try:
        return _read(path)
    except SaveError:
        raise
    except (OSError, ValueError, KeyError, TypeError) as error:
        backup = path.with_suffix(".bak")
        if backup.exists():
            try:
                return _read(backup)
            except (OSError, ValueError, KeyError, TypeError):
                pass
        raise SaveError(f"O save {path.name} está danificado e não pôde ser lido ({error}).") from error


def _info(path: Path) -> SaveInfo:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        summary: Mapping[str, Any] = data["summary"]
        return SaveInfo(path, str(summary["name"]), str(summary["class"]), int(summary["level"]),
                        int(summary["day"]), str(summary["location"]), str(data.get("saved_at", "")),
                        float(summary.get("play_seconds", 0)))
    except (OSError, ValueError, KeyError, TypeError):
        return SaveInfo(path, path.stem, "?", 0, 0, "?", "", 0.0, damaged=True)


def list_saves() -> List[SaveInfo]:
    """Saves disponíveis, do mais recente para o mais antigo."""
    directory = save_dir()
    if not directory.is_dir():
        return []
    infos = [_info(path) for path in directory.glob("*.json") if path.name != SETTINGS_FILENAME]
    return sorted(infos, key=lambda info: info.saved_at, reverse=True)


def delete_save(path: Path) -> None:
    for candidate in (path, path.with_suffix(".bak")):
        try:
            candidate.unlink()
        except FileNotFoundError:
            pass
