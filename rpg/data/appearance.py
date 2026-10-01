"""Opções de customização do personagem: gênero, cabelo, traço marcante, armadura e alinhamento.

Cada opção traz a descrição usada no "retrato" do personagem. ``forms`` define como os
NPCs se dirigem ao herói (os diálogos usam ``{tratamento}`` e ``{bem_vindo}``).
"""

GENDERS = {
    "masculino": {
        "name": "Masculino",
        "description": "Ombros largos de quem carrega o próprio destino.",
        "forms": {"tratamento": "senhor", "bem_vindo": "bem-vindo"},
    },
    "feminino": {
        "name": "Feminino",
        "description": "Postura firme de quem não espera permissão para ser lenda.",
        "forms": {"tratamento": "senhora", "bem_vindo": "bem-vinda"},
    },
    "nao_binario": {
        "name": "Não-binário",
        "description": "Uma presença que não cabe em rótulos — e nem precisa caber.",
        "forms": {"tratamento": "viajante", "bem_vindo": "boas-vindas"},
    },
}

HAIR_STYLES = {
    "curto_desgrenhado": {"name": "Curto e desgrenhado", "description": "fios curtos que parecem nunca ter conhecido um pente"},
    "longo_solto": {"name": "Longo e solto", "description": "cabelos longos que caem sobre os ombros como uma cascata"},
    "trancas_guerreiras": {"name": "Tranças guerreiras", "description": "tranças apertadas, presas com anéis de bronze"},
    "rabo_de_cavalo": {"name": "Rabo de cavalo alto", "description": "um rabo de cavalo alto, prático para a batalha"},
    "raspado_laterais": {"name": "Raspado nas laterais", "description": "laterais raspadas e uma longa faixa no topo"},
    "cachos_volumosos": {"name": "Cachos volumosos", "description": "cachos fartos que desafiam qualquer elmo"},
    "coque_monastico": {"name": "Coque monástico", "description": "um coque firme, como o dos monges da Ordem da Aurora"},
    "moicano": {"name": "Moicano", "description": "uma crista ousada que anuncia sua chegada"},
    "cabeca_raspada": {"name": "Cabeça raspada", "description": "a cabeça lisa, que reluz sob o sol"},
}

HAIR_COLORS = {
    "negro": {"name": "Negro-azeviche", "color": "gray", "adjective": "negro-azeviche"},
    "castanho": {"name": "Castanho", "color": "yellow", "adjective": "castanho"},
    "ruivo": {"name": "Ruivo-fogo", "color": "bright_red", "adjective": "ruivo como brasa"},
    "loiro": {"name": "Loiro-trigo", "color": "bright_yellow", "adjective": "loiro como trigo maduro"},
    "grisalho": {"name": "Grisalho", "color": "white", "adjective": "grisalho, prateado antes do tempo"},
    "branco": {"name": "Branco-lunar", "color": "bright_white", "adjective": "branco como a lua cheia"},
    "azul_noite": {"name": "Azul-noite", "color": "blue", "adjective": "azul-noite, como o céu antes da tempestade"},
}

FEATURES = {
    "nenhum": {"name": "Nenhum", "description": ""},
    "cicatriz": {"name": "Cicatriz no rosto", "description": "Uma cicatriz antiga atravessa a sobrancelha esquerda."},
    "sardas": {"name": "Sardas", "description": "Sardas salpicam o nariz e as maçãs do rosto."},
    "tatuagem_runica": {"name": "Tatuagem rúnica", "description": "Runas azuladas descem pelo pescoço, em uma língua esquecida."},
    "heterocromia": {"name": "Olhos de cores diferentes", "description": "Um olho é verde como musgo; o outro, âmbar como mel."},
    "pintura_de_guerra": {"name": "Pintura de guerra", "description": "Faixas de pintura ocre marcam o rosto, como as dos clãs da serra."},
    "barba_cerrada": {"name": "Barba cerrada", "description": "Uma barba cerrada e bem aparada emoldura o rosto."},
}

ARMOR_COLORS = {
    "carmesim": {"name": "Vermelho carmesim", "color": "red", "description": "vermelho como o estandarte dos heróis antigos"},
    "azul_real": {"name": "Azul real", "color": "blue", "description": "azul profundo, a cor da guarda de Alvorada"},
    "verde_floresta": {"name": "Verde floresta", "color": "green", "description": "verde de musgo, feito para sumir entre as árvores"},
    "negro_onix": {"name": "Negro ônix", "color": "gray", "description": "negro fosco, que bebe a luz das tochas"},
    "branco_marfim": {"name": "Branco marfim", "color": "bright_white", "description": "branco marfim, imaculado como uma promessa"},
    "dourado_solar": {"name": "Dourado solar", "color": "bright_yellow", "description": "dourado como o sol do meio-dia"},
    "roxo_imperial": {"name": "Roxo imperial", "color": "magenta", "description": "roxo imperial, a cor dos reis e dos tolos"},
}

ALIGNMENTS = {
    "leal_bom": {"name": "Leal e Bom", "law": "leal", "moral": "bom",
                 "description": "Honra, dever e compaixão. Cumpre a palavra e protege os indefesos."},
    "neutro_bom": {"name": "Neutro e Bom", "law": "neutro", "moral": "bom",
                   "description": "Faz o bem pelo bem, seguindo ou ignorando leis conforme a necessidade."},
    "caotico_bom": {"name": "Caótico e Bom", "law": "caotico", "moral": "bom",
                    "description": "Coração generoso e espírito livre. Regras são sugestões."},
    "leal_neutro": {"name": "Leal e Neutro", "law": "leal", "moral": "neutro",
                    "description": "A ordem acima de tudo: um código pessoal, uma tradição, um juramento."},
    "neutro": {"name": "Neutro", "law": "neutro", "moral": "neutro",
               "description": "Equilíbrio. Nem santo, nem vilão — apenas alguém que segue o próprio caminho."},
    "caotico_neutro": {"name": "Caótico e Neutro", "law": "caotico", "moral": "neutro",
                       "description": "Liberdade acima de tudo. Imprevisível, leal apenas aos próprios caprichos."},
    "leal_mau": {"name": "Leal e Mau", "law": "leal", "moral": "mau",
                 "description": "Usa as regras como arma. Ambicioso, metódico e sem piedade."},
    "neutro_mau": {"name": "Neutro e Mau", "law": "neutro", "moral": "mau",
                   "description": "Faz o que for preciso para ganhar. Os outros são ferramentas."},
    "caotico_mau": {"name": "Caótico e Mau", "law": "caotico", "moral": "mau",
                    "description": "Crueldade e capricho. O mundo existe para queimar."},
}
