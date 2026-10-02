extends Node
## Tira fotos de tela do jogo em situações típicas (rode com janela, não em --headless):
##     godot --path godot res://tests/screenshots.tscn -- <pasta de saída>
## Útil para conferir o visual depois de mudar arte, mapas ou interface.

var out_dir := "user://screenshots"


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		out_dir = args[0]
	DirAccess.make_dir_recursive_absolute(out_dir)
	# 1. título e criação de personagem
	var title: Node = load("res://scenes/title.tscn").instantiate()
	add_child(title)
	await _frames(20)
	await _shot("01_titulo")
	title._show_creation()
	title.hero_name.text = "Lia"
	title.gender.select(1)
	title.hero_class.select(1)
	title.hair_style.select(1)
	title.hair_color.select(2)
	title.armor_color.select(6)
	title._on_choice_changed()
	await _frames(10)
	await _shot("02_criacao")
	var choices: Dictionary = title.choices()
	title.queue_free()
	await _frames(2)
	# 2. o vale de dia, na entrada da vila
	Game.new_game(choices)
	var main: Node = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	var world: Node = main.world
	await _frames(30)
	await _shot("03_vila_dia")
	# 3. conversa com a Anciã Ysolde
	world.load_map("vale_primordia", Vector2i(28, 14), "up")
	world.arrive()
	world.interact()
	await _frames(90)
	main.dialogue._typing.custom_step(60.0)
	await _frames(5)
	await _shot("04_dialogo")
	main.dialogue.advanced.emit()
	await _frames(90)
	main.dialogue._typing.custom_step(60.0)
	await _frames(10)
	await _shot("05_dialogo_opcoes")
	var last: int = main.dialogue.option_list.get_child_count() - 1
	main.dialogue._pick(last)
	await _frames(10)
	# 4. de noite, perto da estalagem
	Game.minutes = 21 * 60 + 30
	Game.period_changed.emit(Game.period())
	world.update_lighting(false)
	world.load_map("vale_primordia", Vector2i(33, 15), "down")
	world.arrive()
	await _frames(30)
	await _shot("06_vila_noite")
	# 5. diário
	main.journal.open()
	await _frames(10)
	await _shot("07_diario")
	main.journal.close()
	# 6. a gruta (mapa fechado, com a luz do herói)
	var start: Array = Data.map_data("gruta_veu_prata").start
	world.load_map("gruta_veu_prata", Vector2i(int(start[0]), int(start[1])), "up")
	world.arrive()
	await _frames(30)
	await _shot("08_gruta")
	# 7. combate em tempo real na floresta: alvo, ataque automático, números subindo
	Game.level = 5
	HeroStats.invalidate()
	Game.restore()
	Game.refresh_action_bar()
	Game.minutes = 10 * 60
	Game.period_changed.emit(Game.period())
	world.load_map("vale_primordia", Vector2i(13, 9), "left")
	world.update_lighting(false)
	world.spawner.clear()
	var wolf: Node = world.spawner.create("lobo_cinzento", 5, Vector2i(12, 9))
	world.spawner.create("lobo_faminto", 4, Vector2i(11, 11))
	world.combat.attack(wolf)
	await _frames(20)
	world.combat.use_slot(1)
	await _seconds(2.6)
	world.combat.use_slot(2)
	await _seconds(0.5)
	await _shot("09_combate")
	# 8. chefe concentrando um golpe com selos (Sea of Stars) no quadro do alvo
	Game.level = 7
	HeroStats.invalidate()
	Game.restore()
	world.load_map("toca_dos_lobos", Vector2i(13, 11), "right")
	await _frames(5)
	var alpha: Node = null
	for monster: Node in world.spawner.alive_monsters():
		if monster.template_id == "presa_de_gelo":
			alpha = monster
	if alpha != null:
		alpha.place(Vector2i(14, 11))
		world.combat.attack(alpha)
		await _seconds(1.2)
		var howl: Dictionary = alpha.abilities[2]
		alpha.charging = {"ability": howl, "left": 4.0, "total": 6.0, "locks": howl.locks, "broken": [false, true, false]}
		await _seconds(0.6)
	await _shot("10_chefe")
	get_tree().quit()


func _seconds(duration: float) -> void:
	await get_tree().create_timer(duration).timeout


func _frames(count: int) -> void:
	for i in count:
		await get_tree().process_frame


func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var path := out_dir.path_join(name + ".png")
	image.save_png(path)
	print("foto: ", path)
