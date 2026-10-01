"""Itens do jogo (fábrica em ``rpg.items``).

Campos gerais: ``name``, ``type``, ``quality``, ``description`` (texto de ambientação),
``value`` (preço de venda, em moedas de cobre) e ``stack`` (tamanho máximo da pilha).

Equipamentos: ``slot``, ``subtype`` (tipo de arma ou de armadura, que define quais
classes podem usar a peça; joias e mantos não têm), ``armor``, ``damage``, ``stats`` e
``two_handed``. ``dyeable`` indica peças que recebem a cor escolhida na criação.

Consumíveis: ``use`` descreve o efeito — ``heal``/``mana`` (faixa de valores),
``heal_pct``/``mana_pct`` (porcentagem do máximo), ``combat`` (se pode ser usado em
combate) e ``minutes`` (tempo gasto fora de combate).
"""

QUALITIES = {
    "pobre": {"name": "Pobre", "color": "gray"},
    "comum": {"name": "Comum", "color": "white"},
    "incomum": {"name": "Incomum", "color": "bright_green"},
    "raro": {"name": "Raro", "color": "bright_blue"},
    "epico": {"name": "Épico", "color": "bright_magenta"},
    "lendario": {"name": "Lendário", "color": "yellow bold"},
}

SLOTS = {
    "cabeca": "Cabeça",
    "pescoco": "Pescoço",
    "ombros": "Ombros",
    "costas": "Costas",
    "peito": "Peito",
    "maos": "Mãos",
    "cintura": "Cintura",
    "pernas": "Pernas",
    "pes": "Pés",
    "anel": "Anel",
    "arma": "Mão principal",
    "secundaria": "Mão secundária",
}

ITEM_TYPES = {
    "arma": "Arma",
    "escudo": "Escudo",
    "armadura": "Armadura",
    "joia": "Joia",
    "consumivel": "Consumível",
    "material": "Material",
    "lixo": "Sucata",
    "missao": "Item de missão",
    "diverso": "Diverso",
}

#: Tipos de arma e de armadura (``subtype``), com o nome exibido.
SUBTYPES = {
    "espada": "Espada", "machado": "Machado", "maca": "Maça", "adaga": "Adaga", "cajado": "Cajado",
    "escudo": "Escudo", "tecido": "Tecido", "couro": "Couro", "malha": "Malha",
}

ITEMS = {
    # ------------------------------------------------------------------ armas iniciais
    "espada_curta_gasta": {
        "name": "Espada Curta Gasta", "type": "arma", "slot": "arma", "subtype": "espada", "quality": "pobre",
        "damage": [4, 8], "value": 35, "stack": 1,
        "description": "O fio já viu dias melhores, mas o equilíbrio ainda é bom.",
    },
    "escudo_madeira_reforcada": {
        "name": "Escudo de Madeira Reforçada", "type": "escudo", "slot": "secundaria", "subtype": "escudo",
        "quality": "comum", "armor": 12, "value": 40, "stack": 1,
        "description": "Carvalho cintado com ferro. Aguenta mais do que aparenta.",
    },
    "cajado_aprendiz": {
        "name": "Cajado de Aprendiz", "type": "arma", "slot": "arma", "subtype": "cajado", "two_handed": True,
        "quality": "comum", "damage": [2, 5], "stats": {"intelecto": 1}, "value": 40, "stack": 1,
        "description": "Freixo entalhado com runas de iniciante. Ainda cheira a biblioteca.",
    },
    "maca_simples": {
        "name": "Maça Simples", "type": "arma", "slot": "arma", "subtype": "maca", "quality": "comum",
        "damage": [3, 5], "stats": {"espirito": 1}, "value": 38, "stack": 1,
        "description": "Uma maça sem adornos, abençoada às pressas por um sacristão sonolento.",
    },
    "adaga_afiada": {
        "name": "Adaga Afiada", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "comum",
        "damage": [3, 5], "stats": {"agilidade": 1}, "value": 36, "stack": 1,
        "description": "Pequena, discreta e mortalmente afiada.",
    },
    "adaga_curva": {
        "name": "Adaga Curva", "type": "arma", "slot": "secundaria", "subtype": "adaga", "quality": "pobre",
        "damage": [2, 4], "value": 20, "stack": 1,
        "description": "A lâmina curva foi feita para ganchos e truques sujos.",
    },
    # ------------------------------------------------------------------ armaduras iniciais (tingíveis)
    "cota_malha_recruta": {
        "name": "Cota de Malha de Recruta", "type": "armadura", "slot": "peito", "subtype": "malha",
        "quality": "comum", "armor": 28, "value": 45, "stack": 1, "dyeable": True,
        "description": "Anéis de ferro trançados sobre um gibão acolchoado.",
    },
    "manto_aprendiz": {
        "name": "Manto de Aprendiz", "type": "armadura", "slot": "peito", "subtype": "tecido", "quality": "comum",
        "armor": 6, "stats": {"intelecto": 1}, "value": 30, "stack": 1, "dyeable": True,
        "description": "Bordado com estrelas de linha prateada — algumas já soltas.",
    },
    "vestes_novico": {
        "name": "Vestes de Noviço", "type": "armadura", "slot": "peito", "subtype": "tecido", "quality": "comum",
        "armor": 6, "stats": {"espirito": 1}, "value": 30, "stack": 1, "dyeable": True,
        "description": "Linho grosso com o sol nascente da Aurora costurado no peito.",
    },
    "gibao_couro_batido": {
        "name": "Gibão de Couro Batido", "type": "armadura", "slot": "peito", "subtype": "couro", "quality": "comum",
        "armor": 14, "stats": {"agilidade": 1}, "value": 35, "stack": 1, "dyeable": True,
        "description": "Couro endurecido em óleo, silencioso como uma sombra.",
    },
    "calcas_couro_cru": {
        "name": "Calças de Couro Cru", "type": "armadura", "slot": "pernas", "subtype": "couro", "quality": "pobre",
        "armor": 8, "value": 15, "stack": 1,
        "description": "Rangem um pouco a cada passo.",
    },
    "calcas_linho": {
        "name": "Calças de Linho", "type": "armadura", "slot": "pernas", "subtype": "tecido", "quality": "pobre",
        "armor": 3, "value": 10, "stack": 1,
        "description": "Leves e frescas. Nenhuma proteção digna de nota.",
    },
    "botas_gastas": {
        "name": "Botas Gastas", "type": "armadura", "slot": "pes", "subtype": "couro", "quality": "pobre",
        "armor": 5, "value": 12, "stack": 1,
        "description": "Solas finas de tanta estrada. Ainda há chão pela frente.",
    },
    "sandalias_linho": {
        "name": "Sandálias de Linho", "type": "armadura", "slot": "pes", "subtype": "tecido", "quality": "pobre",
        "armor": 2, "value": 8, "stack": 1,
        "description": "Confortáveis — até a primeira poça de lama.",
    },
    # ------------------------------------------------------------------ equipamentos de saque
    "capuz_couro_lobo": {
        "name": "Capuz de Couro de Lobo", "type": "armadura", "slot": "cabeca", "subtype": "couro",
        "quality": "incomum", "armor": 24, "stats": {"agilidade": 2, "vigor": 1}, "value": 140, "stack": 1,
        "description": "As orelhas do lobo ainda estão no capuz. Intimida — ou faz rir.",
    },
    "amuleto_dente_lobo": {
        "name": "Amuleto de Dente de Lobo", "type": "joia", "slot": "pescoco", "quality": "incomum",
        "stats": {"forca": 1, "agilidade": 1, "vigor": 1}, "value": 160, "stack": 1,
        "description": "Um canino amarelado preso num cordão de couro. Os caçadores dizem que dá sorte.",
    },
    "luvas_seda_aranha": {
        "name": "Luvas de Seda de Aranha", "type": "armadura", "slot": "maos", "subtype": "tecido",
        "quality": "incomum", "armor": 7, "stats": {"intelecto": 2, "espirito": 1}, "value": 130, "stack": 1,
        "description": "Leves como ar e frescas ao toque. Os dedos deslizam pelas runas.",
    },
    "botas_couro_javali": {
        "name": "Botas de Couro de Javali", "type": "armadura", "slot": "pes", "subtype": "couro",
        "quality": "incomum", "armor": 20, "stats": {"vigor": 2, "agilidade": 1}, "value": 135, "stack": 1,
        "description": "Grossas, firmes e ainda cheirando a mato.",
    },
    "manto_pele_lobo": {
        "name": "Manto de Pele de Lobo", "type": "armadura", "slot": "costas", "quality": "incomum",
        "armor": 12, "stats": {"vigor": 2}, "value": 150, "stack": 1,
        "description": "Quente o bastante para uma noite inteira na serra.",
    },
    "cajado_galho_sussurrante": {
        "name": "Cajado de Galho Sussurrante", "type": "arma", "slot": "arma", "subtype": "cajado",
        "two_handed": True, "quality": "incomum", "damage": [5, 10], "stats": {"intelecto": 3, "espirito": 2},
        "value": 260, "stack": 1,
        "description": "Um galho da floresta que nunca parou de sussurrar. Às vezes, ele dá conselhos.",
    },
    "machadinha_domador": {
        "name": "Machadinha do Domador", "type": "arma", "slot": "arma", "subtype": "machado", "quality": "incomum",
        "damage": [6, 11], "stats": {"forca": 2, "vigor": 1}, "value": 240, "stack": 1,
        "description": "O cabo tem marcas de dentes. De lobo, espera-se.",
    },
    "capuz_domador": {
        "name": "Capuz do Domador", "type": "armadura", "slot": "cabeca", "subtype": "tecido", "quality": "incomum",
        "armor": 9, "stats": {"intelecto": 2, "espirito": 1, "vigor": 1}, "value": 180, "stack": 1,
        "description": "Negro, com uma lua cortada bordada por dentro, onde ninguém vê.",
    },
    "cinto_couro_trancado": {
        "name": "Cinto de Couro Trançado", "type": "armadura", "slot": "cintura", "subtype": "couro",
        "quality": "incomum", "armor": 12, "stats": {"agilidade": 2, "vigor": 1}, "value": 170, "stack": 1,
        "description": "Três tiras de couro de lobo trançadas com paciência de quem tem tempo de sobra.",
    },
    "presa_gelida": {
        "name": "Presa Gélida", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "raro",
        "damage": [6, 10], "stats": {"agilidade": 3, "vigor": 2}, "value": 700, "stack": 1,
        "description": "Uma presa do Alfa Branco, afiada como vidro. Está sempre coberta de geada.",
    },
    "manto_alfa_branco": {
        "name": "Manto do Alfa Branco", "type": "armadura", "slot": "costas", "quality": "raro",
        "armor": 22, "stats": {"vigor": 3, "forca": 2, "agilidade": 2}, "value": 750, "stack": 1,
        "description": "A pele branca do alfa, macia e fria como neve recém-caída.",
    },
    "anel_uivo_gelido": {
        "name": "Anel do Uivo Gélido", "type": "joia", "slot": "anel", "quality": "raro",
        "stats": {"intelecto": 3, "espirito": 3, "vigor": 2}, "value": 720, "stack": 1,
        "description": "Prata escurecida com um cristal azul. Quando você o gira, ouve um uivo distante.",
    },
    # ------------------------------------------------------------------ consumíveis
    "pao_de_viagem": {
        "name": "Pão de Viagem", "type": "consumivel", "quality": "comum", "value": 5, "stack": 20,
        "use": {"heal_pct": 35, "combat": False, "minutes": 10, "verb": "Você come o pão de viagem sem pressa."},
        "description": "Duro como pedra, mas sustenta qualquer jornada. Restaura 35% da vida fora de combate.",
    },
    "cantil_agua": {
        "name": "Cantil de Água Fresca", "type": "consumivel", "quality": "comum", "value": 5, "stack": 20,
        "use": {"mana_pct": 35, "heal_pct": 10, "combat": False, "minutes": 10,
                "verb": "Você bebe a água fresca em longos goles."},
        "description": "Água do poço de Alvorada, ainda gelada. Restaura 35% da mana fora de combate.",
    },
    "pocao_cura_menor": {
        "name": "Poção de Cura Menor", "type": "consumivel", "quality": "comum", "value": 25, "stack": 5,
        "use": {"heal": [60, 80], "verb": "Você vira a poção de um gole só."},
        "description": "Um líquido vermelho que formiga na língua e fecha pequenos cortes. Restaura 60–80 de vida.",
    },
    "pocao_mana_menor": {
        "name": "Poção de Mana Menor", "type": "consumivel", "quality": "comum", "value": 25, "stack": 5,
        "use": {"mana": [80, 110], "verb": "Você bebe a poção azulada."},
        "description": "Azul cintilante, com gosto de trovão e hortelã. Restaura 80–110 de mana.",
    },
    "pocao_cura": {
        "name": "Poção de Cura", "type": "consumivel", "quality": "comum", "value": 60, "stack": 5,
        "use": {"heal": [130, 170], "verb": "Você bebe a poção espessa e sente as feridas se fecharem."},
        "description": "Vermelho-escura e espessa como xarope. Restaura 130–170 de vida.",
    },
    # ------------------------------------------------------------------ materiais e sucata
    "pena_corvo": {
        "name": "Pena de Corvo", "type": "lixo", "quality": "pobre", "value": 3, "stack": 20,
        "description": "Negra e lustrosa. Algum alfaiate de Alvorada pagaria uns cobres por ela.",
    },
    "bugiganga_brilhante": {
        "name": "Bugiganga Brilhante", "type": "lixo", "quality": "pobre", "value": 18, "stack": 10,
        "description": "Um botão de latão, um elo de corrente e um caco de vidro azul. O corvo tinha bom gosto.",
    },
    "carne_javali": {
        "name": "Carne de Javali", "type": "material", "quality": "comum", "value": 6, "stack": 20,
        "description": "Carne escura e firme. Assada com ervas, seria um banquete.",
    },
    "couro_javali": {
        "name": "Couro de Javali", "type": "material", "quality": "comum", "value": 10, "stack": 20,
        "description": "Grosso e áspero, cheio de cerdas. Ótimo para botas.",
    },
    "presa_javali": {
        "name": "Presa de Javali", "type": "lixo", "quality": "pobre", "value": 12, "stack": 20,
        "description": "Curva e amarelada. Os ferreiros a usam para fazer cabos.",
    },
    "rabo_rato": {
        "name": "Rabo de Rato Gigante", "type": "lixo", "quality": "pobre", "value": 2, "stack": 20,
        "description": "Longo, pelado e nojento. Tobias, o moleiro, talvez se interesse.",
    },
    "escama_lagarto": {
        "name": "Escama de Lagarto", "type": "material", "quality": "pobre", "value": 6, "stack": 20,
        "description": "Verde-musgo e dura como unha.",
    },
    "pele_lobo": {
        "name": "Pele de Lobo", "type": "material", "quality": "comum", "value": 14, "stack": 20,
        "description": "Pelo cinzento e espesso. Os curtidores de Alvorada pagam bem por peles assim.",
    },
    "carne_lobo": {
        "name": "Carne de Lobo Fibrosa", "type": "material", "quality": "comum", "value": 7, "stack": 20,
        "description": "Dura e com gosto forte. Precisa de muito tempero.",
    },
    "presa_lobo": {
        "name": "Presa de Lobo", "type": "lixo", "quality": "pobre", "value": 9, "stack": 20,
        "description": "Um canino afiado. Caçadores penduram no pescoço para contar vitórias.",
    },
    "teia_pegajosa": {
        "name": "Teia Pegajosa", "type": "material", "quality": "comum", "value": 8, "stack": 20,
        "description": "Fios grossos como barbante, ainda grudentos. A matéria-prima da seda de aranha.",
    },
    "glandula_veneno": {
        "name": "Glândula de Veneno", "type": "material", "quality": "comum", "value": 16, "stack": 20,
        "description": "Uma bolsinha esverdeada que lateja. Não aperte.",
    },
    "ectoplasma": {
        "name": "Ectoplasma Sussurrante", "type": "material", "quality": "comum", "value": 20, "stack": 20,
        "description": "Uma geleia fria e luminosa que sussurra quando agitada.",
    },
    "essencia_sussurrante": {
        "name": "Essência Sussurrante", "type": "material", "quality": "incomum", "value": 45, "stack": 20,
        "description": "Um frasco de névoa que se recusa a ficar parada. Alquimistas pagam bem por ela.",
    },
    "fragmento_gelo_eterno": {
        "name": "Fragmento de Gelo Eterno", "type": "material", "quality": "incomum", "value": 40, "stack": 20,
        "description": "Não derrete. Nunca. E está mais frio do que qualquer gelo deveria estar.",
    },
    "asa_morcego": {
        "name": "Asa de Morcego", "type": "lixo", "quality": "pobre", "value": 5, "stack": 20,
        "description": "Fina como papel e com cheiro de caverna.",
    },
    "pele_presa_de_gelo": {
        "name": "Pele de Presa-de-Gelo", "type": "material", "quality": "raro", "value": 350, "stack": 5,
        "description": "A pele branca do Alfa, fria ao toque. Um troféu que todo o vale vai querer ver.",
    },
    # ------------------------------------------------------------------ diversos e missão
    "tocha": {
        "name": "Tocha", "type": "diverso", "quality": "comum", "value": 2, "stack": 10,
        "description": "Breu e estopa num cabo de pinho. Ilumina — e esquenta as mãos.",
    },
    "cartaz_convocacao": {
        "name": "Cartaz de Convocação", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": (
            "\"PROCURAM-SE AVENTUREIROS. O Vale de Primórdia pede ajuda. Recompensa em ouro. "
            "Procurar a Anciã Ysolde.\""
        ),
    },
    "coleira_lua_cortada": {
        "name": "Coleira da Lua Cortada", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": ("Uma coleira de couro negro com uma placa de prata: uma lua minguante cortada ao meio. "
                        "Grande demais para um lobo comum."),
    },
    "aljava_gravada": {
        "name": "Aljava Gravada", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": ("Uma aljava de couro com as iniciais \"R. V.\" gravadas a fogo. Ainda há uma flecha "
                        "dentro, com penas pintadas de azul."),
    },
    "pingente_pedra_da_lua": {
        "name": "Pingente de Pedra-da-Lua", "type": "joia", "slot": "pescoco", "quality": "raro",
        "stats": {"intelecto": 2, "espirito": 3}, "value": 1500, "stack": 1,
        "description": (
            "Uma pedra leitosa presa em prata antiga. Sob a luz da lua, um crescente brilha "
            "em seu interior — como se faltassem outras duas."
        ),
    },
}

#: Itens que todo herói carrega no início da jornada (além dos itens da classe).
STARTING_ITEMS = [["pao_de_viagem", 4], ["cantil_agua", 2], ["tocha", 2], ["cartaz_convocacao", 1]]
STARTING_COPPER = 250
