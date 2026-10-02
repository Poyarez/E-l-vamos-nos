extends CanvasLayer
## A caixa de diálogo, no estilo dos JRPGs: o texto surge letra a letra, E/Enter avança e as
## respostas viram botões (setas + Enter, clique ou as teclas 1 a 9).
## Conduz as conversas com os NPCs pelo mesmo motor de rpg/npcs.py (falas com "if", efeitos,
## opções já vistas em cinza) e também mostra as narrações do mundo (exames, passagens...).

signal advanced              # o jogador pediu para continuar
signal chosen(index: int)    # o jogador escolheu uma resposta

const CHARACTERS_PER_SECOND := 110.0
const TITLE_COLOR := Color(1.0, 0.86, 0.45)
const SEEN_COLOR := Color(0.6, 0.57, 0.66)

var is_open := false

var _typing: Tween
var _waiting := false
var _choosing := false

@onready var root: Control = $Root
@onready var portrait_frame: PanelContainer = %PortraitFrame
@onready var portrait: TextureRect = %Portrait
@onready var name_label: Label = %Name
@onready var title_label: Label = %Title
@onready var text: RichTextLabel = %Text
@onready var next_mark: Label = %Next
@onready var options_panel: PanelContainer = %Options
@onready var option_list: VBoxContainer = %OptionList


func _ready() -> void:
	root.visible = false
	var blink := next_mark.create_tween().set_loops()
	blink.tween_property(next_mark, "modulate:a", 0.25, 0.45)
	blink.tween_property(next_mark, "modulate:a", 1.0, 0.45)


# --------------------------------------------------------------------------- conversas

## Uma conversa completa com o NPC (a mesma lógica de run_dialogue em rpg/npcs.py).
func run_npc(npc_id: String) -> void:
	var npc: Dictionary = Data.npcs[npc_id]
	var met_before := Game.met.has(npc_id)
	Game.met[npc_id] = true
	_open(npc.name, npc.title, GameText.color(npc.color, TITLE_COLOR), npc_portrait(npc_id))
	var shown := {}
	var pending: Array = []      # falas que ainda não apareceram
	var node_id: Variant = "inicio"
	while node_id != null:
		var node: Dictionary = npc.dialogue.get(node_id, {})
		if node.is_empty():
			push_error("Diálogo de %s sem o trecho '%s'" % [npc_id, node_id])
			break
		if not shown.has(node_id):
			shown[node_id] = true
			pending.append_array(node_lines(node, met_before))
			Story.apply_effects(node.get("effects"))
			Game.set_flag("visto:%s:%s" % [npc_id, node_id])
		if not node.has("options"):
			node_id = node.get("next")
			if node_id == null:
				await _present(pending, [])
			continue
		var options := node_options(node, met_before)
		if options.is_empty():
			await _present(pending, [])
			break
		var labels: Array = []
		for option: Dictionary in options:
			var target: Variant = option.get("next")
			var seen := target != null and Game.has_flag("visto:%s:%s" % [npc_id, target])
			labels.append({"text": GameText.plain(option.text), "seen": seen})
		var choice := await _present(pending, labels)
		pending = []
		var picked: Dictionary = options[maxi(choice, 0)]
		Story.apply_effects(picked.get("effects"))
		node_id = picked.get("next")
	_close()


## As falas do trecho que valem agora (cada fala pode ter seu próprio "if").
static func node_lines(node: Dictionary, met_before: bool) -> Array:
	var lines: Array = []
	for entry: Variant in node.get("text", []):
		if entry is String:
			lines.append(entry)
		elif Conditions.met(entry.get("if"), met_before):
			lines.append(entry.text)
	return lines


static func node_options(node: Dictionary, met_before: bool) -> Array:
	var options: Array = []
	for option: Dictionary in node.get("options", []):
		if Conditions.met(option.get("if"), met_before):
			options.append(option)
	return options


## O retrato do NPC: o quadro de frente dele em npcs.png.
static func npc_portrait(npc_id: String) -> Texture2D:
	var atlas := AtlasTexture.new()
	atlas.atlas = preload("res://art/npcs.png")
	atlas.region = Rect2(0, int(Data.art.npcs.rows[npc_id]) * 16, 16, 16)
	return atlas


# --------------------------------------------------------------------------- narração

## Mostra uma narração (exame, passagem, descanso). Devolve a opção escolhida, ou -1.
func show_message(title: String, paragraphs: Array, options: Array = []) -> int:
	_open(title, "", TITLE_COLOR, null)
	var labels: Array = []
	for label: String in options:
		labels.append({"text": label, "seen": false})
	var choice := await _present(paragraphs, labels)
	_close()
	return choice


# --------------------------------------------------------------------------- mecânica

func _open(title: String, subtitle: String, color: Color, face: Texture2D) -> void:
	is_open = true
	root.visible = true
	name_label.text = title
	name_label.add_theme_color_override("font_color", color)
	title_label.text = subtitle
	title_label.visible = not subtitle.is_empty()
	portrait.texture = face
	portrait_frame.visible = face != null
	text.text = ""
	next_mark.visible = false
	options_panel.visible = false


func _close() -> void:
	is_open = false
	root.visible = false
	options_panel.visible = false


## Mostra as falas uma a uma; a última divide a tela com as respostas, se houver.
func _present(paragraphs: Array, options: Array) -> int:
	for index in paragraphs.size():
		await _type(paragraphs[index])
		if index < paragraphs.size() - 1 or options.is_empty():
			await _wait_advance()
	if options.is_empty():
		return -1
	return await _choose(options)


func _type(paragraph: String) -> void:
	text.text = GameText.to_bbcode(paragraph)
	text.visible_ratio = 0.0
	var duration := maxf(0.05, text.get_total_character_count() / CHARACTERS_PER_SECOND)
	_typing = create_tween()
	_typing.tween_property(text, "visible_ratio", 1.0, duration)
	await _typing.finished


func _wait_advance() -> void:
	next_mark.visible = true
	_waiting = true
	await advanced
	_waiting = false
	next_mark.visible = false


func _choose(options: Array) -> int:
	for child in option_list.get_children():
		option_list.remove_child(child)
		child.queue_free()
	for index in options.size():
		var button := Button.new()
		button.text = "%d. %s" % [index + 1, options[index].text]
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		if options[index].seen:
			button.add_theme_color_override("font_color", SEEN_COLOR)
		button.pressed.connect(_pick.bind(index))
		option_list.add_child(button)
	options_panel.visible = true
	option_list.get_child(0).grab_focus()
	_choosing = true
	var index: int = await chosen
	_choosing = false
	options_panel.visible = false
	return index


func _pick(index: int) -> void:
	if _choosing:
		chosen.emit(index)


func _unhandled_input(event: InputEvent) -> void:
	if not is_open:
		return
	if _choosing:
		if event is InputEventKey and event.pressed and not event.echo:
			var number: int = event.keycode - KEY_1
			if number >= 0 and number < option_list.get_child_count():
				get_viewport().set_input_as_handled()
				_pick(number)
				return
		if event.is_action_pressed("interact"):
			get_viewport().set_input_as_handled()
			var focused := get_viewport().gui_get_focus_owner()
			if focused and focused.get_parent() == option_list:
				_pick(focused.get_index())
		return
	var click: bool = event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT
	if click or event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		if _typing and _typing.is_running():
			_typing.custom_step(60.0)
		elif _waiting:
			advanced.emit()
