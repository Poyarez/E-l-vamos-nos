# Crônicas de Primórdia

RPG de fantasia medieval para o terminal, escrito em Python puro. Ele combina três referências:

- **WoW Classic:** classes clássicas com Mana, Raiva e Energia, barra de ações, recargas, talentos e a curva de nível original (400 XP para o nível 2, até o 60).
- **Old School RuneScape:** perícias de coleta e produção independentes do combate, cada uma de 1 a 99, com a tabela de XP clássica (83 XP para o nível 2 e 13.034.431 XP para o 99).
- **Sea of Stars:** exploração com descrições ricas, minimapa em arte ASCII, ciclo de dia e noite, fases da lua e segredos escondidos no cenário.

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

## O que já dá para jogar (Etapa 1)

- **Menu principal:** continuar o último save, novo jogo, carregar ou apagar saves, opções e ajuda.
- **Criação de personagem**, passo a passo ou sorteada, sempre com uma tela de resumo onde qualquer escolha pode ser alterada:
  - nome, gênero (masculino, feminino ou não-binário) e classe (Guerreiro, Mago, Sacerdote ou Ladino);
  - estilo e cor do cabelo e um traço marcante;
  - cor da armadura inicial, que tinge o equipamento de verdade;
  - alinhamento (os 9 clássicos).

  Ao final, um retrato em texto descreve o personagem. Os NPCs se dirigem ao herói de acordo com o gênero escolhido.
- **Vale de Primórdia:** zona inicial de 60×30 coordenadas (1.347 tiles transitáveis) com 10 regiões e 39 locais notáveis. Cada local tem descrição de dia e de noite, um texto de exame e, em alguns casos, pontos de coleta.
- **Exploração:**
  - névoa de guerra e minimapa ASCII ao lado da descrição, mais um mapa completo com coordenadas;
  - movimento em 8 direções, com caminhadas longas (`n 5`) e viagem rápida até locais conhecidos (`ir estalagem`);
  - pistas sensoriais que guiam até lugares ainda não descobertos ("Você ouve o rugido de muita água caindo, em algum lugar ao norte").
- **Tempo:** cada passo custa minutos de jogo (a estrada é rápida, o pântano é lento). Existem dias, períodos do dia, clima e fases da lua. À noite o raio de visão encolhe. Dormir na estalagem leva até o amanhecer.
- **Progressão:** descobrir regiões, locais e segredos rende XP. Ao subir de nível, os atributos crescem e novas habilidades são desbloqueadas.
- **10 NPCs** com rotina diária e diálogos ramificados. As falas mudam conforme a classe, o alinhamento, os locais visitados e as pistas encontradas.
- **Diário:** pistas, rumores e segredos ficam registrados, junto com os locais descobertos por região.
- **Primeiro segredo:** há uma passagem escondida em algum lugar do vale, que leva a um mapa secreto com tesouro e um mistério. Converse com os moradores e examine tudo.
- **Saves em JSON:**
  - um arquivo por personagem;
  - salvamento automático a cada amanhecer e ao dormir;
  - escrita atômica e cópia de segurança `.bak`.

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
| `ficha` `mochila` `pericias` `habilidades` `diario` | telas do personagem |
| `salvar` `opcoes` `ajuda` `menu` | sistema |

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
  combat.py              escolas de dano (elementos) e fraquezas/resistências
  crafting.py            reservado para coleta e ofícios (Etapa 3)
  world.py               mapas em coordenadas, terrenos, regiões, locais, passagens, pathfinding
  time_system.py         relógio, períodos do dia, clima e fases da lua
  npcs.py                fábrica de NPCs, rotinas e motor de diálogos (condições e efeitos)
  state.py               estado completo da partida (o que vai para o save)
  save_system.py         saves em JSON: escrita atômica, backup, versões e migrações
  session.py             regras da exploração: movimento, visão, descobertas, tempo, segredos
  commands.py            registro de comandos, apelidos, sugestões e ajuda automática
  screens.py, mapview.py telas e mapas em arte ASCII
  character_creation.py  criação de personagem e prólogo
  data/                  o "banco de dados": classes, aparência, itens, terrenos, perícias, NPCs
    maps/                um módulo por mapa (vale_primordia.py, gruta_veu_prata.py)
tests/                   testes automatizados (unittest, sem dependências)
```

Os módulos de `rpg/data` contêm **apenas dados**. Os módulos de regra funcionam como fábricas que transformam esses dicionários em objetos do jogo. Para expandir o mundo, basta, na maioria das vezes, editar os dados:

- **Novo mapa:** crie `rpg/data/maps/<id>.py` com o desenho ASCII, a legenda, as regiões, os locais e as passagens, e registre o módulo em `rpg/data/maps/__init__.py`. O caractere do desenho é o mesmo que aparece no minimapa.
- **Novo NPC:** acrescente uma entrada em `rpg/data/npcs.py` com a rotina e os nós de diálogo. Condições (`if`) e efeitos (`effects`) cobrem flags, pistas no diário, itens, ouro e XP.
- **Novo item, classe ou habilidade:** edite `rpg/data/items.py` ou `rpg/data/classes.py`.
- **Novo comando:** use o decorador `@command(...)` em `rpg/commands.py`. Ele já aparece na ajuda.

Os testes em `tests/test_world.py` validam todo o banco de dados: coordenadas válidas, locais alcançáveis, passagens com destino, diálogos sem nós quebrados e marcadores de texto conhecidos.

## Saves

Os saves ficam em `saves/<nome>-<id>.json` (a pasta pode ser trocada pela variável de ambiente `PRIMORDIA_SAVE_DIR`). O formato é JSON legível. Cada save guarda o número da versão do formato, para que versões futuras do jogo consigam migrar saves antigos sem perder progresso.

## Testes

```
python -m unittest
```

São 50 testes:

- curvas de XP do WoW e do OSRS;
- atributos e equipamento de todas as classes;
- integridade dos mapas e dos diálogos;
- regras de movimento, visão, tempo e segredos;
- saves, incluindo a recuperação pela cópia de segurança;
- uma partida completa executando o `main.py` com entradas roteirizadas.

## Roteiro

- [x] **Etapa 1:** estrutura modular, menu, criação de personagem, Vale de Primórdia explorável, NPCs com diálogos, tempo, diário, saves.
- [ ] **Etapa 2:** combate por turnos no estilo WoW Classic:
  - barra de ações e recargas;
  - Mana, Raiva e Energia em ação;
  - timing de golpes e fraquezas elementares no estilo Sea of Stars;
  - primeiras zonas de monstros (Floresta Sussurrante, Toca dos Lobos), com tabelas de loot por porcentagem.
- [ ] **Etapa 3:** coleta e ofícios no estilo OSRS (mineração, metalurgia, pesca, culinária, alfaiataria e alquimia) usando os pontos de coleta já marcados no mapa.
- [ ] **Etapa 4:**
  - missões a partir das pistas do diário;
  - as três luas, a Mina de Ferro-Velho, o Bando do Corvo e a ilhota do lago;
  - baús trancados, NPCs ocultos, novas cidades e progressão de longo prazo.
