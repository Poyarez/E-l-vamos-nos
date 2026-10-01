"""Camada de terminal: cores ANSI, símbolos, molduras, barras, menus e leitura de entrada.

Todo texto do jogo passa por aqui. O resto do código não precisa saber se o terminal
aceita cores, Unicode ou o efeito de máquina de escrever: basta usar ``style``, ``sym``,
``box``, ``choose`` etc. Sem cores (ou com a saída redirecionada), tudo continua legível.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
from typing import Callable, Iterable, List, Optional, Sequence

from .utils import normalize

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_TOKEN_RE = re.compile(r"(\x1b\[[0-9;]*m)")
RESET = "\x1b[0m"

_CODES = {
    "bold": "1", "dim": "2", "italic": "3", "underline": "4",
    "black": "30", "red": "31", "green": "32", "yellow": "33",
    "blue": "34", "magenta": "35", "cyan": "36", "white": "37",
    "gray": "90", "bright_red": "91", "bright_green": "92", "bright_yellow": "93",
    "bright_blue": "94", "bright_magenta": "95", "bright_cyan": "96", "bright_white": "97",
}

# Cada símbolo tem uma versão Unicode e uma alternativa ASCII de MESMA largura.
_SYMBOLS = {
    "h2": ("═", "="), "v2": ("║", "|"), "tl2": ("╔", "+"), "tr2": ("╗", "+"),
    "bl2": ("╚", "+"), "br2": ("╝", "+"),
    "h": ("─", "-"), "v": ("│", "|"), "tl": ("┌", "+"), "tr": ("┐", "+"),
    "bl": ("└", "+"), "br": ("┘", "+"),
    "full": ("█", "#"), "empty": ("░", "."),
    "bullet": ("•", "*"), "diamond": ("◆", "*"), "star": ("✦", "*"), "star_off": ("✧", "-"), "arrow": ("»", ">"),
    "sun": ("☼", "*"), "moon": ("☾", "("), "dot": ("·", "."), "heart": ("♥", "+"),
    "up": ("▲", "^"), "check": ("✔", "v"), "cross": ("✖", "x"), "ellipsis": ("…", "."),
}


class Display:
    """O que o terminal suporta, combinado com as preferências do jogador."""

    def __init__(self) -> None:
        self.ansi = False           # o terminal entende sequências ANSI
        self.stdin_tty = False      # a entrada vem do teclado (e não de um pipe)
        self.interactive = False    # entrada e saída são um terminal de verdade
        self.unicode_ok = True      # a codificação da saída aceita Unicode
        self.color = False
        self.unicode = True
        self.typewriter = False
        self.clear_screen = False
        self.typewriter_delay = 0.008


display = Display()


class InputClosed(Exception):
    """A entrada padrão acabou (EOF): o jogo deve encerrar com elegância."""


#: Função usada para ler a entrada. Os testes podem substituí-la.
input_func: Callable[[str], str] = input


# --------------------------------------------------------------------------- setup

def init_terminal() -> None:
    """Detecta as capacidades do terminal. Chamada uma vez, na inicialização."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(errors="replace")
            except (ValueError, OSError):
                pass
    stdout_tty = _isatty(sys.stdout)
    display.stdin_tty = _isatty(sys.stdin)
    display.interactive = stdout_tty and display.stdin_tty
    display.ansi = stdout_tty and _enable_windows_ansi()
    display.unicode_ok = _can_encode("╔═█░◆☼☾»✦·…")


def configure(color: bool = True, unicode: bool = True, typewriter: bool = True,
              clear_screen: bool = True) -> None:
    """Aplica as preferências do jogador respeitando o que o terminal suporta."""
    display.color = color and display.ansi and "NO_COLOR" not in os.environ
    display.unicode = unicode and display.unicode_ok
    display.typewriter = typewriter and display.interactive
    display.clear_screen = clear_screen and display.ansi


def _isatty(stream: object) -> bool:
    try:
        return bool(stream.isatty())  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        return False


def _can_encode(sample: str) -> bool:
    encoding = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        sample.encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def _enable_windows_ansi() -> bool:
    """No Windows, liga o processamento de sequências ANSI no console."""
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:  # noqa: BLE001 - qualquer falha significa "sem ANSI"
        return False


# --------------------------------------------------------------------------- estilo

def style(text: str, *names: str) -> str:
    """Aplica estilos ANSI ("green", "bold", "bright_cyan"...). Aceita "green bold".

    Estilos aninhados são preservados: o estilo externo é reaplicado após cada reset interno.
    """
    if not display.color or not text:
        return text
    codes = [_CODES[part] for name in names if name for part in name.split()]
    if not codes:
        return text
    seq = "\x1b[" + ";".join(codes) + "m"
    return seq + text.replace(RESET, RESET + seq) + RESET


def sym(name: str) -> str:
    """Símbolo Unicode ou sua alternativa ASCII, conforme o terminal."""
    unicode_char, ascii_char = _SYMBOLS[name]
    return unicode_char if display.unicode else ascii_char


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def visible_len(text: str) -> int:
    return len(strip_ansi(text))


def pad(text: str, width: int, align: str = "left") -> str:
    """Completa com espaços até ``width`` colunas visíveis."""
    gap = width - visible_len(text)
    if gap <= 0:
        return text
    if align == "right":
        return " " * gap + text
    if align == "center":
        left = gap // 2
        return " " * left + text + " " * (gap - left)
    return text + " " * gap


def truncate(text: str, width: int) -> str:
    """Corta o texto em ``width`` colunas visíveis, sem quebrar códigos ANSI."""
    if visible_len(text) <= width:
        return text
    if width <= 0:
        return ""
    keep = width - 1
    out: List[str] = []
    count = 0
    for token in _TOKEN_RE.split(text):
        if ANSI_RE.fullmatch(token):
            out.append(token)
            continue
        take = token[: max(0, keep - count)]
        out.append(take)
        count += len(take)
        if count >= keep:
            break
    result = "".join(out) + sym("ellipsis")
    return result + RESET if "\x1b[" in result else result


def _active_after(fragment: str, active: str) -> str:
    """Quais códigos ANSI continuam abertos depois de ``fragment``."""
    for code in ANSI_RE.findall(fragment):
        active = "" if code == RESET else active + code
    return active


def wrap(text: str, width: int, indent: str = "") -> List[str]:
    """Quebra o texto em linhas de até ``width`` colunas visíveis (``\\n`` separa parágrafos).

    Um estilo aberto no fim de uma linha é fechado e reaberto na seguinte, para que a
    cor não "vaze" para colunas vizinhas quando o texto é posto lado a lado com o mapa.
    """
    width = max(10, width)
    lines: List[str] = []
    active = ""
    for paragraph in text.split("\n"):
        line = indent + active
        line_len = len(indent)
        has_words = False
        for word in paragraph.split(" "):
            if not word:
                continue
            word_len = visible_len(word)
            if has_words and line_len + 1 + word_len > width:
                lines.append(line + (RESET if active else ""))
                line = indent + active
                line_len = len(indent)
                has_words = False
            if has_words:
                line += " "
                line_len += 1
            line += word
            line_len += word_len
            has_words = True
            active = _active_after(word, active)
        lines.append(line + (RESET if active else ""))
    return lines


# --------------------------------------------------------------------------- layout

def labeled(label: str, value: str, label_width: int, width: int, indent: str = "  ") -> List[str]:
    """Rótulo alinhado + valor quebrado em linhas que respeitam o alinhamento do rótulo."""
    rows = wrap(value, width - len(indent) - label_width)
    first = indent + pad(label, label_width) + rows[0]
    return [first] + [indent + " " * label_width + row for row in rows[1:]]



def term_width() -> int:
    """Largura útil do terminal (limitada para manter a leitura confortável)."""
    columns = shutil.get_terminal_size((100, 30)).columns
    return max(60, min(columns, 120))


def content_width() -> int:
    """Largura para parágrafos de texto corrido."""
    return min(term_width(), 100) - 4


def box(lines: Sequence[str], width: int, title: str = "", double: bool = False,
        color: str = "gray") -> List[str]:
    """Moldura com título opcional. ``width`` é a largura total, incluindo as bordas."""
    width = max(width, 10)
    inner = width - 4
    kind = "2" if double else ""
    h, v = sym("h" + kind), sym("v" + kind)
    if title:
        label = " " + truncate(title, width - 6) + " "
        top = (style(sym("tl" + kind) + h, color) + label
               + style(h * max(0, width - 3 - visible_len(label)) + sym("tr" + kind), color))
    else:
        top = style(sym("tl" + kind) + h * (width - 2) + sym("tr" + kind), color)
    edge = style(v, color)
    rows = [top]
    rows.extend(edge + " " + pad(truncate(line, inner), inner) + " " + edge for line in lines)
    rows.append(style(sym("bl" + kind) + h * (width - 2) + sym("br" + kind), color))
    return rows


def side_by_side(left: Sequence[str], right: Sequence[str], left_width: int, gap: int = 2) -> List[str]:
    """Junta duas colunas de linhas (respeitando a largura visível da esquerda)."""
    rows = []
    for index in range(max(len(left), len(right))):
        left_part = left[index] if index < len(left) else ""
        right_part = right[index] if index < len(right) else ""
        rows.append((pad(left_part, left_width) + " " * gap + right_part).rstrip())
    return rows


def bar(current: float, maximum: float, width: int, color: str, empty_color: str = "gray") -> str:
    """Barra de progresso: ``█████░░░░░``."""
    ratio = 0.0 if maximum <= 0 else max(0.0, min(1.0, current / maximum))
    filled = int(round(ratio * width))
    if current > 0 and filled == 0:
        filled = 1
    if 0 < maximum and current < maximum and filled == width:
        filled = width - 1
    return style(sym("full") * filled, color) + style(sym("empty") * (width - filled), empty_color)


def rule(width: Optional[int] = None, color: str = "gray") -> str:
    return style(sym("h") * (width or content_width()), color)


# --------------------------------------------------------------------------- saída

def echo(text: str = "") -> None:
    print(text)


def echo_lines(rows: Iterable[str]) -> None:
    for row in rows:
        print(row)


def paragraph(text: str, indent: str = "  ", width: Optional[int] = None) -> None:
    echo_lines(wrap(text, width or content_width(), indent))


def clear() -> None:
    """Limpa a tela (ou apenas pula uma linha, se o terminal não permitir)."""
    if display.clear_screen:
        sys.stdout.write("\x1b[2J\x1b[H")
        sys.stdout.flush()
    else:
        print()


def narrate(text: str, indent: str = "  ", width: Optional[int] = None) -> None:
    """Escreve um texto narrativo, letra a letra se o efeito estiver ligado.

    Ctrl+C durante a animação apenas a pula, mostrando o restante de uma vez.
    """
    rows = wrap(text, width or content_width(), indent)
    if not display.typewriter:
        echo_lines(rows)
        return
    delay = display.typewriter_delay
    for row_index, row in enumerate(rows):
        tokens = _TOKEN_RE.split(row)
        for token_index, token in enumerate(tokens):
            if ANSI_RE.fullmatch(token):
                sys.stdout.write(token)
                continue
            for char_index, char in enumerate(token):
                try:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    if not char.isspace():
                        time.sleep(delay)
                except KeyboardInterrupt:
                    sys.stdout.write(token[char_index + 1:] + "".join(tokens[token_index + 1:]) + "\n")
                    sys.stdout.write("".join(rest + "\n" for rest in rows[row_index + 1:]))
                    sys.stdout.flush()
                    return
        sys.stdout.write("\n")
    sys.stdout.flush()


# --------------------------------------------------------------------------- entrada

def ask(prompt: str = "") -> str:
    """Lê uma linha. Levanta ``InputClosed`` quando a entrada acaba (EOF)."""
    try:
        answer = input_func(prompt)
    except EOFError:
        print()
        raise InputClosed() from None
    if not display.stdin_tty:
        print(answer)   # ecoa comandos vindos de pipe: a saída fica legível
    return answer.strip()


def pause(message: str = "Pressione Enter para continuar...") -> None:
    ask(style("  " + message + " ", "gray"))


def confirm(question: str, default: Optional[bool] = None) -> bool:
    """Pergunta de sim/não. Enter vazio usa ``default`` (se houver)."""
    hint = {True: "[S/n]", False: "[s/N]", None: "[s/n]"}[default]
    while True:
        answer = normalize(ask(f"  {question} {style(hint, 'gray')} "))
        if not answer and default is not None:
            return default
        if answer in ("s", "sim", "y", "yes"):
            return True
        if answer in ("n", "nao", "no"):
            return False
        echo(style("  Responda com 's' (sim) ou 'n' (não).", "gray"))


def choose(options: Sequence[str], prompt: str = "Escolha", cancel: Optional[str] = None,
           details: Optional[Sequence[str]] = None) -> Optional[int]:
    """Lista opções numeradas e devolve o índice escolhido.

    Aceita o número ou o começo do nome da opção. Com ``cancel``, a opção ``[0]``
    devolve ``None``.
    """
    for number, option in enumerate(options, 1):
        echo(f"  {style(f'[{number}]', 'bright_yellow')} {option}")
        if details and details[number - 1]:
            echo_lines(wrap(style(details[number - 1], "gray"), content_width(), "      "))
    if cancel:
        echo(f"  {style('[0]', 'gray')} {cancel}")
    keys = [normalize(strip_ansi(option)) for option in options]
    while True:
        answer = ask(f"  {style(prompt, 'bold')} {sym('arrow')} ")
        key = normalize(answer)
        if cancel and key in ("0", "voltar", "cancelar"):
            return None
        if key.isdigit():
            number = int(key)
            if 1 <= number <= len(options):
                return number - 1
        elif key:
            matches = [index for index, name in enumerate(keys) if name.startswith(key)]
            if len(matches) == 1:
                return matches[0]
        echo(style("  Opção inválida. Digite o número de uma das opções.", "gray"))
