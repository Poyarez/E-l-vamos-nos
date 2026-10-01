"""Funções utilitárias sem dependência de terminal: texto, sorteios estáveis e dinheiro."""

from __future__ import annotations

import re
import unicodedata
import zlib
from typing import Sequence, TypeVar

T = TypeVar("T")

COPPER_PER_SILVER = 100
COPPER_PER_GOLD = 100 * COPPER_PER_SILVER


def normalize(text: str) -> str:
    """Minúsculas, sem acentos e com espaços simples — usado para comparar comandos e nomes."""
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(without_marks.lower().split())


def slugify(text: str) -> str:
    """Converte um nome em um identificador seguro para arquivos ("Árwen Lua" -> "arwen-lua")."""
    slug = re.sub(r"[^a-z0-9]+", "-", normalize(text)).strip("-")
    return slug or "heroi"


def stable_hash(*parts: object) -> int:
    """Hash determinístico (o ``hash()`` do Python muda a cada execução para strings)."""
    return zlib.crc32("|".join(str(part) for part in parts).encode("utf-8"))


def stable_choice(options: Sequence[T], *seed_parts: object) -> T:
    """Escolhe sempre o mesmo elemento para as mesmas sementes (ex.: coordenadas de um tile)."""
    if not options:
        raise ValueError("stable_choice precisa de pelo menos uma opção")
    return options[stable_hash(*seed_parts) % len(options)]


def format_money(copper: int) -> str:
    """Formata moedas no padrão ouro/prata/cobre: 12345 -> '1o 23p 45c'."""
    copper = max(0, int(copper))
    gold, rest = divmod(copper, COPPER_PER_GOLD)
    silver, copper = divmod(rest, COPPER_PER_SILVER)
    parts = []
    if gold:
        parts.append(f"{gold}o")
    if silver or gold:
        parts.append(f"{silver}p")
    parts.append(f"{copper}c")
    return " ".join(parts)


def format_duration(seconds: float) -> str:
    """Tempo de jogo legível: 3725 -> '1h 02min'."""
    minutes = int(seconds) // 60
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes:02d}min"
    return f"{minutes}min"


def plural(count: int, singular: str, plural_form: str) -> str:
    return singular if count == 1 else plural_form


def capitalize_first(text: str) -> str:
    """Como ``str.capitalize``, mas sem rebaixar o resto do texto."""
    return text[:1].upper() + text[1:]
