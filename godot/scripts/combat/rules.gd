class_name CombatRules
extends RefCounted
## As regras do combate em tempo real, no estilo do WoW Classic e do RuneScape.
##
## São as fórmulas de rpg/combat.py e rpg/monsters.py (armadura, acerto, crítico, Raiva, XP
## por abate, saque), só que contadas em segundos. Cada "turno" dos dados vale TURN segundos:
## recargas, efeitos periódicos (que pulsam a cada TURN) e bônus mantêm as proporções do
## terminal. Atordoamentos e outros controles valem menos por turno, para não travar a ação.

const TURN := 3.0                 # segundos por turno dos dados
const LONG_BUFF_TURN := 12.0      # bônus em si mesmo de 5+ turnos duram mais (Brado, Armadura de Gelo...)
const LONG_BUFF_TURNS := 5
const CC_TURN_ON_MONSTER := 2.0   # atordoar, congelar e apavorar criaturas
const CC_TURN_ON_HERO := 1.5      # o mesmo, no herói
const GCD := 1.5                  # recarga global, como no WoW
const ENERGY_GCD := 1.0           # ladinos têm a recarga global mais curta
const MONSTER_SWING := 2.0        # um golpe das criaturas a cada 2 segundos
const MONSTER_HP_SCALE := 1.6        # em tempo real o herói age mais vezes que no terminal
const ELITE_HP_SCALE := 1.2          # chefes já têm muita vida
const MONSTER_DAMAGE_SCALE := 1.25
const ELITE_DAMAGE_SCALE := 1.0      # chefes já batem forte com os golpes concentrados
const SUMMON_SCALE := 1.0            # reforços chamados no meio da luta: vida e dano do terminal
const RAGE_GAIN_SCALE := 1.3         # em tempo real a Raiva precisa render um pouco mais
const UNARMED_SPEED := 2.0
const ITEM_COOLDOWN := 8.0        # poções, frascos e comidas
const COMBAT_TIMEOUT := 5.0       # segundos sem trocar golpes para sair de combate
const ENERGY_PER_SECOND := 10.0   # 20 a cada 2 segundos
const RAGE_DECAY := 2.0           # por segundo, fora de combate
const REST_HP_RATE := 0.03        # fração da vida recuperada por segundo fora de combate
const REST_MANA_RATE := 0.03
const XP_RATE := 2.0

const MELEE_RANGE := 1            # tiles (vizinhos, inclusive nas diagonais)
const SPELL_RANGE := 7
const THROW_RANGE := 5
const AOE_MELEE := 2
const AOE_SPELL := 3
const CHARGE_RANGE := 7           # Investida

const HIT_CHANCE := 0.95
const SPELL_HIT_CHANCE := 0.96
const MONSTER_HIT_CHANCE := 0.93
const CRIT_MULTIPLIER := 2.0
const SPELL_CRIT_MULTIPLIER := 1.5
const MONSTER_CRIT_CHANCE := 0.05
const MONSTER_CRIT_MULTIPLIER := 1.5
const WEAKNESS_MULTIPLIER := 1.5
const RESISTANCE_MULTIPLIER := 0.5
const OFFHAND_FACTOR := 0.5
const MAX_COMBO := 5

const ELEMENTS := {
	"fisico": {"name": "Físico", "color": "#f2f2f2"}, "fogo": {"name": "Fogo", "color": "#ff7a4a"},
	"gelo": {"name": "Gelo", "color": "#8fe0ff"}, "arcano": {"name": "Arcano", "color": "#e08fff"},
	"sagrado": {"name": "Sagrado", "color": "#ffe27a"}, "sombra": {"name": "Sombra", "color": "#b05fc8"},
	"natureza": {"name": "Natureza", "color": "#8fe07f"},
}

## Magias com tempo de conjuração (segundos); as outras habilidades são instantâneas.
const CAST_TIMES := {
	"bola_de_fogo": 2.0, "seta_de_gelo": 1.8, "pirolancamento": 3.0, "lanca_gelo": 1.5,
	"punicao": 1.8, "cura_menor": 1.8, "fogo_sagrado": 2.2,
}
## Magias canalizadas: os "hits" dos dados saem em pulsos durante a canalização.
const CHANNELED := {"misseis_arcanos": 2.4, "acoite_mental": 2.4}

## Segundos entre golpes, por tipo de arma.
const WEAPON_SPEED := {"adaga": 1.7, "espada": 2.4, "maca": 2.6, "machado": 2.7, "cajado": 2.9}


static func element_name(element: String) -> String:
	return ELEMENTS.get(element, ELEMENTS.fisico).name


static func element_color(element: String) -> Color:
	return Color(ELEMENTS.get(element, ELEMENTS.fisico).color)


## Multiplicador de dano de um elemento contra um alvo: imunidade anula, fraqueza aumenta,
## resistência reduz (fraqueza e resistência ao mesmo elemento se cancelam).
static func element_multiplier(element: String, weaknesses: Array, resistances: Array,
		immunities: Array = []) -> float:
	if element in immunities:
		return 0.0
	var weak := element in weaknesses
	var resistant := element in resistances
	if weak and not resistant:
		return WEAKNESS_MULTIPLIER
	if resistant and not weak:
		return RESISTANCE_MULTIPLIER
	return 1.0


## Fração do dano físico absorvida pela armadura (fórmula do WoW Classic, até 75%).
static func armor_mitigation(armor: float, attacker_level: int) -> float:
	armor = maxf(0.0, armor)
	return minf(0.75, armor / (armor + 400 + 85 * attacker_level))


## Constante de conversão de dano em Raiva do WoW Classic.
static func rage_factor(level: int) -> float:
	return 0.0091107836 * level * level + 3.225598133 * level + 4.2652911


## Vida, dano médio por golpe e armadura de uma criatura comum do nível (rpg/monsters.py).
static func monster_curve(level: int) -> Array:
	return [38 + 15 * (level - 1), 3.8 + 1.7 * (level - 1), 15 + 22 * level]


## Quantos níveis abaixo do herói uma criatura deixa de dar experiência (tabela do WoW).
static func zero_difference(level: int) -> int:
	for pair: Array in [[7, 5], [9, 6], [11, 7], [15, 8], [19, 9], [29, 11], [39, 12], [44, 13], [49, 14],
			[54, 15], [59, 16]]:
		if level <= pair[0]:
			return pair[1]
	return 17


## XP por abate: nível × 5 + 45 contra o mesmo nível, mais 5% por nível acima, dobrada para elites.
static func kill_xp(player_level: int, monster_level: int, elite: bool = false) -> int:
	var base := player_level * 5 + 45.0
	var diff := monster_level - player_level
	var xp := 0.0
	if diff >= 0:
		xp = base * (1 + 0.05 * mini(diff, 4))
	else:
		var gap := zero_difference(player_level)
		if -diff >= gap:
			return 0
		xp = base * (1 - float(-diff) / gap)
	if elite:
		xp *= 2
	return roundi(xp * XP_RATE)


## Cor de dificuldade do WoW: cinza, verde, amarelo, laranja e vermelho.
static func con_color(player_level: int, monster_level: int) -> Color:
	var diff := monster_level - player_level
	if diff >= 5:
		return Color("#ff4a3a")
	if diff >= 3:
		return Color("#ff9a3a")
	if diff >= -2:
		return Color("#ffe27a")
	if kill_xp(player_level, monster_level) > 0:
		return Color("#7fe06a")
	return Color("#a0a0a0")


## Sorteia o saque de uma criatura: {"items": [[item, quantidade]...], "copper": n}.
static func roll_loot(template: Dictionary, rng: RandomNumberGenerator) -> Dictionary:
	var items: Array = []
	for entry: Dictionary in template.get("loot", []):
		if rng.randf() * 100 >= float(entry.get("chance", 100)):
			continue
		var item_id: String = entry.item if entry.has("item") else entry.one_of[rng.randi_range(0, entry.one_of.size() - 1)]
		var qty: Array = entry.get("qty", [1, 1])
		items.append([item_id, rng.randi_range(int(qty[0]), int(qty[1]))])
	var copper_range: Array = template.get("copper", [0, 0])
	var copper := rng.randi_range(int(copper_range[0]), int(copper_range[1])) if int(copper_range[1]) else 0
	return {"items": items, "copper": copper}


## Duração em segundos de um efeito de habilidade ("turns" nos dados).
static func effect_seconds(turns: float, kind: String, on_hero: bool) -> float:
	if kind in ["stun", "freeze", "fear"]:
		return turns * (CC_TURN_ON_HERO if on_hero else CC_TURN_ON_MONSTER)
	if kind == "buff" and on_hero and turns >= LONG_BUFF_TURNS:
		return turns * LONG_BUFF_TURN
	return turns * TURN


static func weapon_speed(weapon: Dictionary) -> float:
	if weapon.is_empty():
		return UNARMED_SPEED
	return WEAPON_SPEED.get(weapon.get("subtype", ""), 2.4)


static func cast_time(ability_id: String) -> float:
	return CAST_TIMES.get(ability_id, CHANNELED.get(ability_id, 0.0))


static func is_channeled(ability_id: String) -> bool:
	return CHANNELED.has(ability_id)


## Corpo a corpo (golpes de arma e de força) ou à distância (magias).
static func is_melee(ability: Dictionary) -> bool:
	if ability.get("element", "fisico") != "fisico":
		return false
	for spec: Dictionary in ability.get("effects", []):
		if spec.get("scale", "") == "sp":
			return false
	return true


## Alcance (em tiles) de uma habilidade contra inimigos; 0 para as que miram o próprio herói.
static func ability_range(ability: Dictionary) -> int:
	var mode: String = ability.get("target", "enemy")
	if mode == "self":
		return 0
	if mode == "all_enemies":
		return AOE_MELEE if is_melee(ability) else AOE_SPELL
	if ability.get("requires", {}).get("first_round", false):
		return CHARGE_RANGE
	return MELEE_RANGE if is_melee(ability) else SPELL_RANGE


## Distância em tiles contando as diagonais como um passo (como no RuneScape).
static func tile_distance(a: Vector2i, b: Vector2i) -> int:
	return maxi(absi(a.x - b.x), absi(a.y - b.y))
