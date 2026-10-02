extends CanvasLayer
## O diário (tecla J): missões em andamento e concluídas, pistas e segredos anotados e o que o
## herói carrega. Junta as telas 'missoes', 'diario' e 'inventario' do terminal.

signal closed

const GOLD := "#ffdb73"
const MUTED := "#a9a3b6"
const CYAN := "#8ff0f0"
const VIOLET := "#e08fff"

var is_open := false

@onready var root: Control = $Root
@onready var text: RichTextLabel = %Text


func open() -> void:
	is_open = true
	root.visible = true
	text.text = build_text()
	text.scroll_to_line(0)
	text.grab_focus()


func close() -> void:
	is_open = false
	root.visible = false
	closed.emit()


func _unhandled_input(event: InputEvent) -> void:
	if is_open and (event.is_action_pressed("journal") or event.is_action_pressed("menu")):
		get_viewport().set_input_as_handled()
		close()


static func build_text() -> String:
	var parts := PackedStringArray()
	parts.append("[b][color=%s]Missões[/color][/b]" % GOLD)
	var finished := PackedStringArray()
	for quest_id: String in Game.quests:
		var data := Story.quest(quest_id)
		if data.is_empty():
			continue
		if Game.quest_done(quest_id):
			finished.append("[color=%s]%s — concluída[/color]" % [MUTED, GameText.escape(data.name)])
			continue
		var category: String = Data.quests.get("categories", {}).get(data.category, "")
		parts.append("[color=%s]%s[/color] [color=%s](%s · %s)[/color]" % [GOLD, GameText.escape(data.name), MUTED,
				category, GameText.escape(data.giver)])
		parts.append(GameText.to_bbcode(Story.current_stage(quest_id).get("text", "")))
	if Game.quests.is_empty():
		parts.append("[i]Nenhuma missão por enquanto. Converse com o povo do vale.[/i]")
	parts.append_array(finished)
	parts.append("")
	parts.append("[b][color=%s]Anotações[/color][/b]" % GOLD)
	for index in range(Game.journal.size() - 1, -1, -1):
		var entry: Dictionary = Game.journal[index]
		var color := VIOLET if entry.get("category") == "segredo" else CYAN
		parts.append("[color=%s]%s[/color] [color=%s](Dia %d)[/color]" % [color, GameText.escape(entry.title), MUTED,
				int(entry.get("day", 1))])
		parts.append(GameText.to_bbcode(entry.text))
	parts.append("")
	parts.append("[b][color=%s]Mochila[/color][/b] [color=%s]%s[/color]" % [GOLD, MUTED,
			Game.money_text(Game.copper)])
	var bag := PackedStringArray()
	for item_id: String in Game.items:
		bag.append("%s x%d" % [GameText.escape(Data.item_name(item_id)), Game.count_item(item_id)])
	parts.append(", ".join(bag) if not bag.is_empty() else "[i]Vazia.[/i]")
	return "\n".join(parts)
