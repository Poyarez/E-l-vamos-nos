"""NPCs do Vale de Primórdia e seus diálogos.

Estrutura de um NPC:
  ``schedule`` — onde o NPC está em cada período do dia (a primeira regra que bate vale;
  sem regra correspondente, o NPC não está no mapa naquele horário). Uma regra pode ter
  ``if`` (o NPC só aparece sob condições: fantasmas, resgatados, mercadores que chegam
  com a história) e ``map`` (outro mapa que não o de ``map``).
  ``dialogue`` — nós de conversa. A conversa começa em ``"inicio"``.

Estrutura de um nó:
  ``text``    — falas. Linhas entre *asteriscos* são narração. Uma linha pode ser
                ``{"if": {...}, "text": "..."}`` para aparecer só sob condições.
  ``options`` — escolhas: ``{"text", "next", "if"}`` (``next: None`` encerra a conversa).
  ``next``    — sem opções: volta automaticamente para este nó.
  ``effects`` — ao exibir o nó: ``set_flag``, ``journal``, ``xp``, ``give_item`` e
                ``take_item`` (``[item, qtd]`` ou uma lista desses pares), ``give_copper``,
                ``take_copper``, ``restore``, ``start_quest`` (começa uma missão de
                ``rpg.data.quests``), ``reset_talents`` e ``open_shop`` (abre a loja do NPC,
                definida em ``shop``, assim que a conversa termina).

Condições (``if``): as de ``rpg.conditions`` — ``flag``, ``not_flag``, ``journal``,
``discovered``, ``class``, ``moral``, ``law``, ``period``, ``night``, ``met``, ``min_level``,
``item`` (ter ``[item, qtd]`` na mochila), ``owns``, ``skill`` (``{"perícia": nível}``),
``copper``, ``moon``, ``quest_active``/``quest_done``/``quest_stage``, ``talents`` e ``any``.

Marcadores de texto: ``{nome}``, ``{tratamento}``/``{Tratamento}``, ``{bem_vindo}``/``{Bem_vindo}``
e ``{classe}``.
"""

DAY = ["amanhecer", "manha", "tarde"]
AWAKE = ["amanhecer", "manha", "tarde", "entardecer", "noite"]

NPCS = {
    # ================================================================== ANCIÃ YSOLDE
    "ysolde": {
        "name": "Anciã Ysolde",
        "short": "Ysolde",
        "title": "Guardiã das Memórias do Vale",
        "color": "bright_magenta",
        "description": ("Uma senhora miúda, de trança branca até a cintura e olhos de um cinza tão claro que "
                        "parecem prateados."),
        "map": "vale_primordia",
        "schedule": [{"periods": AWAKE, "x": 28, "y": 13}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ela ergue os olhos de um pergaminho e sorri devagar.*"},
                    {"if": {"met": False}, "text": (
                        "Então o cartaz chegou a Alvorada, afinal. {Bem_vindo} a Primórdia, {tratamento}. Eu sou "
                        "Ysolde. Escrevi aquele cartaz com estas mãos velhas — e confesso que não esperava que "
                        "alguém viesse.")},
                    {"if": {"met": True}, "text": (
                        "*Ysolde aponta a cadeira à sua frente.* De volta, {nome}? Sente-se. O chá ainda está "
                        "quente.")},
                ],
                "options": [
                    {"text": "Quem é a senhora?", "next": "quem"},
                    {"text": "Por que o vale precisa de ajuda?", "next": "problemas"},
                    {"text": "O que são as ruínas a nordeste?", "next": "ruinas"},
                    {"text": "Encontrei uma passagem atrás da cachoeira.", "next": "gruta",
                     "if": {"flag": "segredo_cachoeira"}},
                    {"text": "Vi um mural na gruta: um gigante adormecido.", "next": "primordial",
                     "if": {"flag": "lenda_primordial"}},
                    {"text": "Como vai a busca pelas três luas?", "next": "luas_progresso",
                     "if": {"quest_active": "tres_luas", "not_flag": "vigia_desperto"}},
                    {"text": "O Vigia despertou. O Primordial voltou a dormir.", "next": "final",
                     "if": {"flag": "vigia_desperto", "not_flag": "ysolde_final"}},
                    {"text": "E agora, anciã? Como fica o vale?", "next": "depois", "if": {"flag": "ysolde_final"}},
                    {"text": "Com quem devo falar na vila?", "next": "conselhos"},
                    {"text": "Até logo, anciã.", "next": None},
                ],
            },
            "quem": {
                "text": [
                    ("Sou a guardiã das memórias deste vale. Quando eu era menina, minha avó me ensinou as "
                     "histórias que a avó dela lhe ensinou — e assim por diante, até o tempo em que as pedras "
                     "brancas ainda eram um templo."),
                    "Hoje sou só uma velha que lembra demais. Mas lembrar, {tratamento}, às vezes é a única arma que temos.",
                ],
                "next": "inicio",
            },
            "problemas": {
                "text": [
                    "*Ela pousa a xícara com cuidado, como se o assunto fosse frágil.*",
                    ("Começou há três luas, com os tremores. Pequenos, no início: louça tilintando nas prateleiras. "
                     "Depois, o Passo do Norte desabou e a estrada para Pedravale se fechou."),
                    ("Então vieram os lobos da Floresta Sussurrante, mais ousados e espertos, liderados por uma "
                     "fera branca que ninguém consegue caçar. Os mineiros fugiram da Mina de Ferro-Velho falando "
                     "de criaturas pequenas e cânticos no escuro. E, nas noites sem lua, uma luz violeta dança "
                     "sobre as ruínas."),
                    "Para completar, bandidos fecharam a Rota dos Mercadores, ao sul. Estamos isolados, {tratamento}. E com medo.",
                ],
                "effects": {"journal": {
                    "id": "rumor_tremores", "title": "Os problemas do vale",
                    "text": ("Desde as tremuras, há três luas: o Passo do Norte desabou, lobos liderados por uma fera "
                             "branca rondam a Floresta Sussurrante, criaturas tomaram a Mina de Ferro-Velho, uma luz "
                             "violeta surge nas ruínas e bandidos fecharam a Rota dos Mercadores.")}},
                "next": "inicio",
            },
            "ruinas": {
                "text": [
                    ("Vel'Tharas. Era assim que os antigos chamavam aquele lugar — e a si mesmos. Um povo que "
                     "viveu aqui muito antes de nós, que estudava a lua e falava com as pedras."),
                    ("Dizem as histórias que eles guardavam alguma coisa. Algo que dorme sob o vale. Quando "
                     "partiram — ou morreram, ninguém sabe —, deixaram seus Vigias para continuar a guarda. O "
                     "último deles, Kael, está enterrado no cemitério da colina."),
                    "*Ela fica em silêncio por um momento.* Às vezes acho que os tremores são esse algo se mexendo no sono.",
                ],
                "effects": {"journal": {
                    "id": "lenda_veltharas", "title": "O povo de Vel'Tharas",
                    "text": ("Os antigos de Vel'Tharas estudavam a lua e guardavam algo que dorme sob o vale. O "
                             "último Vigia da Lua, Kael, está enterrado no Cemitério da Colina.")}},
                "next": "inicio",
            },
            "gruta": {
                "text": [
                    ("*Os olhos prateados de Ysolde se arregalam.* A passagem atrás do véu? Minha avó falava "
                     "dela, mas eu achava que era história para crianças..."),
                    "Tome cuidado lá dentro, {nome}. Os Vigias não escondiam coisas sem motivo.",
                ],
                "next": "inicio",
            },
            "primordial": {
                "text": [
                    "*Ysolde empalidece e segura sua mão entre as dela, frias e finas como papel.*",
                    "Então é verdade. O Primordial... aquele que deu forma ao vale com as próprias mãos. E o sono dele está se rompendo.",
                    ("As três luas do mural — crescente, cheia e minguante. Os Vigias as usavam para cantar o sono "
                     "do gigante. Se alguém conseguisse reuni-las de novo, talvez desse para acalmá-lo. Ou para "
                     "acordá-lo de vez, se caírem nas mãos erradas."),
                    "Procure as luas, {nome}. E desconfie de quem também as procura.",
                ],
                "effects": {
                    "set_flag": "ysolde_tres_luas",
                    "journal": {
                        "id": "missao_tres_luas", "title": "As três luas",
                        "text": ("Segundo Ysolde, as três luas dos Vigias (crescente, cheia e minguante) podem "
                                 "acalmar o Primordial — ou despertá-lo de vez. Outras pessoas podem estar atrás "
                                 "delas.")},
                    "xp": 60,
                },
                "next": "inicio",
            },
            "luas_progresso": {
                "text": [
                    {"if": {"quest_stage": ["tres_luas", 0]}, "text": (
                        "A primeira lua... \"Onde a água cai em véu de prata, a lua dorme em sua casa.\" A balada do "
                        "bardo fala da cachoeira, {nome}. Procure atrás da água.")},
                    {"if": {"quest_stage": ["tres_luas", 1]}, "text": (
                        "Você achou a crescente! Agora precisamos de alguém que saiba das outras. Os Vigias estão "
                        "enterrados no cemitério da colina, e minha avó jurava que Kael nunca descansou de verdade. "
                        "Vá até o túmulo dele — à noite.")},
                    {"if": {"quest_stage": ["tres_luas", 2]}, "text": (
                        "Uma canção nas pedras da ilhota? Então você vai precisar de um barco. O Anselmo tem um — "
                        "furado, mas tem. Talvez você consiga consertá-lo.")},
                    {"if": {"quest_stage": ["tres_luas", 3]}, "text": (
                        "Com a canção, o Carvalho Ancião deve abrir o coração para você. Mas só à noite: árvores "
                        "velhas dormem de dia, como as velhas.")},
                    {"if": {"quest_stage": ["tres_luas", 4]}, "text": (
                        "A minguante está com a Senhora da Lua Cortada, sob o Círculo de Runas. A Torre Tombada diz "
                        "que o caminho se revela quando o olho se abre — na lua cheia. Ou talvez os próprios "
                        "cultistas carreguem alguma chave...")},
                    {"if": {"quest_stage": ["tres_luas", 5]}, "text": (
                        "Partida ao meio? *Ela fecha os olhos por um momento.* Prata une o que a lua quebra, dizia "
                        "minha avó. Leve as metades ao Brom — e uma barra de prata, se tiver.")},
                    {"if": {"quest_stage": ["tres_luas", 6]}, "text": (
                        "As três luas, enfim! *As mãos dela tremem.* Leve-as à porta selada, na gruta atrás da "
                        "cachoeira.")},
                    {"if": {"quest_stage": ["tres_luas", 7]}, "text": (
                        "O Vigia está atrás da porta, sonhando o pesadelo que plantaram nele. Vá com cuidado, "
                        "{nome}. Leve poções. Leve coragem. E volte.")},
                ],
                "next": "inicio",
            },
            "final": {
                "text": [
                    "*Ysolde fica muito tempo em silêncio. Depois ri baixinho, e as lágrimas descem sem pressa.*",
                    ("Os tremores pararam. Eu senti, hoje de manhã: a louça não tilintou. Pela primeira vez em três "
                     "luas, a louça não tilintou."),
                    ("*Ela abre um baú aos pés da cama e tira de lá um manto cinza-prateado, dobrado com cuidado.* "
                     "Era dos Vigias. Minha avó o guardou para \"quem um dia merecer\". Eu achava que esse dia não "
                     "vinha nunca."),
                    "Obrigada, {nome}. Em nome do vale — e em nome de todos os que cantaram antes de você.",
                ],
                "effects": {"set_flag": "ysolde_final"},
                "next": "inicio",
            },
            "depois": {
                "text": [
                    ("O vale vai se curar devagar, como os velhos. A mina trabalha de novo, as caravanas voltaram, "
                     "e as crianças brincam de \"Vigia e Senhora\" na praça — você sempre ganha, sabia?"),
                    ("Mas o Passo do Norte continua fechado, e a ponte do Rio Largo caiu. Lá fora, o mundo ainda "
                     "treme em outros lugares. Gente como você nunca fica sem estrada por muito tempo."),
                ],
                "next": "inicio",
            },
            "conselhos": {
                "text": [
                    ("A Capitã Renna guarda o Portão Norte: é durona, mas justa, e sabe tudo sobre os perigos lá "
                     "fora. Brom, o ferreiro, conhece cada pedra das colinas. A Irmã Celeste, na capela, cuida do "
                     "corpo e da alma."),
                    ("E se quiser ouvir boatos, vá ao Javali Dourado. Marta, a estalajadeira, ouve tudo — e o "
                     "bardo hospedado lá ouve o resto."),
                ],
                "next": "inicio",
            },
        },
    },
    # ================================================================== CAPITÃ RENNA
    "renna": {
        "name": "Capitã Renna Valbrand",
        "short": "Renna",
        "title": "Capitã da Guarda do Vale",
        "color": "bright_blue",
        "description": ("Alta, de cabelo raspado nas laterais e uma cicatriz no queixo. A armadura de couro leva o "
                        "brasão do vale, e a mão dela nunca sai do cabo da espada."),
        "map": "vale_primordia",
        "schedule": [{"periods": ["amanhecer", "manha", "tarde", "entardecer"], "x": 30, "y": 11},
                     {"periods": ["noite"], "x": 33, "y": 14}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ela mede você de cima a baixo, sem pressa.*"},
                    {"if": {"met": False}, "text": (
                        "Renna Valbrand, capitã da guarda — de uma guarda de seis pessoas, se contar o Tomé, e eu "
                        "não conto. Você veio pelo cartaz da Anciã, imagino.")},
                    {"if": {"met": False, "class": "guerreiro"},
                     "text": "Postura de quem já segurou um escudo de verdade. Bom. Preciso de gente assim."},
                    {"if": {"met": False, "class": "mago"}, "text": (
                        "Magia, é? Só peço uma coisa: nada de bolas de fogo perto do trigal. O último que veio "
                        "quase queimou a colheita.")},
                    {"if": {"met": False, "class": "sacerdote"},
                     "text": "Que a Aurora abençoe seu caminho — e o nosso também, que estamos precisando."},
                    {"if": {"met": False, "class": "ladino"},
                     "text": "Hum. Vou contar minhas moedas depois que você for embora. Nada pessoal."},
                    {"if": {"met": False, "moral": "mau"},
                     "text": "*Os olhos dela se estreitam.* E saiba: estou de olho em você."},
                    {"if": {"met": True}, "text": "*Ela acena com a cabeça.* {Tratamento}. Alguma novidade lá fora?"},
                ],
                "options": [
                    {"text": "Que perigos há no vale?", "next": "perigos"},
                    {"text": "O que aconteceu com a Rota dos Mercadores?", "next": "rota"},
                    {"text": "E o Passo do Norte?", "next": "passo"},
                    {"text": "Quem é Tomé?", "next": "tome"},
                    {"text": "Vi a marca de uma bota humana na Toca dos Lobos.", "next": "toca",
                     "if": {"discovered": "toca_lobos"}},
                    {"text": "Encontrei esta aljava na toca. Tem as iniciais R. V.", "next": "aljava",
                     "if": {"flag": "toca_aljava", "not_flag": "renna_aljava"}},
                    {"text": "O domador da toca usava esta coleira: uma lua cortada.", "next": "coleira",
                     "if": {"flag": "varek_derrotado", "not_flag": "renna_viu_coleira"}},
                    {"text": "O Alfa Branco está morto. A Toca dos Lobos está livre.", "next": "alfa",
                     "if": {"flag": "presa_de_gelo_derrotado", "not_flag": "renna_recompensa_alfa"}},
                    {"text": "Você parece preocupada, capitã.", "next": "tome_sumiu",
                     "if": {"min_level": 9, "not_flag": "renna_tome_sumiu"}},
                    {"text": "Tomé está a salvo. Ele já está voltando para casa.", "next": "tome_salvo",
                     "if": {"flag": "tome_salvo", "not_flag": "renna_tome"}},
                    {"text": "Encontrei esta carta no cofre do capataz da mina.", "next": "carta",
                     "if": {"item": "carta_capataz", "not_flag": "renna_carta"}},
                    {"text": "Ulric Corvo-Negro está morto. O Bando do Corvo acabou.", "next": "rota_livre",
                     "if": {"flag": "ulric_derrotado", "not_flag": "rota_liberada"}},
                    {"text": "Até mais, capitã.", "next": None},
                ],
            },
            "perigos": {
                "text": [
                    ("Escute bem, que não vou repetir. A oeste, a Floresta Sussurrante: os lobos estão estranhos, "
                     "organizados demais, e quem manda neles é uma fera branca de olhos azuis. Já perdemos dois "
                     "caçadores."),
                    ("A leste, nas colinas, a Mina de Ferro-Velho. Algo tomou o lugar: coisas pequenas, muitas, "
                     "que cantam no escuro. E a nordeste, as ruínas... ali eu nem mando meus guardas."),
                    "Durante o dia, as estradas são seguras. À noite, fique perto da vila. Isso não é um conselho, é uma ordem.",
                ],
                "effects": {"journal": {
                    "id": "rumor_perigos", "title": "Os perigos do vale",
                    "text": ("A Capitã Renna alerta: lobos organizados, liderados por uma fera branca de olhos azuis, "
                             "na Floresta Sussurrante; criaturas pequenas que cantam no escuro na Mina de "
                             "Ferro-Velho; e as ruínas, onde nem a guarda entra. À noite, fique perto da vila.")}},
                "next": "inicio",
            },
            "rota": {
                "text": [
                    ("O Bando do Corvo. Bandidos que desceram das terras áridas do sul e decidiram que a Rota dos "
                     "Mercadores é deles. Atacam caravanas, cobram 'pedágio' e somem nas colinas."),
                    ("Fechei o Portão Sul para ninguém morrer à toa. A caravana do Zahir, nos Prados do Norte, foi "
                     "a última a passar — e por pouco."),
                ],
                "effects": {"journal": {
                    "id": "rumor_bandidos", "title": "O Bando do Corvo",
                    "text": ("Bandidos do Bando do Corvo dominam a Rota dos Mercadores. O Portão Sul do Vale está "
                             "fechado por ordem da Capitã Renna.")}},
                "next": "inicio",
            },
            "passo": {
                "text": [
                    ("Desabou na primeira grande tremura. Mandei dois homens olharem: voltaram jurando que as "
                     "pedras estavam derretidas, como vidro. Pedras não derretem sozinhas, {tratamento}."),
                    "Pedravale deve estar tentando abrir do lado de lá. Até lá, estamos presos.",
                ],
                "next": "inicio",
            },
            "tome": {
                "text": [
                    ("*Ela suspira longamente.* Meu sobrinho. Dezesseis anos e a cabeça cheia de histórias de "
                     "heróis. Já tentou entrar na mina duas vezes e nas ruínas uma vez."),
                    "Se vir um garoto magrelo com uma espada de madeira fazendo besteira, me avise.",
                ],
                "next": "inicio",
            },
            "toca": {
                "text": [
                    ("*Renna fica muito séria. Ela olha para o norte, na direção das ruínas, e depois de volta "
                     "para você.* Bota humana? Então não é só fome nem loucura dos bichos. Alguém está por trás "
                     "disso."),
                    "Não comente com ninguém, por enquanto. Não quero pânico na vila.",
                ],
                "effects": {
                    "set_flag": "renna_suspeita",
                    "journal": {
                        "id": "pista_bota", "title": "Pegadas humanas na Toca dos Lobos",
                        "text": ("Junto às pegadas da fera branca havia a marca de uma bota humana. A Capitã Renna "
                                 "suspeita que alguém controla os lobos.")},
                },
                "next": "inicio",
            },
            "aljava": {
                "text": [
                    ("*Renna pega a aljava com as duas mãos. Por um longo momento, ela não diz nada. Quando "
                     "fala, a voz falha.*"),
                    ("Rurik. Meu irmão mais novo. Era um dos dois caçadores que não voltaram. Fui eu que ensinei "
                     "ele a atirar..."),
                    ("*Ela passa os dedos pelas penas azuis da última flecha e respira fundo, voltando a ser a "
                     "capitã.* Obrigada, {nome}. Pelo menos agora eu sei. Pelo menos agora ele pode ter um túmulo."),
                ],
                "effects": {
                    "take_item": ["aljava_gravada", 1],
                    "set_flag": "renna_aljava",
                    "xp": 150,
                    "journal": {
                        "id": "rurik_valbrand", "title": "Rurik Valbrand",
                        "text": ("A aljava encontrada na Galeria dos Ossos pertencia a Rurik Valbrand, irmão da "
                                 "Capitã Renna e um dos caçadores desaparecidos na Floresta Sussurrante.")},
                },
                "next": "inicio",
            },
            "coleira": {
                "text": [
                    ("*Renna examina a coleira e passa o polegar sobre a placa de prata. O rosto dela "
                     "endurece.*"),
                    ("A lua cortada. Já vi esse símbolo riscado nas pedras das ruínas e em árvores mortas. Achei "
                     "que fosse coisa de moleque. Não é."),
                    ("Alguém está domando as feras do vale, {tratamento} — e alguém está mandando nesse alguém. "
                     "Fique de olhos abertos. E não confie em ninguém de capa negra."),
                ],
                "effects": {
                    "set_flag": "renna_viu_coleira",
                    "journal": {
                        "id": "pista_culto", "title": "O culto da Lua Cortada",
                        "text": ("Varek, o Domador, usava a lua cortada ao meio. A Capitã Renna acredita que há "
                                 "alguém acima dele, comandando as feras do vale.")},
                },
                "next": "inicio",
            },
            "alfa": {
                "text": [
                    ("*Renna fica em silêncio por um longo instante. Depois, devagar, tira a mão do cabo da "
                     "espada.*"),
                    ("Presa-de-Gelo... morto. Por você. *Ela solta uma risada curta, incrédula.* Os caçadores vão "
                     "poder voltar para a floresta. As crianças vão poder brincar perto da orla de novo."),
                    ("Tome. É pouco, mas é o que o vale pode pagar. E saiba: de hoje em diante, a guarda de "
                     "Primórdia confia em você."),
                ],
                "effects": {"set_flag": "renna_recompensa_alfa", "give_copper": 500, "xp": 250},
                "next": "inicio",
            },
            "tome_sumiu": {
                "text": [
                    ("*Renna esfrega o rosto com as duas mãos.* O Tomé sumiu. Ontem à noite ele saiu dizendo que ia "
                     "ver \"o olho se abrir\", lá na Torre Tombada, nas ruínas. Não voltou."),
                    ("Eu não posso largar o portão: se eu sair, metade da guarda vai atrás de mim, e a vila fica "
                     "aberta. *Ela olha nos seus olhos.* Você pode ir? À noite. É à noite que aquele lugar acorda."),
                ],
                "effects": {"set_flag": "renna_tome_sumiu", "start_quest": "sobrinho"},
                "next": "inicio",
            },
            "tome_salvo": {
                "text": [
                    "*Renna fecha os olhos e solta o ar devagar, como se o segurasse desde ontem.*",
                    ("Cultistas. Na torre. Com o meu sobrinho. *A mão dela aperta o cabo da espada até os dedos "
                     "ficarem brancos.* Obrigada, {nome}. De verdade."),
                    ("Tome: a capa da guarda. Era do meu pai. O Tomé vai ficar com inveja — ótimo. Talvez assim ele "
                     "entenda que capa se ganha, não se pega."),
                ],
                "effects": {"set_flag": "renna_tome"},
                "next": "inicio",
            },
            "carta": {
                "text": [
                    "*Renna lê a carta uma vez. Depois lê de novo, mais devagar, e o rosto dela vai endurecendo.*",
                    ("\"M.\" — a Senhora da Lua Cortada. Então é isso: o culto paga o Bando do Corvo com as flechas "
                     "da mina para manter o vale isolado. Ninguém entra, ninguém sai, ninguém pede ajuda."),
                    ("*Ela dobra a carta e a guarda no peito.* Vou abrir o Portão Sul — para você. Desça a Rota dos "
                     "Mercadores, encontre o acampamento desse tal Ulric e acabe com o Bando. Sem flechas, sem "
                     "pedágio, sem cerco."),
                ],
                "effects": {
                    "take_item": ["carta_capataz", 1],
                    "set_flag": ["renna_carta", "rota_aberta"],
                    "journal": {
                        "id": "portao_sul_aberto", "title": "O Portão Sul se abre",
                        "text": ("A carta do capataz prova que o culto paga o Bando do Corvo para isolar o vale. A "
                                 "Capitã Renna abriu o Portão Sul: o acampamento de Ulric Corvo-Negro fica em algum "
                                 "lugar da Rota dos Mercadores.")},
                },
                "next": "inicio",
            },
            "rota_livre": {
                "text": [
                    "*Renna fica um bom tempo olhando para o sul, para a estrada vazia.*",
                    ("Então acabou. Amanhã mesmo eu mando avisar Alvorada: a Rota dos Mercadores está aberta. As "
                     "caravanas vão voltar, e o Zahir finalmente vai poder vender aquela seda toda."),
                    ("*Ela tira do dedo um anel de bronze gasto, com o brasão do vale.* A guarda de Primórdia só "
                     "deu três destes. Agora são quatro."),
                ],
                "effects": {"set_flag": "rota_liberada"},
                "next": "inicio",
            },
        },
    },
    # ================================================================== DONA GRAÇA, A QUITANDEIRA
    "graca": {
        "name": "Dona Graça",
        "short": "Graça",
        "title": "Quitandeira do Mercado",
        "color": "bright_green",
        "description": ("Uma senhora de lenço florido na cabeça, avental cheio de bolsos e o sorriso de quem já "
                        "viu de tudo — e vendeu metade."),
        "map": "vale_primordia",
        "shop": "graca",
        "schedule": [{"periods": ["manha", "tarde"], "x": 32, "y": 16}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ela ajeita as maçãs na banca e abre um sorriso largo.*"},
                    {"if": {"met": False}, "text": (
                        "Freguesia nova! Graça, às suas ordens. Pão, água, poções, tochas... E compro o que você "
                        "trouxer do mato, desde que esteja inteiro. Ou quase.")},
                    {"if": {"met": True}, "text": "Voltou, {nome}! Trouxe peles? Dentes? Fofoca? Eu compro tudo."},
                ],
                "options": [
                    {"text": "Quero negociar.", "next": "negociar"},
                    {"text": "O que você compra?", "next": "compra"},
                    {"text": "Como anda o mercado?", "next": "mercado"},
                    {"text": "Precisa de alguma ajuda, Dona Graça?", "next": "pedido", "if": {"not_flag": "graca_pedido"}},
                    {"text": "Trouxe cinco peles de lobo.", "next": "peles_entregues",
                     "if": {"quest_active": "peles", "item": ["pele_lobo", 5]}},
                    {"text": "Até mais, Dona Graça.", "next": None},
                ],
            },
            "negociar": {
                "text": ["Pois não! Vamos ver o que temos hoje..."],
                "effects": {"open_shop": True},
            },
            "compra": {
                "text": [
                    ("Peles, carnes, dentes, teias... tudo o que os bichos da floresta deixam para trás. Os "
                     "curtidores e alquimistas de Alvorada pagam bem — quando a estrada está aberta. Até lá, eu "
                     "estoco."),
                    "*Ela baixa a voz.* E se achar alguma joia ou arma boa, pense duas vezes antes de vender. Lá fora, ela pode salvar a sua pele.",
                ],
                "next": "inicio",
            },
            "mercado": {
                "text": [
                    {"if": {"not_flag": "rota_liberada"}, "text": (
                        "Fraco, {tratamento}. Sem as caravanas do sul, vendo pão para quem tem dinheiro e fiado para "
                        "quem não tem. Se as coisas não melhorarem, só os lobos vão engordar neste inverno.")},
                    {"if": {"flag": "rota_liberada"}, "text": (
                        "Com as caravanas de volta? Uma beleza! Vendi mais esta semana do que nas três luas "
                        "anteriores. E aquele Zahir montou banca do meu lado — concorrência boa, das que trazem "
                        "freguês.")},
                ],
                "next": "inicio",
            },
            "pedido": {
                "text": [
                    ("Ajuda? Ah, se preciso! O inverno vem aí, e meus netos estão sem casaco. Se você me trouxer "
                     "cinco peles de lobo — inteiras, hein! —, eu costuro casacos para eles."),
                    "E para você eu faço uma bolsa de lã das boas, que cabe o dobro do que parece.",
                ],
                "effects": {"set_flag": "graca_pedido", "start_quest": "peles"},
                "next": "inicio",
            },
            "peles_entregues": {
                "text": [
                    "*Graça examina cada pele contra a luz, puxa o pelo, cheira, e finalmente sorri.*",
                    "Peles boas! Os meninos vão passar o inverno parecendo filhotes de lobo. Tome a sua bolsa, como prometi.",
                ],
                "effects": {"take_item": ["pele_lobo", 5], "set_flag": "graca_peles"},
                "next": "inicio",
            },
        },
    },
    # ================================================================== BROM, O FERREIRO
    "brom": {
        "name": "Brom Martelo-Rubro",
        "short": "Brom",
        "title": "Ferreiro da Vila",
        "color": "bright_red",
        "description": "Um homem enorme, de barba ruiva trançada e braços cobertos de cicatrizes de queimadura.",
        "map": "vale_primordia",
        "shop": "brom",
        "schedule": [{"periods": DAY, "x": 28, "y": 16}, {"periods": ["entardecer", "noite"], "x": 33, "y": 14}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ele larga o martelo na bigorna; o som ecoa como um sino.*"},
                    {"if": {"met": False}, "text": (
                        "Brom Martelo-Rubro, ferreiro. Se precisar de lâmina afiada, ferradura ou dente consertado "
                        "— sim, já fiz isso também —, é comigo.")},
                    {"if": {"met": True}, "text": "*Brom limpa as mãos no avental de couro.* {nome}! Precisa de alguma coisa?"},
                ],
                "options": [
                    {"text": "Pode me ensinar a trabalhar o metal?", "next": "metalurgia",
                     "if": {"not_flag": "brom_aula"}},
                    {"text": "Como funciona mesmo a forja?", "next": "forja_ajuda", "if": {"flag": "brom_aula"}},
                    {"text": "Olhe: fundi minha primeira barra de bronze!", "next": "primeira_barra",
                     "if": {"flag": "brom_aula", "not_flag": "brom_primeira_barra", "item": "barra_bronze"}},
                    {"text": "Quero ver suas mercadorias.", "next": "negociar"},
                    {"text": "Onde consigo minério?", "next": "minerio"},
                    {"text": "De quem é o martelo com o nome \"Davi\"?", "next": "davi",
                     "if": {"discovered": "forja", "not_flag": "davi_resgatado"}},
                    {"text": "Davi está vivo! Eu o tirei da mina.", "next": "davi_voltou",
                     "if": {"flag": "davi_resgatado", "not_flag": "brom_davi_voltou"}},
                    {"text": "Consegue juntar as duas metades desta lua de pedra?", "next": "metades",
                     "if": {"item": "metades_lua_minguante"}},
                    {"text": "Até mais, Brom.", "next": None},
                ],
            },
            "metalurgia": {
                "text": [
                    ("*Ele ri, uma risada grave.* Ensinar? Com prazer! Mas metal sem minério é só vontade. Arranje "
                     "uma picareta, traga cobre e estanho das colinas, e eu mostro como fundir sua primeira barra "
                     "de bronze."),
                    "Todo ferreiro começa assim: com as mãos sujas e os dedos queimados.",
                    ("*Ele tira um martelo de uma prateleira e o joga para você.* Tome, um dos meus velhos. Sem "
                     "martelo, bigorna é só um peso de porta."),
                ],
                "effects": {
                    "set_flag": "brom_aula",
                    "give_item": ["martelo_ferreiro", 1],
                    "journal": {
                        "id": "pista_metalurgia", "title": "Aulas de metalurgia",
                        "text": ("Brom ensina a fundir bronze a quem trouxer minério de cobre e estanho das Colinas "
                                 "de Cobre. Na fornalha da forja, cobre e estanho viram barras; na bigorna, as "
                                 "barras viram armas e armaduras (comando 'forjar'). Será preciso uma picareta "
                                 "('minerar').")}},
                "next": "inicio",
            },
            "forja_ajuda": {
                "text": [
                    ("Minério na fornalha vira barra: um de cobre e um de estanho dão bronze. Barra na bigorna vira "
                     "lâmina, elmo, escudo, picareta... É só dizer 'forjar' perto delas."),
                    ("Quanto mais você forja, mais coisas sabe fazer — e o ferro só obedece a quem já suou muito "
                     "no bronze. De noite eu tranco tudo: ladrão de ferro é o que não falta."),
                ],
                "next": "inicio",
            },
            "primeira_barra": {
                "text": [
                    "*Brom pega a barra, gira contra a luz e assente devagar.*",
                    ("Bolhas aqui, aqui... e uma rachadura. Péssima. *Ele abre um sorriso enorme.* A minha primeira "
                     "foi pior. Bem-vindo à forja, {nome}."),
                ],
                "effects": {"set_flag": "brom_primeira_barra", "xp": 100},
                "next": "inicio",
            },
            "negociar": {
                "text": ["Picaretas, martelos e o que mais sair da bigorna. Preço justo — mais ou menos."],
                "effects": {"open_shop": True},
            },
            "minerio": {
                "text": [
                    ("No Afloramento de Cobre, nas colinas a leste: cobre e estanho a céu aberto, fáceis de tirar. "
                     "Os mineiros largaram umas picaretas por lá quando fugiram; alguma ainda deve prestar. "
                     "Ferro bom mesmo, só na Mina de Ferro-Velho..."),
                    "*O rosto dele se fecha.* ...mas da mina ninguém chega mais perto.",
                ],
                "next": "inicio",
            },
            "davi": {
                "text": [
                    "*Brom fica em silêncio por um longo tempo. Quando fala, a voz sai baixa.*",
                    ("Davi era meu aprendiz. Bom menino, mãos firmes. Estava na mina, buscando ferro para a "
                     "primeira espada dele, quando veio a grande tremura. Os outros mineiros saíram correndo, "
                     "falando de monstros. Davi não saiu."),
                    "Deixei o martelo e o capacete dele ali. Um dia alguém vai me trazer notícias dele. Boas ou más, qualquer uma serve.",
                ],
                "effects": {"journal": {
                    "id": "pista_davi", "title": "O aprendiz desaparecido",
                    "text": ("Davi, aprendiz de Brom, desapareceu na Mina de Ferro-Velho durante a grande tremura. "
                             "Brom espera por notícias.")}},
                "next": "inicio",
            },
            "davi_voltou": {
                "text": [
                    ("*Brom larga o martelo e esmaga você num abraço que estala três costelas.* EU SEI! Ele entrou "
                     "por aquela porta pedindo pão e trabalho, nessa ordem!"),
                    ("Magro como um cabo de vassoura, mas inteiro. *O ferreiro enxuga os olhos com o avental, "
                     "fingindo que é fuligem.* Você trouxe o meu menino de volta, {nome}."),
                    ("E a mina livre quer dizer ferro de novo — e carvão. Vou ensinar o Davi a fazer aço, e a forja "
                     "volta a vender coisa boa. Ah, e ele fez questão de forjar uma peça para você, do jeito que "
                     "você luta. Não conte que eu contei."),
                ],
                "effects": {"set_flag": "brom_davi_voltou"},
                "next": "inicio",
            },
            "metades": {
                "text": [
                    "*Brom gira as duas metades contra a luz da forja, com uma delicadeza que você não esperava.*",
                    ("Pedra-da-lua. Nunca trabalhei com isso... Mas pedra quebrada se junta com metal macio. Prata, "
                     "de preferência — prata pura, da boa, como a do véu da cachoeira."),
                ],
                "options": [
                    {"text": "Aqui está uma barra de prata.", "next": "juntar_lua", "if": {"item": "barra_prata"}},
                    {"text": "Não tenho prata. Pode usar a sua? (3 moedas de prata)", "next": "juntar_lua_pago",
                     "if": {"copper": 300, "not_flag": "brom_lua_paga"}},
                    {"text": "Vou buscar a prata.", "next": "inicio"},
                ],
            },
            "juntar_lua_pago": {
                "text": [
                    ("*Brom some nos fundos da forja e volta com uma barrinha de prata embrulhada num pano.* Era para "
                     "a aliança de alguém que desistiu de casar. Melhor ter um destino nobre."),
                    ("*Ele aquece a prata até ela ficar mole como mel e a passa, com um pincel de ferro, na fratura "
                     "da pedra. As duas metades se encaixam com um estalo, e a luz delas para de piscar.*"),
                ],
                "effects": {"take_copper": 300, "set_flag": "brom_lua_paga",
                            "take_item": ["metades_lua_minguante", 1], "give_item": ["lua_minguante", 1], "xp": 300},
                "next": "inicio",
            },
            "juntar_lua": {
                "text": [
                    ("*Brom aquece a prata até ela ficar mole como mel e a passa, com um pincel de ferro, na fratura "
                     "da pedra. As duas metades se encaixam com um estalo, e a luz delas para de piscar.*"),
                    "Pronto. A cicatriz vai brilhar mais que o resto, mas... *ele dá de ombros* ...cicatriz também é história.",
                ],
                "effects": {"take_item": [["metades_lua_minguante", 1], ["barra_prata", 1]],
                            "give_item": ["lua_minguante", 1], "xp": 300},
                "next": "inicio",
            },
        },
    },
    # ================================================================== MARTA, A ESTALAJADEIRA
    "marta": {
        "name": "Marta",
        "short": "Marta",
        "title": "Estalajadeira do Javali Dourado",
        "color": "bright_yellow",
        "description": "Bochechas coradas, avental florido e quatro canecas equilibradas numa mão só.",
        "map": "vale_primordia",
        "schedule": [{"x": 33, "y": 14}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ela sorri para você com uma simpatia imediata — e um pouco avaliadora.*"},
                    {"if": {"met": False}, "text": (
                        "{Bem_vindo} ao Javali Dourado! Eu sou Marta. Sente-se, sente-se! Você tem cara de quem "
                        "passou três dias numa carroça — e cheira assim também, se me permite.")},
                    {"if": {"met": True}, "text": "{nome}! Seu canto perto da lareira está livre. O que vai ser hoje?"},
                ],
                "options": [
                    {"text": "Quero um quarto para descansar.", "next": "quarto"},
                    {"text": "Ouviu algum boato interessante?", "next": "boatos"},
                    {"text": "Quem é o bardo que toca aqui?", "next": "bardo"},
                    {"text": "Pode me ensinar a cozinhar?", "next": "cozinhar", "if": {"not_flag": "marta_cozinha"}},
                    {"text": "Alguma dica de cozinha?", "next": "dicas_cozinha", "if": {"flag": "marta_cozinha"}},
                    {"text": "\"Tobias + Marta\", na Pedra do Viajante...", "next": "tobias",
                     "if": {"discovered": "pedra_viajante"}},
                    {"text": "Até mais, Marta.", "next": None},
                ],
            },
            "cozinhar": {
                "text": [
                    ("*Ela joga um pano de prato no ombro.* Cozinhar? Fogo baixo, paciência alta e nunca, NUNCA vire "
                     "as costas para uma truta na grelha. Pode usar minha cozinha quando quiser — só lave as panelas."),
                    ("Leve estas carnes de javali para treinar. E, se um dia acertar a mão no ensopado, ponha uns "
                     "cogumelos-lume da floresta: é o segredo que eu não conto para ninguém."),
                ],
                "effects": {
                    "set_flag": "marta_cozinha",
                    "give_item": ["carne_javali", 2],
                    "journal": {
                        "id": "pista_culinaria", "title": "A cozinha do Javali Dourado",
                        "text": ("Marta deixa você usar a cozinha da estalagem (comando 'cozinhar'). O segredo do "
                                 "ensopado de javali dela: cogumelos-lume da floresta.")}},
                "next": "inicio",
            },
            "dicas_cozinha": {
                "text": [
                    ("Quanto mais você cozinha, menos queima. E a minha cozinha queima menos que qualquer fogueira "
                     "de acampamento — pode confiar."),
                    ("Comida boa faz mais que encher a barriga: quem come bem antes de sair luta melhor. Truta em "
                     "torta, javali em ensopado, lobo com as especiarias da caravana... Experimente!"),
                ],
                "next": "inicio",
            },
            "quarto": {
                "text": [
                    ("Os quartos ficam lá em cima, e para você é por conta da casa. Quem veio ajudar o vale não paga "
                     "para dormir no Javali!"),
                    "*(Use o comando 'descansar' aqui na estalagem para dormir até o amanhecer. O jogo é salvo ao acordar.)*",
                ],
                "next": "inicio",
            },
            "boatos": {
                "text": [
                    "*Marta se inclina sobre o balcão e baixa a voz.*",
                    ("Meu falecido Joaquim, que a Aurora o tenha, pescava perto da Cachoeira do Véu de Prata. Ele "
                     "jurava que, em noites de lua, via uma luz ATRÁS da água. Atrás, não na frente. Diziam que era "
                     "a bebida, mas o Joaquim nunca bebia antes de pescar."),
                    "E tem o espantalho do Tobias. As crianças dizem que ele muda de lugar à noite. Eu digo que é o Tobias que bebe. *Ela pisca.*",
                ],
                "effects": {"journal": [
                    {"id": "pista_cachoeira", "title": "Uma luz atrás da cachoeira",
                     "text": ("Marta contou que o falecido marido via, em noites de lua, uma luz ATRÁS da água da "
                              "Cachoeira do Véu de Prata, ao norte do vale.")},
                    {"id": "rumor_espantalho", "title": "O espantalho que anda",
                     "text": "As crianças da vila dizem que o espantalho do moinho de Tobias muda de lugar à noite."},
                ]},
                "next": "inicio",
            },
            "bardo": {
                "text": [
                    ("Lírio! Chegou com a última caravana e não foi mais embora — acho que se apaixonou pelo meu "
                     "ensopado. Ou pela plateia. De dia canta na praça por moedas; à noite, enche minha estalagem."),
                    "Se quiser uma canção sobre o vale, é só pedir. Ele sabe todas — e inventa as que não sabe.",
                ],
                "next": "inicio",
            },
            "tobias": {
                "text": [
                    "*Marta fica vermelha até a raiz dos cabelos.*",
                    ("Isso foi há quarenta anos! Éramos crianças! *Ela se abana com o avental.* O Tobias entalhou "
                     "aquilo, depois eu me casei com o Joaquim, e ele nunca me perdoou. Ou nunca se perdoou, sei lá."),
                    "Não conte para ninguém que você viu. Especialmente para o Tobias.",
                ],
                "next": "inicio",
            },
        },
    },
    # ================================================================== IRMÃ CELESTE
    "celeste": {
        "name": "Irmã Celeste",
        "short": "Celeste",
        "title": "Sacerdotisa da Aurora",
        "color": "bright_white",
        "description": "Jovem, de vestes brancas com um sol bordado a ouro. Há olheiras fundas sob seus olhos serenos.",
        "map": "vale_primordia",
        "schedule": [{"periods": AWAKE, "x": 31, "y": 12}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ela termina de acender uma vela e se vira com um sorriso sereno.*"},
                    {"if": {"met": False}, "text": (
                        "Que a Aurora ilumine seu caminho, {tratamento}. Sou a Irmã Celeste. As portas desta capela "
                        "estão sempre abertas a quem precisa de cura — ou de silêncio.")},
                    {"if": {"met": False, "class": "sacerdote"}, "text": (
                        "*Os olhos dela se iluminam ao ver o símbolo em suas vestes.* Alguém da fé! A Aurora ouviu "
                        "minhas preces. Há tanto trabalho e tão poucas mãos.")},
                    {"if": {"met": True}, "text": "{nome}. A paz da Aurora esteja com você."},
                ],
                "options": [
                    {"text": "Quem é a Senhora da Aurora?", "next": "aurora"},
                    {"text": "Por que há uma lua no vitral?", "next": "lua", "if": {"discovered": "capela"}},
                    {"text": "Você parece cansada.", "next": "cansada"},
                    {"text": "Pode me abençoar?", "next": "bencao"},
                    {"text": "Posso ajudar a capela de alguma forma?", "next": "ajuda", "if": {"not_flag": "celeste_pedido"}},
                    {"text": "Trouxe três poções de cura menor para os feridos.", "next": "pocoes",
                     "if": {"quest_active": "remedios", "item": ["pocao_cura_menor", 3]}},
                    {"text": "Pode me ajudar a esquecer o que aprendi? (talentos)", "next": "esquecer",
                     "if": {"min_level": 10, "talents": True}},
                    {"text": "Que a Aurora a guarde, Irmã.", "next": None},
                ],
            },
            "aurora": {
                "text": [
                    ("A Senhora da Aurora é a luz que vence toda noite. Ela não promete que a escuridão não virá — "
                     "apenas que, todas as manhãs, sem falta, ela volta."),
                    "Os antigos deste vale tinham uma fé mais velha. Mas cremos que a Aurora acolhe todas as luzes, até as da lua.",
                ],
                "next": "inicio",
            },
            "lua": {
                "text": [
                    ("*Ela olha para o vitral e sorri.* Poucos reparam. Os fundadores usaram pedras das ruínas para "
                     "erguer a capela e mandaram incluir a lua no vitral, por respeito aos Vigias que guardavam o "
                     "vale antes de nós."),
                    ("Há uma prece antiga: 'Que a Aurora nos guie e a Lua nos guarde, até que o Guardião desperte em "
                     "paz.' Rezamos sem entender. Talvez seja hora de entender."),
                ],
                "effects": {"journal": {
                    "id": "pista_guardiao", "title": "A prece do Guardião",
                    "text": ("A prece da Capela da Aurora fala de um Guardião que um dia despertará. Os fundadores da "
                             "vila respeitavam os antigos Vigias da Lua.")}},
                "next": "inicio",
            },
            "cansada": {
                "text": [
                    ("*Ela hesita.* São os sonhos. Desde as tremuras, toda noite sonho com o mesmo lugar: uma porta "
                     "de pedra, no escuro, com três buracos em forma de lua. E alguém do outro lado, respirando."),
                    "A Mãe Brígida, a erveira do pântano, diz que meus sonhos são verdadeiros. Tenho medo de que ela esteja certa.",
                ],
                "effects": {"journal": {
                    "id": "pista_sonhos", "title": "Os sonhos de Celeste",
                    "text": ("A Irmã Celeste sonha toda noite com uma porta de pedra com três buracos em forma de "
                             "lua — e alguém respirando do outro lado.")}},
                "next": "inicio",
            },
            "bencao": {
                "text": [
                    ("*Ela pousa a mão em sua testa e murmura uma prece. Um calor suave se espalha pelo seu corpo, "
                     "levando embora o cansaço da estrada.*"),
                    "Vá em paz, {nome}. E volte — é o que mais importa.",
                ],
                "effects": {"restore": True},
                "next": "inicio",
            },
            "ajuda": {
                "text": [
                    ("Desde as tremuras, a capela vive cheia: gente que caiu, que se cortou fugindo de lobo, que não "
                     "dorme. As poções da Mãe Brígida acabam antes de chegar aqui."),
                    "Se você conseguir três poções de cura menor, eu as divido entre os feridos. A Aurora retribui — e eu também.",
                ],
                "effects": {"set_flag": "celeste_pedido", "start_quest": "remedios"},
                "next": "inicio",
            },
            "pocoes": {
                "text": [
                    "*Celeste segura as poções como se fossem frágeis como ovos.*",
                    ("O velho Joaquim do moinho vai poder dormir. E a menina dos Moreira, que cortou a mão na cerca... "
                     "Obrigada, {nome}. Tome isto: um símbolo da Aurora, abençoado no altar."),
                ],
                "effects": {"take_item": ["pocao_cura_menor", 3], "set_flag": "celeste_remedios"},
                "next": "inicio",
            },
            "esquecer": {
                "text": [
                    ("A Aurora ensina que todo dia é um recomeço. Há uma prece antiga de esquecimento: ela devolve o "
                     "que você aprendeu nos seus caminhos de luta, para que possa escolher de novo."),
                    "Só peço uma oferta para o óleo das lamparinas: duas moedas de prata.",
                ],
                "options": [
                    {"text": "Faça a prece. (2 moedas de prata)", "next": "esquecer_feito", "if": {"copper": 200}},
                    {"text": "Agora não, Irmã.", "next": "inicio"},
                ],
            },
            "esquecer_feito": {
                "text": [
                    ("*Celeste pousa as mãos na sua cabeça e reza baixinho. Por um instante, você esquece o peso das "
                     "armas, o ritmo das magias, os truques aprendidos a duras penas... e sente tudo isso voltar, "
                     "leve, esperando ser escolhido de novo.*"),
                ],
                "effects": {"take_copper": 200, "reset_talents": True},
                "next": "inicio",
            },
        },
    },
    # ================================================================== ANSELMO, O PESCADOR
    "anselmo": {
        "name": "Velho Anselmo",
        "short": "Anselmo",
        "title": "Pescador do Lago",
        "color": "cyan",
        "description": "Pele queimada de sol, chapéu de palha furado e uma vara de pesca entre os joelhos.",
        "map": "vale_primordia",
        "shop": "anselmo",
        "schedule": [{"periods": DAY, "x": 41, "y": 22}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ele não tira os olhos da água.*"},
                    {"if": {"met": False}, "text": (
                        "Shh. Fala baixo. Os peixes deste lago são desconfiados como uma sogra. Anselmo, pescador. "
                        "Sente-se, se quiser — mas em silêncio.")},
                    {"if": {"met": True}, "text": "*Anselmo ergue dois dedos em cumprimento, sem tirar os olhos da linha.*"},
                ],
                "options": [
                    {"text": "Pode me ensinar a pescar?", "next": "pescar", "if": {"not_flag": "anselmo_rede"}},
                    {"text": "O que mais morde por aqui?", "next": "peixes", "if": {"flag": "anselmo_rede"}},
                    {"text": "Vende vara e iscas?", "next": "negociar"},
                    {"text": "Que ilhota é aquela no meio do lago?", "next": "ilhota"},
                    {"text": "O \"Rei do Lago\" existe mesmo?", "next": "rei"},
                    {"text": "Posso ajudar a consertar o seu barco?", "next": "barco",
                     "if": {"journal": "rumor_ilhota", "not_flag": "anselmo_barco"}},
                    {"text": "Trouxe os pregos, o piche e o remendo para o barco.", "next": "barco_pronto",
                     "if": {"flag": "anselmo_barco", "not_flag": "barco_consertado",
                            "item": [["pregos_bronze", 10], ["piche", 2], ["remendo_lona", 1]]}},
                    {"text": "E o Rei do Lago? Onde ele mora?", "next": "rei_missao",
                     "if": {"flag": "barco_consertado", "not_flag": "anselmo_rei_missao"}},
                    {"text": "Olhe o que eu fisguei no Poço do Rei!", "next": "rei_pescado",
                     "if": {"item": "rei_do_lago", "quest_active": "rei_do_lago"}},
                    {"text": "Você conhece a Cachoeira do Véu de Prata?", "next": "cachoeira"},
                    {"text": "Boa pescaria.", "next": None},
                ],
            },
            "pescar": {
                "text": [
                    ("Ensinar? *Ele finalmente olha para você, com um meio sorriso.* Pescar não se ensina, se aprende. "
                     "Arranje uma vara e iscas, sente aqui e espere. Camarão e sardinha mordem fácil. Truta, só no "
                     "ribeirão, e só para quem tem paciência."),
                    "Depois leve o que pescar para a Marta. Ela cozinha como ninguém — e talvez até ensine você.",
                    ("*Ele aponta com o queixo para as redes no varal.* Leve aquela ali, a remendada. Para "
                     "camarão, serve."),
                ],
                "effects": {
                    "set_flag": "anselmo_rede",
                    "give_item": ["rede_pesca", 1],
                    "journal": {
                        "id": "pista_pesca", "title": "Pescaria no lago",
                        "text": ("Anselmo diz que camarões (com rede) e sardinhas (com vara e minhocas) mordem fácil "
                                 "no Píer do Lago Espelhado; trutas, só no ribeirão. Comando: 'pescar'.")}},
                "next": "inicio",
            },
            "peixes": {
                "text": [
                    ("Camarão se pega de rede, aqui na beirada. Sardinha quer vara e minhoca. Truta e salmão moram no "
                     "Vau das Lavadeiras e só mordem mosca: pena de corvo amarrada no anzol."),
                    ("*Ele baixa a voz.* E dizem que debaixo da cachoeira tem um lago onde os peixes nem olhos têm. "
                     "Bobagem, claro. *Ele não parece achar bobagem.*"),
                ],
                "next": "inicio",
            },
            "negociar": {
                "text": ["*Anselmo indica um caixote sem tirar os olhos da água.* Vara, rede e minhoca. Pague o "
                         "que está escrito e não espante os peixes."],
                "effects": {"open_shop": True},
            },
            "ilhota": {
                "text": [
                    ("A Ilhota da Garça. Ninguém pisa lá faz anos. Meu barco furou, e os outros barqueiros não vão — "
                     "dizem que a ilha canta à noite."),
                    "*Ele cospe na água.* Bobagem. Mas que tem alguma coisa lá, tem. Toda lua cheia vejo uma luz azul entre as árvores.",
                ],
                "effects": {"journal": {
                    "id": "rumor_ilhota", "title": "A Ilhota da Garça",
                    "text": ("Ninguém visita a ilhota do Lago Espelhado há anos. Em noites de lua cheia, Anselmo vê uma "
                             "luz azul entre as árvores. Será preciso um barco.")}},
                "next": "inicio",
            },
            "rei": {
                "text": [
                    ("*Os olhos do velho brilham.* Existe. Um peixe do tamanho de um bezerro, escamas azul-prateadas "
                     "e uma barbatana que parece uma coroa. Fisguei uma vez, quarenta anos atrás. Ele arrebentou "
                     "minha linha e levou meu orgulho junto."),
                    "Um dia ele volta a morder. E eu vou estar aqui.",
                ],
                "next": "inicio",
            },
            "barco": {
                "text": [
                    ("*Anselmo tira o chapéu e coça a cabeça.* Consertar? Ele está furado de lado a lado, mas o "
                     "casco é bom. Carvalho do vale."),
                    ("Precisa de dez pregos de bronze, que não enferrujam; dois potes de piche para vedar; e um "
                     "remendo de lona para o buraco grande. O Brom faz pregos, a Brígida tem piche e a Graça vende "
                     "lona. Ou você mesmo faz, se tiver mãos para isso."),
                ],
                "effects": {"set_flag": "anselmo_barco", "start_quest": "barco"},
                "next": "inicio",
            },
            "barco_pronto": {
                "text": [
                    "*Anselmo examina cada prego, cheira o piche e estica o remendo contra o sol.*",
                    ("Serve. Serve muito bem. *Algumas horas e muitos palavrões depois, o barquinho flutua de novo, "
                     "sem uma gota de água dentro.* Pode usar quando quiser. Só traga ele de volta."),
                    "*(Use 'navegar' no píer para ir à Ilhota da Garça.)*",
                ],
                "effects": {"take_item": [["pregos_bronze", 10], ["piche", 2], ["remendo_lona", 1]],
                            "set_flag": "barco_consertado"},
                "next": "inicio",
            },
            "rei_missao": {
                "text": [
                    ("O Rei mora no Poço do Rei, na ponta leste da ilhota. Eu via ele de longe, quando ainda tinha "
                     "barco. Mas segurar um bicho daqueles... só um pescador de mão muito firme."),
                    ("*Ele estende a mão calejada.* Faça o seguinte: fisgue um Rei do Lago e me mostre. Se fizer "
                     "isso, eu dou a você a minha vara. Ela merece um dono que ainda tenha os dois joelhos bons."),
                ],
                "effects": {"set_flag": "anselmo_rei_missao", "start_quest": "rei_do_lago"},
                "next": "inicio",
            },
            "rei_pescado": {
                "text": [
                    "*Anselmo fica de pé pela primeira vez desde que você o conhece. O chapéu cai na água.*",
                    ("Um Rei do Lago. Um REI DO LAGO! Então são vários... o que arrebentou a minha linha há quarenta "
                     "anos devia ser o avô deste aqui. *Ele ri e chora ao mesmo tempo.*"),
                    "A vara é sua, como prometi. E o peixe vai para a Marta: hoje o Javali Dourado janta como um rei.",
                ],
                "effects": {"take_item": ["rei_do_lago", 1], "set_flag": "anselmo_rei"},
                "next": "inicio",
            },
            "cachoeira": {
                "text": [
                    ("Conheço. Pesquei lá a vida inteira com o Joaquim, que a Aurora o tenha. Ele vivia dizendo que "
                     "havia alguma coisa atrás da água."),
                    ("*Anselmo dá de ombros.* Eu nunca vi nada. Mas também nunca olhei de perto — aquelas pedras são "
                     "escorregadias como sabão, e eu gosto dos meus ossos inteiros."),
                ],
                "effects": {"journal": {
                    "id": "pista_cachoeira", "title": "Algo atrás da cachoeira",
                    "text": ("O falecido Joaquim dizia haver alguma coisa atrás da água da Cachoeira do Véu de Prata. "
                             "Ninguém nunca olhou de perto.")}},
                "next": "inicio",
            },
        },
    },
    # ================================================================== MÃE BRÍGIDA
    "brigida": {
        "name": "Mãe Brígida",
        "short": "Brígida",
        "title": "Erveira do Pântano",
        "color": "green",
        "description": "Corcunda, de nariz adunco, óculos redondos e olhos verdes vivíssimos. Cheira a hortelã e fumaça.",
        "map": "vale_primordia",
        "shop": "brigida",
        "schedule": [{"x": 9, "y": 23}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*A porta se abre antes que você bata.*"},
                    {"if": {"met": False}, "text": (
                        "Eu sabia que você vinha. Os sapos me contaram. *Ela ri, um cacarejo seco.* Entra, entra, que "
                        "o charco não é lugar de ficar parado. Mãe Brígida, a seu dispor — ou você ao meu, veremos.")},
                    {"if": {"met": False, "moral": "mau"}, "text": (
                        "*Ela fareja o ar e franze o nariz.* Hum. Cheiro de escolhas ruins. Não importa: escolhas "
                        "ruins também pagam bem.")},
                    {"if": {"met": True}, "text": "*Ela mexe o caldeirão sem olhar.* De volta, criança? O que o charco trouxe para mim hoje?"},
                ],
                "options": [
                    {"text": "Que remédios você prepara?", "next": "remedios", "if": {"not_flag": "brigida_aula"}},
                    {"text": "Como se faz uma poção mesmo?", "next": "alquimia_ajuda", "if": {"flag": "brigida_aula"}},
                    {"text": "Posso ver o que você vende?", "next": "negociar"},
                    {"text": "O que sabe sobre as tremuras?", "next": "tremuras"},
                    {"text": "A Irmã Celeste disse que você entende de sonhos.", "next": "sonhos",
                     "if": {"journal": "pista_sonhos"}},
                    {"text": "Por que há uma lua cortada na Árvore dos Enforcados?", "next": "arvore",
                     "if": {"discovered": "arvore_enforcados"}},
                    {"text": "Tirei esta chave de pedra negra de um acólito.", "next": "chave",
                     "if": {"item": "chave_lua_cortada"}},
                    {"text": "Preciso ir.", "next": None},
                ],
            },
            "remedios": {
                "text": [
                    ("Unguentos para cortes, xaropes para tosse, chás para coração partido — esses vendem mais. Tudo "
                     "do pântano. As melhores ervas crescem onde ninguém quer pisar."),
                    "Se quiser aprender, traga ervas e paciência. Alquimia não é cozinhar: é convencer as plantas a fazer o que você quer.",
                    ("*Ela enfia na sua mão um almofariz rachado e três frascos.* Toma. Folha-de-charco cresce aí "
                     "fora, até no meu quintal. Duas folhas, um frasco: poção de cura. Comece por aí."),
                ],
                "effects": {
                    "set_flag": "brigida_aula",
                    "give_item": [["almofariz", 1], ["frasco_vazio", 3]],
                    "journal": {
                        "id": "pista_alquimia", "title": "Lições de alquimia",
                        "text": ("Mãe Brígida ensina alquimia: ervas colhidas ('colher') viram poções no almofariz "
                                 "('preparar'). As misturas fortes — elixires, óleos e frascos — só no caldeirão "
                                 "da cabana dela.")}},
                "next": "inicio",
            },
            "alquimia_ajuda": {
                "text": [
                    ("Cada erva tem um gênio. Folha-de-charco fecha feridas, cogumelo-lume desperta a mana, "
                     "flor-de-breu quer pegar fogo, presa de javali deixa o sangue teimoso, glândula de aranha "
                     "envenena..."),
                    ("Poção simples você faz em qualquer canto, com o almofariz. Elixires, óleos e frascos de "
                     "arremesso, só no meu caldeirão — e comigo olhando. *Ela aponta um dedo torto.* E não toque "
                     "nos potes."),
                ],
                "next": "inicio",
            },
            "negociar": {
                "text": ["*Ela abre um armário que range como um gato velho.* Frascos, remédios, um almofariz novo. "
                         "Nada de olhos de sapo hoje: acabaram."],
                "effects": {"open_shop": True},
            },
            "tremuras": {
                "text": [
                    ("*Ela para de mexer o caldeirão.* O gigante está sonhando mal, criança. Sonho ruim faz a terra "
                     "tremer, as feras enlouquecerem e o fogo violeta subir. Os antigos sabiam cantar para ele dormir."),
                    "Mas os cantores morreram, e as canções se perderam. Ou quase. Três luas, três notas. Quem tiver as três, terá a canção.",
                ],
                "effects": {"journal": {
                    "id": "pista_gigante", "title": "O gigante que sonha",
                    "text": ("Mãe Brígida diz que um gigante sonha sob o vale e que os antigos cantavam para ele "
                             "dormir: \"três luas, três notas\".")}},
                "next": "inicio",
            },
            "sonhos": {
                "text": [
                    ("*Ela fica séria pela primeira vez.* A menina da capela sonha com a porta. Claro que sonha. "
                     "Sonhos verdadeiros procuram quem sabe ouvir."),
                    ("A porta existe, criança. Fica atrás da água que cai. E o que respira do outro lado espera "
                     "alguém com as três luas na mão."),
                ],
                "effects": {"journal": {
                    "id": "pista_porta", "title": "A porta atrás da água",
                    "text": ("Mãe Brígida confirma: a porta dos sonhos de Celeste existe e fica \"atrás da água que "
                             "cai\".")}},
                "next": "inicio",
            },
            "arvore": {
                "text": [
                    ("Lua minguante cortada ao meio. *Ela cospe no chão.* É a marca de quem quer quebrar o ciclo: "
                     "acordar o gigante de vez e tomar o poder dele para si."),
                    ("Tem gente no vale usando essa marca. Gente de capa negra, que anda à noite pelas ruínas. "
                     "Cuidado com eles, criança. Eles também procuram as luas."),
                ],
                "effects": {
                    "set_flag": "conhece_lua_cortada",
                    "journal": {
                        "id": "pista_capa_negra", "title": "A lua cortada",
                        "text": ("A lua minguante cortada ao meio é a marca de um grupo de capas negras que quer "
                                 "despertar o gigante. Eles também procuram as luas.")},
                },
                "next": "inicio",
            },
            "chave": {
                "text": [
                    ("*Brígida pega a chave com a ponta de dois dedos, como se fosse um sapo morto.* Pedra de lua "
                     "nova. Isso abre o que só se abre na lua cheia, criança."),
                    ("Já viu o disco das pedras que giram, nas ruínas? Com isto na mão, ele gira em qualquer noite. "
                     "Ou dia. *Ela devolve a chave.* E, onde tem chave, tem fechadura. Procure as duas."),
                ],
                "effects": {"journal": {
                    "id": "pista_chave_negra", "title": "A chave de lua nova",
                    "text": ("Segundo Mãe Brígida, a chave de pedra negra dos acólitos abre o disco do Círculo de "
                             "Pedras Rúnicas em qualquer noite — e talvez alguma fechadura do culto.")}},
                "next": "inicio",
            },
        },
    },
    # ================================================================== LÍRIO, O BARDO
    "lirio": {
        "name": "Lírio",
        "short": "Lírio",
        "title": "Bardo Errante",
        "color": "magenta",
        "description": "Chapéu emplumado, sorriso enorme e um alaúde que parece mais bem cuidado que o próprio dono.",
        "map": "vale_primordia",
        "schedule": [{"periods": ["manha", "tarde"], "x": 30, "y": 15},
                     {"periods": ["entardecer", "noite"], "x": 33, "y": 14}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ele arremata a melodia que tocava com um floreio exagerado.*"},
                    {"if": {"met": False}, "text": (
                        "Um rosto novo! E um rosto de herói, eu diria — heróis sempre têm essa cara de quem não "
                        "dormiu direito. Lírio, bardo, poeta e cronista de feitos ainda não realizados. Uma canção?")},
                    {"if": {"met": True}, "text": "*Lírio levanta o chapéu.* Meu herói favorito! Ou pelo menos o mais recente. Uma canção?"},
                ],
                "options": [
                    {"text": "Cante a Balada de Vel'Tharas.", "next": "balada"},
                    {"text": "Cante algo alegre.", "next": "alegre"},
                    {"text": "Por que você ficou no vale?", "next": "porque"},
                    {"text": "Quem é \"L.\" na Pedra do Viajante?", "next": "pedra",
                     "if": {"discovered": "pedra_viajante"}},
                    {"text": "Ouvi dizer que você compôs uma balada nova.", "next": "balada_heroi",
                     "if": {"flag": "vigia_desperto"}},
                    {"text": "Talvez mais tarde.", "next": None},
                ],
            },
            "balada": {
                "text": [
                    "*Ele dedilha acordes menores, lentos e graves, e canta com uma voz surpreendentemente bonita:*",
                    "Onde a água cai em véu de prata, / a lua dorme em sua casa. / Na mata antiga a outra espera, / no altar partido, a derradeira.",
                    "Três luas cantam, o gigante dorme; / se uma se cala, a terra freme. / Ó Vigia, ó Vigia, onde estás? / O sono é curto, e a noite é demais.",
                    "*Ele abafa as cordas com a palma da mão.* Ninguém sabe quem escreveu. Minha avó dizia que é mais velha que o reino.",
                ],
                "effects": {"journal": {
                    "id": "pista_balada", "title": "A Balada de Vel'Tharas",
                    "text": ("Uma canção antiga: \"Onde a água cai em véu de prata, a lua dorme em sua casa. Na mata "
                             "antiga a outra espera, no altar partido, a derradeira.\"")}},
                "next": "inicio",
            },
            "alegre": {
                "text": [
                    ("*Ele ataca o alaúde com entusiasmo e canta sobre um javali que roubou o chapéu de um rei, "
                     "perseguido por três cavaleiros e uma estalajadeira furiosa. É ridículo e contagiante, e você "
                     "se pega batendo o pé no ritmo.*"),
                    "Ah, a música! Melhor que qualquer poção. Mais barata também — só um pouco.",
                ],
                "next": "inicio",
            },
            "porque": {
                "text": [
                    ("Porque as melhores histórias nascem onde as coisas dão errado, e aqui está dando tudo errado! "
                     "*Ele ri.* Lobos, tremores, luzes misteriosas, bandidos... É um épico esperando para ser escrito."),
                    "Só falta o herói. *Ele olha para você com ar significativo.* Sem pressão.",
                ],
                "next": "inicio",
            },
            "balada_heroi": {
                "text": [
                    "*Lírio sobe numa cadeira, pigarreia, afina o alaúde e anuncia: \"A Balada de {nome}!\"*",
                    ("Veio de longe, com um cartaz na mão, / sem saber de lua, de culto ou de dragão. / Desceu à "
                     "mina, subiu ao altar, / e ensinou um gigante de pedra a cantar."),
                    ("Três luas acesas, o sono guardado, / o vale dormindo, o corvo calado. / E se a terra tremer "
                     "noutro lugar qualquer, / já sabem o nome de quem vai lá resolver."),
                    "*Ele faz uma reverência exagerada.* Ainda falta rimar \"Primordial\". Estou trabalhando nisso.",
                ],
                "next": "inicio",
            },
            "pedra": {
                "text": [
                    ("*Lírio ri, sem graça.* Você leu aquilo? Foi numa noite ruim. Perdi tudo num jogo de dados com o "
                     "guarda da caravana. Mas fiquei, e não me arrependo."),
                    ("A propósito, viu o recado do tal \"K.\"? 'Atrás do véu de prata'... Parece um verso da minha "
                     "balada. Coincidência, não acha?"),
                ],
                "next": "inicio",
            },
        },
    },
    # ================================================================== ZAHIR, O MERCADOR
    "zahir": {
        "name": "Zahir ibn Kadir",
        "short": "Zahir",
        "title": "Mercador de Maravilhas",
        "color": "yellow",
        "description": "Turbante índigo, barba bem aparada e anéis em todos os dedos.",
        "map": "vale_primordia",
        "shop": "zahir",
        "schedule": [{"periods": DAY, "x": 32, "y": 16, "if": {"flag": "rota_liberada"}},
                     {"periods": DAY, "x": 35, "y": 9}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ele se levanta de uma almofada bordada com uma reverência teatral.*"},
                    {"if": {"met": False}, "text": (
                        "Saudações, viajante! Zahir ibn Kadir, mercador de maravilhas, especiarias e coisas que você "
                        "não sabia que precisava. Infelizmente, no momento, também mercador de coisa nenhuma: "
                        "estamos presos neste vale encantador.")},
                    {"if": {"met": True, "not_flag": "rota_liberada"},
                     "text": "Ah, meu cliente favorito, que ainda não comprou nada! *Ele sorri.* Como vai?"},
                    {"if": {"flag": "rota_liberada"}, "text": (
                        "*Zahir abre os braços diante da banca nova, no mercado da vila.* A rota está aberta! Meus "
                        "fardos finalmente respiram! E chegaram coisas novas de Alvorada, vá vendo, vá vendo...")},
                ],
                "options": [
                    {"text": "O que você vende?", "next": "mercadorias"},
                    {"text": "Não dá para abrir um fardo só para mim?", "next": "fardo", "if": {"flag": "zahir_fardos"}},
                    {"text": "Como vocês chegaram até aqui?", "next": "chegada"},
                    {"text": "Por que há uma flecha cravada na sua carroça?", "next": "flecha",
                     "if": {"discovered": "caravana"}},
                    {"text": "Encontrei um fardo seu no acampamento do Corvo.", "next": "fardo_devolvido",
                     "if": {"item": "fardo_zahir"}},
                    {"text": "Adeus, Zahir.", "next": None},
                ],
            },
            "mercadorias": {
                "text": [
                    ("Seda de Qadira, pimenta das ilhas, mapas de lugares que talvez existam e lamparinas que nunca "
                     "se apagam — bem, quase nunca. Meus fardos estão cheios, mas meus compradores estão longe."),
                    ("Quando a rota for reaberta, monto minha banca no mercado da vila. Até lá, tudo fica bem "
                     "amarrado: o Bando do Corvo tem um faro excelente para seda."),
                    "*Ele olha você de cima a baixo.* A não ser, é claro, que alguém me peça com muito jeito...",
                ],
                "effects": {"set_flag": "zahir_fardos"},
                "next": "inicio",
            },
            "fardo": {
                "text": [
                    ("*Zahir olha para os lados, teatral.* Para meu cliente favorito... um fardo. Um só! "
                     "Especiarias, um pouco de seda, uma ou outra ferramenta de qualidade."),
                    "E não conte à Capitã: ela cobra imposto até de sorriso.",
                ],
                "effects": {"open_shop": True},
            },
            "chegada": {
                "text": [
                    ("Pela Rota dos Mercadores, uns três dias antes de você. Os corvos nos emboscaram no "
                     "Desfiladeiro das Viúvas. Perdi uma carroça e dois camelos — que a areia os receba."),
                    "Chegamos com o que sobrou. E agora a Capitã diz que não podemos sair. *Ele suspira.* Ao menos o ensopado da estalagem é bom.",
                ],
                "next": "inicio",
            },
            "fardo_devolvido": {
                "text": [
                    "*Zahir rompe o lacre com o polegar, enfia o nariz na seda e respira fundo, de olhos fechados.*",
                    ("Seda de Qadira, intacta! Achei que nunca mais a veria. *Ele aperta a sua mão com as duas "
                     "dele.* Um mercador paga as dívidas — sobretudo as de honra. Tome, e não discuta: discutir "
                     "preço comigo é perder duas vezes."),
                ],
                "effects": {"take_item": ["fardo_zahir", 1], "give_copper": 800, "xp": 200,
                            "set_flag": "zahir_fardo_devolvido"},
                "next": "inicio",
            },
            "flecha": {
                "text": [
                    "*Zahir arranca a flecha da madeira e mostra a você. As penas são negras, de corvo.*",
                    ("Lembrança do Bando do Corvo. Repare na ponta: ferro bom, forjado com cuidado. Bandidos comuns "
                     "não têm ferreiros assim. Alguém está armando aqueles canalhas."),
                ],
                "effects": {"journal": {
                    "id": "pista_flecha", "title": "Flechas bem forjadas",
                    "text": ("As flechas do Bando do Corvo têm pontas de ferro de excelente qualidade. Zahir suspeita "
                             "que alguém está armando os bandidos.")}},
                "next": "inicio",
            },
        },
    },
    # ================================================================== TOBIAS, O MOLEIRO
    "tobias": {
        "name": "Tobias",
        "short": "Tobias",
        "title": "Moleiro",
        "color": "white",
        "description": "Um velho magro, coberto de farinha da cabeça aos pés, carregando um saco maior que ele.",
        "map": "vale_primordia",
        "shop": "tobias",
        "schedule": [{"periods": ["amanhecer", "manha", "tarde", "entardecer"], "x": 39, "y": 18}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ele solta o saco de farinha, que levanta uma nuvem branca.*"},
                    {"if": {"met": False}, "text": (
                        "Visita! Tobias, moleiro. Desculpe a farinha, ela gruda em tudo — até na alma. Veio pelos "
                        "ratos? Diga que veio pelos ratos.")},
                    {"if": {"met": True}, "text": "*Tobias espirra uma nuvem de farinha.* Ah, é você! Alguma notícia boa? Estou precisando."},
                ],
                "options": [
                    {"text": "Que ratos?", "next": "ratos"},
                    {"text": "Trouxe cinco rabos de rato do celeiro.", "next": "rabos",
                     "if": {"journal": "rumor_ratos", "item": ["rabo_rato", 5]}},
                    {"text": "Dei um jeito nos ratos dos campos.", "next": "ratos_mortos",
                     "if": {"quest_stage": ["ratos", 1]}},
                    {"text": "Quero comprar farinha.", "next": "negociar"},
                    {"text": "O espantalho muda mesmo de lugar à noite?", "next": "espantalho",
                     "if": {"discovered": "espantalho"}},
                    {"text": "Você conhece a Marta da estalagem?", "next": "marta",
                     "if": {"discovered": "pedra_viajante"}},
                    {"text": "Até logo, Tobias.", "next": None},
                ],
            },
            "ratos": {
                "text": [
                    ("Ratos do tamanho de cachorros! Apareceram depois das tremuras, saindo de buracos no chão do "
                     "celeiro. Comem o grão, roem os sacos e me olham como se eu fosse a próxima refeição."),
                    "Pago bem a quem der um jeito neles. Em farinha, mas farinha boa!",
                ],
                "effects": {
                    "start_quest": "ratos",
                    "journal": {
                        "id": "rumor_ratos", "title": "Ratos gigantes no moinho",
                        "text": ("O celeiro de Tobias está infestado de ratos gigantes que saíram de buracos no chão "
                                 "depois das tremuras. Ele paga em farinha: cinco sacos a cada cinco rabos de "
                                 "rato.")},
                },
                "next": "inicio",
            },
            "rabos": {
                "text": [
                    "*Tobias conta os rabos um por um, com uma careta de nojo e um sorriso de orelha a orelha.*",
                    "Cinco! Cinco ratos a menos no meu celeiro! Tome, farinha da boa, como prometi.",
                ],
                "effects": {"take_item": ["rabo_rato", 5], "give_item": ["farinha", 5], "xp": 40},
                "next": "inicio",
            },
            "ratos_mortos": {
                "text": [
                    "*Tobias abraça você e deixa uma marca de farinha do tamanho de um moleiro na sua roupa.*",
                    ("Seis ratos! Ontem à noite o celeiro ficou quietinho pela primeira vez em três luas. Dormi como "
                     "uma pedra. Tome, tome: dinheiro e pão, que farinha você já deve ter até nas orelhas."),
                ],
                "effects": {"set_flag": "tobias_ratos"},
                "next": "inicio",
            },
            "negociar": {
                "text": ["Farinha fresquinha, moída hoje. E pão, para quem tem pressa. *Ele espirra.* Saúde para mim."],
                "effects": {"open_shop": True},
            },
            "espantalho": {
                "text": [
                    ("*Tobias fica pálido sob a farinha.* Muda. Juro pela Aurora. Eu finco o espantalho virado para "
                     "a estrada, e de manhã ele está virado para as ruínas. Todo santo dia."),
                    ("Uma noite fiquei acordado para ver. Não vi nada, mas ouvi: passos no trigal e alguém cantando "
                     "baixinho. Uma canção sobre luas."),
                ],
                "effects": {"journal": {
                    "id": "pista_espantalho", "title": "O espantalho e as ruínas",
                    "text": ("O espantalho de Tobias amanhece sempre virado para as ruínas. Numa noite, Tobias ouviu "
                             "passos no trigal e alguém cantando uma canção sobre luas.")}},
                "next": "inicio",
            },
            "marta": {
                "text": [
                    "*Tobias fica vermelho como um tomate.* M-Marta? Conheço, claro. Todo mundo conhece a Marta. Por quê? Ela falou de mim?",
                    "*Ele pigarreia.* Esquece. Coisa de criança, faz quarenta anos. *Uma pausa.* Ela ainda faz aquele bolo de mel?",
                ],
                "next": "inicio",
            },
        },
    },
    # ================================================================== KAEL, O ÚLTIMO VIGIA (fantasma)
    "kael": {
        "name": "Kael, o Último Vigia",
        "short": "Kael",
        "title": "Fantasma do Cemitério da Colina",
        "color": "bright_cyan",
        "description": ("Um homem translúcido, de armadura antiga e manto cinza-prateado, sentado sobre a lápide mais "
                        "velha do cemitério. Os olhos dele são dois pedaços de luar."),
        "map": "vale_primordia",
        "schedule": [{"periods": ["noite", "madrugada"], "x": 37, "y": 11,
                      "if": {"flag": "bau_gruta_aberto", "not_flag": "kael_descansa"}}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": (
                        "*O fantasma ergue os olhos. Por um instante eles brilham mais forte, na direção da lua "
                        "crescente que você carrega.*")},
                    {"if": {"met": False}, "text": (
                        "Você traz a lua crescente. Faz trezentos anos que espero alguém que a encontre. Eu sou "
                        "Kael — o último dos Vigias da Lua. Ou o que sobrou dele.")},
                    {"if": {"met": True, "not_flag": "vigia_desperto"},
                     "text": "*Kael inclina a cabeça.* O vale ainda treme, {nome}. Mas treme menos quando você está por perto."},
                    {"if": {"flag": "vigia_desperto"}, "text": (
                        "*Kael está de pé, e a luz dele está mais forte e mais fraca ao mesmo tempo.* Ele canta de "
                        "novo. Eu ouço daqui. Você conseguiu, {nome}.")},
                ],
                "options": [
                    {"text": "O que são as três luas?", "next": "luas"},
                    {"text": "Onde está a lua cheia?", "next": "cheia", "if": {"flag": "kael_conversou"}},
                    {"text": "E a lua minguante?", "next": "minguante", "if": {"flag": "kael_conversou"}},
                    {"text": "O que é o Vigia?", "next": "vigia"},
                    {"text": "Por que você ainda está aqui?", "next": "porque", "if": {"not_flag": "vigia_desperto"}},
                    {"text": "Pode descansar agora, Kael.", "next": "adeus", "if": {"flag": "vigia_desperto"}},
                    {"text": "Até a próxima noite.", "next": None},
                ],
            },
            "luas": {
                "text": [
                    ("As três luas são as vozes da canção que faz o Primordial dormir: a crescente, a cheia e a "
                     "minguante. Juntas, elas cantam. Separadas, são só pedras bonitas."),
                    ("Mas pedra não canta sozinha: precisa de alguém que saiba a canção. Eu a escondi onde o culto "
                     "nunca procuraria — nas pedras que cantam, na ilha da garça, no meio do lago. Só à noite elas "
                     "lembram."),
                ],
                "effects": {
                    "set_flag": "kael_conversou",
                    "xp": 300,
                    "journal": {
                        "id": "kael_cancao", "title": "Kael, o último Vigia",
                        "text": ("O fantasma de Kael, o último Vigia da Lua, aparece à noite no Cemitério da Colina. "
                                 "A canção que faz o Primordial dormir está nas Pedras que Cantam, na Ilhota da "
                                 "Garça — e só se ouve à noite. Para chegar lá, é preciso um barco.")},
                },
                "next": "inicio",
            },
            "cheia": {
                "text": [
                    ("A cheia eu entreguei ao Carvalho Ancião, na mata antiga, quando os Vigias acabaram. Ele a "
                     "guarda no coração, enrolada nas raízes."),
                    "Cante para ele, à noite, e ele abrirá. Árvores velhas dormem de dia, como os velhos.",
                ],
                "effects": {"journal": {
                    "id": "pista_lua_cheia", "title": "A lua cheia",
                    "text": "Kael entregou a lua cheia ao Carvalho Ancião. Cantando a canção dos Vigias para ele, à "
                            "noite, a árvore se abre."}},
                "next": "inicio",
            },
            "minguante": {
                "text": [
                    ("A minguante ficava no altar das ruínas. Foi roubada há três luas — e foi aí que os tremores "
                     "começaram. Uma mulher de cabelos prateados a levou: Morwen. Ela se chama de Senhora da Lua "
                     "Cortada."),
                    ("Os seguidores dela se escondem sob o círculo de pedras rúnicas. Na lua cheia, o círculo se abre "
                     "para quem sabe olhar."),
                ],
                "effects": {"journal": {
                    "id": "pista_minguante", "title": "A lua minguante",
                    "text": ("Morwen, a Senhora da Lua Cortada, roubou a lua minguante do Altar Rachado. O culto se "
                             "esconde sob o Círculo de Pedras Rúnicas, que se abre nas noites de lua cheia.")}},
                "next": "inicio",
            },
            "vigia": {
                "text": [
                    ("O Vigia não sou eu. Eu fui só o último dos Vigias vivos. O Vigia é um guardião de pedra que "
                     "dorme junto do Primordial e canta para ele, atrás da porta das três luas."),
                    ("Se o culto o acordar no meio de um pesadelo, ele acordará o gigante junto. Mas se alguém o "
                     "acordar com as três luas e a canção... ele cantará de volta."),
                ],
                "next": "inicio",
            },
            "porque": {
                "text": [
                    "Porque jurei guardar o sono dele até o fim, e o fim ainda não chegou.",
                    "*Ele sorri, triste.* Ou talvez eu só esteja esperando alguém para passar a vigília adiante.",
                ],
                "next": "inicio",
            },
            "adeus": {
                "text": [
                    ("*Kael se levanta e, pela primeira vez, a luz dele não treme.* Então eu passo a vigília para "
                     "você, {nome}. Cante de vez em quando. Ele gosta."),
                    "*O fantasma se desfaz em poeira de luar, que sobe devagar, devagar, até se perder entre as estrelas.*",
                ],
                "effects": {"set_flag": "kael_descansa", "xp": 200},
            },
        },
    },
    # ================================================================== DAVI, O APRENDIZ
    "davi": {
        "name": "Davi",
        "short": "Davi",
        "title": "Aprendiz de Ferreiro",
        "color": "red",
        "description": "Um rapaz magro, de braços queimados de forja e olhos fundos, com um sorriso que volta aos poucos.",
        "map": "vale_primordia",
        "schedule": [
            {"map": "mina_ferro_velho", "x": 27, "y": 10,
             "if": {"flag": "gorran_derrotado", "not_flag": "davi_resgatado"}},
            {"periods": DAY, "x": 28, "y": 16, "if": {"flag": "davi_resgatado"}},
            {"periods": ["entardecer", "noite"], "x": 33, "y": 14, "if": {"flag": "davi_resgatado"}},
        ],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"not_flag": "davi_resgatado"},
                     "text": "*O rapaz acorrentado à bigorna olha para você como quem vê um fantasma.*"},
                    {"if": {"not_flag": "davi_resgatado"}, "text": (
                        "Você... você não é um deles. Derrubou o Gorran! Eu sou Davi, aprendiz do Brom, lá da vila. "
                        "Ou era.")},
                    {"if": {"flag": "davi_resgatado"},
                     "text": "*Davi ergue o martelo em cumprimento, sem perder o ritmo.* {nome}! A forja nunca esteve tão animada."},
                ],
                "options": [
                    {"text": "Vim tirar você daqui. Vamos para casa.", "next": "resgate",
                     "if": {"not_flag": "davi_resgatado"}},
                    {"text": "O que eles obrigavam você a fazer?", "next": "flechas"},
                    {"text": "Como está a forja?", "next": "forja", "if": {"flag": "davi_resgatado"}},
                    {"text": "Até mais, Davi.", "next": None},
                ],
            },
            "resgate": {
                "text": [
                    "*Uma pancada no cadeado gasto, e a corrente cai. Davi esfrega os pulsos, sem acreditar.*",
                    ("Três luas aqui embaixo... Conheço o caminho de olhos fechados: fiz ele mil vezes empurrando "
                     "vagonete. Vou para casa. Diga ao Brom... não, eu mesmo digo!"),
                    ("*Ele para na saída do fosso.* Ah: o capataz guardava as cartas da Senhora num cofre, no quarto "
                     "dele. A chave ficava no cinto. Boa sorte, {nome}. E obrigado."),
                ],
                "effects": {
                    "set_flag": "davi_resgatado",
                    "xp": 200,
                    "journal": {
                        "id": "davi_livre", "title": "Davi está livre",
                        "text": ("Davi, o aprendiz de Brom, estava acorrentado à forja do capataz, no fundo da mina. "
                                 "Livre, ele voltou para a vila. O capataz guardava as cartas da Senhora num cofre, "
                                 "e a chave ficava com ele.")},
                },
            },
            "flechas": {
                "text": [
                    ("Pontas de flecha. Milhares. O Gorran dizia que eram para \"os corvos\", na estrada do sul, e "
                     "que a Senhora pagava bem por elas."),
                    ("Eu fazia malfeito de propósito, quando dava: uma ponta torta aqui, outra mal temperada ali. *Ele "
                     "sorri pela primeira vez.* Uma vingança pequenininha."),
                ],
                "effects": {"journal": {
                    "id": "pista_flechas_mina", "title": "As flechas do Corvo",
                    "text": ("As flechas do Bando do Corvo eram forjadas por Davi, à força, na Mina de Ferro-Velho. "
                             "Quem pagava era a Senhora da Lua Cortada.")}},
                "next": "inicio",
            },
            "forja": {
                "text": [
                    ("Com o ferro da mina de volta, o Brom está me ensinando aço de verdade: ferro e carvão no fogo "
                     "mais quente que a fornalha aguenta."),
                    "Se precisar de uma lâmina boa, a forja vende. Se precisar de uma ótima, fale comigo. *Ele pisca.*",
                ],
                "next": "inicio",
            },
        },
    },
    # ================================================================== PIP, O KOBOLD
    "pip": {
        "name": "Pip",
        "short": "Pip",
        "title": "Kobold Comerciante",
        "color": "bright_yellow",
        "description": ("Um kobold do tamanho de uma criança, de focinho de rato e olhos de brasa, com uma vela acesa "
                        "presa no capacete e um sorriso cheio de dentinhos."),
        "map": "mina_ferro_velho",
        "shop": "pip",
        "schedule": [{"x": 4, "y": 3, "if": {"flag": "gorran_derrotado"}}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*O kobold dá um pulo para trás e quase derruba a vela do capacete.*"},
                    {"if": {"met": False}, "text": (
                        "Gente-alta! Não bate! Pip é amigo! Gente-alta derrubou o Homem-Chicote, Pip viu! Kobolds "
                        "livres! Pip agradece. Pip... vende coisas?")},
                    {"if": {"met": True},
                     "text": "Gente-alta voltou! Pip tem vela, tem carvão, tem pedra-de-ferro. Gente-alta compra?"},
                ],
                "options": [
                    {"text": "Quero ver suas coisas.", "next": "negociar"},
                    {"text": "Por que os kobolds vieram para a mina?", "next": "vieram"},
                    {"text": "Quem era o Homem-Chicote?", "next": "gorran"},
                    {"text": "O que tem lá embaixo, no poço?", "next": "fundo", "if": {"discovered": "poco_fundo"}},
                    {"text": "Até mais, Pip.", "next": None},
                ],
            },
            "negociar": {
                "text": ["Pip tem coisas boas! Pip não rouba. Pip não rouba MUITO."],
                "effects": {"open_shop": True},
            },
            "vieram": {
                "text": [
                    ("Grande Barulho! *Pip imita um tremor com o corpo inteiro.* Pedra Grande lá embaixo sonha mal, "
                     "vira de lado, e Fundo-Fundo desaba. Kobolds sobem, sobem, sobem..."),
                    "...e acham buraco de gente-alta, cheio de ferro! Kobolds gostam de ferro. Ferro é bonito.",
                ],
                "effects": {"journal": {
                    "id": "rumor_kobolds", "title": "Os kobolds da mina",
                    "text": ("Os kobolds vieram do \"Fundo-Fundo\", bem abaixo da mina, fugindo do \"Grande "
                             "Barulho\": a Pedra Grande que sonha mal. Eles sentem o Primordial.")}},
                "next": "inicio",
            },
            "gorran": {
                "text": [
                    ("Homem-Chicote chegou com fogo roxo. Disse: kobolds cavam ou kobolds queimam. Kobolds "
                     "cavaram. *Pip mostra uma queimadura no braço.*"),
                    "Mulher-da-Lua mandava cartas para ele. Pip não sabe ler. Pip sabe que as cartas cheiravam a vela roxa.",
                ],
                "next": "inicio",
            },
            "fundo": {
                "text": [
                    ("Fundo-Fundo. Casa de kobold. Muito longe, muito quente, muito escuro. Pip não volta lá: corda "
                     "cortada, e coisa grande mexe lá embaixo, perto da Pedra Grande."),
                    ("*Ele baixa a voz.* Do outro lado da montanha, gente-alta cava também. Pedravale. Pip ouve as "
                     "picaretas deles quando encosta a orelha na pedra."),
                ],
                "effects": {"journal": {
                    "id": "pista_fundo_fundo", "title": "O Fundo-Fundo",
                    "text": ("Sob a Mina de Ferro-Velho, um poço desce até o Fundo-Fundo, o lar dos kobolds. A corda "
                             "foi cortada. Pip diz que, do outro lado da montanha, os mineiros de Pedravale também "
                             "cavam fundo.")}},
                "next": "inicio",
            },
        },
    },
    # ================================================================== TOMÉ, O SOBRINHO DA CAPITÃ
    "tome": {
        "name": "Tomé Valbrand",
        "short": "Tomé",
        "title": "Sobrinho da Capitã",
        "color": "blue",
        "description": ("Um garoto magrelo de dezesseis anos, com uma espada de madeira na cintura e um cabelo que "
                        "nenhum pente jamais venceu."),
        "map": "vale_primordia",
        "schedule": [
            {"x": 48, "y": 1, "if": {"flag": "tome_cultistas", "not_flag": "tome_salvo"}},
            {"periods": DAY, "x": 29, "y": 11, "if": {"flag": "tome_salvo"}},
        ],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"not_flag": "tome_salvo"},
                     "text": "*O garoto ainda segura a espada de madeira com as duas mãos, tremendo.*"},
                    {"if": {"not_flag": "tome_salvo"}, "text": (
                        "Você... derrubou os dois! Eu vi! Foi incrível! Eu sou Tomé. Tomé Valbrand. Minha tia vai me "
                        "matar.")},
                    {"if": {"flag": "tome_salvo"}, "text": (
                        "*Tomé abaixa a espada de madeira, que estava usando contra um poste.* {nome}! Estou "
                        "treinando! A tia disse que, se eu treinar todo dia, um dia entro para a guarda.")},
                ],
                "options": [
                    {"text": "Você está bem? Sua tia está desesperada.", "next": "salvo",
                     "if": {"not_flag": "tome_salvo"}},
                    {"text": "O que você viu nas ruínas?", "next": "viu"},
                    {"text": "Como vai o treino?", "next": "treino", "if": {"flag": "tome_salvo"}},
                    {"text": "Até mais, Tomé.", "next": None},
                ],
            },
            "salvo": {
                "text": [
                    ("*Tomé fica vermelho até as orelhas.* Eu só queria ver o olho se abrir! Está escrito na torre: "
                     "\"quando o olho se abre, o caminho se revela\". E aí eles chegaram..."),
                    "*Ele respira fundo.* Vou para casa. Juro. Direto, sem parar em lugar nenhum.",
                ],
                "effects": {"set_flag": "tome_salvo", "xp": 150},
                "next": "viu",
            },
            "viu": {
                "text": [
                    ("Eles falavam de descer debaixo do círculo de pedras, na lua cheia. E de uma chave de pedra preta "
                     "que abre o círculo em qualquer noite: os acólitos levam uma, lá na Árvore dos Enforcados, no "
                     "pântano."),
                    "E da Senhora. Todo mundo tem medo da Senhora. Até os que têm espada de verdade.",
                ],
                "effects": {"journal": {
                    "id": "pista_circulo", "title": "O que Tomé ouviu",
                    "text": ("Os cultistas descem sob o Círculo de Pedras Rúnicas nas noites de lua cheia. Os "
                             "acólitos da Árvore dos Enforcados, no pântano, carregam uma chave de pedra negra que "
                             "abre o círculo em qualquer noite.")}},
                "next": "inicio",
            },
            "treino": {
                "text": [
                    ("Ataque, defesa, ataque, defesa! A tia diz que o mais importante é saber quando correr. Eu acho "
                     "que é saber quando NÃO correr."),
                    "*Ele pensa um pouco.* Ela disse que eu pareço você. Acho que foi um elogio. Acho.",
                ],
                "next": "inicio",
            },
        },
    },
    # ================================================================== O VIGIA
    "vigia": {
        "name": "O Vigia",
        "short": "Vigia",
        "title": "Guardião do Sono do Primordial",
        "color": "bright_white",
        "description": ("Um gigante de pedra branca sentado de pernas cruzadas, com as mãos abertas sobre os joelhos. "
                        "Os olhos dele são calmos e cinzentos como um lago ao amanhecer."),
        "map": "camara_vigia",
        "schedule": [{"x": 13, "y": 4, "if": {"flag": "vigia_desperto"}}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": (
                        "*O gigante de pedra inclina a cabeça, devagar, como uma montanha que faz uma reverência. A "
                        "voz dele é tão grave que você a sente nos ossos.*")},
                    {"if": {"met": False}, "text": (
                        "Pequeno cantor. Você me tirou do sonho ruim. Há trezentos anos ninguém cantava para mim.")},
                    {"if": {"met": True}, "text": "*O Vigia abre um olho.* Pequeno cantor. O sono dele está bom hoje."},
                ],
                "options": [
                    {"text": "Quem é você, de verdade?", "next": "quem"},
                    {"text": "O Primordial vai acordar de novo?", "next": "primordial"},
                    {"text": "O que eu faço com as três luas?", "next": "luas"},
                    {"text": "Existem outros como ele?", "next": "outros"},
                    {"text": "Durma bem, Vigia.", "next": None},
                ],
            },
            "quem": {
                "text": [
                    ("Fui feito pelos Vigias da Lua, com a pedra do próprio vale, para cantar enquanto eles "
                     "descansavam. Eles se foram, um a um. Eu continuei cantando."),
                    "Até que alguém roubou a minha voz minguante e plantou um pesadelo no meu sono.",
                ],
                "next": "inicio",
            },
            "primordial": {
                "text": [
                    ("Ele dorme, e vai dormir por muito tempo, se ninguém o acordar. Mas a Senhora não era a única que "
                     "queria o poder dele. Haverá outros. Sempre há."),
                ],
                "next": "inicio",
            },
            "luas": {
                "text": [
                    ("Fique com elas. Enquanto as três estiverem juntas, nas mãos de quem conhece a canção, o sono "
                     "dele está guardado. Você é a vigília agora, {nome}."),
                ],
                "next": "inicio",
            },
            "outros": {
                "text": [
                    ("O mundo é feito de gigantes adormecidos, pequeno cantor. Um sob este vale. Outro sob as "
                     "montanhas do norte, onde a gente de Pedravale cava fundo demais. Outros sob o mar."),
                    "Quando as montanhas tremerem lá também, lembre-se da canção.",
                ],
                "effects": {"journal": {
                    "id": "outros_primordiais", "title": "Outros gigantes adormecidos",
                    "text": ("O Vigia contou que há outros Primordiais adormecidos: um sob as montanhas do norte, "
                             "perto de Pedravale, e outros sob o mar.")}},
                "next": "inicio",
            },
        },
    },
}
