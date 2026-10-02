extends Node
## Tabela de balanceamento do combate em tempo real (não faz parte dos testes automáticos):
##     godot --headless --path godot res://tests/combat_sim.tscn
##     godot --headless --path godot res://tests/combat_sim.tscn -- chefes 15   (só os chefes, 15 lutas)
## Cada linha: classe e nível contra um grupo de criaturas, N lutas: vitórias, duração média,
## vida que sobra e poções gastas.

const Sim := preload("res://tests/sim.gd")
const FIGHTS := 6
## [nível do herói, grupo de criaturas, poções (item, quantidade)]
const SCENARIOS := [
	[1, [["javali_jovem", 1]], []], [1, [["rato_gigante", 2]], []], [2, [["corvo_ladrao", 2]], []],
	[3, [["lobo_faminto", 3]], []], [3, [["lagarto_ribeirao", 3]], []],
	[3, [["lobo_faminto", 2], ["lobo_faminto", 2]], []],
	[5, [["lobo_cinzento", 5]], []], [5, [["aranha_da_mata", 5]], []], [5, [["javali_espinhento", 5]], []],
	[6, [["espirito_sussurrante", 6]], []], [6, [["varek_domador", 6]], ["pocao_cura_menor", 3]],
	[7, [["presa_de_gelo", 7]], ["pocao_cura_menor", 3]],
	[8, [["kobold_escavador", 8]], []], [8, [["sentinela_ruinas", 9]], []],
	[9, [["acolito_lua", 9], ["acolito_lua", 9]], ["pocao_cura", 2]], [10, [["guarda_capa_negra", 11]], []],
	[10, [["capataz_gorran", 10]], ["pocao_cura", 3]], [11, [["ulric", 11]], ["pocao_cura", 3]],
	[12, [["morwen", 12]], ["pocao_cura", 3]], [13, [["vigia_atormentado", 13]], ["pocao_cura", 4]],
]


func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await get_tree().process_frame
	var world: Node = main.world
	world.overlay_open = true
	world.combat.hero_died.disconnect(world._on_hero_died)
	var spot := Sim.open_spot(world)
	# -- chefes [lutas]: só as lutas contra chefes, com mais repetições
	var args := OS.get_cmdline_user_args()
	var only_bosses := "chefes" in args
	var fights := int(args[args.size() - 1]) if args.size() > 1 else FIGHTS
	var classes := ["guerreiro", "mago", "sacerdote", "ladino"]
	print("cenário                                   | ", " | ".join(PackedStringArray(classes)))
	for scenario: Array in SCENARIOS:
		if only_bosses and not Data.monster(scenario[1][0][0]).get("boss", false):
			continue
		var cells := PackedStringArray()
		for class_id: String in classes:
			var wins := 0
			var seconds := 0.0
			var hp := 0.0
			var potions := 0
			for fight in fights:
				Sim.prepare_hero(class_id, scenario[0], scenario[2])
				world.load_map("vale_primordia", spot, "down")
				var result := Sim.fight(world, scenario[1], class_id)
				if result.won:
					wins += 1
					hp += result.hp
				seconds += result.seconds
				potions += result.potions
			cells.append("%3d%% %4.1fs vida %3d%% poções %.1f" % [wins * 100 / fights, seconds / fights,
					roundi(hp / maxi(1, wins) * 100), float(potions) / fights])
		var label := "nv %2d vs %s" % [scenario[0], ", ".join(PackedStringArray(scenario[1].map(
				func(pair: Array) -> String: return "%s %d" % [pair[0], pair[1]])))]
		print(label.rpad(42), "| ", " | ".join(cells))
	get_tree().quit()
