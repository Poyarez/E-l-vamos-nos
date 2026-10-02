class_name GameText
extends RefCounted
## Texto dos dados -> texto na tela: marcadores ({nome}, {tratamento}...), narração entre
## *asteriscos* (em itálico cinza, como no terminal) e as cores ANSI dos dados viram Color.

const NARRATION_COLOR := "#a7a1b8"

## Cores ANSI usadas nos dados (NPCs, terrenos) traduzidas para a paleta da versão Godot.
const COLORS := {
	"black": "#3a3a46", "red": "#c94f4f", "green": "#5fae58", "yellow": "#d8b04a",
	"blue": "#5a7fd6", "magenta": "#b05fc8", "cyan": "#4fb3bf", "white": "#d9d4c7", "gray": "#8f8a99",
	"bright_black": "#6b6878", "bright_red": "#ff7a6b", "bright_green": "#8fe07f", "bright_yellow": "#ffe27a",
	"bright_blue": "#8fb0ff", "bright_magenta": "#e08fff", "bright_cyan": "#8ff0f0", "bright_white": "#ffffff",
}

static var _narration: RegEx


## Troca {nome}, {tratamento}, {Bem_vindo}, {classe}... pelas palavras do herói.
## Marcadores desconhecidos ficam como estão (igual ao Python).
static func format(text: String) -> String:
	return text.format(Game.forms())


## Escapa colchetes para o BBCode do RichTextLabel não confundir texto com tags.
static func escape(text: String) -> String:
	return text.replace("[", "[lb]")


## Uma fala dos dados -> BBCode: *narração* em itálico cinza, o resto como fala.
static func to_bbcode(text: String) -> String:
	if _narration == null:
		_narration = RegEx.create_from_string("\\*(.+?)\\*")
	var escaped := escape(format(text).strip_edges())
	return _narration.sub(escaped, "[i][color=%s]$1[/color][/i]" % NARRATION_COLOR, true)


## Texto puro (sem asteriscos), para avisos curtos.
static func plain(text: String) -> String:
	return format(text).replace("*", "").strip_edges()


## "bright_magenta bold" -> Color
static func color(name: String, fallback: Color = Color.WHITE) -> Color:
	for word in name.split(" ", false):
		if COLORS.has(word):
			return Color(COLORS[word])
	return fallback
