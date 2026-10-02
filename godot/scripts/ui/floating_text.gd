extends CanvasLayer
## Os números que sobem da cabeça de quem leva dano ou cura, como no WoW: brancos para os
## golpes do herói, dourados e maiores nos críticos, vermelhos no herói, verdes nas curas.
## Ficam numa camada de tela (nítidos em qualquer zoom), no ponto onde o golpe aconteceu.

const RISE := 18.0
const DURATION := 0.9

var world: Node2D


func show_text(at: Vector2, text: String, color: Color, size: int) -> void:
	if world == null:
		return
	var label := Label.new()
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color(0.05, 0.04, 0.08))
	label.add_theme_constant_override("outline_size", 4)
	add_child(label)
	var screen: Vector2 = world.get_viewport().get_canvas_transform() * at
	label.reset_size()
	label.position = screen - Vector2(label.size.x / 2 + randf_range(-6, 6), label.size.y)
	label.pivot_offset = label.size / 2
	var tween := label.create_tween()
	if size >= 11:
		label.scale = Vector2(1.4, 1.4)
		tween.tween_property(label, "scale", Vector2.ONE, 0.15)
	tween.tween_property(label, "position:y", label.position.y - RISE, DURATION)
	tween.parallel().tween_property(label, "modulate:a", 0.0, 0.35).set_delay(DURATION - 0.35)
	tween.tween_callback(label.queue_free)
