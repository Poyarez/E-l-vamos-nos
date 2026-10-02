class_name UiTheme
extends RefCounted
## O visual da interface: painéis escuros com borda lilás (o violeta das ruínas), botões
## que acendem no foco e itálico para a narração. tools/build_project.gd salva este tema em
## res://ui/theme.tres, que o projeto usa por padrão; depois disso dá para ajustar as cores
## direto no editor de temas do Godot.

const THEME_PATH := "res://ui/theme.tres"

const BACKGROUND := Color(0.07, 0.06, 0.11, 0.9)
const BORDER := Color(0.55, 0.46, 0.76)
const TEXT := Color(0.93, 0.91, 0.86)
const MUTED := Color(0.66, 0.63, 0.72)
const HIGHLIGHT := Color(0.32, 0.25, 0.5, 0.95)
const GOLD := Color(1.0, 0.86, 0.45)


static func make() -> Theme:
	var theme := Theme.new()
	theme.default_font_size = 10
	theme.set_stylebox("panel", "PanelContainer", _box(BACKGROUND, BORDER, 6, 4))
	theme.set_stylebox("panel", "Panel", _box(BACKGROUND, BORDER, 6, 4))
	theme.set_color("font_color", "Label", TEXT)
	theme.set_color("default_color", "RichTextLabel", TEXT)
	var italic := FontVariation.new()   # sem fonte base: usa a fonte padrão do tema
	italic.variation_transform = Transform2D(Vector2(1, 0), Vector2(0.22, 1), Vector2.ZERO)
	theme.set_font("italics_font", "RichTextLabel", italic)
	theme.set_stylebox("focus", "RichTextLabel", StyleBoxEmpty.new())
	theme.set_stylebox("normal", "RichTextLabel", StyleBoxEmpty.new())
	theme.set_stylebox("normal", "Button", _box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 6, 2))
	theme.set_stylebox("hover", "Button", _box(HIGHLIGHT, Color(0, 0, 0, 0), 6, 2))
	theme.set_stylebox("pressed", "Button", _box(HIGHLIGHT, BORDER, 6, 2))
	theme.set_stylebox("focus", "Button", _box(HIGHLIGHT, BORDER, 6, 2))
	theme.set_stylebox("disabled", "Button", _box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 6, 2))
	theme.set_color("font_color", "Button", TEXT)
	theme.set_color("font_hover_color", "Button", GOLD)
	theme.set_color("font_focus_color", "Button", GOLD)
	theme.set_color("font_pressed_color", "Button", GOLD)
	theme.set_color("font_hover_pressed_color", "Button", GOLD)
	theme.set_color("font_disabled_color", "Button", MUTED.darkened(0.3))
	for type_name in ["LineEdit", "OptionButton"]:
		theme.set_stylebox("normal", type_name, _box(Color(0.12, 0.1, 0.18, 0.95), BORDER.darkened(0.3), 6, 2))
		theme.set_stylebox("focus", type_name, _box(Color(0.12, 0.1, 0.18, 0.95), GOLD, 6, 2))
		theme.set_color("font_color", type_name, TEXT)
	theme.set_stylebox("hover", "OptionButton", _box(HIGHLIGHT, BORDER, 6, 2))
	theme.set_stylebox("pressed", "OptionButton", _box(HIGHLIGHT, BORDER, 6, 2))
	theme.set_color("font_hover_color", "OptionButton", GOLD)
	theme.set_color("font_focus_color", "OptionButton", GOLD)
	theme.set_stylebox("panel", "PopupMenu", _box(BACKGROUND.lightened(0.05), BORDER, 4, 4))
	theme.set_stylebox("hover", "PopupMenu", _box(HIGHLIGHT, Color(0, 0, 0, 0), 4, 1))
	theme.set_color("font_color", "PopupMenu", TEXT)
	theme.set_color("font_hover_color", "PopupMenu", GOLD)
	return theme


static func _box(fill: Color, border: Color, margin_x: int, margin_y: int) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = fill
	box.border_color = border
	box.set_border_width_all(1 if border.a > 0 else 0)
	box.set_corner_radius_all(3)
	box.content_margin_left = margin_x
	box.content_margin_right = margin_x
	box.content_margin_top = margin_y
	box.content_margin_bottom = margin_y
	return box
