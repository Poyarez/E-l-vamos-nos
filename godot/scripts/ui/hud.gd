extends CanvasLayer
## A interface sobre o mapa, no jeito do WoW: o quadro do herói (vida e Mana/Raiva/Energia),
## o quadro do alvo (com a barra do golpe que ele concentra e os selos), a barra de ações com
## as recargas, a barra de experiência, o lugar e o relógio, avisos que somem sozinhos, o
## cartão do local (a descrição rica do terminal) e a dica do que o botão de interagir faz.

const MAX_TOASTS := 6
const SLOT_SIZE := Vector2(32, 30)
const KEYS := ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

## Cor de cada tipo de aviso (o "kind" de Game.notify).
const KIND_COLORS := {
	"area": Color(0.88, 0.56, 1.0), "discovery": Color(1.0, 0.86, 0.45), "secret": Color(0.88, 0.56, 1.0),
	"treasure": Color(1.0, 0.86, 0.45), "journal": Color(0.56, 0.94, 0.94), "quest": Color(1.0, 0.86, 0.45),
	"xp": Color(0.88, 0.56, 1.0), "level": Color(1.0, 0.9, 0.5), "item": Color(0.93, 0.91, 0.86),
	"time": Color(0.66, 0.63, 0.72), "lore": Color(0.8, 0.77, 0.88), "warn": Color(1.0, 0.48, 0.42),
}
const RESOURCE_COLORS := {"mana": Color(0.25, 0.45, 0.95), "raiva": Color(0.85, 0.2, 0.15),
		"energia": Color(0.95, 0.82, 0.2)}

var world: Node   # o mundo (ligado pelo main.gd)

var _banner_tween: Tween
var _error_tween: Tween
var _card_landmark := ""      # o local cujo cartão está à mostra
var _card_until := 0.0        # o cartão some sozinho depois de alguns segundos
var _slots: Array = []        # {panel, name, key, count, shade, timer}

@onready var player_name: Label = %PlayerName
@onready var player_level: Label = %PlayerLevel
@onready var hp_bar: ProgressBar = %HpBar
@onready var hp_text: Label = %HpText
@onready var resource_bar: ProgressBar = %ResourceBar
@onready var resource_text: Label = %ResourceText
@onready var combo_label: Label = %Combo
@onready var card: PanelContainer = %Card
@onready var card_text: RichTextLabel = %CardText
@onready var target_frame: PanelContainer = %TargetFrame
@onready var target_name: Label = %TargetName
@onready var target_level: Label = %TargetLevel
@onready var target_hp_bar: ProgressBar = %TargetHpBar
@onready var target_hp_text: Label = %TargetHpText
@onready var target_cast: Control = %TargetCast
@onready var target_cast_bar: ProgressBar = %TargetCastBar
@onready var target_cast_text: Label = %TargetCastText
@onready var seals: HBoxContainer = %Seals
@onready var target_effects: Label = %TargetEffects
@onready var place_title: Label = %PlaceTitle
@onready var place_sub: Label = %PlaceSub
@onready var clock: Label = %Clock
@onready var moon: Label = %Moon
@onready var money: Label = %Money
@onready var toasts: VBoxContainer = %Toasts
@onready var error_label: Label = %ErrorLabel
@onready var banner: Control = %Banner
@onready var banner_title: Label = %BannerTitle
@onready var banner_text: Label = %BannerText
@onready var hint: Label = %Hint
@onready var cast_box: Control = %CastBox
@onready var cast_bar: ProgressBar = %CastBar
@onready var cast_text: Label = %CastText
@onready var action_bar: HBoxContainer = %ActionBar
@onready var xp_bar: ProgressBar = %XpBar
@onready var xp_text: Label = %XpText


func _ready() -> void:
	Game.changed.connect(refresh)
	Game.notified.connect(toast)
	_style_bar(hp_bar, Color(0.2, 0.75, 0.25))
	_style_bar(target_hp_bar, Color(0.85, 0.2, 0.18))
	_style_bar(cast_bar, Color(1.0, 0.75, 0.25))
	_style_bar(target_cast_bar, Color(0.75, 0.45, 1.0))
	_style_bar(xp_bar, Color(0.62, 0.35, 0.85))
	_build_action_bar()


func bind(world_node: Node) -> void:
	world = world_node
	world.location_changed.connect(refresh)
	world.area_discovered.connect(show_banner)
	world.combat.error.connect(show_error)
	refresh()


# --------------------------------------------------------------------------- quadro a quadro

func _process(_delta: float) -> void:
	if world == null:
		return
	var free: bool = not world.busy and not world.hero.moving
	hint.text = world.interaction_hint() if not world.busy else ""
	card.visible = free and not _card_landmark.is_empty() and Time.get_ticks_msec() / 1000.0 < _card_until \
			and not world.combat.in_combat()
	_update_player()
	_update_target()
	_update_cast()
	_update_slots()


func _update_player() -> void:
	var maximum: int = world.hero.maximum_hp()
	hp_bar.value = float(Game.hp) / maxi(1, maximum)
	hp_text.text = "%d / %d" % [Game.hp, maximum]
	var resource_max := HeroStats.max_resource()
	resource_bar.value = float(Game.resource) / maxi(1, resource_max)
	resource_text.text = "%s %d / %d" % [HeroStats.resource_name(), Game.resource, resource_max]
	var combo: int = world.combat.combo
	combo_label.visible = HeroStats.resource_id() == "energia"
	combo_label.text = "Pontos de combo: %d/%d" % [combo, CombatRules.MAX_COMBO]


func _update_target() -> void:
	var target: Node = world.combat.target
	target_frame.visible = target != null and is_instance_valid(target)
	if not target_frame.visible:
		return
	var color := CombatRules.con_color(Game.level, target.level)
	target_name.text = target.unit_name()
	target_name.add_theme_color_override("font_color", color)
	var tag := " Chefe" if target.boss else (" Elite" if target.elite else "")
	target_level.text = "Nv %d%s" % [target.level, tag]
	target_level.add_theme_color_override("font_color", color)
	target_hp_bar.value = float(target.hp) / maxi(1, target.max_hp)
	target_hp_text.text = "%d / %d" % [target.hp, target.max_hp]
	var charging: Dictionary = target.charging
	target_cast.visible = not charging.is_empty()
	if target_cast.visible:
		target_cast_bar.value = 1.0 - charging.left / charging.total
		target_cast_text.text = charging.ability.name
		_update_seals(charging)
	var names: Array = []
	for effect: Dictionary in target.effects:
		names.append("%s %ds" % [effect.name, ceili(effect.left)])
	target_effects.text = " · ".join(PackedStringArray(names))
	target_effects.visible = not names.is_empty()


## Os selos do golpe concentrado: um quadradinho da cor de cada elemento (apagado se rompido).
func _update_seals(charging: Dictionary) -> void:
	var locks: Array = charging.locks
	while seals.get_child_count() < locks.size():
		var seal := ColorRect.new()
		seal.custom_minimum_size = Vector2(9, 5)
		seal.mouse_filter = Control.MOUSE_FILTER_IGNORE
		seals.add_child(seal)
	for index in seals.get_child_count():
		var seal: ColorRect = seals.get_child(index)
		seal.visible = index < locks.size()
		if seal.visible:
			seal.color = Color(0.25, 0.25, 0.28) if charging.broken[index] else CombatRules.element_color(locks[index])
			seal.tooltip_text = "Selo de %s" % CombatRules.element_name(locks[index])


func _update_cast() -> void:
	var cast: Dictionary = world.combat.cast
	cast_box.visible = not cast.is_empty()
	if cast_box.visible:
		var progress: float = 1.0 - cast.left / cast.total
		cast_bar.value = 1.0 - progress if cast.channel else progress
		cast_text.text = "%s  %.1fs" % [cast.ability.name, maxf(0.0, cast.left)]


# --------------------------------------------------------------------------- barra de ações

func _build_action_bar() -> void:
	for index in KEYS.size():
		var panel := Panel.new()
		panel.custom_minimum_size = SLOT_SIZE
		panel.mouse_filter = Control.MOUSE_FILTER_STOP
		panel.gui_input.connect(_on_slot_input.bind(index))
		var shade := ColorRect.new()
		shade.color = Color(0, 0, 0, 0.62)
		shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
		panel.add_child(shade)
		var name_label := _slot_label(panel, 8, HORIZONTAL_ALIGNMENT_CENTER, VERTICAL_ALIGNMENT_CENTER)
		var key_label := _slot_label(panel, 6, HORIZONTAL_ALIGNMENT_LEFT, VERTICAL_ALIGNMENT_TOP)
		key_label.text = KEYS[index]
		key_label.add_theme_color_override("font_color", Color(0.75, 0.72, 0.8))
		var count_label := _slot_label(panel, 6, HORIZONTAL_ALIGNMENT_RIGHT, VERTICAL_ALIGNMENT_BOTTOM)
		var timer_label := _slot_label(panel, 9, HORIZONTAL_ALIGNMENT_CENTER, VERTICAL_ALIGNMENT_CENTER)
		timer_label.add_theme_color_override("font_color", Color(1.0, 0.95, 0.6))
		action_bar.add_child(panel)
		_slots.append({"panel": panel, "name": name_label, "key": key_label, "count": count_label, "shade": shade,
				"timer": timer_label})


func _slot_label(panel: Panel, size: int, horizontal: int, vertical: int) -> Label:
	var label := Label.new()
	label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	label.offset_left = 2
	label.offset_right = -2
	label.horizontal_alignment = horizontal
	label.vertical_alignment = vertical
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_outline_color", Color(0.05, 0.04, 0.08))
	label.add_theme_constant_override("outline_size", 3)
	panel.add_child(label)
	return label


func _update_slots() -> void:
	for index in _slots.size():
		var slot: Dictionary = _slots[index]
		var info: Dictionary = world.combat.slot_info(index)
		var panel: Panel = slot.panel
		slot.name.text = info.label
		panel.tooltip_text = info.tooltip
		slot.count.text = str(info.count) if info.count >= 0 else ""
		var cooling: bool = info.cooldown > 0.05
		var shade: ColorRect = slot.shade
		shade.visible = cooling
		if cooling:
			var ratio: float = clampf(info.cooldown / info.total, 0.0, 1.0)
			shade.position = Vector2(0, SLOT_SIZE.y * (1.0 - ratio))
			shade.size = Vector2(SLOT_SIZE.x, SLOT_SIZE.y * ratio)
		slot.timer.text = str(ceili(info.cooldown)) if info.cooldown >= 1.5 else ""
		var style := _slot_style(info)
		panel.add_theme_stylebox_override("panel", style)
		panel.modulate = Color(1, 1, 1) if info.usable or info.entry.is_empty() else Color(0.55, 0.55, 0.75)


func _slot_style(info: Dictionary) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.08, 0.15, 0.92) if not info.entry.is_empty() else Color(0.06, 0.05, 0.09, 0.6)
	style.set_border_width_all(1)
	style.border_color = Color(1.0, 0.86, 0.45) if info.active else Color(0.45, 0.38, 0.62)
	style.set_corner_radius_all(3)
	return style


func _on_slot_input(event: InputEvent, index: int) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		world.combat.use_slot(index)
		get_viewport().set_input_as_handled()


# --------------------------------------------------------------------------- lugar, relógio e avisos

func refresh() -> void:
	if world == null or world.map.is_empty():
		return
	var cell: Vector2i = world.hero.cell
	var region: Dictionary = world.region_at(cell)
	var landmark: Dictionary = world.landmark_at(cell)
	place_title.text = region.get("name", world.map.name)
	place_sub.text = landmark.get("name", "") if not landmark.is_empty() \
			else "%s · %s" % [world.map.name, world.terrain_at(cell).get("name", "")]
	clock.text = "Dia %d · %s · %s" % [Game.day(), Game.time_text(), Game.period_name()]
	moon.text = Game.moon_phase()
	money.text = Game.money_text(Game.copper)
	player_name.text = Game.hero.name
	player_level.text = "%s nv %d" % [Game.class_name_text(), Game.level]
	_style_bar(resource_bar, RESOURCE_COLORS.get(HeroStats.resource_id(), Color(0.3, 0.5, 1.0)))
	var needed := Game.xp_needed()
	xp_bar.value = float(Game.xp) / needed if needed else 1.0
	xp_text.text = "XP %d / %d" % [Game.xp, needed] if needed else "Nível máximo"
	if landmark.is_empty():
		_card_landmark = ""
	elif landmark.id != _card_landmark:
		# a descrição rica do local, como no terminal (some depois de um tempo)
		var night: bool = world.outdoor() and Game.is_night() and landmark.get("night", "")
		var text: String = landmark.night if night else landmark.description
		_card_landmark = landmark.id
		_card_until = Time.get_ticks_msec() / 1000.0 + clampf(4.0 + text.length() / 18.0, 8.0, 20.0)
		card_text.text = "[color=#ffdb73]%s[/color]\n%s" % [GameText.escape(landmark.name), GameText.to_bbcode(text)]


## Um aviso que aparece embaixo do relógio e some sozinho (mais tempo se for longo).
func toast(text: String, kind: String = "") -> void:
	var panel := PanelContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.size_flags_horizontal = Control.SIZE_SHRINK_END
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = 190
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	label.add_theme_font_size_override("font_size", 8)
	label.add_theme_color_override("font_color", KIND_COLORS.get(kind, Color(0.93, 0.91, 0.86)))
	panel.add_child(label)
	toasts.add_child(panel)
	while toasts.get_child_count() > MAX_TOASTS:
		toasts.get_child(0).free()
	var tween := panel.create_tween()
	tween.tween_interval(clampf(2.5 + text.length() / 22.0, 3.0, 12.0))
	tween.tween_property(panel, "modulate:a", 0.0, 0.6)
	tween.tween_callback(panel.queue_free)


## Faixa grande na primeira visita a uma região.
func show_banner(title: String, text: String) -> void:
	banner_title.text = title
	banner_text.text = GameText.plain(text)
	if _banner_tween:
		_banner_tween.kill()
	_banner_tween = create_tween()
	_banner_tween.tween_property(banner, "modulate:a", 1.0, 0.5)
	_banner_tween.tween_interval(clampf(2.0 + text.length() / 25.0, 3.0, 9.0))
	_banner_tween.tween_property(banner, "modulate:a", 0.0, 0.8)


## Mensagem de erro em vermelho no alto da tela ("Fora de alcance", "Raiva insuficiente").
func show_error(text: String) -> void:
	error_label.text = text
	if _error_tween:
		_error_tween.kill()
	error_label.modulate.a = 1.0
	_error_tween = create_tween()
	_error_tween.tween_interval(1.3)
	_error_tween.tween_property(error_label, "modulate:a", 0.0, 0.5)


static func _style_bar(bar: ProgressBar, color: Color) -> void:
	var fill := StyleBoxFlat.new()
	fill.bg_color = color
	fill.set_corner_radius_all(2)
	var background := StyleBoxFlat.new()
	background.bg_color = Color(0.05, 0.04, 0.08, 0.9)
	background.border_color = Color(0.3, 0.26, 0.4)
	background.set_border_width_all(1)
	background.set_corner_radius_all(2)
	bar.add_theme_stylebox_override("fill", fill)
	bar.add_theme_stylebox_override("background", background)
