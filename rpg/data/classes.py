"""Classes jogáveis (estilo WoW Classic): atributos, recursos, habilidades e talentos.

Atributos crescem a cada nível (``growth``); vida e recurso máximos derivam deles.
Habilidades têm nível de aprendizado, custo, recarga em turnos e elemento.
"""

STATS = {
    "forca": {"name": "Força", "short": "FOR", "description": "Poder de ataque corpo a corpo e bloqueio."},
    "agilidade": {"name": "Agilidade", "short": "AGI", "description": "Chance de crítico, esquiva e armadura."},
    "vigor": {"name": "Vigor", "short": "VIG", "description": "Pontos de vida máximos."},
    "intelecto": {"name": "Intelecto", "short": "INT", "description": "Mana máxima e chance de crítico mágico."},
    "espirito": {"name": "Espírito", "short": "ESP", "description": "Regeneração de vida e mana fora de combate."},
}

RESOURCES = {
    "mana": {
        "name": "Mana",
        "color": "bright_blue",
        "max": None,           # derivada do Intelecto e do nível
        "starts_full": True,
        "description": "Energia mística. Começa cheia e se regenera devagar, guiada pelo Espírito.",
    },
    "raiva": {
        "name": "Raiva",
        "color": "red",
        "max": 100,
        "starts_full": False,
        "description": "Nasce vazia e cresce a cada golpe dado ou recebido; esfria fora de combate.",
    },
    "energia": {
        "name": "Energia",
        "color": "bright_yellow",
        "max": 100,
        "starts_full": True,
        "description": "Fôlego explosivo: recupera 20 pontos por turno. Golpes rápidos geram pontos de combo.",
    },
}

CLASSES = {
    "guerreiro": {
        "names": {"masculino": "Guerreiro", "feminino": "Guerreira", "nao_binario": "Guerreiro"},
        "color": "yellow",
        "role": "Tanque / Dano corpo a corpo",
        "resource": "raiva",
        "difficulty": 1,
        "tagline": "Aço, escudo e uma fúria que só cresce.",
        "description": (
            "Mestres das armas e da linha de frente. Guerreiros alimentam-se do caos da batalha: "
            "cada golpe dado ou recebido acende sua Raiva, que vira golpes devastadores, gritos de "
            "guerra e a resistência de uma muralha de escudo."
        ),
        "playstyle": "Comece com Investida, acumule Raiva e gaste-a em Golpe Heroico e Dilacerar.",
        "armor": "Malha (Placas a partir do nível 40)",
        "weapons": "Espadas, machados, maças, armas de haste e escudos",
        "base_stats": {"forca": 23, "agilidade": 20, "vigor": 22, "intelecto": 17, "espirito": 18},
        "growth": {"forca": 2.2, "agilidade": 1.2, "vigor": 2.0, "intelecto": 0.2, "espirito": 0.5},
        "base_hp": 60,
        "hp_per_level": 14,
        "abilities": [
            {"id": "golpe_heroico", "name": "Golpe Heroico", "level": 1, "cost": 15, "cooldown": 0,
             "element": "fisico", "kind": "dano",
             "description": "Um golpe amplo e brutal que soma dano extra ao ataque da arma."},
            {"id": "investida", "name": "Investida", "level": 1, "cost": 0, "cooldown": 4,
             "element": "fisico", "kind": "controle",
             "description": "Abre o combate avançando contra o inimigo: gera 15 de Raiva e o atordoa por 1 turno."},
            {"id": "brado_de_batalha", "name": "Brado de Batalha", "level": 1, "cost": 10, "cooldown": 0,
             "element": "fisico", "kind": "bônus",
             "description": "Um grito de guerra que aumenta o poder de ataque por 5 turnos."},
            {"id": "dilacerar", "name": "Dilacerar", "level": 4, "cost": 10, "cooldown": 0,
             "element": "fisico", "kind": "dano",
             "description": "Abre um corte profundo que sangra por 3 turnos."},
            {"id": "trovoada", "name": "Trovoada", "level": 6, "cost": 20, "cooldown": 3,
             "element": "fisico", "kind": "dano",
             "description": "Golpeia o chão, ferindo todos os inimigos próximos e reduzindo sua velocidade."},
            {"id": "executar", "name": "Executar", "level": 8, "cost": 15, "cooldown": 0,
             "element": "fisico", "kind": "dano",
             "description": "Só contra inimigos abaixo de 20% de vida: converte toda a Raiva restante em dano."},
            {"id": "muralha_de_escudo", "name": "Muralha de Escudo", "level": 10, "cost": 0, "cooldown": 8,
             "element": "fisico", "kind": "bônus",
             "description": "Reduz em 75% o dano recebido por 2 turnos. Exige escudo."},
        ],
        "talent_trees": [
            {"name": "Armas", "description": "Armas de duas mãos, sangramentos e o temido Golpe Mortal."},
            {"name": "Fúria", "description": "Duas armas, ataques frenéticos e Raiva sem fim."},
            {"name": "Proteção", "description": "Escudo erguido: a muralha que protege os aliados."},
        ],
        "starting_equipment": {
            "arma": "espada_curta_gasta",
            "secundaria": "escudo_madeira_reforcada",
            "peito": "cota_malha_recruta",
            "pernas": "calcas_couro_cru",
            "pes": "botas_gastas",
        },
        "starting_items": [["pocao_cura_menor", 2]],
    },
    "mago": {
        "names": {"masculino": "Mago", "feminino": "Maga", "nao_binario": "Mago"},
        "color": "bright_cyan",
        "role": "Dano mágico à distância / Controle",
        "resource": "mana",
        "difficulty": 2,
        "tagline": "Fogo, gelo e os segredos do Arcano.",
        "description": (
            "Estudiosos que dobram a realidade com fórmulas antigas. Frágeis no corpo a corpo, "
            "magos compensam com dano avassalador e controle: congelam, incendeiam e bombardeiam "
            "inimigos com mísseis de energia pura."
        ),
        "playstyle": "Mantenha distância, explore fraquezas elementares e controle a Mana.",
        "armor": "Tecido",
        "weapons": "Cajados, varinhas, adagas e espadas leves",
        "base_stats": {"forca": 17, "agilidade": 17, "vigor": 18, "intelecto": 24, "espirito": 22},
        "growth": {"forca": 0.2, "agilidade": 0.3, "vigor": 0.9, "intelecto": 2.2, "espirito": 1.8},
        "base_hp": 40,
        "hp_per_level": 8,
        "base_mana": 60,
        "mana_per_level": 18,
        "abilities": [
            {"id": "bola_de_fogo", "name": "Bola de Fogo", "level": 1, "cost": 30, "cooldown": 0,
             "element": "fogo", "kind": "dano",
             "description": "Arremessa uma esfera flamejante que queima o alvo por 2 turnos."},
            {"id": "armadura_de_gelo", "name": "Armadura de Gelo", "level": 1, "cost": 20, "cooldown": 0,
             "element": "gelo", "kind": "bônus",
             "description": "Uma crosta de gelo aumenta a armadura e retarda quem atacar corpo a corpo."},
            {"id": "seta_de_gelo", "name": "Seta de Gelo", "level": 4, "cost": 25, "cooldown": 0,
             "element": "gelo", "kind": "dano",
             "description": "Projétil congelante que causa dano e reduz a velocidade do alvo."},
            {"id": "impacto_de_fogo", "name": "Impacto de Fogo", "level": 6, "cost": 40, "cooldown": 3,
             "element": "fogo", "kind": "dano",
             "description": "Explosão instantânea de chamas, perfeita para finalizar inimigos."},
            {"id": "misseis_arcanos", "name": "Mísseis Arcanos", "level": 8, "cost": 45, "cooldown": 0,
             "element": "arcano", "kind": "dano",
             "description": "Três mísseis de energia pura que nunca erram o alvo."},
            {"id": "nova_congelante", "name": "Nova Congelante", "level": 10, "cost": 35, "cooldown": 4,
             "element": "gelo", "kind": "controle",
             "description": "Congela no lugar todos os inimigos próximos por 2 turnos."},
        ],
        "talent_trees": [
            {"name": "Arcano", "description": "Mana inesgotável, mísseis e a manipulação do tempo."},
            {"name": "Fogo", "description": "Incêndios, explosões e críticos que se espalham."},
            {"name": "Gelo", "description": "Lentidão, congelamento e escudos de gelo."},
        ],
        "starting_equipment": {
            "arma": "cajado_aprendiz",
            "peito": "manto_aprendiz",
            "pernas": "calcas_linho",
            "pes": "sandalias_linho",
        },
        "starting_items": [["pocao_cura_menor", 1], ["pocao_mana_menor", 2]],
    },
    "sacerdote": {
        "names": {"masculino": "Sacerdote", "feminino": "Sacerdotisa", "nao_binario": "Sacerdote"},
        "color": "bright_white",
        "role": "Cura / Dano de Sombra",
        "resource": "mana",
        "difficulty": 2,
        "tagline": "A luz que cura e a sombra que corrói.",
        "description": (
            "Devotos da Senhora da Aurora — e, às vezes, de segredos mais escuros. Sacerdotes "
            "mantêm aliados de pé com preces e escudos de luz, mas também sabem sussurrar "
            "palavras sombrias que consomem a mente do inimigo."
        ),
        "playstyle": "Proteja-se com o Escudo, cure com sabedoria e desgaste o inimigo com Sombra.",
        "armor": "Tecido",
        "weapons": "Maças, cajados, varinhas e adagas",
        "base_stats": {"forca": 17, "agilidade": 17, "vigor": 18, "intelecto": 22, "espirito": 24},
        "growth": {"forca": 0.3, "agilidade": 0.3, "vigor": 1.0, "intelecto": 1.9, "espirito": 2.2},
        "base_hp": 45,
        "hp_per_level": 9,
        "base_mana": 60,
        "mana_per_level": 17,
        "abilities": [
            {"id": "punicao", "name": "Punição", "level": 1, "cost": 25, "cooldown": 0,
             "element": "sagrado", "kind": "dano",
             "description": "Invoca a luz da Aurora para queimar o inimigo."},
            {"id": "cura_menor", "name": "Cura Menor", "level": 1, "cost": 30, "cooldown": 0,
             "element": "sagrado", "kind": "cura",
             "description": "Uma prece curta que restaura uma pequena quantidade de vida."},
            {"id": "palavra_de_poder_fortitude", "name": "Palavra de Poder: Fortitude", "level": 1, "cost": 30,
             "cooldown": 0, "element": "sagrado", "kind": "bônus",
             "description": "Aumenta o Vigor do alvo durante todo o combate."},
            {"id": "palavra_sombria_dor", "name": "Palavra Sombria: Dor", "level": 4, "cost": 25, "cooldown": 0,
             "element": "sombra", "kind": "dano",
             "description": "Uma palavra proibida que corrói o alvo por 4 turnos."},
            {"id": "palavra_de_poder_escudo", "name": "Palavra de Poder: Escudo", "level": 6, "cost": 45,
             "cooldown": 3, "element": "sagrado", "kind": "bônus",
             "description": "Um escudo de luz que absorve dano por 3 turnos."},
            {"id": "renovar", "name": "Renovar", "level": 8, "cost": 40, "cooldown": 0,
             "element": "sagrado", "kind": "cura",
             "description": "Restaura vida no início de cada turno, por 4 turnos."},
            {"id": "grito_psiquico", "name": "Grito Psíquico", "level": 10, "cost": 50, "cooldown": 6,
             "element": "sombra", "kind": "controle",
             "description": "Aterroriza os inimigos próximos, que fogem por 2 turnos."},
        ],
        "talent_trees": [
            {"name": "Disciplina", "description": "Escudos, força de vontade e mana bem aproveitada."},
            {"name": "Sagrado", "description": "Curas poderosas e a luz que pune os mortos-vivos."},
            {"name": "Sombra", "description": "Forma de Sombra, dano contínuo e terror."},
        ],
        "starting_equipment": {
            "arma": "maca_simples",
            "peito": "vestes_novico",
            "pernas": "calcas_linho",
            "pes": "sandalias_linho",
        },
        "starting_items": [["pocao_cura_menor", 1], ["pocao_mana_menor", 2]],
    },
    "ladino": {
        "names": {"masculino": "Ladino", "feminino": "Ladina", "nao_binario": "Ladino"},
        "color": "bright_yellow",
        "role": "Dano corpo a corpo / Furtividade",
        "resource": "energia",
        "difficulty": 3,
        "tagline": "Lâminas rápidas, passos silenciosos.",
        "description": (
            "Mestres da furtividade e do golpe certeiro. Ladinos escolhem quando a luta começa: "
            "emergem das sombras, acumulam pontos de combo com ataques rápidos e encerram tudo "
            "com finalizadores letais antes que o inimigo entenda o que aconteceu."
        ),
        "playstyle": "Abra em Furtividade, gere combos com Golpe Sinistro e finalize com Eviscerar.",
        "armor": "Couro",
        "weapons": "Adagas, espadas leves, arcos e armas de arremesso",
        "base_stats": {"forca": 19, "agilidade": 24, "vigor": 20, "intelecto": 17, "espirito": 18},
        "growth": {"forca": 1.1, "agilidade": 2.3, "vigor": 1.4, "intelecto": 0.2, "espirito": 0.5},
        "base_hp": 50,
        "hp_per_level": 11,
        "abilities": [
            {"id": "golpe_sinistro", "name": "Golpe Sinistro", "level": 1, "cost": 40, "cooldown": 0,
             "element": "fisico", "kind": "dano",
             "description": "Um ataque rápido e traiçoeiro. Gera 1 ponto de combo."},
            {"id": "eviscerar", "name": "Eviscerar", "level": 1, "cost": 35, "cooldown": 0,
             "element": "fisico", "kind": "dano",
             "description": "Finalizador: consome os pontos de combo — quanto mais pontos, maior o dano."},
            {"id": "furtividade", "name": "Furtividade", "level": 1, "cost": 0, "cooldown": 3,
             "element": "sombra", "kind": "utilidade",
             "description": "Funde-se às sombras: o primeiro ataque a partir delas é sempre crítico."},
            {"id": "apunhalar", "name": "Apunhalar", "level": 4, "cost": 60, "cooldown": 0,
             "element": "fisico", "kind": "dano",
             "description": "Golpe pelas costas com adaga, de dano altíssimo. Gera 1 ponto de combo."},
            {"id": "evasao", "name": "Evasão", "level": 8, "cost": 0, "cooldown": 6,
             "element": "fisico", "kind": "bônus",
             "description": "Aumenta drasticamente a chance de esquiva por 2 turnos."},
            {"id": "chute", "name": "Chute", "level": 10, "cost": 25, "cooldown": 3,
             "element": "fisico", "kind": "controle",
             "description": "Interrompe a magia que o inimigo estiver conjurando."},
        ],
        "talent_trees": [
            {"name": "Assassinato", "description": "Venenos, críticos e finalizadores implacáveis."},
            {"name": "Combate", "description": "Duas armas, aparar golpes e a Adrenalina."},
            {"name": "Sutileza", "description": "Sombras, emboscadas e truques sujos."},
        ],
        "starting_equipment": {
            "arma": "adaga_afiada",
            "secundaria": "adaga_curva",
            "peito": "gibao_couro_batido",
            "pernas": "calcas_couro_cru",
            "pes": "botas_gastas",
        },
        "starting_items": [["pocao_cura_menor", 2]],
    },
}

#: A partir deste nível cada nível concede 1 ponto de talento (como no WoW Classic).
TALENT_START_LEVEL = 10
