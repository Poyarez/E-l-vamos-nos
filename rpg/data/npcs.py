"""NPCs do Vale de Primórdia e seus diálogos.

Estrutura de um NPC:
  ``schedule`` — onde o NPC está em cada período do dia (a primeira regra que bate vale;
  sem regra correspondente, o NPC não está no mapa naquele horário).
  ``dialogue`` — nós de conversa. A conversa começa em ``"inicio"``.

Estrutura de um nó:
  ``text``    — falas. Linhas entre *asteriscos* são narração. Uma linha pode ser
                ``{"if": {...}, "text": "..."}`` para aparecer só sob condições.
  ``options`` — escolhas: ``{"text", "next", "if"}`` (``next: None`` encerra a conversa).
  ``next``    — sem opções: volta automaticamente para este nó.
  ``effects`` — ao exibir o nó: ``set_flag``, ``journal``, ``xp``, ``give_item``,
                ``take_item``, ``give_copper``, ``restore`` e ``open_shop`` (abre a loja do NPC,
                definida em ``shop``, assim que a conversa termina).

Condições (``if``): ``flag``, ``not_flag``, ``journal``, ``discovered``, ``class``,
``moral``, ``law``, ``period``, ``night``, ``met`` e ``min_level``.

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
                    ("Fraco, {tratamento}. Sem as caravanas do sul, vendo pão para quem tem dinheiro e fiado para "
                     "quem não tem. Se as coisas não melhorarem, só os lobos vão engordar neste inverno."),
                ],
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
                    {"text": "Pode me ensinar a trabalhar o metal?", "next": "metalurgia"},
                    {"text": "Onde consigo minério?", "next": "minerio"},
                    {"text": "De quem é o martelo com o nome \"Davi\"?", "next": "davi",
                     "if": {"discovered": "forja"}},
                    {"text": "Até mais, Brom.", "next": None},
                ],
            },
            "metalurgia": {
                "text": [
                    ("*Ele ri, uma risada grave.* Ensinar? Com prazer! Mas metal sem minério é só vontade. Arranje "
                     "uma picareta, traga cobre e estanho das colinas, e eu mostro como fundir sua primeira barra "
                     "de bronze."),
                    "Todo ferreiro começa assim: com as mãos sujas e os dedos queimados.",
                ],
                "effects": {"journal": {
                    "id": "pista_metalurgia", "title": "Aulas de metalurgia",
                    "text": ("Brom ensina a fundir bronze a quem trouxer minério de cobre e estanho das Colinas de "
                             "Cobre. Será preciso uma picareta.")}},
                "next": "inicio",
            },
            "minerio": {
                "text": [
                    ("No Afloramento de Cobre, nas colinas a leste: cobre e estanho a céu aberto, fáceis de tirar. "
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
                    {"text": "\"Tobias + Marta\", na Pedra do Viajante...", "next": "tobias",
                     "if": {"discovered": "pedra_viajante"}},
                    {"text": "Até mais, Marta.", "next": None},
                ],
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
                    {"text": "Pode me ensinar a pescar?", "next": "pescar"},
                    {"text": "Que ilhota é aquela no meio do lago?", "next": "ilhota"},
                    {"text": "O \"Rei do Lago\" existe mesmo?", "next": "rei"},
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
                ],
                "effects": {"journal": {
                    "id": "pista_pesca", "title": "Pescaria no lago",
                    "text": ("Anselmo diz que camarões e sardinhas mordem fácil no Píer do Lago Espelhado; trutas, "
                             "só no ribeirão. Será preciso uma vara e iscas.")}},
                "next": "inicio",
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
                    {"text": "Que remédios você prepara?", "next": "remedios"},
                    {"text": "O que sabe sobre as tremuras?", "next": "tremuras"},
                    {"text": "A Irmã Celeste disse que você entende de sonhos.", "next": "sonhos",
                     "if": {"journal": "pista_sonhos"}},
                    {"text": "Por que há uma lua cortada na Árvore dos Enforcados?", "next": "arvore",
                     "if": {"discovered": "arvore_enforcados"}},
                    {"text": "Preciso ir.", "next": None},
                ],
            },
            "remedios": {
                "text": [
                    ("Unguentos para cortes, xaropes para tosse, chás para coração partido — esses vendem mais. Tudo "
                     "do pântano. As melhores ervas crescem onde ninguém quer pisar."),
                    "Se quiser aprender, traga ervas e paciência. Alquimia não é cozinhar: é convencer as plantas a fazer o que você quer.",
                ],
                "effects": {"journal": {
                    "id": "pista_alquimia", "title": "Lições de alquimia",
                    "text": "Mãe Brígida ensina alquimia a quem lhe trouxer ervas do pântano — e paciência."}},
                "next": "inicio",
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
        "schedule": [{"periods": DAY, "x": 35, "y": 9}],
        "dialogue": {
            "inicio": {
                "text": [
                    {"if": {"met": False}, "text": "*Ele se levanta de uma almofada bordada com uma reverência teatral.*"},
                    {"if": {"met": False}, "text": (
                        "Saudações, viajante! Zahir ibn Kadir, mercador de maravilhas, especiarias e coisas que você "
                        "não sabia que precisava. Infelizmente, no momento, também mercador de coisa nenhuma: "
                        "estamos presos neste vale encantador.")},
                    {"if": {"met": True}, "text": "Ah, meu cliente favorito, que ainda não comprou nada! *Ele sorri.* Como vai?"},
                ],
                "options": [
                    {"text": "O que você vende?", "next": "mercadorias"},
                    {"text": "Como vocês chegaram até aqui?", "next": "chegada"},
                    {"text": "Por que há uma flecha cravada na sua carroça?", "next": "flecha",
                     "if": {"discovered": "caravana"}},
                    {"text": "Adeus, Zahir.", "next": None},
                ],
            },
            "mercadorias": {
                "text": [
                    ("Seda de Qadira, pimenta das ilhas, mapas de lugares que talvez existam e lamparinas que nunca "
                     "se apagam — bem, quase nunca. Meus fardos estão cheios, mas meus compradores estão longe."),
                    ("Quando a rota for reaberta, monto minha banca no mercado da vila. Até lá, tudo fica bem "
                     "amarrado: o Bando do Corvo tem um faro excelente para seda."),
                ],
                "next": "inicio",
            },
            "chegada": {
                "text": [
                    ("Pela Rota dos Mercadores, uns três dias antes de você. Os corvos nos emboscaram no "
                     "Desfiladeiro das Viúvas. Perdi uma carroça e dois camelos — que a areia os receba."),
                    "Chegamos com o que sobrou. E agora a Capitã diz que não podemos sair. *Ele suspira.* Ao menos o ensopado da estalagem é bom.",
                ],
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
                "effects": {"journal": {
                    "id": "rumor_ratos", "title": "Ratos gigantes no moinho",
                    "text": ("O celeiro de Tobias está infestado de ratos gigantes que saíram de buracos no chão "
                             "depois das tremuras. Ele paga em farinha.")}},
                "next": "inicio",
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
}
