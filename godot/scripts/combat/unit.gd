class_name Unit
extends Node2D
## Quem luta: o herói e as criaturas. Guarda o tile e os efeitos ativos (sangramentos, curas
## contínuas, escudos, bônus, penalidades, atordoamentos), que contam em segundos.
## Quem aplica dano, cura e efeitos é o combate (scripts/combat/combat.gd).

## Efeito: {id, name, kind, left (segundos), amount, stat, element, tick (segundos até o
## próximo pulso)}. kind: dot, hot, shield, buff, debuff, stun, freeze, fear ou stealth.
var effects: Array = []
var cell := Vector2i.ZERO


# --------------------------------------------------------------------------- a implementar

func unit_name() -> String:
	return name


func is_hero() -> bool:
	return false


func current_hp() -> int:
	return 0


func set_current_hp(_value: int) -> void:
	pass


func maximum_hp() -> int:
	return 1


func unit_level() -> int:
	return 1


func unit_armor() -> float:
	return 0.0


## Onde mostrar os números de dano (acima da cabeça).
func head_position() -> Vector2:
	return global_position - Vector2(0, 20)


# --------------------------------------------------------------------------- efeitos

func alive() -> bool:
	return current_hp() > 0


func modifier(stat: String) -> float:
	var total := 0.0
	for effect: Dictionary in effects:
		if effect.get("stat", "") == stat:
			total += float(effect.amount)
	return total


func find_effect(effect_id: String) -> Dictionary:
	for effect: Dictionary in effects:
		if effect.id == effect_id:
			return effect
	return {}


## Aplica um efeito; o mesmo efeito de novo substitui o antigo (renova a duração).
func add_effect(effect: Dictionary) -> void:
	remove_effect(effect.id)
	effect["tick"] = CombatRules.TURN
	effects.append(effect)


func remove_effect(effect_id: String) -> void:
	for index in range(effects.size() - 1, -1, -1):
		if effects[index].id == effect_id:
			effects.remove_at(index)


func has_kind(kind: String) -> bool:
	for effect: Dictionary in effects:
		if effect.kind == kind:
			return true
	return false


## Atordoado, congelado ou apavorado (não age).
func incapacitated() -> String:
	for effect: Dictionary in effects:
		if effect.kind in ["stun", "freeze", "fear"]:
			return effect.kind
	return ""
