"""Tipos de terreno.

Cada mapa liga os caracteres do seu desenho a estes ids (``legend``). O caractere
desenhado no mapa é o mesmo exibido no minimapa; a cor vem daqui.

* ``cost``   — minutos de jogo gastos para atravessar um tile.
* ``vision`` — modificador do raio de visão (colinas ampliam, mata fechada reduz).
* ``day`` / ``night`` — variações de descrição; cada tile sorteia sempre a mesma.
"""

TERRAIN = {
    # ------------------------------------------------------------------ ao ar livre
    "planicie": {
        "name": "Campina", "color": "green", "passable": True, "cost": 10, "vision": 0,
        "day": [
            "A relva baixa ondula ao vento, salpicada de trevos e margaridas.",
            "Um campo aberto se estende em todas as direções; gafanhotos saltam a cada passo seu.",
            "Borboletas amarelas dançam sobre a grama, indiferentes às preocupações do vale.",
            "O capim cheira a orvalho e terra úmida. Ao longe, um falcão desenha círculos no céu.",
            "Pedras cobertas de líquen marcam uma antiga divisa de pastagem, há muito esquecida.",
        ],
        "night": [
            "Vaga-lumes acendem e apagam sobre a relva escura, como estrelas que caíram cedo demais.",
            "O campo é um mar de sombras prateadas; grilos cantam em coro.",
            "O vento frio da noite arrepia a grama e traz o cheiro distante de fumaça de lareira.",
        ],
    },
    "relva_alta": {
        "name": "Relva alta", "color": "bright_green", "passable": True, "cost": 12, "vision": 0,
        "day": [
            "O capim alto bate na sua cintura e esconde o chão. Algo pequeno foge, farfalhando.",
            "Hastes douradas balançam em ondas; sementes grudam em suas roupas.",
            "Você abre caminho pela relva densa, deixando uma trilha amassada para trás.",
            "Flores silvestres roxas despontam entre o capim, zumbindo de abelhas.",
        ],
        "night": [
            "O capim alto sussurra ao seu redor. Impossível saber o que se move ali dentro.",
            "A relva molhada de sereno encharca suas pernas; corujas piam por perto.",
        ],
    },
    "lavoura": {
        "name": "Lavoura", "color": "bright_yellow", "passable": True, "cost": 12, "vision": 0,
        "day": [
            "Fileiras de trigo dourado se curvam ao vento, pesadas de grãos.",
            "Sulcos bem cuidados de nabo e repolho mostram o capricho de alguma família da vila.",
            "Um espantalho torto vigia o milharal; corvos o ignoram com desdém.",
            "O cheiro de terra revirada e esterco anuncia o trabalho duro dos lavradores.",
        ],
        "night": [
            "As plantações são um labirinto escuro. O trigo range como se alguém caminhasse nele.",
            "Sob a lua, o milharal parece mais alto — e mais fechado — do que durante o dia.",
        ],
    },
    "floresta": {
        "name": "Floresta", "color": "green", "passable": True, "cost": 15, "vision": 0,
        "day": [
            "Carvalhos e faias formam um teto verde; a luz chega ao chão em fachos de poeira dourada.",
            "Raízes retorcidas atravessam a trilha. Um esquilo observa você, desconfiado, de um galho.",
            "O chão é um tapete macio de folhas secas que estalam a cada passo.",
            "Cogumelos alaranjados crescem em um tronco caído, coberto de musgo.",
            "Pássaros invisíveis trocam cantos entre as copas. O ar é fresco e úmido.",
        ],
        "night": [
            "A escuridão entre as árvores é quase sólida. Galhos estalam em algum lugar à sua esquerda.",
            "Olhos refletem a pouca luz por um instante — e somem entre os troncos.",
            "O vento nas copas soa como milhares de vozes sussurrando ao mesmo tempo.",
        ],
    },
    "mata_antiga": {
        "name": "Mata antiga", "color": "green bold", "passable": True, "cost": 20, "vision": -1,
        "day": [
            "Árvores colossais, de troncos largos como torres, bloqueiam quase toda a luz do sol.",
            "Barbas de musgo pendem dos galhos. O silêncio aqui é antigo e pesado.",
            "Raízes do tamanho de pontes erguem-se do chão; é preciso escalar para avançar.",
            "Um cheiro de resina e terra preta enche o ar. Esta mata já era velha quando o reino nasceu.",
        ],
        "night": [
            "Breu absoluto. Apenas fungos azulados nas raízes dão alguma forma ao mundo.",
            "Algo enorme respira devagar na escuridão — ou será apenas o vento nas copas?",
        ],
    },
    "colinas": {
        "name": "Colinas", "color": "red", "passable": True, "cost": 20, "vision": 1,
        "day": [
            "A encosta avermelhada é íngreme e salpicada de cascalho. Do alto, a vista se abre.",
            "Veios esverdeados de cobre oxidado riscam as pedras expostas da colina.",
            "Um vento seco sopra entre as colinas, levantando poeira cor de ferrugem.",
            "Cabras-monteses observam você de um rochedo, mastigando com ar de superioridade.",
        ],
        "night": [
            "As colinas são silhuetas contra o céu estrelado. Pedrinhas rolam sob suas botas.",
            "O vento uiva entre os morros, frio e cortante.",
        ],
    },
    "rochas": {
        "name": "Pedregulhos", "color": "gray", "passable": True, "cost": 15, "vision": 0,
        "day": [
            "Rochas grandes e arredondadas se amontoam aqui, como ovos de algum gigante.",
            "Lagartos tomam sol sobre as pedras quentes e fogem quando você se aproxima.",
            "Entre os pedregulhos, a passagem é estreita e exige cuidado.",
        ],
        "night": [
            "As pedras ainda guardam o calor do dia. Sombras se acumulam entre elas.",
            "Você tateia pelas rochas no escuro, tentando não torcer o tornozelo.",
        ],
    },
    "agua": {
        "name": "Águas profundas", "color": "blue", "passable": False, "cost": 0, "vision": 0,
        "day": ["Águas profundas e frias."], "night": ["Águas negras e profundas."],
    },
    "agua_rasa": {
        "name": "Águas rasas", "color": "bright_cyan", "passable": True, "cost": 20, "vision": 0,
        "day": [
            "A água gelada bate em seus joelhos. Peixinhos prateados fogem entre as pedras do fundo.",
            "Você avança com cuidado pelo leito raso; a correnteza puxa suas botas.",
            "Seixos lisos e escorregadios forram o fundo da água cristalina.",
        ],
        "night": [
            "A água escura gela até os ossos. Você sente, mais do que vê, o caminho pelo leito.",
            "O reflexo das estrelas se parte em mil pedaços a cada passo seu na água.",
        ],
    },
    "pantano": {
        "name": "Pântano", "color": "cyan", "passable": True, "cost": 25, "vision": 0,
        "day": [
            "Lama negra suga suas botas a cada passo. Bolhas sobem da água parada com um cheiro podre.",
            "Juncos altos e árvores mortas erguem-se de um lodo esverdeado. Mosquitos zumbem sem trégua.",
            "Uma névoa baixa paira sobre o charco, mesmo sob o sol.",
            "Sapos coaxam em coro e silenciam de repente, todos ao mesmo tempo.",
        ],
        "night": [
            "Luzes pálidas flutuam sobre o pântano — fogos-fátuos que parecem chamar você.",
            "A água negra borbulha. Algo grande se move logo abaixo da superfície.",
            "O fedor do lodo é mais forte à noite, e o silêncio, mais inquietante.",
        ],
    },
    "estrada": {
        "name": "Estrada", "color": "yellow", "passable": True, "cost": 6, "vision": 0,
        "day": [
            "Uma estrada de terra batida, marcada por sulcos de rodas de carroça.",
            "Pedras de calçamento antigo despontam aqui e ali na estrada, restos de uma obra do império.",
            "Marcos de pedra contam as léguas à beira do caminho, gastos pela chuva.",
            "A estrada segue firme e segura. Pegadas de botas e cascos se misturam na poeira.",
        ],
        "night": [
            "A estrada é uma faixa pálida no escuro, fácil de seguir mesmo sem tocha.",
            "Seus passos ecoam na estrada vazia. Nenhum viajante ousa andar a esta hora.",
        ],
    },
    "ponte": {
        "name": "Ponte", "color": "white bold", "passable": True, "cost": 6, "vision": 0,
        "day": [
            "Tábuas e pedras firmes cruzam a água. Lá embaixo, a correnteza murmura.",
            "Você atravessa a passagem sobre a água; o vento aqui é mais fresco.",
        ],
        "night": [
            "A passagem range sob seus pés. A água corre invisível, logo abaixo.",
        ],
    },
    "calcamento": {
        "name": "Ruas da vila", "color": "white", "passable": True, "cost": 5, "vision": 0,
        "day": [
            "Ruas de pedra irregulares, gastas por gerações de botas e tamancos.",
            "Galinhas ciscam entre as pedras da rua; um gato dorme sobre um muro ensolarado.",
            "Moradores passam com cestos e ferramentas, cumprimentando você com um aceno curioso.",
            "Varais de roupa cruzam a rua entre as casas, balançando ao vento.",
        ],
        "night": [
            "As ruas estão vazias. Luz amarelada escapa pelas frestas das janelas.",
            "Um cão late ao longe. Lampiões de óleo tremulam nos cantos das casas.",
        ],
    },
    "construcao": {
        "name": "Construções", "color": "bright_red", "passable": True, "cost": 5, "vision": 0,
        "day": [
            "Casas de pedra e madeira com telhados de palha, floreiras nas janelas e fumaça nas chaminés.",
            "Uma casa simples, de porta azul descascada. Alguém canta lá dentro enquanto trabalha.",
            "Um galpão de ferramentas, cheirando a feno e óleo de linhaça.",
        ],
        "night": [
            "As janelas estão fechadas e as portas trancadas. Lá dentro, alguém ronca alto.",
            "A luz de uma vela dança atrás das venezianas de uma casa.",
        ],
    },
    "ruinas": {
        "name": "Ruínas", "color": "magenta", "passable": True, "cost": 15, "vision": 0,
        "day": [
            "Blocos de pedra branca, lisos demais para mãos humanas, jazem tombados na relva.",
            "Restos de uma coluna entalhada mostram figuras de olhos grandes contemplando uma lua.",
            "Arcos partidos emolduram o céu. O vento assobia por entre as pedras de forma estranha.",
            "Musgo violeta, que você nunca viu em outro lugar, cresce nas frestas das ruínas.",
        ],
        "night": [
            "As pedras das ruínas parecem brilhar levemente, um tom violeta quase imperceptível.",
            "Sombras se movem entre os arcos partidos — ou é só a lua passando entre as nuvens?",
        ],
    },
    "tumulos": {
        "name": "Túmulos", "color": "gray", "passable": True, "cost": 10, "vision": 0,
        "day": [
            "Lápides de pedra inclinadas, com nomes quase apagados pelo tempo.",
            "Flores secas repousam diante de um túmulo recente. Corvos observam do muro.",
        ],
        "night": [
            "Uma névoa fria se arrasta entre as lápides. Algo arranha a terra em algum lugar.",
            "O silêncio do cemitério à noite é tão profundo que você ouve o próprio coração.",
        ],
    },
    "caverna": {
        "name": "Entrada de caverna", "color": "white bold", "passable": True, "cost": 10, "vision": 0,
        "day": ["Uma abertura escura se abre na rocha, exalando ar frio e úmido."],
        "night": ["A boca da caverna é um buraco ainda mais negro que a noite."],
    },
    "montanha": {
        "name": "Montanhas", "color": "white", "passable": False, "cost": 0, "vision": 0,
        "day": ["Paredões de rocha intransponíveis."], "night": ["Paredões de rocha intransponíveis."],
    },
    "cachoeira": {
        "name": "Cachoeira", "color": "bright_cyan bold", "passable": False, "cost": 0, "vision": 0,
        "day": ["Uma cortina de água despenca do penhasco."], "night": ["A cachoeira ruge na escuridão."],
    },
    # ------------------------------------------------------------------ subterrâneo
    "chao_gruta": {
        "name": "Chão da gruta", "color": "gray", "passable": True, "cost": 10, "vision": 0,
        "day": [
            "O chão de pedra é liso e úmido. Gotas caem do teto em um ritmo hipnótico.",
            "Seus passos ecoam pela gruta, voltando de direções que não fazem sentido.",
            "O ar é frio e cheira a pedra molhada e a algo floral, inexplicável.",
        ],
    },
    "parede_gruta": {
        "name": "Paredes de rocha", "color": "white", "passable": False, "cost": 0, "vision": 0,
        "day": ["Rocha maciça."],
    },
    "cristais": {
        "name": "Cristais", "color": "bright_cyan", "passable": True, "cost": 12, "vision": 1,
        "day": [
            "Cristais azulados brotam do chão e das paredes, emitindo uma luz suave e fria.",
            "Os cristais vibram com um zumbido baixo quando você passa — quase uma melodia.",
        ],
    },
    "lago_subterraneo": {
        "name": "Lago subterrâneo", "color": "blue", "passable": False, "cost": 0, "vision": 0,
        "day": ["Água negra e imóvel como um espelho."],
    },
    "entalhes": {
        "name": "Paredes entalhadas", "color": "magenta", "passable": True, "cost": 10, "vision": 0,
        "day": [
            "Relevos cobrem cada palmo da rocha: luas, olhos e figuras de mãos dadas.",
            "Os entalhes são precisos como joalheria. Quem os fez tinha séculos de paciência.",
        ],
    },
    "chao_toca": {
        "name": "Chão da toca", "color": "yellow", "passable": True, "cost": 10, "vision": 0,
        "day": [
            "Terra batida e úmida, coberta de pegadas de lobo — dezenas, umas sobre as outras.",
            "O chão está forrado de pelos e folhas secas arrastadas para dentro pelas feras.",
            "Um fio de água escorre pela parede e some numa fresta do chão.",
        ],
    },
    "ossos": {
        "name": "Ossada", "color": "white", "passable": True, "cost": 12, "vision": 0,
        "day": [
            "Ossos estalam sob suas botas: costelas, crânios pequenos, um chifre de cervo partido.",
            "Uma pilha de ossos roídos, alguns ainda com restos de carne.",
        ],
    },
    "raizes": {
        "name": "Raízes pendentes", "color": "green", "passable": True, "cost": 14, "vision": -1,
        "day": [
            "Raízes grossas pendem do teto como cortinas; é preciso afastá-las com as mãos para passar.",
            "Raízes da floresta lá em cima atravessam o túnel, retorcidas como dedos.",
        ],
    },
    "porta_selada": {
        "name": "Porta selada", "color": "bright_magenta", "passable": False, "cost": 0, "vision": 0,
        "day": ["Uma porta de pedra sem fechadura nem dobradiças."],
    },
}
