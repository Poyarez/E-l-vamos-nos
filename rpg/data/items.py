"""Itens do jogo (fábrica em ``rpg.items``).

Campos gerais: ``name``, ``type``, ``quality``, ``description`` (texto de ambientação),
``value`` (preço de venda, em moedas de cobre) e ``stack`` (tamanho máximo da pilha).

Equipamentos: ``slot``, ``subtype`` (tipo de arma ou de armadura, que define quais
classes podem usar a peça; joias e mantos não têm), ``armor``, ``damage``, ``stats`` e
``two_handed``. ``dyeable`` indica peças que recebem a cor escolhida na criação.

Consumíveis: ``use`` descreve o efeito — ``heal``/``mana`` (faixa de valores),
``heal_pct``/``mana_pct`` (porcentagem do máximo), ``combat`` (se pode ser usado em
combate), ``minutes`` (tempo gasto fora de combate), ``buff`` (bônus temporário: comidas,
elixires e venenos de arma) e ``damage`` + ``element`` (frascos arremessados em combate,
com ``combat_only``).

Ferramentas: ``tool`` (o tipo — picareta, rede, vara, martelo, agulha, tesoura ou
almofariz) e ``power`` (bônus na chance de coleta). Bolsas: ``bag_slots`` (espaços extras
na mochila).
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
    "bolsa": "Bolsa",
}

ITEM_TYPES = {
    "arma": "Arma",
    "escudo": "Escudo",
    "armadura": "Armadura",
    "joia": "Joia",
    "consumivel": "Consumível",
    "material": "Material",
    "ferramenta": "Ferramenta",
    "bolsa": "Bolsa",
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
        "name": "Pena de Corvo", "type": "material", "quality": "comum", "value": 3, "stack": 50,
        "description": ("Negra e lustrosa. Amarrada num anzol, vira a isca de mosca preferida das trutas e dos "
                        "salmões."),
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
        "name": "Presa de Javali", "type": "material", "quality": "comum", "value": 12, "stack": 20,
        "description": "Curva e amarelada. Moída no almofariz, dizem as erveiras, dá a teimosia de um javali.",
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
        "name": "Presa de Lobo", "type": "material", "quality": "comum", "value": 9, "stack": 20,
        "description": "Um canino afiado. Caçadores enfiam as presas num cordão para contar vitórias.",
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
        "name": "Asa de Morcego", "type": "material", "quality": "comum", "value": 5, "stack": 20,
        "description": "Fina como papel e com cheiro de caverna. Ingrediente clássico de elixires de visão noturna.",
    },
    "pele_presa_de_gelo": {
        "name": "Pele de Presa-de-Gelo", "type": "material", "quality": "raro", "value": 350, "stack": 5,
        "description": "A pele branca do Alfa, fria ao toque. Um troféu que todo o vale vai querer ver.",
    },
    # ================================================================== Etapa 3: coleta e ofícios
    # ------------------------------------------------------------------ ferramentas
    "picareta_velha": {
        "name": "Picareta Velha", "type": "ferramenta", "tool": "picareta", "power": 0.0, "quality": "pobre",
        "value": 6, "stack": 1,
        "description": "O cabo está rachado e a ponta, cega. Ainda arranca minério — devagar.",
    },
    "picareta_bronze": {
        "name": "Picareta de Bronze", "type": "ferramenta", "tool": "picareta", "power": 0.06, "quality": "comum",
        "value": 30, "stack": 1,
        "description": ("Bronze recém-forjado num cabo de freixo. Morde a rocha com vontade. "
                        "(+6% de chance na mineração)"),
    },
    "picareta_ferro": {
        "name": "Picareta de Ferro", "type": "ferramenta", "tool": "picareta", "power": 0.14, "quality": "incomum",
        "value": 90, "stack": 1,
        "description": "Pesada, equilibrada e com a ponta temperada. Mineiros de verdade não aceitam menos. "
                       "(+14% de chance na mineração)",
    },
    "rede_pesca": {
        "name": "Rede de Pesca", "type": "ferramenta", "tool": "rede", "power": 0.0, "quality": "comum",
        "value": 5, "stack": 1,
        "description": "Uma rede de malha miúda, remendada em vários pontos. Ideal para camarões.",
    },
    "vara_pesca": {
        "name": "Vara de Pesca", "type": "ferramenta", "tool": "vara", "power": 0.0, "quality": "comum",
        "value": 12, "stack": 1,
        "description": "Bambu, linha encerada e um anzol de bronze. Precisa de isca: minhocas ou penas.",
    },
    "martelo_ferreiro": {
        "name": "Martelo de Ferreiro", "type": "ferramenta", "tool": "martelo", "power": 0.0, "quality": "comum",
        "value": 10, "stack": 1,
        "description": "Cabeça quadrada, cabo curto e gasto pela mão de alguém. Indispensável na bigorna.",
    },
    "kit_costura": {
        "name": "Agulha e Linha", "type": "ferramenta", "tool": "agulha", "power": 0.0, "quality": "comum",
        "value": 4, "stack": 1,
        "description": "Agulhas de osso, um dedal de latão e um carretel de linha forte. Costura-se em qualquer lugar.",
    },
    "tesoura_tosquia": {
        "name": "Tesoura de Tosquia", "type": "ferramenta", "tool": "tesoura", "power": 0.0, "quality": "comum",
        "value": 8, "stack": 1,
        "description": "Duas lâminas largas presas por uma mola. As ovelhas não gostam de vê-la.",
    },
    "almofariz": {
        "name": "Almofariz e Pilão", "type": "ferramenta", "tool": "almofariz", "power": 0.0, "quality": "comum",
        "value": 8, "stack": 1,
        "description": "Pedra-sabão gasta por gerações de erveiras. Toda poção começa aqui.",
    },
    # ------------------------------------------------------------------ insumos comprados
    "isca_minhoca": {
        "name": "Minhocas", "type": "material", "quality": "comum", "value": 1, "stack": 50,
        "description": "Gordas, num pote de terra úmida. Isca para sardinhas e peixes de água parada.",
    },
    "frasco_vazio": {
        "name": "Frasco Vazio", "type": "material", "quality": "comum", "value": 1, "stack": 50,
        "description": "Vidro grosso e uma rolha de cortiça. Toda poção precisa de um.",
    },
    "farinha": {
        "name": "Farinha de Trigo", "type": "material", "quality": "comum", "value": 2, "stack": 20,
        "description": "Moída no moinho do Tobias. Ainda tem um gato desenhado no saco.",
    },
    "especiarias": {
        "name": "Especiarias do Sul", "type": "material", "quality": "comum", "value": 6, "stack": 20,
        "description": "Pimenta, cominho e um pó vermelho que arde só de olhar. Coisa da caravana.",
    },
    # ------------------------------------------------------------------ mineração e metalurgia
    "minerio_cobre": {
        "name": "Minério de Cobre", "type": "material", "quality": "comum", "value": 3, "stack": 50,
        "description": "Pedra esverdeada com veios alaranjados. Com estanho, vira bronze.",
    },
    "minerio_estanho": {
        "name": "Minério de Estanho", "type": "material", "quality": "comum", "value": 3, "stack": 50,
        "description": "Cinzento e pesado. Sozinho não serve para muita coisa; com cobre, vira bronze.",
    },
    "minerio_ferro": {
        "name": "Minério de Ferro", "type": "material", "quality": "comum", "value": 8, "stack": 50,
        "description": "Avermelhado e cheio de impurezas. Só um ferreiro paciente tira uma barra boa disso.",
    },
    "minerio_prata": {
        "name": "Minério de Prata", "type": "material", "quality": "comum", "value": 14, "stack": 50,
        "description": "Brilha mesmo na penumbra da gruta. Os ourives da capital pagariam bem.",
    },
    "cristal_eco": {
        "name": "Cristal-de-eco", "type": "material", "quality": "raro", "value": 120, "stack": 20,
        "description": "Um cristal azul-escuro que ainda vibra, como se guardasse a última nota que ouviu.",
    },
    "granada_bruta": {
        "name": "Granada Bruta", "type": "material", "quality": "incomum", "value": 45, "stack": 20,
        "description": "Uma pedra vermelho-sangue presa num pedaço de rocha. Lapidada, daria um belo anel.",
    },
    "barra_bronze": {
        "name": "Barra de Bronze", "type": "material", "quality": "comum", "value": 10, "stack": 50,
        "description": "Cobre e estanho fundidos juntos. O começo de todo ferreiro.",
    },
    "barra_ferro": {
        "name": "Barra de Ferro", "type": "material", "quality": "comum", "value": 22, "stack": 50,
        "description": "Ferro limpo, batido e dobrado. Mais duro e mais pesado que o bronze.",
    },
    "barra_prata": {
        "name": "Barra de Prata", "type": "material", "quality": "incomum", "value": 35, "stack": 50,
        "description": "Macia demais para armas, perfeita para joias.",
    },
    # ------------------------------------------------------------------ equipamentos forjados
    "adaga_bronze": {
        "name": "Adaga de Bronze", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "comum",
        "damage": [4, 7], "value": 18, "stack": 1,
        "description": "Curta, simples e com o brilho alaranjado do bronze novo.",
    },
    "machadinha_bronze": {
        "name": "Machadinha de Bronze", "type": "arma", "slot": "arma", "subtype": "machado", "quality": "comum",
        "damage": [5, 9], "value": 20, "stack": 1,
        "description": "Serve para lenha, para lobos e para impressionar na taverna.",
    },
    "maca_bronze": {
        "name": "Maça de Bronze", "type": "arma", "slot": "arma", "subtype": "maca", "quality": "comum",
        "damage": [4, 8], "stats": {"espirito": 1}, "value": 20, "stack": 1,
        "description": "Cabeça flangeada sobre um cabo de carvalho. Simples e convincente.",
    },
    "espada_bronze": {
        "name": "Espada de Bronze", "type": "arma", "slot": "arma", "subtype": "espada", "quality": "comum",
        "damage": [5, 10], "value": 24, "stack": 1,
        "description": "Uma lâmina reta e bem temperada. Não é aço, mas corta do mesmo jeito.",
    },
    "elmo_bronze": {
        "name": "Elmo de Bronze", "type": "armadura", "slot": "cabeca", "subtype": "malha", "quality": "comum",
        "armor": 16, "value": 18, "stack": 1,
        "description": "Um elmo aberto, com protetor de nariz. Esquenta no sol.",
    },
    "botas_bronze": {
        "name": "Botas de Bronze", "type": "armadura", "slot": "pes", "subtype": "malha", "quality": "comum",
        "armor": 12, "value": 16, "stack": 1,
        "description": "Couro grosso com placas de bronze no peito do pé. Ninguém chega de mansinho com elas.",
    },
    "escudo_bronze": {
        "name": "Escudo de Bronze", "type": "escudo", "slot": "secundaria", "subtype": "escudo", "quality": "comum",
        "armor": 22, "value": 30, "stack": 1,
        "description": "Redondo e martelado à mão. As marcas do martelo ainda aparecem na borda.",
    },
    "cota_bronze": {
        "name": "Cota de Malha de Bronze", "type": "armadura", "slot": "peito", "subtype": "malha",
        "quality": "comum", "armor": 38, "value": 40, "stack": 1, "dyeable": True,
        "description": "Milhares de anéis de bronze, um a um. Pesa, mas segura uma mordida de lobo.",
    },
    "perneiras_bronze": {
        "name": "Perneiras de Bronze", "type": "armadura", "slot": "pernas", "subtype": "malha",
        "quality": "comum", "armor": 26, "value": 34, "stack": 1,
        "description": "Placas sobrepostas que tilintam a cada passo.",
    },
    "adaga_ferro": {
        "name": "Adaga de Ferro", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "comum",
        "damage": [6, 10], "stats": {"agilidade": 1}, "value": 40, "stack": 1,
        "description": "Fina, escura e equilibrada para ser arremessada — mas é melhor não arremessar.",
    },
    "maca_ferro": {
        "name": "Maça de Ferro", "type": "arma", "slot": "arma", "subtype": "maca", "quality": "comum",
        "damage": [6, 11], "stats": {"espirito": 2}, "value": 48, "stack": 1,
        "description": "Seis flanges de ferro e um sol nascente gravado no pomo, a pedido da capela.",
    },
    "espada_ferro": {
        "name": "Espada de Ferro", "type": "arma", "slot": "arma", "subtype": "espada", "quality": "comum",
        "damage": [7, 13], "stats": {"forca": 1}, "value": 50, "stack": 1,
        "description": "Lâmina de ferro dobrado, com sulco de sangue. Uma espada de verdade.",
    },
    "machado_ferro": {
        "name": "Machado de Ferro", "type": "arma", "slot": "arma", "subtype": "machado", "quality": "comum",
        "damage": [8, 14], "stats": {"forca": 1}, "value": 52, "stack": 1,
        "description": "Uma meia-lua de ferro num cabo de freixo. Faz lenha de qualquer coisa.",
    },
    "elmo_ferro": {
        "name": "Elmo de Ferro", "type": "armadura", "slot": "cabeca", "subtype": "malha", "quality": "comum",
        "armor": 24, "value": 40, "stack": 1,
        "description": "Fechado nas laterais, com fendas estreitas para os olhos.",
    },
    "botas_ferro": {
        "name": "Botas de Ferro", "type": "armadura", "slot": "pes", "subtype": "malha", "quality": "comum",
        "armor": 18, "value": 34, "stack": 1,
        "description": "Biqueira de ferro. Chutar portas nunca foi tão fácil.",
    },
    "escudo_ferro": {
        "name": "Escudo de Ferro", "type": "escudo", "slot": "secundaria", "subtype": "escudo", "quality": "comum",
        "armor": 32, "value": 60, "stack": 1,
        "description": "Um escudo de lágrima, com reforço de ferro em cruz.",
    },
    "cota_ferro": {
        "name": "Cota de Malha de Ferro", "type": "armadura", "slot": "peito", "subtype": "malha",
        "quality": "comum", "armor": 56, "value": 80, "stack": 1, "dyeable": True,
        "description": "Anéis de ferro rebitados, um trabalho de semanas. Flechas e presas escorregam nela.",
    },
    "perneiras_ferro": {
        "name": "Perneiras de Ferro", "type": "armadura", "slot": "pernas", "subtype": "malha",
        "quality": "comum", "armor": 38, "value": 66, "stack": 1,
        "description": "Pesadas e barulhentas. Ninguém vai confundir você com um ladino.",
    },
    "anel_prata": {
        "name": "Anel de Prata", "type": "joia", "slot": "anel", "quality": "comum",
        "stats": {"intelecto": 1, "espirito": 1}, "value": 45, "stack": 1,
        "description": "Um aro liso de prata do Véu. Esfria o dedo e acalma a cabeça.",
    },
    "anel_granada": {
        "name": "Anel de Granada", "type": "joia", "slot": "anel", "quality": "incomum",
        "stats": {"forca": 2, "vigor": 2}, "value": 120, "stack": 1,
        "description": "Prata trabalhada em garras, segurando uma granada cor de sangue.",
    },
    "amuleto_eco": {
        "name": "Amuleto de Cristal-de-eco", "type": "joia", "slot": "pescoco", "quality": "raro",
        "stats": {"intelecto": 3, "espirito": 3, "vigor": 2}, "value": 400, "stack": 1,
        "description": "O cristal ainda canta baixinho, preso em prata. Quem o usa ouve os próprios pensamentos com "
                       "mais clareza.",
    },
    # ------------------------------------------------------------------ pesca e culinária
    "camarao_cru": {
        "name": "Camarões Crus", "type": "material", "quality": "comum", "value": 1, "stack": 20,
        "description": "Um punhado de camarões cinzentos que ainda se mexem. Precisam de fogo.",
    },
    "sardinha_crua": {
        "name": "Sardinha Crua", "type": "material", "quality": "comum", "value": 2, "stack": 20,
        "description": "Pequena, prateada e escorregadia.",
    },
    "truta_crua": {
        "name": "Truta Crua", "type": "material", "quality": "comum", "value": 6, "stack": 20,
        "description": "Pintada de vermelho e verde, ainda com cheiro de ribeirão.",
    },
    "salmao_cru": {
        "name": "Salmão Cru", "type": "material", "quality": "comum", "value": 10, "stack": 20,
        "description": "Grande, rosado e cheio de força. Subiu o ribeirão inteiro para acabar na sua mochila.",
    },
    "peixe_cego_cru": {
        "name": "Peixe-cego Cru", "type": "material", "quality": "incomum", "value": 18, "stack": 20,
        "description": "Pálido, quase transparente e sem olhos. Vive no escuro desde antes da vila existir.",
    },
    "bota_velha": {
        "name": "Bota Velha Encharcada", "type": "lixo", "quality": "pobre", "value": 1, "stack": 5,
        "description": "Alguém perdeu isto no lago há muito tempo. Um caranguejo morava dentro.",
    },
    "comida_queimada": {
        "name": "Comida Queimada", "type": "lixo", "quality": "pobre", "value": 1, "stack": 20,
        "description": "Carvão em formato de comida. Nem o gato da estalagem quer.",
    },
    "camarao_assado": {
        "name": "Camarões Assados", "type": "consumivel", "quality": "comum", "value": 3, "stack": 20,
        "use": {"heal_pct": 25, "combat": False, "minutes": 10, "verb": "Você come os camarões, casca e tudo."},
        "description": "Crocantes e salgadinhos. Restauram 25% da vida fora de combate.",
    },
    "sardinha_assada": {
        "name": "Sardinha Assada", "type": "consumivel", "quality": "comum", "value": 4, "stack": 20,
        "use": {"heal_pct": 30, "combat": False, "minutes": 10, "verb": "Você come a sardinha com os dedos."},
        "description": "Pele tostada e carne macia. Restaura 30% da vida fora de combate.",
    },
    "bisteca_javali": {
        "name": "Bisteca de Javali", "type": "consumivel", "quality": "comum", "value": 8, "stack": 20,
        "use": {"heal_pct": 40, "combat": False, "minutes": 10,
                "verb": "Você rói a bisteca até o osso."},
        "description": "Grossa, suculenta e com uma crosta de sal. Restaura 40% da vida fora de combate.",
    },
    "truta_assada": {
        "name": "Truta Assada", "type": "consumivel", "quality": "comum", "value": 10, "stack": 20,
        "use": {"heal_pct": 45, "combat": False, "minutes": 10,
                "verb": "Você come a truta devagar, tirando as espinhas."},
        "description": "Assada na brasa com uma pitada de sal. Restaura 45% da vida fora de combate.",
    },
    "salmao_assado": {
        "name": "Salmão Assado", "type": "consumivel", "quality": "comum", "value": 15, "stack": 20,
        "use": {"heal_pct": 60, "combat": False, "minutes": 10,
                "verb": "Você saboreia o salmão, que se desfaz em lascas."},
        "description": "Rosado por dentro e dourado por fora. Restaura 60% da vida fora de combate.",
    },
    "peixe_cego_assado": {
        "name": "Peixe-cego Assado", "type": "consumivel", "quality": "incomum", "value": 28, "stack": 20,
        "use": {"heal_pct": 70, "combat": False, "minutes": 10,
                "verb": "A carne branca do peixe-cego tem gosto de chuva e de pedra.",
                "buff": {"id": "bem_alimentado", "name": "Bem alimentado", "group": "comida", "minutes": 120,
                         "stats": {"espirito": 4}}},
        "description": "Restaura 70% da vida fora de combate. Bem alimentado: +4 de Espírito por 2 horas.",
    },
    "espetinho_lobo": {
        "name": "Espetinho Apimentado de Lobo", "type": "consumivel", "quality": "comum", "value": 16, "stack": 20,
        "use": {"heal_pct": 40, "combat": False, "minutes": 10,
                "verb": "As especiarias do sul domam a carne dura do lobo. Seus olhos lacrimejam.",
                "buff": {"id": "bem_alimentado", "name": "Bem alimentado", "group": "comida", "minutes": 120,
                         "stats": {"forca": 3, "agilidade": 2}}},
        "description": ("Restaura 40% da vida fora de combate. Bem alimentado: +3 de Força e +2 de Agilidade "
                        "por 2 horas."),
    },
    "ensopado_javali": {
        "name": "Ensopado de Javali com Cogumelos", "type": "consumivel", "quality": "comum", "value": 20,
        "stack": 20,
        "use": {"heal_pct": 55, "combat": False, "minutes": 15,
                "verb": "Você raspa a tigela. Os cogumelos-lume deixam um brilho azulado na colher.",
                "buff": {"id": "bem_alimentado", "name": "Bem alimentado", "group": "comida", "minutes": 120,
                         "stats": {"vigor": 4}}},
        "description": "O prato da casa da estalagem, melhorado. Restaura 55% da vida fora de combate. "
                       "Bem alimentado: +4 de Vigor por 2 horas.",
    },
    "torta_truta": {
        "name": "Torta de Truta", "type": "consumivel", "quality": "comum", "value": 22, "stack": 20,
        "use": {"heal_pct": 50, "combat": False, "minutes": 15, "verb": "Massa crocante, recheio quente. Que torta.",
                "buff": {"id": "bem_alimentado", "name": "Bem alimentado", "group": "comida", "minutes": 120,
                         "stats": {"intelecto": 3, "espirito": 3}}},
        "description": "Restaura 50% da vida fora de combate. Bem alimentado: +3 de Intelecto e +3 de Espírito "
                       "por 2 horas.",
    },
    # ------------------------------------------------------------------ alfaiataria
    "linho": {
        "name": "Fibra de Linho", "type": "material", "quality": "comum", "value": 1, "stack": 50,
        "description": "Talos de linho secos ao sol. Fiados na roca, viram linha.",
    },
    "la_crua": {
        "name": "Lã Crua", "type": "material", "quality": "comum", "value": 3, "stack": 50,
        "description": "Um chumaço de lã de ovelha, ainda com capim preso.",
    },
    "fio_linho": {
        "name": "Fio de Linho", "type": "material", "quality": "comum", "value": 3, "stack": 50,
        "description": "Um carretel de fio claro e resistente.",
    },
    "novelo_la": {
        "name": "Novelo de Lã", "type": "material", "quality": "comum", "value": 6, "stack": 50,
        "description": "Macio e quente. Cheira um pouco a ovelha.",
    },
    "fio_seda": {
        "name": "Fio de Seda de Aranha", "type": "material", "quality": "incomum", "value": 18, "stack": 50,
        "description": "Fiado das teias da mata. Fino como cabelo e mais forte que corda.",
    },
    "bolsa_linho": {
        "name": "Bolsa de Linho", "type": "bolsa", "slot": "bolsa", "bag_slots": 4, "quality": "comum",
        "value": 20, "stack": 1,
        "description": "Uma bolsa de pano com alça de ombro. +4 espaços na mochila.",
    },
    "bolsa_la": {
        "name": "Bolsa de Lã", "type": "bolsa", "slot": "bolsa", "bag_slots": 6, "quality": "comum",
        "value": 45, "stack": 1,
        "description": "Lã grossa com fundo de couro de javali. +6 espaços na mochila.",
    },
    "bolsa_seda": {
        "name": "Bolsa de Seda de Aranha", "type": "bolsa", "slot": "bolsa", "bag_slots": 8,
        "quality": "incomum", "value": 110, "stack": 1,
        "description": "Leve como uma pluma e quase impossível de rasgar. +8 espaços na mochila.",
    },
    "tunica_linho": {
        "name": "Túnica de Linho", "type": "armadura", "slot": "peito", "subtype": "tecido", "quality": "comum",
        "armor": 8, "stats": {"intelecto": 1, "espirito": 1}, "value": 16, "stack": 1, "dyeable": True,
        "description": "Costurada à mão, com pontos miúdos e tingida na sua cor.",
    },
    "luvas_linho": {
        "name": "Luvas de Linho", "type": "armadura", "slot": "maos", "subtype": "tecido", "quality": "comum",
        "armor": 3, "stats": {"intelecto": 1}, "value": 8, "stack": 1,
        "description": "Finas o bastante para virar as páginas de um grimório.",
    },
    "capuz_la": {
        "name": "Capuz de Lã", "type": "armadura", "slot": "cabeca", "subtype": "tecido", "quality": "comum",
        "armor": 6, "stats": {"vigor": 1, "espirito": 1}, "value": 20, "stack": 1, "dyeable": True,
        "description": "Quentinho e com uma borla na ponta, que você pode cortar se quiser parecer sério.",
    },
    "calcas_la": {
        "name": "Calças de Lã", "type": "armadura", "slot": "pernas", "subtype": "tecido", "quality": "comum",
        "armor": 8, "stats": {"intelecto": 2}, "value": 24, "stack": 1,
        "description": "Grossas e um pouco ásperas. Perfeitas para noites de estudo na torre.",
    },
    "manto_la": {
        "name": "Manto de Lã", "type": "armadura", "slot": "costas", "quality": "comum",
        "armor": 6, "stats": {"vigor": 2}, "value": 26, "stack": 1, "dyeable": True,
        "description": "Um manto de viagem com capuz e broche de osso.",
    },
    "colar_presas": {
        "name": "Colar de Presas de Lobo", "type": "joia", "slot": "pescoco", "quality": "comum",
        "stats": {"forca": 1, "agilidade": 1}, "value": 24, "stack": 1,
        "description": "Três presas num cordão de linho trançado. Cada uma, uma história.",
    },
    "gibao_couro_javali": {
        "name": "Gibão de Couro de Javali", "type": "armadura", "slot": "peito", "subtype": "couro",
        "quality": "comum", "armor": 22, "stats": {"agilidade": 2}, "value": 40, "stack": 1, "dyeable": True,
        "description": "Couro grosso costurado em gomos. Ainda tem algumas cerdas no colarinho.",
    },
    "vestes_seda": {
        "name": "Vestes de Seda de Aranha", "type": "armadura", "slot": "peito", "subtype": "tecido",
        "quality": "incomum", "armor": 12, "stats": {"intelecto": 3, "espirito": 2}, "value": 120, "stack": 1,
        "dyeable": True,
        "description": "Brilham levemente quando você se move, como orvalho numa teia ao amanhecer.",
    },
    # ------------------------------------------------------------------ alquimia
    "folha_charco": {
        "name": "Folha-de-charco", "type": "material", "quality": "comum", "value": 2, "stack": 50,
        "description": "Folhas largas e lustrosas que crescem com os pés na água. A base de todo remédio.",
    },
    "cogumelo_lume": {
        "name": "Cogumelo-lume", "type": "material", "quality": "comum", "value": 4, "stack": 50,
        "description": "Brilha em azul mesmo depois de colhido. Desperta a mente — e a mana.",
    },
    "flor_breu": {
        "name": "Flor-de-breu", "type": "material", "quality": "comum", "value": 6, "stack": 50,
        "description": "Pétalas negras e pegajosas que cheiram a piche. Pegam fogo com uma faísca.",
    },
    "orquidea_termal": {
        "name": "Orquídea-das-termas", "type": "material", "quality": "comum", "value": 9, "stack": 50,
        "description": "Só cresce no vapor da fonte termal. Morna ao toque, como se tivesse febre.",
    },
    "musgo_prata": {
        "name": "Musgo-prata", "type": "material", "quality": "comum", "value": 12, "stack": 50,
        "description": "Cresce nas pedras molhadas pela cachoeira. Fecha feridas como nenhuma outra planta.",
    },
    "lirio_lua": {
        "name": "Lírio-da-lua", "type": "material", "quality": "incomum", "value": 25, "stack": 50,
        "description": "Um lírio branco que só se abre sob a lua. Colhido, guarda um pouco de luz.",
    },
    "elixir_javali": {
        "name": "Elixir do Javali", "type": "consumivel", "quality": "comum", "value": 20, "stack": 10,
        "use": {"combat": False, "minutes": 2,
                "verb": "Grosso, amargo e com gosto de terra. Você sente o pescoço engrossar.",
                "buff": {"id": "elixir_javali", "name": "Elixir do Javali", "group": "elixir", "minutes": 90,
                         "stats": {"vigor": 4}}},
        "description": "Beba antes da luta: +4 de Vigor por 1h30.",
    },
    "elixir_morcego": {
        "name": "Elixir dos Olhos de Morcego", "type": "consumivel", "quality": "comum", "value": 22, "stack": 10,
        "use": {"combat": False, "minutes": 2, "verb": "O mundo escurece por um instante... e então tudo fica nítido.",
                "buff": {"id": "elixir_morcego", "name": "Olhos de Morcego", "group": "elixir", "minutes": 120,
                         "vision": 1}},
        "description": "Visão aguçada: +1 de raio de visão por 2 horas (ótimo à noite e nas cavernas).",
    },
    "elixir_lobo": {
        "name": "Elixir do Lobo", "type": "consumivel", "quality": "comum", "value": 30, "stack": 10,
        "use": {"combat": False, "minutes": 2, "verb": "Você sente o faro e os reflexos de uma fera.",
                "buff": {"id": "elixir_lobo", "name": "Elixir do Lobo", "group": "elixir", "minutes": 90,
                         "stats": {"agilidade": 3, "forca": 2}}},
        "description": "Beba antes da luta: +3 de Agilidade e +2 de Força por 1h30.",
    },
    "elixir_sussurrante": {
        "name": "Elixir da Mente Sussurrante", "type": "consumivel", "quality": "incomum", "value": 55, "stack": 10,
        "use": {"combat": False, "minutes": 2, "verb": "Vozes distantes sussurram segredos de magia no seu ouvido.",
                "buff": {"id": "elixir_sussurrante", "name": "Mente Sussurrante", "group": "elixir", "minutes": 90,
                         "stats": {"intelecto": 5, "espirito": 4}}},
        "description": "Beba antes da luta: +5 de Intelecto e +4 de Espírito por 1h30.",
    },
    "veneno_aranha": {
        "name": "Veneno de Aranha", "type": "consumivel", "quality": "comum", "value": 20, "stack": 10,
        "use": {"combat": False, "minutes": 2, "verb": "Você passa o veneno esverdeado no fio da arma, com cuidado.",
                "buff": {"id": "veneno_aranha", "name": "Lâmina envenenada", "group": "arma", "minutes": 60,
                         "coating": {"element": "natureza", "damage": [3, 5]}}},
        "description": "Aplicado na arma: cada golpe da arma causa 3–5 de dano de Natureza extra por 1 hora.",
    },
    "oleo_inflamavel": {
        "name": "Óleo Inflamável", "type": "consumivel", "quality": "comum", "value": 15, "stack": 10,
        "use": {"damage": [22, 30], "element": "fogo", "combat_only": True, "verb": "Você arremessa o frasco"},
        "description": "Arremesse em combate: 22–30 de dano de Fogo. Rompe selos de Fogo.",
    },
    "frasco_gelo": {
        "name": "Frasco de Gelo Eterno", "type": "consumivel", "quality": "comum", "value": 30, "stack": 10,
        "use": {"damage": [26, 34], "element": "gelo", "combat_only": True, "verb": "Você arremessa o frasco"},
        "description": "Arremesse em combate: 26–34 de dano de Gelo. Rompe selos de Gelo.",
    },
    "frasco_luz": {
        "name": "Frasco de Luz Lunar", "type": "consumivel", "quality": "incomum", "value": 40, "stack": 10,
        "use": {"damage": [30, 40], "element": "sagrado", "combat_only": True, "verb": "Você arremessa o frasco"},
        "description": "Arremesse em combate: 30–40 de dano Sagrado. Rompe selos Sagrados. Espíritos odeiam.",
    },
    "frasco_eco": {
        "name": "Frasco de Eco", "type": "consumivel", "quality": "raro", "value": 90, "stack": 10,
        "use": {"damage": [40, 54], "element": "arcano", "combat_only": True, "verb": "Você arremessa o frasco"},
        "description": "Arremesse em combate: 40–54 de dano Arcano. Rompe selos Arcanos.",
    },
    "pocao_mana": {
        "name": "Poção de Mana", "type": "consumivel", "quality": "comum", "value": 60, "stack": 5,
        "use": {"mana": [160, 210], "verb": "Você bebe a poção, que brilha como um céu de tempestade."},
        "description": "Azul-escura e cintilante. Restaura 160–210 de mana.",
    },
    # ------------------------------------------------------------------ diversos e missão
    "tocha": {
        "name": "Tocha", "type": "diverso", "quality": "comum", "value": 2, "stack": 10,
        "description": "Breu e estopa num cabo de pinho. Ilumina — e acende fogueiras apagadas.",
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
    # ================================================================== Etapa 4
    # ------------------------------------------------------------------ metalurgia: aço e carvão
    "carvao": {
        "name": "Carvão Mineral", "type": "material", "quality": "comum", "value": 4, "stack": 50,
        "description": "Pedra negra que suja os dedos e queima quente como o inferno. Ferro + carvão = aço.",
    },
    "barra_aco": {
        "name": "Barra de Aço", "type": "material", "quality": "comum", "value": 20, "stack": 50,
        "description": "Ferro casado com carvão no fogo mais quente da fornalha. Duro, flexível e caro.",
    },
    "pregos_bronze": {
        "name": "Pregos de Bronze", "type": "material", "quality": "comum", "value": 1, "stack": 50,
        "description": "Pregos que não enferrujam, os favoritos de quem constrói perto da água.",
    },
    "adaga_aco": {
        "name": "Adaga de Aço", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "comum",
        "damage": [8, 13], "stats": {"agilidade": 2}, "value": 70, "stack": 1,
        "description": "A lâmina faz um som limpo ao sair da bainha, como uma nota de sino.",
    },
    "maca_aco": {
        "name": "Maça de Aço", "type": "arma", "slot": "arma", "subtype": "maca", "quality": "comum",
        "damage": [8, 14], "stats": {"espirito": 3}, "value": 78, "stack": 1,
        "description": "Flanges de aço polido e um sol nascente cinzelado no pomo.",
    },
    "espada_aco": {
        "name": "Espada de Aço", "type": "arma", "slot": "arma", "subtype": "espada", "quality": "comum",
        "damage": [9, 16], "stats": {"forca": 2}, "value": 82, "stack": 1,
        "description": "Aço temperado em óleo, com o fio que só a paciência dá.",
    },
    "machado_aco": {
        "name": "Machado de Aço", "type": "arma", "slot": "arma", "subtype": "machado", "quality": "comum",
        "damage": [10, 17], "stats": {"forca": 2}, "value": 85, "stack": 1,
        "description": "Pesado na cabeça e leve no cabo: o machado que todo lenhador sonha ter.",
    },
    "elmo_aco": {
        "name": "Elmo de Aço", "type": "armadura", "slot": "cabeca", "subtype": "malha", "quality": "comum",
        "armor": 32, "stats": {"vigor": 1}, "value": 64, "stack": 1,
        "description": "Um elmo de aço com protetor de nariz. Esquenta no sol, mas segura uma clava.",
    },
    "botas_aco": {
        "name": "Botas de Aço", "type": "armadura", "slot": "pes", "subtype": "malha", "quality": "comum",
        "armor": 24, "stats": {"vigor": 1}, "value": 56, "stack": 1,
        "description": "Escamas de aço sobre couro grosso. Cada passo soa como uma decisão.",
    },
    "escudo_aco": {
        "name": "Escudo de Aço", "type": "escudo", "slot": "secundaria", "subtype": "escudo", "quality": "comum",
        "armor": 44, "stats": {"vigor": 1}, "value": 96, "stack": 1,
        "description": "Um escudo redondo de aço batido, com bossa no centro. Flechas ricocheteiam nele.",
    },
    "cota_aco": {
        "name": "Cota de Malha de Aço", "type": "armadura", "slot": "peito", "subtype": "malha",
        "quality": "comum", "armor": 74, "stats": {"vigor": 2}, "value": 130, "stack": 1, "dyeable": True,
        "description": "Anéis de aço miúdos e rebitados, um a um. Uma armadura para a vida inteira.",
    },
    "perneiras_aco": {
        "name": "Perneiras de Aço", "type": "armadura", "slot": "pernas", "subtype": "malha",
        "quality": "comum", "armor": 50, "stats": {"vigor": 1}, "value": 104, "stack": 1,
        "description": "Placas de aço articuladas nos joelhos. Ajoelhar para rezar ficou mais difícil.",
    },
    "picareta_aco": {
        "name": "Picareta de Aço", "type": "ferramenta", "tool": "picareta", "power": 0.22, "quality": "incomum",
        "value": 150, "stack": 1,
        "description": "Aço temperado na ponta e freixo no cabo. Arranca carvão como quem tira pão do forno. "
                       "(+22% de chance na mineração)",
    },
    # ------------------------------------------------------------------ coleta e produção da Etapa 4
    "piche": {
        "name": "Pote de Piche", "type": "material", "quality": "comum", "value": 8, "stack": 20,
        "description": "Breu de flor-de-breu cozido até virar cola negra. Veda qualquer coisa — e gruda em tudo.",
    },
    "remendo_lona": {
        "name": "Remendo de Lona", "type": "material", "quality": "comum", "value": 10, "stack": 10,
        "description": "Um retalho de lona grossa, tecido com fio de linho bem apertado. Serve para velas e cascos.",
    },
    "tecido_negro": {
        "name": "Tecido Negro", "type": "material", "quality": "comum", "value": 6, "stack": 50,
        "description": "Retalhos das capas do culto: lã fina, tingida de preto, com fios prateados na barra.",
    },
    "poeira_lunar": {
        "name": "Poeira Lunar", "type": "material", "quality": "incomum", "value": 12, "stack": 50,
        "description": "Um pó prateado e frio que brilha no escuro. Fica nos dedos de quem toca os ecos.",
    },
    "carpa_prateada": {
        "name": "Carpa Prateada Crua", "type": "material", "quality": "comum", "value": 12, "stack": 20,
        "description": "Uma carpa gorda de escamas prateadas, do poço fundo da ilhota.",
    },
    "carpa_assada": {
        "name": "Carpa Prateada Assada", "type": "consumivel", "quality": "comum", "value": 24, "stack": 20,
        "use": {"heal_pct": 65, "combat": False, "minutes": 10,
                "verb": "A carne da carpa é branca, gorda e cheira a lago limpo.",
                "buff": {"id": "bem_alimentado", "name": "Bem alimentado", "group": "comida", "minutes": 120,
                         "stats": {"vigor": 3, "espirito": 3}}},
        "description": "Restaura 65% da vida fora de combate. Bem alimentado: +3 de Vigor e +3 de Espírito por "
                       "2 horas.",
    },
    "rei_do_lago": {
        "name": "Rei do Lago", "type": "diverso", "quality": "raro", "value": 150, "stack": 5,
        "description": ("Um peixe do tamanho de um bezerro, de escamas azul-prateadas e uma barbatana dorsal que "
                        "parece mesmo uma coroa. Anselmo precisa ver isto."),
    },
    "vela_kobold": {
        "name": "Vela de Kobold", "type": "consumivel", "quality": "comum", "value": 6, "stack": 20,
        "use": {"combat": False, "minutes": 1,
                "verb": "Você acende o toco de vela e o prende no chapéu, como fazem os kobolds.",
                "buff": {"id": "vela_kobold", "name": "Vela acesa", "group": "luz", "minutes": 90, "vision": 1}},
        "description": "Cera amarela e pavio grosso, feita para durar. Acesa: +1 de raio de visão por 1h30.",
    },
    "pocao_cura_maior": {
        "name": "Poção de Cura Maior", "type": "consumivel", "quality": "incomum", "value": 120, "stack": 5,
        "use": {"heal": [240, 300], "verb": "A poção prateada desce fria e fecha até as feridas antigas."},
        "description": "Vermelho-escura com reflexos de prata. Restaura 240–300 de vida.",
    },
    "vestes_acolito": {
        "name": "Vestes de Acólito", "type": "armadura", "slot": "peito", "subtype": "tecido", "quality": "incomum",
        "armor": 14, "stats": {"intelecto": 3, "espirito": 3, "vigor": 1}, "value": 140, "stack": 1,
        "description": ("Tecido negro do culto, recortado de novo e sem a lua cortada no peito. Agora é só uma "
                        "boa veste."),
    },
    "capuz_negro": {
        "name": "Capuz Negro", "type": "armadura", "slot": "cabeca", "subtype": "tecido", "quality": "incomum",
        "armor": 10, "stats": {"intelecto": 2, "espirito": 2, "vigor": 1}, "value": 120, "stack": 1,
        "description": "Fundo o bastante para esconder o rosto e quente o bastante para as noites nas ruínas.",
    },
    # ------------------------------------------------------------------ saques comuns e sucata
    "garra_toupeira": {
        "name": "Garra de Toupeira-de-Ferro", "type": "lixo", "quality": "pobre", "value": 7, "stack": 20,
        "description": "Uma garra curva, dura como ferro de verdade. Os curtidores usam para raspar couro.",
    },
    "fragmento_runico": {
        "name": "Fragmento Rúnico", "type": "lixo", "quality": "pobre", "value": 9, "stack": 20,
        "description": "Um caco de pedra branca com metade de uma runa. Colecionadores de Alvorada pagam por isso.",
    },
    "presa_sombria": {
        "name": "Presa Sombria", "type": "lixo", "quality": "pobre", "value": 10, "stack": 20,
        "description": "Um dente negro que solta um fio de fumaça violeta quando ninguém está olhando.",
    },
    "ponta_flecha": {
        "name": "Pontas de Flecha de Ferro", "type": "lixo", "quality": "pobre", "value": 4, "stack": 20,
        "description": "Ferro bom, forjado com capricho. Alguém com mãos de ferreiro fez isto — e não por gosto.",
    },
    "bolsa_roubada": {
        "name": "Bolsa Roubada", "type": "lixo", "quality": "pobre", "value": 25, "stack": 5,
        "description": ("Uma bolsinha de couro com as iniciais de outra pessoa. Dentro, algumas moedas — vale o "
                        "que pesa."),
    },
    # ------------------------------------------------------------------ saques raros das criaturas
    "anel_geomante": {
        "name": "Anel do Geomante", "type": "joia", "slot": "anel", "quality": "incomum",
        "stats": {"intelecto": 2, "espirito": 2, "vigor": 1}, "value": 260, "stack": 1,
        "description": "Uma pedrinha lisa amarrada num aro de cobre. Quando você fica parado, ela zumbe.",
    },
    "luvas_toupeira": {
        "name": "Luvas de Couro de Toupeira", "type": "armadura", "slot": "maos", "subtype": "couro",
        "quality": "incomum", "armor": 18, "stats": {"forca": 2, "agilidade": 2}, "value": 240, "stack": 1,
        "description": "Couro duro como ferro, com as garras ainda nas pontas dos dedos.",
    },
    "amuleto_lua_cortada": {
        "name": "Amuleto da Lua Cortada", "type": "joia", "slot": "pescoco", "quality": "incomum",
        "stats": {"intelecto": 3, "espirito": 1, "vigor": 1}, "value": 280, "stack": 1,
        "description": "Prata negra em forma de lua partida. Pesa mais do que deveria, e esfria quando a lua sobe.",
    },
    "capa_negra": {
        "name": "Capa Negra de Guarda", "type": "armadura", "slot": "costas", "quality": "incomum",
        "armor": 16, "stats": {"forca": 2, "vigor": 2}, "value": 270, "stack": 1,
        "description": "Lã pesada, forrada de couro. Feita para esconder uma cota de malha — e quem a veste.",
    },
    "tiara_veltharas": {
        "name": "Tiara de Vel'Tharas", "type": "armadura", "slot": "cabeca", "subtype": "tecido", "quality": "raro",
        "armor": 12, "stats": {"intelecto": 3, "espirito": 3, "vigor": 1}, "value": 420, "stack": 1,
        "description": "Um fio de prata antiga com uma pedra-da-lua do tamanho de uma lágrima. Os ecos a usavam.",
    },
    "luvas_arqueiro": {
        "name": "Luvas de Arqueiro", "type": "armadura", "slot": "maos", "subtype": "couro", "quality": "incomum",
        "armor": 18, "stats": {"agilidade": 3, "vigor": 1}, "value": 260, "stack": 1,
        "description": "Couro fino nos dedos e grosso na palma. Cheiram a pena queimada.",
    },
    "ombreiras_brutamontes": {
        "name": "Ombreiras do Brutamontes", "type": "armadura", "slot": "ombros", "subtype": "malha",
        "quality": "incomum", "armor": 30, "stats": {"forca": 2, "vigor": 2}, "value": 280, "stack": 1,
        "description": "Duas placas de ferro amassadas, com pregos de enfeite. Largas como um portão.",
    },
    "botas_batedor": {
        "name": "Botas de Batedor", "type": "armadura", "slot": "pes", "subtype": "couro", "quality": "incomum",
        "armor": 24, "stats": {"agilidade": 3, "vigor": 1}, "value": 260, "stack": 1,
        "description": "Solado macio, que não faz barulho nem em cascalho. Os batedores do Corvo juram por elas.",
    },
    # ------------------------------------------------------------------ chefes da Etapa 4
    "machado_capataz": {
        "name": "Machado do Capataz", "type": "arma", "slot": "arma", "subtype": "machado", "quality": "raro",
        "damage": [11, 19], "stats": {"forca": 3, "vigor": 3}, "value": 900, "stack": 1,
        "description": "Ainda morno da forja violeta. Na lâmina, riscos que contam os dias do cativeiro de alguém.",
    },
    "botas_capataz": {
        "name": "Botas do Capataz", "type": "armadura", "slot": "pes", "subtype": "malha", "quality": "raro",
        "armor": 34, "stats": {"forca": 2, "vigor": 3}, "value": 850, "stack": 1,
        "description": "Botas de ferro com biqueira de aço, feitas para chutar kobolds. Agora chutam coisa pior.",
    },
    "cinto_capataz": {
        "name": "Cinto do Capataz", "type": "armadura", "slot": "cintura", "subtype": "couro", "quality": "raro",
        "armor": 22, "stats": {"agilidade": 3, "vigor": 2}, "value": 820, "stack": 1,
        "description": "Couro grosso com fivela de ferro e argolas para chaves — todas vazias, agora.",
    },
    "adaga_corvo": {
        "name": "Bico do Corvo", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "raro",
        "damage": [9, 15], "stats": {"agilidade": 4, "vigor": 2}, "value": 950, "stack": 1,
        "description": "Uma adaga curva e negra como um bico. O cabo é enrolado em penas trançadas.",
    },
    "gibao_corvo": {
        "name": "Gibão do Corvo-Negro", "type": "armadura", "slot": "peito", "subtype": "couro", "quality": "raro",
        "armor": 48, "stats": {"agilidade": 4, "vigor": 2}, "value": 950, "stack": 1,
        "description": "Couro negro costurado com penas sobrepostas, como uma asa fechada.",
    },
    "espada_corvo": {
        "name": "Sabre de Ulric", "type": "arma", "slot": "arma", "subtype": "espada", "quality": "raro",
        "damage": [11, 18], "stats": {"forca": 3, "agilidade": 2}, "value": 980, "stack": 1,
        "description": "Um dos dois sabres curvos do chefe do Bando. O outro, dizem, está no fundo do Rio Largo.",
    },
    "capuz_corvo": {
        "name": "Capuz do Corvo-Negro", "type": "armadura", "slot": "cabeca", "subtype": "couro", "quality": "raro",
        "armor": 30, "stats": {"agilidade": 3, "vigor": 2}, "value": 900, "stack": 1,
        "description": "Um capuz com um bico de couro sobre os olhos. Quem o usa enxerga longe e é visto pouco.",
    },
    "cajado_lua_cortada": {
        "name": "Cajado da Lua Cortada", "type": "arma", "slot": "arma", "subtype": "cajado", "two_handed": True,
        "quality": "raro", "damage": [9, 16], "stats": {"intelecto": 6, "espirito": 3, "vigor": 2}, "value": 1200,
        "stack": 1,
        "description": "Ébano com um crescente de prata partido no topo. Ainda sussurra o nome de Morwen.",
    },
    "manto_senhora": {
        "name": "Manto da Senhora", "type": "armadura", "slot": "costas", "quality": "raro", "armor": 24,
        "stats": {"intelecto": 3, "espirito": 3, "vigor": 2}, "value": 1100, "stack": 1,
        "description": "Veludo negro bordado com todas as fases da lua — menos uma, rasgada a faca.",
    },
    "anel_lua_nova": {
        "name": "Anel da Lua Nova", "type": "joia", "slot": "anel", "quality": "raro",
        "stats": {"forca": 3, "agilidade": 3, "vigor": 2}, "value": 1050, "stack": 1,
        "description": "Um aro de ferro negro sem pedra nenhuma: a lua nova é a que não se vê.",
    },
    "adaga_eclipse": {
        "name": "Adaga do Eclipse", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "raro",
        "damage": [7, 12], "stats": {"intelecto": 4, "espirito": 3}, "value": 1000, "stack": 1,
        "description": "Uma adaga ritual de lâmina escura, que escurece ainda mais quando a lua some.",
    },
    "lagrima_vigia": {
        "name": "Lágrima do Vigia", "type": "joia", "slot": "anel", "quality": "epico",
        "stats": {"forca": 3, "agilidade": 3, "intelecto": 3, "espirito": 3, "vigor": 3}, "value": 3500, "stack": 1,
        "description": ("Uma gota de pedra-da-lua presa num aro de luar sólido. O Vigia chorou uma única vez em "
                        "trezentos anos — e foi quando acordou."),
    },
    # ------------------------------------------------------------------ recompensas de missões
    "escudo_davi": {
        "name": "Escudo do Aprendiz", "type": "escudo", "slot": "secundaria", "subtype": "escudo",
        "quality": "raro", "armor": 46, "stats": {"vigor": 3, "forca": 1}, "value": 400, "stack": 1,
        "description": "Forjado por Davi na primeira semana de volta à forja. No verso, gravado: \"obrigado\".",
    },
    "cajado_aco": {
        "name": "Cajado com Ponteira de Aço", "type": "arma", "slot": "arma", "subtype": "cajado", "two_handed": True,
        "quality": "raro", "damage": [7, 13], "stats": {"intelecto": 4, "espirito": 2, "vigor": 2}, "value": 400,
        "stack": 1,
        "description": ("Freixo escuro com ponteira e anéis de aço. Davi jura que não sabe nada de magia. O cajado "
                        "discorda."),
    },
    "maca_davi": {
        "name": "Maça do Aprendiz", "type": "arma", "slot": "arma", "subtype": "maca", "quality": "raro",
        "damage": [9, 15], "stats": {"espirito": 3, "intelecto": 2, "vigor": 1}, "value": 400, "stack": 1,
        "description": "Uma maça de aço com um sol cinzelado por mãos ainda inseguras — e muito caprichosas.",
    },
    "adaga_davi": {
        "name": "Adaga do Aprendiz", "type": "arma", "slot": "arma", "subtype": "adaga", "quality": "raro",
        "damage": [8, 13], "stats": {"agilidade": 3, "vigor": 2}, "value": 400, "stack": 1,
        "description": "Equilibrada para a mão de quem sabe usá-la. Davi testou o fio cortando um fio de cabelo.",
    },
    "anel_guarda": {
        "name": "Anel da Guarda do Vale", "type": "joia", "slot": "anel", "quality": "raro", "value": 600, "stack": 1,
        "stats": {"vigor": 3, "forca": 1, "agilidade": 1, "intelecto": 1, "espirito": 1},
        "description": ("Bronze gasto com o brasão do vale — o sol atrás da montanha. Renna só deu três destes na "
                        "vida."),
    },
    "capa_guarda": {
        "name": "Capa da Guarda", "type": "armadura", "slot": "costas", "quality": "incomum", "armor": 18,
        "stats": {"vigor": 3, "forca": 1, "agilidade": 1}, "value": 300, "stack": 1,
        "description": "Azul-escura, com o brasão do vale bordado nas costas. Tomé tem uma igual — de brinquedo.",
    },
    "simbolo_aurora": {
        "name": "Símbolo da Aurora", "type": "joia", "slot": "pescoco", "quality": "incomum",
        "stats": {"espirito": 3, "vigor": 2, "intelecto": 1}, "value": 260, "stack": 1,
        "description": "Um sol de latão polido num cordão de linho. Esquenta um pouco ao amanhecer.",
    },
    "vara_anselmo": {
        "name": "Vara do Anselmo", "type": "ferramenta", "tool": "vara", "power": 0.15, "quality": "raro",
        "value": 300, "stack": 1,
        "description": "Bambu curado por quarenta anos e uma linha que já segurou um rei. (+15% de chance na pesca)",
    },
    "manto_vigias": {
        "name": "Manto dos Vigias da Lua", "type": "armadura", "slot": "costas", "quality": "epico", "armor": 30,
        "stats": {"vigor": 4, "forca": 2, "agilidade": 2, "intelecto": 2, "espirito": 2}, "value": 3000, "stack": 1,
        "description": ("O manto cinza-prateado dos antigos Vigias, guardado por Ysolde a vida inteira para "
                        "\"quem um dia merecer\". Sob a lua, ele brilha de leve."),
    },
    # ------------------------------------------------------------------ missão: as três luas e o vale
    "lua_cheia": {
        "name": "Lua Cheia", "type": "missao", "quality": "raro", "value": 0, "stack": 1,
        "description": ("Um disco de pedra-da-lua do tamanho da palma da mão, perfeitamente redondo. Brilha como a "
                        "lua cheia — e, de perto, você ouve uma nota longa e grave."),
    },
    "metades_lua_minguante": {
        "name": "Metades da Lua Minguante", "type": "missao", "quality": "raro", "value": 0, "stack": 1,
        "description": ("As duas metades de um crescente de pedra-da-lua, partido com violência. A luz delas pisca, "
                        "fraca, como um coração doente. Talvez um bom ferreiro consiga juntá-las."),
    },
    "lua_minguante": {
        "name": "Lua Minguante", "type": "missao", "quality": "raro", "value": 0, "stack": 1,
        "description": ("O crescente minguante, unido de novo por um fio de prata. A cicatriz brilha mais que o "
                        "resto da pedra."),
    },
    "chave_lua_cortada": {
        "name": "Chave da Lua Cortada", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": ("Uma chave de pedra negra em forma de lua partida, morna ao toque. Não há fechadura no vale "
                        "com esse formato... a não ser, talvez, nas ruínas."),
    },
    "chave_capataz": {
        "name": "Chave do Capataz", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": "Uma chave de ferro pesada, presa num aro com a lua cortada. Abre algum cofre na mina.",
    },
    "carta_capataz": {
        "name": "Carta do Capataz", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": ("\"Gorran: mande as pontas de flecha a Ulric, no Desfiladeiro das Viúvas, toda lua nova. "
                        "O vale precisa continuar isolado até a noite sem lua. O aprendiz não sai da forja. "
                        "— M.\""),
    },
    "chave_corvo": {
        "name": "Chave do Corvo", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": "Uma chave de bronze com uma pena negra amarrada. Ulric a carregava no pescoço.",
    },
    "fardo_zahir": {
        "name": "Fardo de Seda de Zahir", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": "Um fardo de seda de Qadira com o selo de cera de Zahir ibn Kadir. Ainda intacto.",
    },
}

#: Itens que todo herói carrega no início da jornada (além dos itens da classe).
STARTING_ITEMS = [["pao_de_viagem", 4], ["cantil_agua", 2], ["tocha", 2], ["cartaz_convocacao", 1]]
STARTING_COPPER = 250
