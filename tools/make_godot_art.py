"""Gera a arte provisória da versão Godot: tiles de terreno, personagens e ícones.

Tudo é desenhado por código (Python puro, sem bibliotecas), em pixel art 16x16, para que o
jogo tenha cara de jogo desde já. A ideia é trocar estes PNGs por arte de verdade depois
(por exemplo, os pacotes gratuitos do Kenney): basta manter o mesmo tamanho dos tiles.

Uso (na raiz do repositório):

    python tools/make_godot_art.py

Saída em ``godot/art/``:

* ``tiles.png``     — uma linha por terreno, até 3 variações por linha (16x16 cada);
* ``hero.png``      — camadas do herói (corpo, roupa e cabelos), 4 direções x 2 passos;
* ``npcs.png``      — os moradores do vale, já coloridos, 4 direções x 2 passos;
* ``icons.png``     — marcadores: local novo, local conhecido, passagem e "!";
* ``monsters.png``  — as criaturas de perfil (olhando para a esquerda), parado e passo.

E ``godot/data/art.json``, que diz ao Godot onde está cada coisa nas imagens.
"""

from __future__ import annotations

import json
import random
import struct
import sys
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpg.data.npcs import NPCS  # noqa: E402
from rpg.data.terrain import TERRAIN  # noqa: E402

ART_DIR = ROOT / "godot" / "art"
DATA_DIR = ROOT / "godot" / "data"
TILE = 16
VARIANTS = 3

Color = Tuple[int, int, int, int]
CLEAR: Color = (0, 0, 0, 0)


def hex_color(code: str, alpha: int = 255) -> Color:
    code = code.lstrip("#")
    return int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), alpha


def shade(color: Color, factor: float) -> Color:
    return (min(255, int(color[0] * factor)), min(255, int(color[1] * factor)), min(255, int(color[2] * factor)),
            color[3])


# --------------------------------------------------------------------------- imagem e PNG

class Canvas:
    def __init__(self, width: int, height: int) -> None:
        self.width, self.height = width, height
        self.pixels: List[List[Color]] = [[CLEAR] * width for _ in range(height)]

    def set(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def get(self, x: int, y: int) -> Color:
        return self.pixels[y][x]

    def fill(self, x0: int, y0: int, w: int, h: int, color: Color) -> None:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.set(x, y, color)

    def paste(self, other: "Canvas", ox: int, oy: int) -> None:
        for y in range(other.height):
            for x in range(other.width):
                color = other.get(x, y)
                if color[3]:
                    self.set(ox + x, oy + y, color)

    def stamp(self, rows: Sequence[str], palette: Dict[str, Color], ox: int = 0, oy: int = 0,
              mirror: bool = False) -> None:
        """Desenha um molde em texto: cada letra é uma cor da paleta; '.' é transparente."""
        for y, row in enumerate(rows):
            for x, char in enumerate(row[::-1] if mirror else row):
                if char != "." and char in palette:
                    self.set(ox + x, oy + y, palette[char])

    def scaled(self, factor: int) -> "Canvas":
        big = Canvas(self.width * factor, self.height * factor)
        for y in range(self.height):
            for x in range(self.width):
                big.fill(x * factor, y * factor, factor, factor, self.get(x, y))
        return big

    def save(self, path: Path) -> None:
        raw = b"".join(b"\x00" + bytes(channel for pixel in row for channel in pixel) for row in self.pixels)

        def chunk(tag: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9))
                         + chunk(b"IEND", b""))


# --------------------------------------------------------------------------- terrenos

def speckle(tile: Canvas, rng: random.Random, colors: Sequence[Color], count: int,
            size: int = 1) -> None:
    for _ in range(count):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        color = rng.choice(colors)
        for dy in range(size):
            for dx in range(size):
                tile.set(x + dx, y + dy, color)


def base(color: str, rng: random.Random, light: str, dark: str, amount: int = 26) -> Canvas:
    tile = Canvas(TILE, TILE)
    tile.fill(0, 0, TILE, TILE, hex_color(color))
    speckle(tile, rng, [hex_color(light)], amount)
    speckle(tile, rng, [hex_color(dark)], amount)
    return tile


TREE = [
    "................",
    ".....oooooo.....",
    "...ooLLLLLLoo...",
    "..oLLLLLLLLLLo..",
    ".oLLLlLLLLLLlLo.",
    ".oLLLLLLLlLLLLo.",
    "oLLlLLLLLLLLLLLo",
    "oLLLLLLlLLLLlLLo",
    "oDLLLLLLLLLLLLDo",
    ".oDDLLLlLLLLDDo.",
    "..ooDDDDDDDDoo..",
    "....ooottooo....",
    "......otto......",
    "......otto......",
    ".....ottto......",
    "................",
]

PINE = [
    ".......oo.......",
    "......oLLo......",
    ".....oLLLLo.....",
    "....oLLlLLLo....",
    "...oLLLLLLlLo...",
    "....ooLLLLoo....",
    "...oLLLLlLLLo...",
    "..oLLlLLLLLLLo..",
    ".oLLLLLLLlLLLLo.",
    "..ooDLLLLLLDoo..",
    ".oDDLLLlLLLLDDo.",
    "oDDDDLLLLLLDDDDo",
    ".oooooottooooo..",
    "......otto......",
    "......otto......",
    "................",
]

MOUNTAIN = [
    "................",
    ".......oo.......",
    "......owwo......",
    ".....owwwlo.....",
    "....owwwllMo....",
    "...oMwwlMMMMo...",
    "...oMMMMMMMMo...",
    "..oMMMMlMMMMDo..",
    "..oMMMMMMMMDDo..",
    ".oMMMlMMMMDDDDo.",
    ".oMMMMMMMMMDDDo.",
    "oMMMMMMlMMDDDDDo",
    "oMlMMMMMMMMDDDDo",
    "oMMMMMMMMMMMDDDo",
    "oooooooooooooooo",
    "................",
]

HOUSE = [
    "................",
    "......oooo......",
    "....ooRRRRoo....",
    "...oRRRRRRRRo...",
    "..oRRrRRRRrRRo..",
    ".oRRRRRRRRRRRRo.",
    "oRRrRRRRRRRRrRRo",
    "oooooooooooooooo",
    ".oWWWWWWWWWWWWo.",
    ".oWWbbWWWWbbWWo.",
    ".oWWbbWWWWbbWWo.",
    ".oWWWWWddWWWWWo.",
    ".oWWWWWddWWWWWo.",
    ".oWWWWWddWWWWWo.",
    ".oooooooooooooo.",
    "................",
]

TENT = [
    "................",
    ".......oo.......",
    "......oRRo......",
    ".....oRRRRo.....",
    "....oRRRrRRo....",
    "....oRRRrRRRo...",
    "...oRRRRrRRRRo..",
    "...oRRRdddRRRo..",
    "..oRRRddddRRRRo.",
    "..oRRRddddRRRRo.",
    ".oRRRRddddRRRRRo",
    ".oooooooooooooo.",
    "................",
    "................",
    "................",
    "................",
]

TOMB = [
    "....oooo........",
    "...oSSSSo.......",
    "...oSsSSo.......",
    "...oSSSSo.......",
    "...oSSSSo.......",
    "..oooooooo......",
    "................",
]

STONE = [
    "..oooo..",
    ".oSSSSo.",
    "oSSsSSSo",
    "oSSSSSDo",
    ".oDDDDo.",
    "..oooo..",
]


def ground_tile(terrain_id: str, variant: int) -> Canvas:
    rng = random.Random(f"{terrain_id}:{variant}")
    outline = hex_color("#22201f")
    if terrain_id == "planicie":
        tile = base("#5f9a3e", rng, "#7cb54f", "#4b7f31")
        for _ in range(3):
            x, y = rng.randrange(1, 15), rng.randrange(2, 15)
            tile.set(x, y, hex_color("#9ccf62"))
            tile.set(x, y - 1, hex_color("#9ccf62"))
        if variant == 2:
            tile.set(rng.randrange(2, 14), rng.randrange(2, 14), hex_color("#f2e06b"))
        return tile
    if terrain_id == "relva_alta":
        tile = base("#4f8f35", rng, "#6aac45", "#3d742a", 14)
        for _ in range(9):
            x, y = rng.randrange(0, 16), rng.randrange(4, 16)
            for dy in range(4):
                tile.set(x, y - dy, hex_color("#8fd15a" if dy == 3 else "#6fb546"))
        return tile
    if terrain_id == "lavoura":
        tile = base("#8a5a33", rng, "#9c6a3d", "#734a29", 10)
        for y in range(1, 16, 4):
            for x in range(16):
                tile.set(x, y, hex_color("#6d4325"))
                if (x + variant) % 3:
                    tile.set(x, y - 1, hex_color("#c9b84a" if variant != 1 else "#a8c24a"))
        return tile
    if terrain_id in ("floresta", "mata_antiga"):
        ground = "#3f6b2d" if terrain_id == "floresta" else "#2f5426"
        tile = base(ground, rng, "#4c7d36", "#335a26", 16)
        light, mid, dark = (("#5d9a3f", "#4a8233", "#356326") if terrain_id == "floresta"
                            else ("#3f7a3a", "#2f6330", "#214a25"))
        rows = PINE if variant == 1 and terrain_id == "floresta" else TREE
        tile.stamp(rows, {"o": outline, "L": hex_color(mid), "l": hex_color(light), "D": hex_color(dark),
                          "t": hex_color("#5b3a22")})
        return tile
    if terrain_id == "colinas":
        tile = base("#7d9145", rng, "#93a956", "#677a39", 18)
        for cx in (4 + variant, 11 - variant):
            for dx in range(-3, 4):
                tile.set(cx + dx, 9 - (3 - abs(dx)) // 2, hex_color("#5b6b30"))
        return tile
    if terrain_id == "rochas":
        tile = base("#6f8f45", rng, "#829f55", "#5c7a39", 14)
        palette = {"o": outline, "S": hex_color("#9a9a9a"), "s": hex_color("#c4c4c4"), "D": hex_color("#6b6b6b")}
        tile.stamp(STONE, palette, 1 + variant, 2)
        tile.stamp(STONE, palette, 8 - variant, 9)
        return tile
    if terrain_id in ("agua", "lago_subterraneo"):
        deep, light, dark = (("#2f5f9f", "#4f86c6", "#28528a") if terrain_id == "agua"
                             else ("#1d3557", "#2c4f7c", "#162a45"))
        tile = base(deep, rng, light, dark, 10)
        for y in (3 + variant, 10 - variant):
            x = rng.randrange(1, 9)
            for dx in range(5):
                tile.set(x + dx, y, hex_color("#8fc3ea" if terrain_id == "agua" else "#4a78a8"))
        return tile
    if terrain_id == "agua_rasa":
        tile = base("#4f9ac6", rng, "#6fb2d9", "#3f88b3", 12)
        speckle(tile, rng, [hex_color("#c9b98a")], 6)
        x = rng.randrange(1, 10)
        for dx in range(4):
            tile.set(x + dx, 6 + variant, hex_color("#bfe3f5"))
        return tile
    if terrain_id == "pantano":
        tile = base("#4f5a2f", rng, "#616d3a", "#3f4826", 18)
        tile.fill(3 + variant, 7, 6, 3, hex_color("#2f3a2a"))
        tile.fill(4 + variant, 6, 4, 1, hex_color("#2f3a2a"))
        for x in (11, 13):
            for dy in range(4):
                tile.set(x - variant, 12 - dy, hex_color("#7a8a3f"))
        return tile
    if terrain_id == "estrada":
        tile = base("#b08a5a", rng, "#c4a070", "#957347", 22)
        speckle(tile, rng, [hex_color("#d9bc8c"), hex_color("#7d5f3a")], 5)
        return tile
    if terrain_id == "ponte":
        tile = Canvas(TILE, TILE)
        for y in range(16):
            plank = "#a8743f" if (y // 4) % 2 else "#93653a"
            for x in range(16):
                tile.set(x, y, hex_color(plank))
            if y % 4 == 3:
                for x in range(16):
                    tile.set(x, y, hex_color("#5b3a22"))
        for y in range(16):
            tile.set(0, y, hex_color("#4a2f1c"))
            tile.set(15, y, hex_color("#4a2f1c"))
        return tile
    if terrain_id == "calcamento":
        tile = Canvas(TILE, TILE)
        tile.fill(0, 0, 16, 16, hex_color("#5f5f5f"))
        for row in range(4):
            offset = (row % 2) * 4 + variant
            for col in range(-1, 3):
                x0 = col * 8 + offset
                tile.fill(x0 + 1, row * 4 + 1, 6, 3, hex_color("#8f8f8f" if (row + col) % 2 else "#9a9a9a"))
                tile.set(x0 + 1, row * 4 + 1, hex_color("#b0b0b0"))
        return tile
    if terrain_id == "construcao":
        tile = Canvas(TILE, TILE)
        tile.fill(0, 0, 16, 16, hex_color("#c9b08a"))
        roof = ("#a8443a", "#7a2f2a") if variant != 1 else ("#7a5a3a", "#5b412a")
        tile.stamp(HOUSE, {"o": outline, "R": hex_color(roof[0]), "r": hex_color(roof[1]),
                           "W": hex_color("#d9c49a"), "b": hex_color("#4f86c6"), "d": hex_color("#5b3a22")})
        return tile
    if terrain_id == "ruinas":
        tile = base("#6f8f45", rng, "#829f55", "#5c7a39", 10)
        for (x, y, w, h) in ((1 + variant, 2, 6, 4), (9, 7 - variant, 5, 5), (2, 10, 5, 4)):
            tile.fill(x, y, w, h, hex_color("#d9d4c7"))
            tile.fill(x, y + h - 1, w, 1, hex_color("#b0aa9a"))
            tile.set(x + w - 1, y, hex_color("#b0aa9a"))
        return tile
    if terrain_id == "tumulos":
        tile = base("#5f8a3e", rng, "#729f4c", "#4b7031", 12)
        palette = {"o": outline, "S": hex_color("#a0a0a0"), "s": hex_color("#c8c8c8")}
        tile.stamp(TOMB, palette, 1 + variant, 2)
        tile.stamp(TOMB, palette, 8, 8 - variant)
        return tile
    if terrain_id == "caverna":
        tile = base("#6b6b6b", rng, "#808080", "#585858", 14)
        for y in range(4, 15):
            half = min(6, (y - 3) * 2)
            for x in range(8 - half, 8 + half):
                tile.set(x, y, hex_color("#141414"))
        return tile
    if terrain_id == "montanha":
        tile = base("#6f6f6f", rng, "#7d7d7d", "#5f5f5f", 10)
        tile.stamp(MOUNTAIN, {"o": outline, "M": hex_color("#8a8a8a"), "l": hex_color("#a8a8a8"),
                              "D": hex_color("#666666"), "w": hex_color("#eeeeee")})
        return tile
    if terrain_id == "cachoeira":
        tile = Canvas(TILE, TILE)
        tile.fill(0, 0, 16, 16, hex_color("#4f86c6"))
        for x in range(16):
            for y in range(16):
                if (x * 3 + y + variant * 5) % 7 < 2:
                    tile.set(x, y, hex_color("#e0f2ff"))
                elif (x + y * 2) % 5 == 0:
                    tile.set(x, y, hex_color("#8fc3ea"))
        return tile
    if terrain_id in ("chao_gruta", "chao_toca", "chao_mina"):
        colors = {"chao_gruta": ("#4a4540", "#5c5650", "#3a3632"), "chao_toca": ("#6b5233", "#7d6240", "#5a442a"),
                  "chao_mina": ("#7a5f3a", "#8f7045", "#664e30")}[terrain_id]
        tile = base(colors[0], rng, colors[1], colors[2], 24)
        return tile
    if terrain_id == "parede_gruta":
        tile = base("#2a2624", rng, "#3a3430", "#1e1b1a", 30)
        for y in range(0, 16, 5):
            for x in range(16):
                if (x + y + variant) % 9 < 5:
                    tile.set(x, y + 1, hex_color("#3d3632"))
        return tile
    if terrain_id == "cristais":
        tile = base("#4a4540", rng, "#5c5650", "#3a3632", 18)
        for (x, y, h) in ((3 + variant, 12, 6), (8, 13, 8), (12 - variant, 11, 5)):
            for dy in range(h):
                tile.set(x, y - dy, hex_color("#6fe0f0"))
                tile.set(x + 1, y - dy, hex_color("#b8f4ff" if dy < h - 1 else "#6fe0f0"))
            tile.set(x, y - h, hex_color("#e8fdff"))
        return tile
    if terrain_id == "entalhes":
        tile = base("#5a4a6a", rng, "#66557a", "#4a3d58", 16)
        for (cx, cy) in ((4, 4), (11, 11)):
            for dx, dy in ((0, -2), (1, -2), (2, -1), (2, 0), (2, 1), (1, 2), (0, 2)):
                tile.set(cx + dx - variant % 2, cy + dy, hex_color("#b8a6d9"))
        return tile
    if terrain_id == "ossos":
        tile = base("#6b5233", rng, "#7d6240", "#5a442a", 18)
        for (x, y) in ((2 + variant, 4), (9, 10 - variant), (4, 12)):
            tile.fill(x, y, 5, 1, hex_color("#e8e0cc"))
            tile.set(x, y - 1, hex_color("#e8e0cc"))
            tile.set(x + 4, y + 1, hex_color("#e8e0cc"))
        return tile
    if terrain_id == "raizes":
        tile = base("#6b5233", rng, "#7d6240", "#5a442a", 14)
        for x in (2 + variant, 7, 12 - variant):
            length = rng.randrange(7, 14)
            for y in range(length):
                tile.set(x + (y // 4) % 2, y, hex_color("#5a7a32" if y % 3 else "#6b4a2a"))
        return tile
    if terrain_id == "porta_selada":
        tile = Canvas(TILE, TILE)
        tile.fill(0, 0, 16, 16, hex_color("#8f86a8"))
        tile.fill(0, 0, 16, 1, outline)
        tile.fill(0, 15, 16, 1, outline)
        for cx in (3, 8, 13):
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                tile.set(cx + dx, 7 + dy, hex_color("#e6e0ff"))
            tile.set(cx, 7, hex_color("#5a4a7a"))
        return tile
    if terrain_id == "trilhos":
        tile = base("#7a5f3a", rng, "#8f7045", "#664e30", 16)
        for y in range(1, 16, 4):
            tile.fill(2, y, 12, 2, hex_color("#5b3a22"))
        for x in (4, 11):
            tile.fill(x, 0, 1, 16, hex_color("#a8a8a8"))
            tile.fill(x + 1, 0, 1, 16, hex_color("#6b6b6b"))
        return tile
    if terrain_id == "entulho":
        tile = base("#7a5f3a", rng, "#8f7045", "#664e30", 10)
        palette = {"o": outline, "S": hex_color("#8a8a8a"), "s": hex_color("#b0b0b0"), "D": hex_color("#5f5f5f")}
        tile.stamp(STONE, palette, 0 + variant, 1)
        tile.stamp(STONE, palette, 7, 4 + variant)
        tile.stamp(STONE, palette, 2, 9)
        return tile
    if terrain_id == "fogo_violeta":
        tile = base("#2a1f3a", rng, "#36284a", "#20182c", 10)
        for (x, height) in ((3 + variant, 9), (7, 12), (11 - variant, 8)):
            for dy in range(height):
                width = max(1, (height - dy) // 3)
                for dx in range(-width + 1, width):
                    tile.set(x + dx, 15 - dy, hex_color("#e0a8ff" if dy > height - 4 else "#a04fd9"))
        return tile
    if terrain_id == "lajes":
        tile = Canvas(TILE, TILE)
        tile.fill(0, 0, 16, 16, hex_color("#e0dccf"))
        for i in range(16):
            tile.set(i, 0, hex_color("#b8b2a0"))
            tile.set(0, i, hex_color("#b8b2a0"))
            tile.set(i, 8, hex_color("#c8c2b0"))
            tile.set(8, i, hex_color("#c8c2b0"))
        speckle(tile, rng, [hex_color("#ece8dc"), hex_color("#d2cdbd")], 12)
        if variant == 2:
            for dx, dy in ((5, 4), (6, 3), (6, 5), (5, 6)):
                tile.set(dx, dy, hex_color("#a89fc2"))
        return tile
    if terrain_id == "areia":
        tile = base("#e0c98f", rng, "#ecd9a6", "#c9b073", 22)
        if variant == 1:
            for (x, y) in ((4, 5), (11, 11)):
                tile.set(x, y, hex_color("#f6efe0"))
                tile.set(x + 1, y, hex_color("#d9a88a"))
        return tile
    if terrain_id == "barracas":
        tile = base("#8f7a4f", rng, "#a08a5c", "#7a6842", 16)
        canvas = ("#a8443a", "#7a2f2a") if variant != 2 else ("#7a6a4a", "#5a4d35")
        tile.stamp(TENT, {"o": outline, "R": hex_color(canvas[0]), "r": hex_color(canvas[1]),
                          "d": hex_color("#2a1f1a")}, 0, 3)
        return tile
    raise KeyError(f"Sem desenho para o terreno {terrain_id!r}")


def make_tiles() -> Tuple[Canvas, Dict[str, List[int]]]:
    terrain_ids = list(TERRAIN)
    sheet = Canvas(TILE * VARIANTS, TILE * len(terrain_ids))
    atlas = {}
    for row, terrain_id in enumerate(terrain_ids):
        for variant in range(VARIANTS):
            sheet.paste(ground_tile(terrain_id, variant), variant * TILE, row * TILE)
        atlas[terrain_id] = [row, VARIANTS]
    return sheet, atlas


# --------------------------------------------------------------------------- personagens

# Moldes 16x16 do corpo. Letras: o contorno, s pele, S pele na sombra, e olhos, c roupa,
# C roupa na sombra, b cinto e botas, p calças. A roupa vem em tons de cinza: o Godot a
# pinta com a cor da armadura escolhida (e o cabelo, com a cor do cabelo).
BODY = {
    "down": [
        "................",
        "................",
        "......oooo......",
        ".....osssso.....",
        "....osssssso....",
        "....osessesso...",
        "....ossssssso...",
        ".....osssso.....",
        "....occcccco....",
        "...occcbbccco...",
        "...osccccccso...",
        "....occCCcco....",
        "....oppppppo....",
        "....opp..ppo....",
        "....obb..bbo....",
        "....ooo..ooo....",
    ],
    "up": [
        "................",
        "................",
        "......oooo......",
        ".....osssso.....",
        "....osssssso....",
        "....ossssssso...",
        "....ossssssso...",
        ".....osssso.....",
        "....occcccco....",
        "...occcbbccco...",
        "...osccccccso...",
        "....occCCcco....",
        "....oppppppo....",
        "....opp..ppo....",
        "....obb..bbo....",
        "....ooo..ooo....",
    ],
    "left": [
        "................",
        "................",
        "......oooo......",
        ".....osssso.....",
        "....osssssso....",
        "....oessssso....",
        "....osssssso....",
        ".....osssso.....",
        ".....occcco.....",
        "....occbbcco....",
        "....oscccCco....",
        ".....occCco.....",
        ".....oppppo.....",
        ".....opp.po.....",
        ".....obb.bo.....",
        ".....ooo.oo.....",
    ],
}
BODY["right"] = [row[::-1] for row in BODY["left"]]

# Passo: as pernas trocam de posição (as 4 últimas linhas)
STEP = {
    "down": ["....oppppppo....", "....opp..ppo....", "....obb..ooo....", "....ooo........."],
    "up": ["....oppppppo....", "....opp..ppo....", "....ooo..bbo....", ".........ooo...."],
    "left": [".....oppppo.....", "....opp..po.....", "....obb..bo.....", "....ooo..oo....."],
}
STEP["right"] = [row[::-1] for row in STEP["left"]]

# Cabelos (por cima da cabeça). h cabelo, H cabelo na sombra.
HAIR = {
    "curto": {
        "down": ["......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....", "....hH....Hh...."],
        "up": ["......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....", "....hhhhhhhh....",
               "....hHhhhhHh....", ".....hHHHHh....."],
        "left": ["......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....", "....h..hhhhh....",
                 ".......hhhH....."],
    },
    "longo": {
        "down": ["......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....", "...hhH....Hhh...",
                 "...hH......Hh...", "...hH......Hh...", "...hh......hh...", "....h......h...."],
        "up": ["......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....", "...hhhhhhhhhh...",
               "...hhhhhhhhhh...", "...hhHhhhhHhh...", "...hhHHhhHHhh...", "....hhhhhhhh....",
               ".....hHHHHh....."],
        "left": ["......hhhh......", ".....hhhhhh.....", "....hhhhhhhhh...", "....h..hhhhhh...",
                 ".......hhhhhh...", ".......hHhhhh...", "........hhhh....", ".........hh....."],
    },
    "coque": {
        "down": [".......hh.......", "......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....",
                 "....hH....Hh...."],
        "up": [".......hh.......", "......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....",
               "....hhhhhhhh....", "....hHhhhhHh...."],
        "left": [".........hh.....", "......hhhhh.....", ".....hhhhhh.....", "....hhhhhhhh....",
                 "....h..hhhhh...."],
    },
    "moicano": {
        "down": [".......hh.......", ".......hh.......", "......hhhh......", "......hHHh......"],
        "up": [".......hh.......", ".......hh.......", "......hhhh......", "......hhhh......",
               "......hHHh......"],
        "left": ["........hh......", ".......hhhh.....", "......hhhhh.....", ".......hhH......"],
    },
    "careca": {"down": [], "up": [], "left": []},
}
for _style in HAIR.values():
    _style["right"] = [row[::-1] for row in _style["left"]]
HAIR_OFFSET = 1          # o cabelo começa na linha 1 do molde (a cabeça começa na 2)

HAIR_SHAPES = {"curto_desgrenhado": "curto", "raspado_laterais": "curto", "longo_solto": "longo",
               "trancas_guerreiras": "longo", "rabo_de_cavalo": "longo", "cachos_volumosos": "longo",
               "coque_monastico": "coque", "moicano": "moicano", "cabeca_raspada": "careca"}

DIRECTIONS = ("down", "up", "left", "right")
OUTLINE = hex_color("#22201f")
SKIN_TONES = {"clara": ("#f0c8a8", "#d3a585"), "media": ("#d9a066", "#b9824f"), "escura": ("#8d5a3b", "#6f442b")}


def body_frame(direction: str, step: int) -> List[str]:
    rows = list(BODY[direction])
    if step:
        rows[12:16] = STEP[direction]
    return rows


def hero_layers() -> Tuple[Canvas, Dict[str, object]]:
    """Folha do herói: linha 0 = corpo; 1 = roupa; 2+ = cabelos. 8 colunas = 4 direções x 2 passos."""
    shapes = [shape for shape in HAIR if shape != "careca"]
    sheet = Canvas(TILE * 8, TILE * (2 + len(shapes)))
    skin, skin_shadow = SKIN_TONES["clara"]
    body_palette = {"o": OUTLINE, "s": hex_color(skin), "S": hex_color(skin_shadow), "e": OUTLINE,
                    "b": hex_color("#4a3a2a"), "p": hex_color("#4f4f6b")}
    cloth_palette = {"c": hex_color("#f2f2f2"), "C": hex_color("#b4b4b4")}
    hair_palette = {"h": hex_color("#f2f2f2"), "H": hex_color("#b8b8b8")}
    for column, (direction, step) in enumerate((d, s) for d in DIRECTIONS for s in (0, 1)):
        frame = body_frame(direction, step)
        sheet.stamp(frame, body_palette, column * TILE, 0)
        sheet.stamp(frame, cloth_palette, column * TILE, TILE)
        for row, shape in enumerate(shapes):
            sheet.stamp(HAIR[shape][direction], hair_palette, column * TILE, (2 + row) * TILE + HAIR_OFFSET)
    info = {"columns": [f"{d}_{s}" for d in DIRECTIONS for s in (0, 1)], "body_row": 0, "clothes_row": 1,
            "hair_rows": {shape: 2 + index for index, shape in enumerate(shapes)}, "hair_shapes": HAIR_SHAPES}
    return sheet, info


# Visual dos moradores: cabelo (forma e cor), roupa, pele e ajustes especiais.
NPC_LOOKS = {
    "ysolde": ("longo", "#eeeeee", "#7a3f9a", "clara"),
    "renna": ("curto", "#3a2a22", "#2f4fa3", "media"),
    "graca": ("coque", "#a8a8a8", "#3f8f4a", "media"),
    "brom": ("curto", "#b5482c", "#8a3a2a", "clara"),
    "marta": ("coque", "#6b4226", "#c9a43a", "clara"),
    "celeste": ("longo", "#e3c565", "#e8e2d0", "clara"),
    "anselmo": ("careca", "#a8a8a8", "#3f7f8f", "media"),
    "brigida": ("coque", "#d9d9d9", "#4f6b2f", "media"),
    "lirio": ("longo", "#6b4226", "#a03a8f", "clara"),
    "zahir": ("curto", "#2b2421", "#2f3f8f", "escura"),
    "tobias": ("careca", "#eeeeee", "#d9d2c0", "clara"),
    "kael": ("longo", "#cfefff", "#8fb8c8", "clara"),
    "davi": ("curto", "#2b2421", "#8a5a33", "media"),
    "pip": ("kobold", "#d9a92e", "#7a5a3a", "kobold"),
    "tome": ("curto", "#6b4226", "#2f4f8f", "clara"),
    "vigia": ("careca", "#e0dccf", "#c8c2b0", "pedra"),
}

KOBOLD = {
    "down": [
        "................",
        "......o..o......",
        ".....oyooyo.....",
        ".....oyyyyo.....",
        "....oyeyyeyo....",
        "....oyyyyyyo....",
        ".....oyrryo.....",
        "......oyyo......",
        ".....occcco.....",
        "....oyccccyo....",
        "....oyccccyo....",
        ".....occcco.....",
        ".....oy..yo.....",
        ".....oy..yo.....",
        ".....oo..oo.....",
        "................",
    ],
}
KOBOLD["up"] = [row.replace("e", "y").replace("r", "y") for row in KOBOLD["down"]]
KOBOLD["left"] = [
    "................",
    ".......o........",
    "......oyoo......",
    ".....oyyyyo.....",
    "....oeyyyyyo....",
    "...orryyyyyo....",
    "....oyyyyyo.....",
    "......oyyo......",
    ".....occcco.....",
    ".....occccyo....",
    ".....occccyo....",
    ".....occcco.....",
    "......oy.yo.....",
    "......oy.yo.....",
    "......oo.oo.....",
    "................",
]
KOBOLD["right"] = [row[::-1] for row in KOBOLD["left"]]
CANDLE = ["......F.........", ".....fFf........", "......w........."]


def npc_sheet() -> Tuple[Canvas, Dict[str, int]]:
    ids = list(NPCS)
    sheet = Canvas(TILE * 8, TILE * len(ids))
    rows = {}
    for row, npc_id in enumerate(ids):
        hair_shape, hair_color, cloth_color, skin_id = NPC_LOOKS.get(npc_id, ("curto", "#6b4226", "#7a7a7a", "clara"))
        rows[npc_id] = row
        for column, (direction, step) in enumerate((d, s) for d in DIRECTIONS for s in (0, 1)):
            ox, oy = column * TILE, row * TILE
            cloth = hex_color(cloth_color)
            if skin_id == "kobold":
                palette = {"o": OUTLINE, "y": hex_color("#c9a05a"), "e": hex_color("#ff7a2a"),
                           "r": hex_color("#8a5a3a"), "c": cloth}
                sheet.stamp(KOBOLD[direction], palette, ox, oy)
                if direction != "up":
                    sheet.stamp(CANDLE, {"F": hex_color("#ffd36b"), "f": hex_color("#ff9a3a"),
                                         "w": hex_color("#f2e6c8")}, ox + (2 if direction != "right" else 4), oy - 1)
                continue
            if skin_id == "pedra":
                skin, shadow = "#d9d4c7", "#b0aa9a"
            else:
                skin, shadow = SKIN_TONES[skin_id]
            palette = {"o": OUTLINE, "s": hex_color(skin), "S": hex_color(shadow),
                       "e": hex_color("#6fe0f0") if npc_id in ("vigia", "kael") else OUTLINE,
                       "b": hex_color("#4a3a2a"), "p": hex_color("#4f4f6b"), "c": cloth, "C": shade(cloth, 0.72)}
            sheet.stamp(body_frame(direction, step), palette, ox, oy)
            sheet.stamp(HAIR[hair_shape][direction], {"h": hex_color(hair_color),
                                                      "H": shade(hex_color(hair_color), 0.75)}, ox, oy + HAIR_OFFSET)
    return sheet, rows


# --------------------------------------------------------------------------- monstros

# Moldes 16x16 das criaturas, de perfil, olhando para a esquerda (o Godot espelha para a
# direita). Dois quadros: parado e passo. Letras: o contorno, a cor principal, b sombra,
# c clara (barriga, brilho), e olhos, n focinho, w dentes/garras/bico, t cauda, s espinhos.
def _shape(rows: List[str]) -> List[str]:
    assert len(rows) == TILE and all(len(row) == TILE for row in rows), rows
    return rows


MONSTER_SHAPES: Dict[str, Tuple[List[str], List[str]]] = {
    "lobo": (_shape([
        "................",
        "................",
        "................",
        "................",
        "..o.o...........",
        ".oaoao..........",
        ".oaaaao.......o.",
        "oeaaaaaoooooooao",
        "onaaaaaaaaaaaaao",
        ".owaaaaaaaaaaao.",
        "..oobaaaaaaabbo.",
        "....obacccccabo.",
        "....oao.ooo.oao.",
        "....oao.....oao.",
        "....oao.....oao.",
        "....ooo.....ooo.",
    ]), _shape([
        "................",
        "................",
        "................",
        "................",
        "..o.o...........",
        ".oaoao..........",
        ".oaaaao.......o.",
        "oeaaaaaoooooooao",
        "onaaaaaaaaaaaaao",
        ".owaaaaaaaaaaao.",
        "..oobaaaaaaabbo.",
        "....obacccccabo.",
        "...oao..ooo..oao",
        "...oao.......oao",
        "..oao.......oao.",
        "..ooo.......ooo.",
    ])),
    "javali": (_shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....oosoosoo...",
        "...ooaaaaaaaaoo.",
        "..oeaaaaaaaaaaao",
        ".onaaaaaaaaaaaao",
        "ownaaaaaaaaaaaao",
        ".owaabbbbbbbbaao",
        "..ooaaccccccaao.",
        "...oaao...oaao..",
        "...oaao...oaao..",
        "...oooo...oooo..",
        "................",
    ]), _shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....oosoosoo...",
        "...ooaaaaaaaaoo.",
        "..oeaaaaaaaaaaao",
        ".onaaaaaaaaaaaao",
        "ownaaaaaaaaaaaao",
        ".owaabbbbbbbbaao",
        "..ooaaccccccaao.",
        "..oaao.....oaao.",
        "..oaao.....oaao.",
        "..oooo.....oooo.",
        "................",
    ])),
    "rato": (_shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "...oo...........",
        "..oaao..........",
        ".oeaaaoooooo....",
        "onaaaaaaaaaaoo..",
        ".oaaaaaaaaaaaao.",
        "..ocaaaaaaaaaott",
        "...oao...oaoo..t",
        "...oo....oo...t.",
        "................",
    ]), _shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "...oo...........",
        "..oaao..........",
        ".oeaaaoooooo....",
        "onaaaaaaaaaaoo..",
        ".oaaaaaaaaaaaao.",
        "..ocaaaaaaaaaott",
        "..oao.....oao.t.",
        "..oo......oo...t",
        "................",
    ])),
    "toupeira": (_shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....oooooooo...",
        "...ooaaaaaaaaoo.",
        "..oeaacaaaaaaaao",
        ".onaaaaaaaaaaaao",
        "onnaaaaaaaaaaaao",
        ".oaabbbbbbbbbaao",
        "..owwo.....owwo.",
        "..oww.......oww.",
        "..ooo.......ooo.",
        "................",
    ]), _shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....oooooooo...",
        "...ooaaaaaaaaoo.",
        "..oeaacaaaaaaaao",
        ".onaaaaaaaaaaaao",
        "onnaaaaaaaaaaaao",
        ".oaabbbbbbbbbaao",
        ".owwo.......owwo",
        ".oww.........oww",
        ".ooo.........ooo",
        "................",
    ])),
    "corvo": (_shape([
        "................",
        "................",
        "................",
        "................",
        "....ooo.........",
        "...oaaao........",
        ".wwoaeaao.......",
        "...oaaaaaoo.....",
        "....oaaaaaaoo...",
        "....oaaaaaaaaoo.",
        ".....oaabbbaaao.",
        "......oabbbbaao.",
        ".......oaaaaoaao",
        "........ow.w..oo",
        "........w..w....",
        "................",
    ]), _shape([
        "................",
        "................",
        "...........ooo..",
        "..........oaao..",
        "....ooo..oaao...",
        "...oaaao.oaao...",
        ".wwoaeaaoaao....",
        "...oaaaaaaoo....",
        "....oaaaaaaoo...",
        "....oaaaaaaaaoo.",
        ".....oaabbbaaao.",
        "......oabbbbaao.",
        ".......oaaaaoaao",
        "........ow.w..oo",
        ".......w....w...",
        "................",
    ])),
    "morcego": (_shape([
        "................",
        "................",
        "................",
        "................",
        "..o.........o...",
        ".oao.......oao..",
        "oaaao.o.o.oaaao.",
        "oaaaaoaoaoaaaaao",
        "oaaaaoeaeoaaaaao",
        ".oaaaaaaaaaaaao.",
        "..oaa.oaao.aao..",
        "...o..owwo..o...",
        "........o.......",
        "................",
        "................",
        "................",
    ]), _shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "......o.o.......",
        "....ooaoaoo.....",
        "..ooaoeaeoaoo...",
        ".oaaaaaaaaaaao..",
        "oaaaaaoaaoaaaaao",
        "oaao..owwo..oaao",
        ".oo.....o....oo.",
        "................",
        "................",
        "................",
    ])),
    "lagarto": (_shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "..oo............",
        ".oeaooooooo.....",
        "onaaaaaaaaaooo..",
        ".ocaaaaaaaaaaaoo",
        "..oao..oao...ooa",
        "..oo...oo.......",
        "................",
    ]), _shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "..oo............",
        ".oeaooooooo.....",
        "onaaaaaaaaaooo..",
        ".ocaaaaaaaaaaaoo",
        ".oao....oao..oa.",
        ".oo.....oo......",
        "................",
    ])),
    "aranha": (_shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".o..o......o..o.",
        "..o..o....o..o..",
        "...o.oaaaao.o...",
        "o...oaaccaao...o",
        ".ooooaacaaaoooo.",
        "....oaeaeaao....",
        "..ooo.owwo.ooo..",
        ".o...o....o...o.",
        "o...o......o...o",
        "................",
    ]), _shape([
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "..o..o....o..o..",
        ".o..o......o..o.",
        "o..o.oaaaao.o..o",
        "....oaaccaao....",
        "oooooaacaaaooooo",
        "....oaeaeaao....",
        ".ooo..owwo..ooo.",
        "o...o......o...o",
        "...o........o...",
        "................",
    ])),
    "espirito": (_shape([
        "................",
        "................",
        "......oooo......",
        ".....oaaaao.....",
        "....oaaaaaao....",
        "...oaaccaaaao...",
        "...oaeaaeaaao...",
        "...oaaaaaaaao...",
        "..oaaaaoaaaaao..",
        "..oaaaaaaaaaao..",
        ".oaaaaaaaaaaaao.",
        ".oaaaaaaaaaaaao.",
        ".oaabaaabaaabao.",
        "..oo.oao.oao.oo.",
        "......o...o.....",
        "................",
    ]), _shape([
        "................",
        "................",
        "......oooo......",
        ".....oaaaao.....",
        "....oaaaaaao....",
        "...oaaccaaaao...",
        "...oaeaaeaaao...",
        "...oaaaaaaaao...",
        "..oaaaaoaaaaao..",
        "..oaaaaaaaaaao..",
        ".oaaaaaaaaaaaao.",
        ".oaaaaaaaaaaaao.",
        ".obaaabaaabaaao.",
        ".oo.oao.oao.oo..",
        ".....o...o......",
        "................",
    ])),
    "golem": (_shape([
        "................",
        "................",
        ".....oooooo.....",
        "....oaaaaaao....",
        "....oaeaaeao....",
        "....oaaaaaao....",
        "..ooobbbbbbooo..",
        ".oaaaaaaaaaaaao.",
        "oaaaocaaaacoaaao",
        "oaao.oaaaao.oaao",
        "oaao.oacaao.oaao",
        "obbo.oaaaao.obbo",
        ".oo..oaooao..oo.",
        ".....oao.oao....",
        "....oaao.oaao...",
        "....ooo...ooo...",
    ]), _shape([
        "................",
        "................",
        ".....oooooo.....",
        "....oaaaaaao....",
        "....oaeaaeao....",
        "....oaaaaaao....",
        "..ooobbbbbbooo..",
        ".oaaaaaaaaaaaao.",
        "oaaaocaaaacoaaao",
        "oaao.oaaaao.oaao",
        "oaao.oacaao.oaao",
        "obbo.oaaaao.obbo",
        ".oo..oaooao..oo.",
        "....oao...oao...",
        "...oaao...oaao..",
        "...ooo.....ooo..",
    ])),
}

# Criatura -> (molde, cores {letra: hex}, escala). Kobolds e humanoides usam os moldes do
# herói e do Pip, com roupa, pele e cabelo próprios.
MONSTER_LOOKS: Dict[str, Tuple[str, Dict[str, str], float]] = {
    "corvo_ladrao": ("corvo", {"a": "#2b2b38", "b": "#1b1b24", "c": "#4a4a66", "e": "#ffd84a", "w": "#d9a92e"}, 0.9),
    "javali_jovem": ("javali", {"a": "#8a5a3a", "b": "#5a3a22", "c": "#b08060", "e": "#1d1d1d", "n": "#d9a0a0",
                                "w": "#f2e6c8", "s": "#5a3a22"}, 0.9),
    "rato_gigante": ("rato", {"a": "#7a6a5a", "b": "#4a3e33", "c": "#a89a8a", "e": "#ff4a4a", "n": "#d99a9a",
                              "t": "#d99a9a"}, 0.85),
    "lagarto_ribeirao": ("lagarto", {"a": "#4f8f4a", "b": "#2f5f2a", "c": "#9fcf6a", "e": "#ffd84a",
                                     "n": "#2f5f2a"}, 1.0),
    "lobo_faminto": ("lobo", {"a": "#7a6a5a", "b": "#4a3e33", "c": "#a89a8a", "e": "#ffcf4a", "n": "#1d1d1d",
                              "w": "#f2f2f2"}, 0.95),
    "lobo_cinzento": ("lobo", {"a": "#8a8a8a", "b": "#5a5a5a", "c": "#c8c8c8", "e": "#ffcf4a", "n": "#1d1d1d",
                               "w": "#f2f2f2"}, 1.0),
    "aranha_da_mata": ("aranha", {"a": "#3a3a2a", "b": "#22221a", "c": "#7a8a3a", "e": "#ff3a3a",
                                  "w": "#d9d2c0"}, 1.0),
    "javali_espinhento": ("javali", {"a": "#5a4a3a", "b": "#3a2a1e", "c": "#7a6a5a", "e": "#ff6a3a",
                                     "n": "#a07070", "w": "#f2e6c8", "s": "#e0d8c0"}, 1.1),
    "espirito_sussurrante": ("espirito", {"a": "#8fd8c8", "b": "#5fa898", "c": "#d8fff4", "e": "#1d4a44"}, 1.0),
    "lobo_gelido": ("lobo", {"a": "#cfe8ff", "b": "#8fb8d8", "c": "#ffffff", "e": "#2fa0ff", "n": "#2a3a4a",
                             "w": "#ffffff"}, 1.05),
    "morcego_caverna": ("morcego", {"a": "#4a3a4a", "b": "#2e222e", "c": "#6a5a6a", "e": "#ff5a5a",
                                    "w": "#f2f2f2"}, 0.8),
    "varek_domador": ("humano", {"cloth": "#5a4a2a", "hair": "#3a2a22", "shape": "curto", "skin": "media"}, 1.1),
    "presa_de_gelo": ("lobo", {"a": "#f2f8ff", "b": "#a8c8e8", "c": "#ffffff", "e": "#2f80ff", "n": "#2a3a4a",
                               "w": "#ffffff"}, 1.6),
    "kobold_escavador": ("kobold", {"cloth": "#6b5a3a", "skin": "#c9a05a"}, 0.85),
    "kobold_vela": ("kobold", {"cloth": "#8a3a2a", "skin": "#c9a05a", "candle": "sim"}, 0.85),
    "kobold_geomante": ("kobold", {"cloth": "#3a5a8a", "skin": "#9a8a5a"}, 0.9),
    "toupeira_ferro": ("toupeira", {"a": "#5a5a66", "b": "#3a3a44", "c": "#9a9aaa", "e": "#ffcf4a",
                                    "n": "#d99a9a", "w": "#e0e0e0"}, 1.0),
    "capataz_gorran": ("humano", {"cloth": "#5a3a22", "hair": "#2b2421", "shape": "careca", "skin": "ogro"}, 1.5),
    "sentinela_ruinas": ("golem", {"a": "#9a9488", "b": "#6a665c", "c": "#c8c2b0", "e": "#6fe0f0"}, 1.15),
    "acolito_lua": ("humano", {"cloth": "#3a2a5a", "hair": "#2a2040", "shape": "longo", "skin": "clara"}, 1.0),
    "guarda_capa_negra": ("humano", {"cloth": "#26262e", "hair": "#1d1d1d", "shape": "curto", "skin": "media"}, 1.05),
    "eco_veltharas": ("espirito", {"a": "#b08fe0", "b": "#7a5fa8", "c": "#efe4ff", "e": "#3a1a5a"}, 1.05),
    "cao_sombrio": ("lobo", {"a": "#3a2a4a", "b": "#22182e", "c": "#5a4a6a", "e": "#d84aff", "n": "#100c14",
                             "w": "#e8d8ff"}, 1.05),
    "morwen": ("humano", {"cloth": "#4a1a6a", "hair": "#d8d8f0", "shape": "longo", "skin": "clara"}, 1.3),
    "batedor_corvo": ("humano", {"cloth": "#2a2a2a", "hair": "#4a3a2a", "shape": "curto", "skin": "clara"}, 1.0),
    "arqueiro_corvo": ("humano", {"cloth": "#3a4a2a", "hair": "#2b2421", "shape": "longo", "skin": "media"}, 1.0),
    "brutamontes_corvo": ("humano", {"cloth": "#4a3a2a", "hair": "#1d1d1d", "shape": "careca", "skin": "escura"},
                          1.25),
    "ulric": ("humano", {"cloth": "#1d1d26", "hair": "#1d1d1d", "shape": "moicano", "skin": "clara"}, 1.35),
    "vigia_atormentado": ("golem", {"a": "#6a6478", "b": "#46405a", "c": "#9a94b0", "e": "#d84aff"}, 2.0),
}
GHOSTLY_MONSTERS = ["espirito_sussurrante", "eco_veltharas"]


def monster_frame(template_id: str, step: int) -> Canvas:
    """Um quadro 16x16 da criatura, olhando para a esquerda."""
    shape, colors, _scale = MONSTER_LOOKS[template_id]
    frame = Canvas(TILE, TILE)
    if shape == "humano":
        skin = {"ogro": ("#8a9a6a", "#6a7a4a")}.get(colors["skin"]) or SKIN_TONES[colors["skin"]]
        cloth = hex_color(colors["cloth"])
        palette = {"o": OUTLINE, "s": hex_color(skin[0]), "S": hex_color(skin[1]), "e": OUTLINE,
                   "b": hex_color("#3a2e22"), "p": shade(cloth, 0.6), "c": cloth, "C": shade(cloth, 0.72)}
        frame.stamp(body_frame("left", step), palette)
        hair = hex_color(colors["hair"])
        frame.stamp(HAIR[colors["shape"]]["left"], {"h": hair, "H": shade(hair, 0.75)}, 0, HAIR_OFFSET)
        return frame
    if shape == "kobold":
        rows = list(KOBOLD["left"])
        if step:
            rows[12:15] = [".....oy..yo.....", ".....oy..yo.....", "....oo....oo...."]
        palette = {"o": OUTLINE, "y": hex_color(colors["skin"]), "e": hex_color("#ff7a2a"),
                   "r": shade(hex_color(colors["skin"]), 0.7), "c": hex_color(colors["cloth"])}
        frame.stamp(rows, palette)
        if colors.get("candle"):
            frame.stamp(CANDLE, {"F": hex_color("#ffd36b"), "f": hex_color("#ff9a3a"), "w": hex_color("#f2e6c8")},
                        2, -1)
        return frame
    palette = {"o": OUTLINE}
    palette.update({letter: hex_color(code) for letter, code in colors.items()})
    frame.stamp(MONSTER_SHAPES[shape][step], palette)
    return frame


def monster_sheet() -> Tuple[Canvas, Dict[str, int]]:
    """Folha das criaturas: uma linha por modelo, 2 colunas (parado e passo)."""
    ids = list(MONSTER_LOOKS)
    sheet = Canvas(TILE * 2, TILE * len(ids))
    rows = {}
    for row, template_id in enumerate(ids):
        rows[template_id] = row
        for step in (0, 1):
            sheet.paste(monster_frame(template_id, step), step * TILE, row * TILE)
    return sheet, rows


ICON_ROWS = {
    "new": [
        "................",
        "......oooo......",
        ".....oyyyyo.....",
        "....oyyooyyo....",
        "....oooo.oyo....",
        "........oyyo....",
        ".......oyyo.....",
        "......oyyo......",
        "......oyyo......",
        "......oooo......",
        "......oyyo......",
        "......oyyo......",
        "......oooo......",
        "................",
        "................",
        "................",
    ],
    "known": [
        "................",
        ".......oo.......",
        "......oyyo......",
        "......oyyo......",
        "..ooooyyyyoooo..",
        "..oyyyyyyyyyyo..",
        "...oyyyyyyyyo...",
        "....oyyyyyyo....",
        "....oyyyyyyo....",
        "...oyyyooyyyo...",
        "...oyyo..oyyo...",
        "...ooo....ooo...",
        "................",
        "................",
        "................",
        "................",
    ],
    "passage": [
        "................",
        "......oooo......",
        ".....occcco.....",
        "....occcccco....",
        "....occaacco....",
        "....ocaaaaco....",
        "....ocaaaaco....",
        "....ocaaaaco....",
        "....ocaaaaco....",
        "....oooooooo....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "talk": [
        "................",
        ".......oo.......",
        "......oyyo......",
        "......oyyo......",
        "......oyyo......",
        "......oyyo......",
        "......oyyo......",
        ".......oo.......",
        "................",
        ".......oo.......",
        "......oyyo......",
        ".......oo.......",
        "................",
        "................",
        "................",
        "................",
    ],
}


def icon_sheet() -> Tuple[Canvas, Dict[str, int]]:
    sheet = Canvas(TILE * len(ICON_ROWS), TILE)
    columns = {}
    palettes = {
        "new": {"o": OUTLINE, "y": hex_color("#f2f2f2")},
        "known": {"o": OUTLINE, "y": hex_color("#f2c84a")},
        "passage": {"o": OUTLINE, "c": hex_color("#8fc3ea"), "a": hex_color("#1d3557")},
        "talk": {"o": OUTLINE, "y": hex_color("#ffd84a")},
    }
    for column, (name, rows) in enumerate(ICON_ROWS.items()):
        sheet.stamp(rows, palettes[name], column * TILE, 0)
        columns[name] = column
    return sheet, columns


# --------------------------------------------------------------------------- saída

def main(preview: Optional[Path] = None) -> None:
    tiles, tile_atlas = make_tiles()
    hero, hero_info = hero_layers()
    npcs, npc_rows = npc_sheet()
    icons, icon_columns = icon_sheet()
    monsters, monster_rows = monster_sheet()
    tiles.save(ART_DIR / "tiles.png")
    hero.save(ART_DIR / "hero.png")
    npcs.save(ART_DIR / "npcs.png")
    icons.save(ART_DIR / "icons.png")
    monsters.save(ART_DIR / "monsters.png")
    info = {
        "tile_size": TILE,
        "tiles": tile_atlas,                     # terreno -> [linha, número de variações]
        "hero": hero_info,
        "npcs": {"rows": npc_rows, "columns": hero_info["columns"],
                 "scale": {"vigia": 2.5, "tome": 0.9, "pip": 0.85},
                 "ghosts": ["kael"]},
        "icons": icon_columns,
        "monsters": {"rows": monster_rows, "frames": 2,
                     "scale": {template_id: look[2] for template_id, look in MONSTER_LOOKS.items() if look[2] != 1.0},
                     "ghosts": GHOSTLY_MONSTERS},
        "hair_colors": {"negro": "#2b2421", "castanho": "#6b4226", "ruivo": "#b5482c", "loiro": "#e3c565",
                        "grisalho": "#a8a8a8", "branco": "#eeeeee", "azul_noite": "#2e3f7a"},
        "armor_colors": {"carmesim": "#a32d2d", "azul_real": "#2f4fa3", "verde_floresta": "#2f7a3a",
                         "negro_onix": "#2b2b33", "branco_marfim": "#e8e2d0", "dourado_solar": "#d9a92e",
                         "roxo_imperial": "#6b2f8f"},
    }
    (DATA_DIR / "art.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if preview:
        for name, canvas in (("tiles", tiles), ("hero", hero), ("npcs", npcs), ("icons", icons),
                             ("monsters", monsters)):
            canvas.scaled(4).save(preview / f"preview_{name}.png")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    print(f"Arte gerada em {ART_DIR.relative_to(ROOT)}")
