extends Node
## O combate em tempo real, no estilo do WoW Classic com um toque de RuneScape.
##
## O herói escolhe um alvo (Tab ou clique), ataca sozinho no ritmo da arma (ataque
## automático) e usa as habilidades da barra de ações (teclas 1 a 0), que têm recarga global,
## recarga própria e custo de Mana, Raiva ou Energia. Magias levam um tempo para conjurar
## (andar cancela). As criaturas atacam a cada 2 segundos e concentram golpes especiais:
## acertar os elementos dos selos enfraquece ou cancela o golpe (Sea of Stars), e o Chute
## interrompe. Ao ser atacado sem alvo, o herói revida sozinho, como no RuneScape.
##
## As fórmulas são as de rpg/combat.py; as constantes ficam em CombatRules.

signal floating(at: Vector2, text: String, color: Color, size: int)  # números e avisos na tela
signal error(text: String)                                          # "Fora de alcance", "Raiva insuficiente"...
signal target_changed
signal hero_died

const HIT_COLOR := Color(1, 1, 1)
const CRIT_COLOR := Color(1.0, 0.86, 0.3)
const HURT_COLOR := Color(1.0, 0.35, 0.3)
const HEAL_COLOR := Color(0.45, 1.0, 0.45)
const MISS_COLOR := Color(0.75, 0.72, 0.8)
const SPECIAL_COLOR := Color(0.88, 0.56, 1.0)
const SEAL_COLOR := Color(0.56, 0.94, 0.94)

var world: Node
var hero: Unit
var target: Unit = null
var auto_attack := false
var swing_left := 0.0
var offhand_left := 0.0
var gcd_left := 0.0
var item_left := 0.0
var cooldowns: Dictionary = {}     # habilidade -> segundos até ficar pronta
var cast: Dictionary = {}          # conjuração: {ability, left, total, channel, pulses, target}
var combo := 0
var crit_next := false
var combat_left := 0.0
var rng := RandomNumberGenerator.new()

var _hp_fraction := 0.0
var _resource_fraction := 0.0
var _hits: Dictionary = {}         # alvo -> acertou? (efeitos que acompanham um golpe)


func _ready() -> void:
	rng.randomize()


func setup(world_node: Node) -> void:
	world = world_node
	hero = world.hero


func _process(delta: float) -> void:
	if world == null or world.paused:
		return
	step(delta)


## Um passo da simulação (os testes chamam direto, com o tempo que quiserem).
func step(delta: float) -> void:
	gcd_left = maxf(0.0, gcd_left - delta)
	item_left = maxf(0.0, item_left - delta)
	swing_left = maxf(0.0, swing_left - delta)
	offhand_left = maxf(0.0, offhand_left - delta)
	for ability_id: String in cooldowns.keys():
		cooldowns[ability_id] -= delta
		if cooldowns[ability_id] <= 0:
			cooldowns.erase(ability_id)
	if _engaged_monsters().is_empty():
		combat_left = maxf(0.0, combat_left - delta)
	else:
		combat_left = CombatRules.COMBAT_TIMEOUT
	if not hero.alive():
		return
	_regenerate(delta)
	_tick_effects(hero, delta)
	for monster: Node in world.spawner.alive_monsters():
		_tick_effects(monster, delta)
	if not cast.is_empty():
		_advance_cast(delta)
	if target != null and (not is_instance_valid(target) or not target.alive()):
		set_target(null)
	if auto_attack:
		_auto_attack()


# --------------------------------------------------------------------------- consultas

func in_combat() -> bool:
	return combat_left > 0.0


func hero_hidden() -> bool:
	return hero.has_kind("stealth")


func hero_can_move() -> bool:
	return hero.alive() and hero.incapacitated().is_empty()


func is_melee_class() -> bool:
	return HeroStats.resource_id() != "mana"


## Uma criatura parada percebe o herói? (Raio de agressão, como no WoW: maior à noite,
## menor contra heróis bem mais fortes; criaturas "cinzentas" nem ligam.)
func can_aggro(monster: Node) -> bool:
	if not hero.alive() or hero_hidden() or world.busy:
		return false
	var radius: int = monster.aggro_radius
	if not monster.camp.get("fixed", false):
		if world.outdoor() and Game.is_night():
			radius += 1
		radius -= maxi(0, Game.level - monster.level) / 3
		if CombatRules.kill_xp(Game.level, monster.level) == 0:
			return false
	return CombatRules.tile_distance(monster.aggro_center, hero.cell) <= maxi(1, radius) \
			and CombatRules.tile_distance(monster.cell, hero.cell) <= monster.LEASH


func in_range(unit: Node, tiles: int) -> bool:
	return CombatRules.tile_distance(hero.cell, unit.cell) <= tiles


func _engaged_monsters() -> Array:
	return world.spawner.alive_monsters().filter(func(monster: Node) -> bool: return monster.state == "combat")


# --------------------------------------------------------------------------- alvo

func set_target(unit: Unit) -> void:
	if is_instance_valid(target) and target != unit:
		target.targeted = false
		target.queue_redraw()
	target = unit if is_instance_valid(unit) else null
	if unit != null:
		unit.targeted = true
		unit.queue_redraw()
	else:
		auto_attack = false
	target_changed.emit()


## Tab: a criatura viva mais perto (repetindo, passa para a próxima).
func target_next() -> void:
	var candidates: Array = []
	for monster: Node in world.spawner.alive_monsters():
		if monster.state != "evade" and in_range(monster, 10):
			candidates.append(monster)
	if candidates.is_empty():
		error.emit("Nenhum inimigo por perto.")
		return
	candidates.sort_custom(_closer)
	var index := candidates.find(target)
	set_target(candidates[(index + 1) % candidates.size()])


func _closer(a: Node, b: Node) -> bool:
	return CombatRules.tile_distance(hero.cell, a.cell) < CombatRules.tile_distance(hero.cell, b.cell)


## Atacar (clique direito, F ou o primeiro atalho da barra): ataque automático no alvo.
func attack(unit: Unit = null) -> void:
	if unit == null:
		unit = target
	if unit == null or not unit.alive():
		target_next()
		unit = target
	if unit == null:
		return
	set_target(unit)
	auto_attack = true
	_engage(unit)
	if not in_range(unit, CombatRules.MELEE_RANGE):
		world.approach(unit)


func toggle_attack() -> void:
	if auto_attack:
		auto_attack = false
	else:
		attack()


# --------------------------------------------------------------------------- barra de ações

## Usa o atalho da barra (0 a 9).
func use_slot(index: int) -> void:
	if index < 0 or index >= Game.action_bar.size():
		return
	var entry: String = Game.action_bar[index]
	if entry == "attack":
		toggle_attack()
	elif entry.begins_with("ability:"):
		use_ability(entry.substr(8))
	elif entry.begins_with("item:"):
		use_item(entry.substr(5))


## O estado de um atalho, para a barra na tela.
func slot_info(index: int) -> Dictionary:
	var entry: String = Game.action_bar[index] if index < Game.action_bar.size() else ""
	var info := {"entry": entry, "label": "", "name": "", "tooltip": "", "cooldown": 0.0, "total": 1.0,
			"usable": true, "active": false, "count": -1}
	if entry == "attack":
		info.label = "Atq"
		info.name = "Atacar"
		info.tooltip = "Atacar: liga e desliga o ataque automático no alvo (F ou clique direito)."
		info.active = auto_attack
	elif entry.begins_with("ability:"):
		var ability := HeroStats.ability(entry.substr(8))
		var cost := HeroStats.ability_cost(ability)
		info.name = ability.get("name", "")
		info.label = short_label(info.name)
		info.tooltip = "%s\n%s · %s\n%s" % [info.name, _cost_text(cost), _timing_text(ability),
				ability.get("description", "")]
		var left: float = cooldowns.get(ability.get("id", ""), 0.0)
		if left > gcd_left:
			info.cooldown = left
			info.total = maxf(0.1, HeroStats.ability_cooldown(ability))
		else:
			info.cooldown = gcd_left
			info.total = CombatRules.ENERGY_GCD if HeroStats.resource_id() == "energia" else CombatRules.GCD
		info.usable = Game.resource >= cost and _requirements_problem(ability, target).is_empty()
		info.active = not cast.is_empty() and cast.ability.id == ability.get("id", "")
	elif entry.begins_with("item:"):
		var item_id := entry.substr(5)
		info.name = Data.item_name(item_id)
		info.label = short_label(info.name)
		info.count = Game.count_item(item_id)
		info.tooltip = "%s\n%s" % [info.name, Data.item(item_id).get("description", "")]
		info.cooldown = item_left
		info.total = CombatRules.ITEM_COOLDOWN
		info.usable = info.count > 0
	return info


## "Bola de Fogo" -> "BdF"; "Golpe Heroico" -> "GH".
static func short_label(text: String) -> String:
	var words := text.replace(":", "").split(" ", false)
	if words.size() == 1:
		return words[0].substr(0, 3)
	var label := ""
	for word in words:
		label += word.substr(0, 1) if word.length() > 2 else word.substr(0, 1).to_lower()
	return label.substr(0, 3)


func _cost_text(cost: int) -> String:
	return "%d de %s" % [cost, HeroStats.resource_name()] if cost else "sem custo"


func _timing_text(ability: Dictionary) -> String:
	var parts: Array = []
	var time := CombatRules.cast_time(ability.id)
	parts.append(("canaliza %.1fs" if CombatRules.is_channeled(ability.id) else "conjura %.1fs") % time
			if time > 0 else "instantânea")
	var cooldown := HeroStats.ability_cooldown(ability)
	if cooldown > 0:
		parts.append("recarga %ds" % roundi(cooldown))
	var reach := CombatRules.ability_range(ability)
	if reach > 0:
		parts.append("alcance %d" % reach)
	return " · ".join(PackedStringArray(parts))


# --------------------------------------------------------------------------- habilidades

## Por que a habilidade não pode ser usada agora contra esse alvo ("" se pode).
func _requirements_problem(ability: Dictionary, unit: Unit) -> String:
	var requires: Dictionary = ability.get("requires", {})
	if requires.get("first_round", false) and in_combat():
		return "%s só pode abrir a luta (fora de combate)." % ability.name
	if requires.get("shield", false) and not HeroStats.has_shield():
		return "%s exige um escudo equipado." % ability.name
	if requires.get("dagger", false) and not HeroStats.has_dagger():
		return "%s exige uma adaga na mão principal." % ability.name
	if requires.has("combo") and combo < int(requires.combo):
		return "%s precisa de pontos de combo." % ability.name
	if requires.has("target_below"):
		var limit: float = requires.target_below
		if unit == null or not unit.alive() or unit.current_hp() > unit.maximum_hp() * limit:
			return "%s só funciona contra inimigos com menos de %d%% de vida." % [ability.name, roundi(limit * 100)]
	return ""


func use_ability(ability_id: String) -> bool:
	var ability := HeroStats.ability(ability_id)
	if not hero.alive() or gcd_left > 0:
		return false
	var problem := _readiness_problem(ability, ability_id)
	if not problem.is_empty():
		return _refuse(problem)
	var unit: Unit = null
	if ability.get("target", "enemy") == "enemy":
		var reach := CombatRules.ability_range(ability)
		unit = _enemy_target(reach)
		problem = _target_problem(ability, unit, reach)
	if problem.is_empty():
		problem = _requirements_problem(ability, unit)
	if not problem.is_empty():
		return _refuse(problem)
	if unit != null:
		set_target(unit)
		if is_melee_class():
			auto_attack = true
	gcd_left = CombatRules.ENERGY_GCD if HeroStats.resource_id() == "energia" else CombatRules.GCD
	var time := CombatRules.cast_time(ability_id)
	if time > 0:
		cast = {"ability": ability, "left": time, "total": time, "channel": CombatRules.is_channeled(ability_id),
				"pulses": 0, "target": unit}
		if cast.channel:
			_pay(ability)
	else:
		_resolve(ability, unit, true)
	return true


## Conhecida, sem controle no herói, sem outra conjuração, fora de recarga e com recurso.
func _readiness_problem(ability: Dictionary, ability_id: String) -> String:
	if ability.is_empty() or not HeroStats.knows(ability_id):
		return "Você ainda não conhece essa habilidade."
	if not hero.incapacitated().is_empty():
		return "Você não consegue agir agora!"
	if not cast.is_empty():
		return "Você já está conjurando."
	if cooldowns.has(ability_id):
		return "%s ainda não está pronta." % ability.name
	if Game.resource < HeroStats.ability_cost(ability):
		return "%s insuficiente." % HeroStats.resource_name()
	return ""


## Alvo válido e ao alcance (golpes corpo a corpo fora de alcance fazem o herói ir até lá).
func _target_problem(ability: Dictionary, unit: Unit, reach: int) -> String:
	if unit == null:
		return "Você não tem um alvo."
	if not in_range(unit, reach):
		if CombatRules.is_melee(ability):
			world.approach(unit)
		return "Fora de alcance."
	if ability.get("requires", {}).get("first_round", false) and in_range(unit, 1):
		return "Perto demais para avançar."
	return ""


## O alvo atual, se servir; senão, o inimigo mais perto que esteja ao alcance (como no WoW).
func _enemy_target(reach: int) -> Unit:
	if target != null and is_instance_valid(target) and target.alive() and target.state != "evade":
		return target
	var best: Unit = null
	for monster: Node in world.spawner.alive_monsters():
		if monster.state == "evade" or not in_range(monster, maxi(reach, CombatRules.MELEE_RANGE)):
			continue
		if best == null or CombatRules.tile_distance(hero.cell, monster.cell) \
				< CombatRules.tile_distance(hero.cell, best.cell):
			best = monster
	return best


func _pay(ability: Dictionary) -> void:
	Game.resource = maxi(0, Game.resource - HeroStats.ability_cost(ability))
	var cooldown := HeroStats.ability_cooldown(ability)
	if cooldown > 0:
		cooldowns[ability.id] = cooldown


func _advance_cast(delta: float) -> void:
	if not hero.incapacitated().is_empty():
		cancel_cast("Interrompido!")
		return
	var unit: Unit = cast.target
	if unit != null and (not is_instance_valid(unit) or not unit.alive()):
		cancel_cast("")
		return
	cast.left -= delta
	var ability: Dictionary = cast.ability
	if cast.channel:
		var hits := _channel_hits(ability)
		var due := mini(hits, int((1.0 - cast.left / cast.total) * hits + 0.0001))
		while cast.pulses < due:
			cast.pulses += 1
			_channel_pulse(ability, unit, cast.pulses == 1)
		if cast.left <= 0:
			cast = {}
		return
	if cast.left <= 0:
		cast = {}
		if Game.resource < HeroStats.ability_cost(ability):
			_refuse("%s insuficiente." % HeroStats.resource_name())
			return
		_resolve(ability, unit, true)


func cancel_cast(reason: String) -> void:
	if cast.is_empty():
		return
	cast = {}
	if reason:
		floating.emit(hero.head_position(), reason, MISS_COLOR, 9)


## Andar interrompe conjurações (como no WoW).
func on_hero_moved() -> void:
	if not cast.is_empty():
		cancel_cast("Interrompido")


func _channel_hits(ability: Dictionary) -> int:
	for spec: Dictionary in ability.get("effects", []):
		if spec.type == "damage":
			return int(spec.get("hits", 1))
	return 1


## Um pulso de uma magia canalizada: um dos "hits" do dano (e os outros efeitos no primeiro).
func _channel_pulse(ability: Dictionary, unit: Unit, first: bool) -> void:
	if unit == null or not unit.alive():
		return
	_hits = {}
	for spec: Dictionary in ability.get("effects", []):
		if spec.type == "damage":
			var single := spec.duplicate()
			single["hits"] = 1
			_apply_spec(single, ability, [unit])
		elif first:
			_apply_spec(spec, ability, [unit])
	_engage(unit)


func _resolve(ability: Dictionary, unit: Unit, pay: bool) -> void:
	if pay:
		_pay(ability)
	var mode: String = ability.get("target", "enemy")
	var targets: Array = []
	if mode == "self":
		targets = [hero]
	elif mode == "all_enemies":
		var reach := CombatRules.ability_range(ability)
		for monster: Node in world.spawner.alive_monsters():
			if monster.state != "evade" and in_range(monster, reach):
				targets.append(monster)
	elif unit != null:
		targets = [unit]
	floating.emit(hero.head_position() - Vector2(0, 8), ability.name, SPECIAL_COLOR, 8)
	if ability.get("requires", {}).get("first_round", false) and unit != null:
		world.charge_to(unit)
	_hits = {}
	for spec: Dictionary in ability.get("effects", []):
		_apply_spec(spec, ability, targets)
	for monster: Unit in targets:
		if monster != hero and monster.alive():
			_engage(monster)


func _power(spec: Dictionary) -> float:
	var base: Array = spec.get("base", [0, 0])
	var value := rng.randf_range(float(base[0]), float(base[1]))
	match spec.get("scale", ""):
		"weapon":
			value += weapon_roll(false) * float(spec.get("weapon_mult", 1.0))
		"ap":
			value += HeroStats.attack_power() * float(spec.get("coef", 0.0))
		"sp":
			value += HeroStats.spell_power() * float(spec.get("coef", 0.0))
	return value


## Um golpe de arma: o dano da arma mais o poder de ataque no ritmo dela (fórmula do WoW).
func weapon_roll(offhand: bool) -> float:
	var weapon := HeroStats.weapon("secundaria" if offhand else "arma")
	var low := 1.0
	var high := 3.0
	if not weapon.is_empty():
		low = float(weapon.damage[0])
		high = float(weapon.damage[1])
	return rng.randf_range(low, high) + HeroStats.attack_power() / 14.0 * CombatRules.weapon_speed(weapon)


## Efeitos das habilidades do herói (os mesmos tipos de rpg/combat.py, em segundos).
func _apply_spec(spec: Dictionary, ability: Dictionary, targets: Array) -> void:
	var kind: String = spec.type
	var element: String = spec.get("element", ability.get("element", "fisico"))
	var spell := element != "fisico"
	var label: String = ability.name
	var enemies: Array = targets.filter(func(unit: Unit) -> bool: return unit != hero)
	var bonus := HeroStats.damage_bonus(element, ability.id)
	match kind:
		"damage":
			for unit: Unit in enemies:
				for hit in int(spec.get("hits", 1)):
					if not unit.alive():
						break
					var dealt := hero_hit(unit, _power(spec) * bonus, element, spell, label)
					_hits[unit] = _hits.get(unit, false) or dealt >= 0
		"finisher":
			if not enemies.is_empty():
				var amount := 0.0
				for point in combo:
					amount += _power(spec)
				if hero_hit(enemies[0], amount * bonus, element, spell, label) >= 0:
					combo = 0
		"execute":
			if not enemies.is_empty():
				var extra := Game.resource
				Game.resource = 0
				var base: Array = spec.base
				hero_hit(enemies[0], (rng.randf_range(base[0], base[1]) + extra * float(spec.get("per_rage", 0))) * bonus,
						element, spell, label)
		"dot":
			for unit: Unit in enemies:
				if unit.alive() and _landed(unit, spell):
					var amount := _power(spec) * bonus * CombatRules.element_multiplier(element, unit.weaknesses,
							unit.resistances, unit.immunities)
					unit.add_effect({"id": spec.id, "name": spec.name, "kind": "dot", "amount": amount,
							"element": element, "left": float(spec.turns) * CombatRules.TURN + 0.05})
		"debuff":
			for unit: Unit in enemies:
				if unit.alive() and _landed(unit, spell):
					unit.add_effect({"id": spec.id, "name": spec.name, "kind": "debuff", "stat": spec.stat,
							"amount": float(spec.value), "left": CombatRules.effect_seconds(spec.turns, "debuff", false)})
		"stun", "freeze", "fear":
			for unit: Unit in enemies:
				if not (unit.alive() and _landed(unit, spell)):
					continue
				if unit.boss:
					floating.emit(unit.head_position(), "Imune", MISS_COLOR, 8)
					continue
				var seconds := CombatRules.effect_seconds(spec.turns, kind, false)
				unit.add_effect({"id": kind, "name": spec.get("name", kind), "kind": kind, "left": seconds})
				floating.emit(unit.head_position(), {"stun": "Atordoado", "freeze": "Congelado", "fear": "Apavorado"}[kind],
						SEAL_COLOR, 8)
		"interrupt":
			for unit: Unit in enemies:
				if not (unit.alive() and _landed(unit, spell)):
					continue
				if not unit.charging.is_empty():
					floating.emit(unit.head_position(), "Interrompido!", CRIT_COLOR, 10)
					unit.charging = {}
					if not unit.boss:
						unit.add_effect({"id": "stun", "name": "Atordoado", "kind": "stun",
								"left": CombatRules.CC_TURN_ON_MONSTER})
		"combo":
			if _hits.values().any(func(landed: bool) -> bool: return landed):
				combo = mini(CombatRules.MAX_COMBO, combo + int(spec.get("value", 1)))
		"heal":
			var amount := _power(spec) * (1 + HeroStats.talent_bonus("heal_pct"))
			if rng.randf() < HeroStats.spell_crit_chance():
				amount *= CombatRules.SPELL_CRIT_MULTIPLIER
			var healed := heal(hero, amount)
			floating.emit(hero.head_position(), "+%d" % healed, HEAL_COLOR, 10)
		"hot":
			hero.add_effect({"id": spec.id, "name": spec.name, "kind": "hot",
					"left": float(spec.turns) * CombatRules.TURN + 0.05,
					"amount": _power(spec) * (1 + HeroStats.talent_bonus("heal_pct"))})
		"shield":
			hero.add_effect({"id": spec.id, "name": spec.name, "kind": "shield",
					"left": float(spec.turns) * CombatRules.TURN, "amount": _power(spec) * (1 + HeroStats.talent_bonus("shield_pct"))})
		"buff":
			hero.add_effect({"id": spec.id, "name": spec.name, "kind": "buff", "stat": spec.stat, "amount": float(spec.value),
					"left": CombatRules.effect_seconds(spec.turns, "buff", true)})
			if spec.stat == "max_hp":
				Game.hp = mini(hero.maximum_hp(), Game.hp + int(spec.value))
		"rage", "resource":
			Game.resource = mini(HeroStats.max_resource(), Game.resource + int(spec.value))
		"stealth":
			hero.add_effect({"id": "furtividade", "name": "Furtividade", "kind": "stealth", "left": 8.0})
			crit_next = true
			auto_attack = false
			for monster: Node in _engaged_monsters():
				monster.evade()
			floating.emit(hero.head_position(), "Furtividade", SPECIAL_COLOR, 9)
		_:
			push_error("Efeito de habilidade desconhecido: %s" % kind)
	Game.changed.emit()


## Efeitos que acompanham um golpe só pegam se ele acertou; sozinhos, testam o acerto.
func _landed(unit: Unit, spell: bool) -> bool:
	if not _hits.has(unit):
		_hits[unit] = _roll_hit(unit, spell)
		if not _hits[unit]:
			floating.emit(unit.head_position(), "Resistiu" if spell else "Esquivou", MISS_COLOR, 8)
	return _hits[unit]


func _roll_hit(unit: Unit, spell: bool) -> bool:
	var chance := (CombatRules.SPELL_HIT_CHANCE if spell else CombatRules.HIT_CHANCE) \
			- 0.02 * maxi(0, unit.unit_level() - Game.level)
	chance += hero.modifier("hit") + HeroStats.talent_bonus("hit")
	if not spell:
		chance -= unit.dodge
	return rng.randf() < chance


# --------------------------------------------------------------------------- golpes do herói

func _auto_attack() -> void:
	if target == null or not target.alive() or target.state == "evade":
		return
	if not cast.is_empty() or not hero.incapacitated().is_empty() or hero_hidden():
		return
	if not in_range(target, CombatRules.MELEE_RANGE) or target.cell == hero.cell:
		# guerreiros e ladinos vão atrás do alvo sozinhos, como no RuneScape
		if is_melee_class() and not hero.moving and not world.is_walking():
			world.approach(target)
		return
	if swing_left <= 0:
		swing_left = CombatRules.weapon_speed(HeroStats.weapon("arma"))
		_swing(false)
	var offhand := HeroStats.weapon("secundaria")
	if not offhand.is_empty() and offhand_left <= 0 and target != null and target.alive():
		offhand_left = CombatRules.weapon_speed(offhand)
		_swing(true)


func _swing(offhand: bool) -> void:
	if not hero.moving:
		hero.face(world.facing_for(target.cell - hero.cell))
	var amount := weapon_roll(offhand) * HeroStats.damage_bonus("fisico")
	if offhand:
		amount *= CombatRules.OFFHAND_FACTOR * (1 + HeroStats.talent_bonus("offhand_pct"))
	var dealt := hero_hit(target, amount, "fisico", false, "")
	_rage_from_damage(dealt, true)


## Resolve um golpe do herói. Devolve o dano causado, ou -1 se errou.
func hero_hit(unit: Unit, amount: float, element: String, spell: bool, _label: String) -> int:
	if unit.state == "evade":
		floating.emit(unit.head_position(), "Evitou", MISS_COLOR, 8)
		return -1
	_engage(unit)
	if not _roll_hit(unit, spell):
		floating.emit(unit.head_position(), "Resistiu" if spell else "Errou", MISS_COLOR, 8)
		return -1
	var crit := crit_next or rng.randf() < (HeroStats.spell_crit_chance() if spell else HeroStats.crit_chance())
	crit_next = false
	hero.remove_effect("furtividade")
	if crit:
		amount *= CombatRules.SPELL_CRIT_MULTIPLIER if spell else CombatRules.CRIT_MULTIPLIER
	if element == "fisico":
		amount *= 1 - CombatRules.armor_mitigation(unit.unit_armor(), Game.level)
	amount *= maxf(0.0, 1 + hero.modifier("damage_dealt"))
	var multiplier := CombatRules.element_multiplier(element, unit.weaknesses, unit.resistances, unit.immunities)
	amount *= multiplier
	var dealt := damage(unit, amount, multiplier > 0)
	var text := str(dealt)
	if multiplier == 0:
		text = "Imune"
	elif multiplier > 1:
		text += " Fraqueza!"
	var color := CRIT_COLOR if crit else (CombatRules.element_color(element) if spell else HIT_COLOR)
	floating.emit(unit.head_position(), text + ("!" if crit else ""), color, 12 if crit else 9)
	if not unit.charging.is_empty() and multiplier > 0:
		_break_lock(unit, element)
	if not unit.alive():
		_on_monster_death(unit)
	return dealt


func _rage_from_damage(amount: int, dealing: bool) -> void:
	if amount <= 0 or HeroStats.resource_id() != "raiva":
		return
	var factor := (9.0 if dealing else 2.5) * (1 + HeroStats.talent_bonus("rage_pct")) * CombatRules.RAGE_GAIN_SCALE
	_resource_fraction += factor * amount / CombatRules.rage_factor(Game.level)
	var whole := int(_resource_fraction)
	_resource_fraction -= whole
	Game.resource = mini(HeroStats.max_resource(), Game.resource + whole)


# --------------------------------------------------------------------------- dano, cura e efeitos

## Aplica dano (escudos absorvem antes). Golpes diretos acordam quem está apavorado e
## podem quebrar o gelo.
func damage(unit: Unit, amount: float, direct: bool = true) -> int:
	var dealt := maxi(1, roundi(amount)) if amount > 0 else 0
	for effect: Dictionary in unit.effects.duplicate():
		if effect.kind != "shield" or dealt <= 0:
			continue
		var absorbed := mini(int(effect.amount), dealt)
		effect.amount -= absorbed
		dealt -= absorbed
		if absorbed:
			floating.emit(unit.head_position() + Vector2(0, 6), "Absorvido %d" % absorbed, SEAL_COLOR, 8)
		if effect.amount < 1:
			unit.remove_effect(effect.id)
	unit.set_current_hp(unit.current_hp() - dealt)
	if direct and dealt > 0 and unit.alive():
		for effect: Dictionary in unit.effects.duplicate():
			if effect.kind == "fear" or (effect.kind == "freeze" and rng.randf() < 0.5):
				unit.remove_effect(effect.id)
	if unit == hero:
		Game.changed.emit()
		if not hero.alive():
			_on_hero_death()
	return dealt


func heal(unit: Unit, amount: float) -> int:
	var before := unit.current_hp()
	unit.set_current_hp(mini(unit.maximum_hp(), before + roundi(amount)))
	if unit == hero:
		Game.changed.emit()
	return unit.current_hp() - before


## Pulsos dos efeitos periódicos (a cada TURN segundos) e fim dos efeitos.
func _tick_effects(unit: Unit, delta: float) -> void:
	for effect: Dictionary in unit.effects.duplicate():
		effect.left -= delta
		if effect.kind == "dot" or effect.kind == "hot":
			effect.tick -= delta
			if effect.tick <= 0:
				effect.tick += CombatRules.TURN
				if effect.kind == "dot":
					var dealt := damage(unit, effect.amount, false)
					floating.emit(unit.head_position(), str(dealt), HURT_COLOR if unit == hero
							else CombatRules.element_color(effect.get("element", "fisico")), 8)
					if unit != hero and not unit.alive():
						_on_monster_death(unit)
						return
					if not unit.alive():
						return
				else:
					floating.emit(unit.head_position(), "+%d" % heal(unit, effect.amount), HEAL_COLOR, 8)
		if effect.left <= 0:
			unit.remove_effect(effect.id)
			if effect.get("stat", "") == "max_hp" and unit == hero:
				Game.hp = mini(Game.hp, hero.maximum_hp())


## Mana, Raiva e Energia; fora de combate, a vida e a mana voltam depressa (como depois de
## comer e beber no WoW).
func _regenerate(delta: float) -> void:
	var fighting := in_combat()
	var maximum := HeroStats.max_resource()
	var gain := 0.0
	match HeroStats.resource_id():
		"energia":
			gain = CombatRules.ENERGY_PER_SECOND * delta
		"mana":
			gain = HeroStats.mana_regen() * delta
			if not fighting:
				gain = maxf(gain, maximum * CombatRules.REST_MANA_RATE * delta)
		"raiva":
			if not fighting:
				gain = -CombatRules.RAGE_DECAY * delta
	_resource_fraction += gain
	var whole := int(_resource_fraction)
	if whole != 0:
		_resource_fraction -= whole
		Game.resource = clampi(Game.resource + whole, 0, maximum)
	if not fighting and Game.hp < hero.maximum_hp():
		_hp_fraction += hero.maximum_hp() * (CombatRules.REST_HP_RATE + HeroStats.stat("espirito") / 25000.0) * delta
		var healed := int(_hp_fraction)
		if healed:
			_hp_fraction -= healed
			Game.hp = mini(hero.maximum_hp(), Game.hp + healed)
			Game.changed.emit()


# --------------------------------------------------------------------------- criaturas

func on_monster_engaged(monster: Node) -> void:
	combat_left = CombatRules.COMBAT_TIMEOUT
	if target == null:
		set_target(monster)
	world.spawner.announce(monster)


func on_monster_evaded(monster: Node) -> void:
	floating.emit(monster.head_position(), "Evitou", MISS_COLOR, 8)
	if target == monster:
		auto_attack = false


func _nearest_engaged() -> Node:
	var best: Node = null
	for monster: Node in _engaged_monsters():
		if best == null or _closer(monster, best):
			best = monster
	return best


func _engage(unit: Unit) -> void:
	combat_left = CombatRules.COMBAT_TIMEOUT
	if unit != hero and unit.state == "idle":
		unit.engage()


## Revide automático (RuneScape): atacado sem alvo (ou pelo próprio alvo), o herói devolve.
func _auto_retaliate(monster: Node) -> void:
	if target == null or not is_instance_valid(target) or not target.alive():
		set_target(monster)
		auto_attack = true
	elif target == monster:
		auto_attack = true


## A vez da criatura: golpe especial (às vezes concentrado, com selos) ou ataque comum.
func monster_act(monster: Node) -> void:
	for ability: Dictionary in monster.abilities:
		var limit: float = ability.get("hp_below", 0.0)
		if limit and not monster.used_once.has(ability.id) and monster.hp <= monster.max_hp * limit:
			monster.used_once[ability.id] = true
			monster_ability(monster, ability)
			return
	for ability: Dictionary in monster.abilities:
		if ability.get("hp_below") or monster.cooldowns.has(ability.id):
			continue
		if rng.randf() >= float(ability.get("chance", 0)):
			continue
		monster.cooldowns[ability.id] = float(ability.get("cooldown", 0)) * CombatRules.TURN + CombatRules.MONSTER_SWING
		if ability.get("charge"):
			var locks: Array = ability.get("locks", [])
			var broken: Array = []
			broken.resize(locks.size())
			broken.fill(false)
			var total := float(ability.charge) * CombatRules.TURN
			monster.charging = {"ability": ability, "left": total, "total": total, "locks": locks, "broken": broken}
			floating.emit(monster.head_position() - Vector2(0, 10), "Concentra %s!" % ability.name, SPECIAL_COLOR, 9)
			return
		monster_ability(monster, ability)
		return
	monster_attack(monster)


func finish_charge(monster: Node) -> void:
	var charge: Dictionary = monster.charging
	monster.charging = {}
	var broken: int = charge.broken.count(true)
	var power := 1.0
	if not charge.locks.is_empty():
		power = 1.0 - 0.75 * broken / float(charge.locks.size())
	if broken:
		floating.emit(monster.head_position() - Vector2(0, 10), "Enfraquecido!", SEAL_COLOR, 9)
	monster_ability(monster, charge.ability, power)


func _break_lock(monster: Node, element: String) -> void:
	var charge: Dictionary = monster.charging
	for index in charge.locks.size():
		if not charge.broken[index] and charge.locks[index] == element:
			charge.broken[index] = true
			floating.emit(monster.head_position() - Vector2(0, 10), "Selo de %s rompido!" % CombatRules.element_name(element),
					SEAL_COLOR, 9)
			if not charge.broken.has(false):
				monster.charging = {}
				floating.emit(monster.head_position() - Vector2(0, 18), "Concentração perdida!", CRIT_COLOR, 10)
				monster.add_effect({"id": "stun", "name": "Atordoado", "kind": "stun",
						"left": CombatRules.CC_TURN_ON_MONSTER})
			return


## Golpe comum de uma criatura (ou o dano de um golpe especial). Devolve o dano, ou -1.
func monster_attack(monster: Node, multiplier: float = 1.0, element: String = "", label: String = "") -> int:
	if not hero.alive():
		return -1
	if element.is_empty():
		element = monster.element
	if hero_hidden():
		return -1
	_auto_retaliate(monster)
	var chance: float = CombatRules.MONSTER_HIT_CHANCE + 0.02 * maxi(0, monster.level - Game.level) \
			+ monster.modifier("hit") - minf(0.75, HeroStats.dodge() + hero.modifier("dodge"))
	if rng.randf() >= chance:
		floating.emit(hero.head_position(), "Esquiva", MISS_COLOR, 8)
		return -1
	var amount: float = rng.randf_range(monster.damage.x, monster.damage.y) * multiplier \
			* maxf(0.0, 1 + monster.modifier("damage_dealt"))
	var crit := rng.randf() < CombatRules.MONSTER_CRIT_CHANCE
	if crit:
		amount *= CombatRules.MONSTER_CRIT_MULTIPLIER
	if element == "fisico":
		amount *= 1 - CombatRules.armor_mitigation(hero.unit_armor(), monster.level)
	amount *= maxf(0.0, 1 + hero.modifier("damage_taken"))
	var dealt := damage(hero, amount, true)
	floating.emit(hero.head_position(), ("%s %d" % [label, dealt]) if label else "-%d" % dealt, HURT_COLOR,
			11 if crit else 9)
	_rage_from_damage(dealt, false)
	return dealt


## Golpe especial de uma criatura (power < 1 quando selos foram rompidos).
func monster_ability(monster: Node, ability: Dictionary, power: float = 1.0) -> void:
	if ability.has("summon"):
		floating.emit(monster.head_position() - Vector2(0, 10), ability.name, SPECIAL_COLOR, 9)
		world.spawner.summon(monster, ability.summon)
		return
	var landed := true
	if ability.has("damage"):
		landed = monster_attack(monster, float(ability.damage) * power, ability.get("element", ""), ability.name) >= 0
	else:
		floating.emit(monster.head_position() - Vector2(0, 10), ability.name, SPECIAL_COLOR, 9)
	var full := power >= 0.999
	for spec: Dictionary in ability.get("effects", []):
		var kind: String = spec.type
		if kind == "heal_self":
			var healed := heal(monster, monster.max_hp * float(spec.value) * power)
			floating.emit(monster.head_position(), "+%d" % healed, HEAL_COLOR, 9)
		elif kind == "buff_self":
			if full:
				monster.add_effect({"id": spec.id, "name": spec.name, "kind": "buff", "stat": spec.stat,
						"amount": float(spec.value), "left": CombatRules.effect_seconds(spec.turns, "buff", false)})
		elif not (landed and full and hero.alive()):
			continue
		elif kind == "dot":
			var per_tick: float = (monster.damage.x + monster.damage.y) / 2.0 * float(spec.power)
			hero.add_effect({"id": spec.id, "name": spec.name, "kind": "dot", "amount": per_tick,
					"element": spec.get("element", "fisico"), "left": float(spec.turns) * CombatRules.TURN + 0.05})
		elif kind in ["stun", "freeze", "fear"]:
			hero.add_effect({"id": kind, "name": spec.get("name", kind), "kind": kind,
					"left": CombatRules.effect_seconds(spec.turns, kind, true)})
			cancel_cast("")
			floating.emit(hero.head_position() - Vector2(0, 8), spec.get("name", kind), HURT_COLOR, 9)
		elif kind == "debuff":
			hero.add_effect({"id": spec.id, "name": spec.name, "kind": "debuff", "stat": spec.stat,
					"amount": float(spec.value), "left": CombatRules.effect_seconds(spec.turns, "debuff", true)})
			floating.emit(hero.head_position() - Vector2(0, 8), spec.name, HURT_COLOR, 8)
		elif kind == "drain_mana":
			if HeroStats.resource_id() == "mana":
				var drained := mini(Game.resource, int(HeroStats.max_resource() * float(spec.value)))
				Game.resource -= drained
				floating.emit(hero.head_position() - Vector2(0, 8), "-%d mana" % drained, Color(0.5, 0.6, 1.0), 8)
		else:
			push_error("Efeito de criatura desconhecido: %s" % kind)
	Game.changed.emit()


# --------------------------------------------------------------------------- itens

## Poções, comidas e frascos de arremesso (com uma recarga compartilhada).
func use_item(item_id: String) -> bool:
	var item := Data.item(item_id)
	var use: Dictionary = item.get("use", {})
	if Game.count_item(item_id) <= 0:
		return _refuse("Você não tem %s." % Data.item_name(item_id))
	if use.is_empty():
		return _refuse("%s não pode ser usado." % item.get("name", item_id))
	if not hero.alive() or not hero.incapacitated().is_empty():
		return _refuse("Você não consegue agir agora!")
	if in_combat() and not use.get("combat", true):
		return _refuse("Não dá para usar %s no meio da luta!" % item.name)
	if item_left > 0:
		return _refuse("Ainda não.")
	var unit: Unit = null
	if use.has("damage"):
		unit = _enemy_target(CombatRules.THROW_RANGE)
		if unit == null or not in_range(unit, CombatRules.THROW_RANGE):
			return _refuse("Você não tem um alvo ao alcance.")
	elif use.get("combat_only", false):
		return _refuse("%s só serve no meio de uma luta." % item.name)
	item_left = CombatRules.ITEM_COOLDOWN
	Game.take_item(item_id)
	if unit != null:
		set_target(unit)
		var low: float = use.damage[0]
		var high: float = use.damage[1]
		hero_hit(unit, rng.randf_range(low, high), use.get("element", "fisico"), true, item.name)
		return true
	var healed := 0
	var amount := float(hero.maximum_hp()) * float(use.get("heal_pct", 0)) / 100.0
	if use.has("heal"):
		amount += rng.randi_range(int(use.heal[0]), int(use.heal[1]))
	if amount > 0:
		healed = heal(hero, amount)
		floating.emit(hero.head_position(), "+%d" % healed, HEAL_COLOR, 10)
	if HeroStats.resource_id() == "mana":
		var mana := float(HeroStats.max_resource()) * float(use.get("mana_pct", 0)) / 100.0
		if use.has("mana"):
			mana += rng.randi_range(int(use.mana[0]), int(use.mana[1]))
		if mana > 0:
			var before := Game.resource
			Game.resource = mini(HeroStats.max_resource(), Game.resource + roundi(mana))
			floating.emit(hero.head_position() + Vector2(0, 8), "+%d mana" % (Game.resource - before), Color(0.5, 0.7, 1.0), 9)
	Game.changed.emit()
	return true


func _refuse(text: String) -> bool:
	error.emit(text)
	return false


# --------------------------------------------------------------------------- vitória e derrota

func _on_monster_death(monster: Node) -> void:
	if monster.state == "dead":
		return
	monster.die()
	if target == monster:
		set_target(null)
		# o próximo da luta vira o alvo, e o herói continua batendo (como o revide do RuneScape)
		var next := _nearest_engaged()
		if next != null:
			set_target(next)
			auto_attack = true
	combo = 0
	var xp := CombatRules.kill_xp(Game.level, monster.level, monster.elite)
	if xp:
		floating.emit(hero.head_position() - Vector2(0, 10), "+%d XP" % xp, SPECIAL_COLOR, 9)
		Game.gain_xp(xp)
	var loot := CombatRules.roll_loot(monster.data, rng)
	for pair: Array in loot.items:
		Game.give_item(pair[0], int(pair[1]))
	if loot.copper:
		Game.give_copper(loot.copper)
	Game.record_kill(monster.template_id)
	world.spawner.on_monster_died(monster)
	Story.update_quests()


func _on_hero_death() -> void:
	auto_attack = false
	cast = {}
	set_target(null)
	hero.effects.clear()
	for monster: Node in _engaged_monsters():
		monster.evade()
	hero_died.emit()


## Depois de cair: perde 10% do cobre e acorda na Capela da Aurora com metade da vida.
func revive() -> int:
	var lost := Game.copper / 10
	Game.copper -= lost
	Game.hp = maxi(1, hero.maximum_hp() / 2)
	Game.resource = HeroStats.max_resource() / 2 if HeroStats.starts_full() else 0
	combat_left = 0.0
	combo = 0
	cooldowns.clear()
	Game.changed.emit()
	return lost


## Ao trocar de mapa: sem alvo, sem conjuração, fora de combate.
func reset() -> void:
	auto_attack = false
	cast = {}
	target = null
	combat_left = 0.0
	target_changed.emit()
