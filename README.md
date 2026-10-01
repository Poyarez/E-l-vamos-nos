# Crônicas de Primórdia

RPG de fantasia medieval para o terminal, escrito em Python puro. Ele combina três referências:

- **WoW Classic:** classes clássicas com Mana, Raiva e Energia, barra de ações, recargas, talentos e a curva de nível original (400 XP para o nível 2, até o 60).
- **Old School RuneScape:** perícias de coleta e produção independentes do combate, cada uma de 1 a 99, com a tabela de XP clássica (83 XP para o nível 2 e 13.034.431 XP para o 99).
- **Sea of Stars:** exploração com descrições ricas, minimapa em arte ASCII, ciclo de dia e noite, fases da lua, segredos escondidos no cenário e um combate por turnos com golpes no tempo certo, fraquezas elementares e selos que cancelam os ataques especiais das criaturas.

```
python main.py
```

Basta ter **Python 3.8 ou mais recente**. O jogo não depende de nenhuma biblioteca externa e roda no Linux, no macOS e no Windows (Windows Terminal, PowerShell ou CMD).

| Opção            | Efeito                                         |
|------------------|------------------------------------------------|
| `--sem-cor`      | desliga as cores ANSI                          |
| `--ascii`        | usa só caracteres ASCII em molduras e barras   |
| `--sem-animacao` | desliga a narração letra a letra               |

As mesmas preferências podem ser ajustadas no menu **Opções** e ficam salvas.

## O que já dá para jogar

### Etapa 1: exploração

- **Menu principal:** continuar o último save, novo jogo, carregar ou apagar saves, opções e ajuda.
- **Criação de personagem**, passo a passo ou sorteada, sempre com uma tela de resumo onde qualquer escolha pode ser alterada:
  - nome, gênero (masculino, feminino ou não-binário) e classe (Guerreiro, Mago, Sacerdote ou Ladino);
  - estilo e cor do cabelo e um traço marcante;
  - cor da armadura inicial, que tinge o equipamento de verdade;
  - alinhamento (os 9 clássicos).

  Ao final, um retrato em texto descreve o personagem. Os NPCs se dirigem ao herói de acordo com o gênero escolhido.
- **Vale de Primórdia:** zona inicial de 60×30 coordenadas (1.347 tiles transitáveis) com 11 regiões e 39 locais notáveis. Cada local tem descrição de dia e de noite, um texto de exame e, em alguns casos, pontos de coleta.
- **Exploração:**
  - névoa de guerra e minimapa ASCII ao lado da descrição, mais um mapa completo com coordenadas;
  - movimento em 8 direções, com caminhadas longas (`n 5`) e viagem rápida até locais conhecidos (`ir estalagem`);
  - pistas sensoriais que guiam até lugares ainda não descobertos ("Você ouve o rugido de muita água caindo, em algum lugar ao norte").
- **Tempo:** cada passo custa minutos de jogo (a estrada é rápida, o pântano é lento). Existem dias, períodos do dia, clima e fases da lua. À noite o raio de visão encolhe. Dormir na estalagem leva até o amanhecer.
- **Progressão:** descobrir regiões, locais e segredos rende XP. Ao subir de nível, os atributos crescem e novas habilidades são desbloqueadas.
- **11 NPCs** com rotina diária e diálogos ramificados. As falas mudam conforme a classe, o alinhamento, os locais visitados e as pistas encontradas.
- **Diário:** pistas, rumores e segredos ficam registrados, junto com os locais descobertos por região.
- **Primeiro segredo:** há uma passagem escondida em algum lugar do vale, que leva a um mapa secreto com tesouro e um mistério. Converse com os moradores e examine tudo.
- **Saves em JSON:**
  - um arquivo por personagem;
  - salvamento automático a cada amanhecer e ao dormir;
  - escrita atômica e cópia de segurança `.bak`.

### Etapa 2: combate

- **Combate por turnos no estilo WoW Classic:**
  - barra de ações com as habilidades da classe (teclas `1` a `9`), recargas contadas em turnos e custos em Mana, Raiva ou Energia;
  - o Guerreiro gera Raiva ao bater e ao apanhar (com a fórmula do Classic) e a perde fora da luta. O Ladino recupera 20 de Energia por turno e acumula até 5 pontos de combo para os finalizadores. Mago e Sacerdote regeneram Mana conforme o Espírito;
  - acerto, esquiva, críticos, armadura com a redução do Classic (até 75%), dano e cura contínuos, escudos, bônus, atordoamento, congelamento e medo;
  - de 6 a 7 habilidades por classe entre os níveis 1 e 10: Investida, Executar, Bola de Fogo, Nova Congelante, Palavra de Poder: Escudo, Grito Psíquico, Furtividade, Apunhalar, Chute e outras.
- **Toques de Sea of Stars:**
  - fraquezas e resistências elementares (Físico, Fogo, Gelo, Arcano, Sagrado, Sombra e Natureza);
  - **selos:** quando uma criatura concentra um golpe especial, surgem selos de elementos. Cada acerto do elemento certo rompe um selo. Romper todos cancela o golpe e atordoa a criatura; romper só alguns enfraquece o golpe;
  - **reflexos:** apertar Enter logo depois do sinal ✦ dá um golpe perfeito (+25% de dano ou de cura) ou um bloqueio perfeito (metade do dano de um golpe especial). O minijogo pode ser desligado em **Opções** e não aparece quando a entrada não vem de um terminal.
- **13 criaturas** de 4 famílias, com saque por porcentagem e moedas. Vida, dano e armadura seguem uma curva por nível. A XP por abate usa a fórmula original (com bônus para criaturas acima do seu nível), e os níveis aparecem com as cores de dificuldade do Classic.
- **Encontros:**
  - tabelas por região, com criaturas diurnas e noturnas;
  - menos chance de encontro na estrada e alguns passos de trégua depois de cada luta;
  - emboscadas, inclusive ao descansar no mato;
  - a opção de tentar evitar a luta, e a de emboscar a presa, exclusiva do Ladino (o primeiro golpe é crítico);
  - o comando `cacar`, que procura uma presa de propósito;
  - a faixa de nível das criaturas da região, mostrada na tela de exploração.
- **Toca dos Lobos:** a primeira masmorra (nível 4 ou mais), com três encontros fixos: a Galeria dos Ossos, o acampamento de Varek, o Domador, e o covil de Presa-de-Gelo, o Alfa Branco. O Alfa é um chefe de elite que chama reforços e não deixa ninguém fugir. Dá para recuar de um encontro fixo e voltar mais preparado.
- **Derrota:** o herói desperta na Capela da Aurora horas depois, com metade da vida e 10% das moedas a menos.
- **Equipamento:**
  - proficiências por classe: armaduras de tecido, couro e malha; espadas, machados, maças, adagas, cajados e escudos;
  - armas de duas mãos e luta com duas armas (Guerreiro e Ladino);
  - peças com atributos; ao equipar, o jogo mostra o que muda na armadura, na vida e no recurso.
- **Consumíveis:** pão e água fora de combate, poções a qualquer hora.
- **Comércio:** Dona Graça, no mercado da vila, vende mantimentos e poções e compra o que você trouxer do mato, com uma opção para vender toda a sucata de uma vez.
- **Bestiário:** registra abates, saques vistos e as fraquezas descobertas, seja acertando o elemento certo ou analisando a criatura (`x`) durante a luta.
- **Novas pistas:** a aljava gravada da Toca, o culto da Lua Cortada e a recompensa da Capitã Renna pelo Alfa Branco.

## Comandos

Acentos e maiúsculas não importam, e quase todo comando tem atalhos. Digite `ajuda` no jogo para ver a lista completa.

| Comando | O que faz |
|---|---|
| `n` `s` `l` `o` `ne` `no` `se` `so` | anda (acrescente um número para dar vários passos: `n 5`) |
| `ir <local>` | viaja até um local já descoberto (`ir praça`, `ir cachoeira`) |
| `olhar` / `examinar` | descreve o lugar / procura detalhes, pistas e segredos |
| `falar [nome]` | conversa com quem estiver no local (marcados com `!` no mapa) |
| `mapa` | mapa completo com coordenadas e legenda |
| `entrar` / `sair` | atravessa entradas e passagens |
| `descansar` / `esperar [h]` | dorme (na estalagem, até o amanhecer) / deixa o tempo passar |
| `cacar` | procura uma presa na região (20 minutos) |
| `equipar [item]` / `remover [item]` | veste ou tira equipamento, mostrando o que muda |
| `usar [item]` | come, bebe ou usa um consumível (`comer pão`, `beber poção`) |
| `largar <item> [qtd]` | joga itens fora para abrir espaço na mochila |
| `comerciar` | compra e vende com o mercador que estiver no local |
| `ficha` `mochila` `pericias` `habilidades` `diario` `bestiario` | telas do personagem |
| `salvar` `opcoes` `ajuda` `menu` | sistema |

Durante a luta:

| Tecla | O que faz |
|---|---|
| `1` a `9` | usa a habilidade da barra de ações (`1 2` usa a habilidade 1 no inimigo 2); o nome da habilidade também funciona |
| `a` | ataca com a arma |
| `d` | defende: o dano recebido cai pela metade até o seu próximo turno |
| `i` | usa um item |
| `x` | analisa um inimigo e revela fraquezas e resistências |
| `f` | foge (impossível contra chefes) |
| `?` | ajuda |

## Estrutura do projeto

```
main.py                  ponto de entrada: menu principal e Main Game Loop
rpg/
  ui.py                  terminal: cores ANSI, molduras, barras, menus, entrada (com alternativa ASCII)
  config.py              título, versão, pasta de saves e preferências
  utils.py               texto, sorteios determinísticos, dinheiro (ouro/prata/cobre)
  player.py              herói: aparência, atributos, curva de XP do WoW Classic, equipamento
  skills.py              perícias com a tabela de XP do OSRS (1 a 99)
  items.py               fábrica de itens, pilhas e mochila
  combat.py              motor de combate: turnos, habilidades, efeitos, selos, críticos e armadura
  battle_ui.py           tela de combate: encontro, barra de ações, reflexos e resultados
  monsters.py            fábrica de monstros, XP por abate, cores de dificuldade, saque e encontros
  shop.py                comércio: preços, compra, venda e sucata
  conditions.py          condições usadas por diálogos e tabelas de encontros
  crafting.py            reservado para coleta e ofícios (Etapa 3)
  world.py               mapas em coordenadas, terrenos, regiões, locais, passagens, pathfinding
  time_system.py         relógio, períodos do dia, clima e fases da lua
  npcs.py                fábrica de NPCs, rotinas e motor de diálogos (condições e efeitos)
  state.py               estado completo da partida (o que vai para o save)
  save_system.py         saves em JSON: escrita atômica, backup, versões e migrações
  session.py             regras da exploração: movimento, visão, tempo, segredos, encontros e derrota
  commands.py            registro de comandos, apelidos, sugestões e ajuda automática
  screens.py, mapview.py telas e mapas em arte ASCII
  character_creation.py  criação de personagem e prólogo
  data/                  o "banco de dados": classes, aparência, itens, terrenos, perícias, NPCs, monstros, lojas
    maps/                um módulo por mapa (vale_primordia.py, gruta_veu_prata.py, toca_dos_lobos.py)
tests/                   testes automatizados (unittest, sem dependências)
```

Os módulos de `rpg/data` contêm **apenas dados**. Os módulos de regra funcionam como fábricas que transformam esses dicionários em objetos do jogo. Para expandir o mundo, basta, na maioria das vezes, editar os dados:

- **Novo mapa:** crie `rpg/data/maps/<id>.py` com o desenho ASCII, a legenda, as regiões, os locais e as passagens, e registre o módulo em `rpg/data/maps/__init__.py`. O caractere do desenho é o mesmo que aparece no minimapa.
- **Novo NPC:** acrescente uma entrada em `rpg/data/npcs.py` com a rotina e os nós de diálogo. Condições (`if`) e efeitos (`effects`) cobrem flags, pistas no diário, itens, ouro e XP.
- **Novo item, classe ou habilidade:** edite `rpg/data/items.py` ou `rpg/data/classes.py`. Os efeitos das habilidades (dano, cura, efeitos periódicos, controle, combos...) são combinações de blocos que o motor de combate já entende.
- **Novo monstro:** acrescente uma entrada em `rpg/data/monsters.py` (faixa de níveis, multiplicadores de vida, dano e armadura, fraquezas, habilidades com selos e tabela de saque). Depois coloque a criatura na tabela `encounters` de uma região ou num encontro fixo (`encounter`) de um local.
- **Nova loja:** crie a entrada em `rpg/data/shops.py` e dê `"shop": "<id>"` a um NPC, com um nó de diálogo que tenha o efeito `open_shop`.
- **Novo comando:** use o decorador `@command(...)` em `rpg/commands.py`. Ele já aparece na ajuda.

Os testes em `tests/test_world.py` validam todo o banco de dados: coordenadas válidas, locais alcançáveis, passagens com destino, diálogos sem nós quebrados, marcadores de texto conhecidos, monstros, tabelas de encontros, habilidades, itens e lojas.

## Saves

Os saves ficam em `saves/<nome>-<id>.json` (a pasta pode ser trocada pela variável de ambiente `PRIMORDIA_SAVE_DIR`). O formato é JSON legível. Cada save guarda o número da versão do formato, para que versões futuras do jogo consigam migrar saves antigos sem perder progresso.

## Testes

```
python -m unittest
```

São 105 testes:

- curvas de XP do WoW e do OSRS;
- atributos e equipamento de todas as classes;
- integridade dos mapas, diálogos, monstros, encontros, habilidades, itens e lojas;
- regras de movimento, visão, tempo e segredos;
- combate: fórmulas do Classic, selos, interrupção, atordoamento, recargas, combos, efeitos periódicos, chefes e reforços;
- vitória, derrota, encontros aleatórios e fixos, caçada, equipamento, consumíveis e comércio;
- a tela de combate com entradas simuladas;
- saves, incluindo a recuperação pela cópia de segurança e o bestiário;
- uma partida completa executando o `main.py` com entradas roteirizadas.

## Roteiro

- [x] **Etapa 1:** estrutura modular, menu, criação de personagem, Vale de Primórdia explorável, NPCs com diálogos, tempo, diário, saves.
- [x] **Etapa 2:** combate por turnos no estilo WoW Classic:
  - barra de ações e recargas;
  - Mana, Raiva e Energia em ação;
  - timing de golpes, selos e fraquezas elementares no estilo Sea of Stars;
  - primeiras zonas de monstros (Floresta Sussurrante, Toca dos Lobos), com tabelas de loot por porcentagem;
  - equipamento, consumíveis, comércio e bestiário.
- [ ] **Etapa 3:** coleta e ofícios no estilo OSRS (mineração, metalurgia, pesca, culinária, alfaiataria e alquimia) usando os pontos de coleta já marcados no mapa.
- [ ] **Etapa 4:**
  - missões a partir das pistas do diário;
  - as três luas, a Mina de Ferro-Velho, o Bando do Corvo e a ilhota do lago;
  - baús trancados, NPCs ocultos, novas cidades e progressão de longo prazo.
