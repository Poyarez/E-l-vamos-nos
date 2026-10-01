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
}

#: Itens que todo herói carrega no início da jornada (além dos itens da classe).
STARTING_ITEMS = [["pao_de_viagem", 4], ["cantil_agua", 2], ["tocha", 2], ["cartaz_convocacao", 1]]
STARTING_COPPER = 250
