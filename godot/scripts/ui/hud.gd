extends CanvasLayer
## A interface sobre o mapa: onde o herói está, relógio e lua, nível e moedas, avisos que
## somem sozinhos, o cartão do local (a descrição rica do terminal) e a dica do que o botão
## de interagir faz agora.

const MAX_TOASTS := 6

## Cor de cada tipo de aviso (o "kind" de Game.notify).
const KIND_COLORS := {
	"area": Color(0.88, 0.56, 1.0), "discovery": Color(1.0, 0.86, 0.45), "secret": Color(0.88, 0.56, 1.0),
	"treasure": Color(1.0, 0.86, 0.45), "journal": Color(0.56, 0.94, 0.94), "quest": Color(1.0, 0.86, 0.45),
	"xp": Color(0.88, 0.56, 1.0), "level": Color(1.0, 0.9, 0.5), "item": Color(0.93, 0.91, 0.86),
	"time": Color(0.66, 0.63, 0.72), "lore": Color(0.8, 0.77, 0.88), "warn": Color(1.0, 0.48, 0.42),
}

var world: Node   # o mundo (ligado pelo main.gd)

var _banner_tween: Tween
var _card_landmark := ""      # o local cujo cartão está à mostra
var _card_until := 0.0        # o cartão some sozinho depois de alguns segundos

@onready var place_title: Label = %PlaceTitle
@onready var place_sub: Label = %PlaceSub
@onready var toasts: VBoxContainer = %Toasts
@onready var clock: Label = %Clock
@onready var moon: Label = %Moon
@onready var hero_line: Label = %HeroLine
@onready var card: PanelContainer = %Card
@onready var card_text: RichTextLabel = %CardText
@onready var hint: Label = %Hint
@onready var help: Label = %Help
@onready var banner: Control = %Banner
@onready var banner_title: Label = %BannerTitle
@onready var banner_text: Label = %BannerText


func _ready() -> void:
	Game.changed.connect(refresh)
	Game.notified.connect(toast)


func bind(world_node: Node) -> void:
	world = world_node
	world.location_changed.connect(refresh)
	world.area_discovered.connect(show_banner)
	refresh()


func _process(_delta: float) -> void:
	if world == null:
		return
	var free: bool = not world.busy and not world.hero.moving
	hint.text = world.interaction_hint() if free else ""
	help.visible = free
	card.visible = free and not _card_landmark.is_empty() and Time.get_ticks_msec() / 1000.0 < _card_until


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
	var needed := Game.xp_needed()
	var xp_text := "XP %d/%d" % [Game.xp, needed] if needed else "nível máximo"
	hero_line.text = "%s · %s nv %d · %s · %s" % [Game.hero.name, Game.class_name_text(), Game.level, xp_text,
			Game.money_text(Game.copper)]
	if landmark.is_empty():
		_card_landmark = ""
	elif landmark.id != _card_landmark:
		# a descrição rica do local, como no terminal (some depois de um tempo)
		var night: bool = world.outdoor() and Game.is_night() and landmark.get("night", "")
		var text: String = landmark.night if night else landmark.description
		_card_landmark = landmark.id
		_card_until = Time.get_ticks_msec() / 1000.0 + clampf(4.0 + text.length() / 18.0, 8.0, 20.0)
		card_text.text = GameText.to_bbcode(text)


## Um aviso que aparece embaixo do nome do lugar e some sozinho (mais tempo se for longo).
func toast(text: String, kind: String = "") -> void:
	var panel := PanelContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = 196
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	label.add_theme_font_size_override("font_size", 9)
	label.add_theme_color_override("font_color", KIND_COLORS.get(kind, Color(0.93, 0.91, 0.86)))
	panel.add_child(label)
	toasts.add_child(panel)
	while toasts.get_child_count() > MAX_TOASTS:
		toasts.get_child(0).free()
	var tween := panel.create_tween()
	tween.tween_interval(clampf(2.5 + text.length() / 22.0, 3.0, 12.0))
	tween.tween_property(panel, "modulate:a", 0.0, 0.6)
	tween.tween_callback(panel.queue_free)


## Faixa grande no meio da tela na primeira visita a uma região.
func show_banner(title: String, text: String) -> void:
	banner_title.text = title
	banner_text.text = GameText.plain(text)
	if _banner_tween:
		_banner_tween.kill()
	_banner_tween = create_tween()
	_banner_tween.tween_property(banner, "modulate:a", 1.0, 0.5)
	_banner_tween.tween_interval(clampf(2.0 + text.length() / 25.0, 3.0, 9.0))
	_banner_tween.tween_property(banner, "modulate:a", 0.0, 0.8)
