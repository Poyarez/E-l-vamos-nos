"""Comércio: comprar e vender com os mercadores do vale.

O preço de compra é o valor do item vezes o ``markup`` da loja; a venda paga o valor do
item (como os vendedores do WoW). Itens de missão não podem ser vendidos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from . import screens, ui
from .data.shops import SHOPS
from .items import ItemStack, get_item, item_name, item_summary
from .utils import format_money

if TYPE_CHECKING:
    from .player import Player
    from .session import GameSession


def get_shop(shop_id: str) -> Dict[str, Any]:
    return SHOPS[shop_id]


def buy_price(shop_id: str, item_id: str) -> int:
    return get_item(item_id)["value"] * get_shop(shop_id)["markup"]


def can_sell(item_id: str) -> bool:
    item = get_item(item_id)
    return item["type"] != "missao" and item["value"] > 0


def buy(player: "Player", shop_id: str, item_id: str, quantity: int = 1) -> int:
    """Compra itens; devolve o total pago. Levanta ``ValueError`` se não der."""
    if item_id not in get_shop(shop_id)["stock"]:
        raise ValueError("Esse item não está à venda aqui.")
    total = buy_price(shop_id, item_id) * quantity
    if total > player.copper:
        raise ValueError(f"Você não tem dinheiro suficiente (custa {format_money(total)}).")
    leftover = player.inventory.add(item_id, quantity)
    if leftover:
        player.inventory.remove(item_id, quantity - leftover)
        raise ValueError("Não há espaço na mochila para tudo isso.")
    player.copper -= total
    return total


def sell(player: "Player", stack: ItemStack, quantity: int) -> int:
    """Vende unidades de uma pilha da mochila; devolve o valor recebido."""
    if not can_sell(stack.item_id):
        raise ValueError(f"{stack.data['name']} não pode ser vendido.")
    quantity = max(1, min(quantity, stack.quantity))
    earned = stack.data["value"] * quantity
    player.inventory.take(stack, quantity)
    player.copper += earned
    return earned


def junk(player: "Player") -> List[ItemStack]:
    return [stack for stack in player.inventory if stack.data["type"] == "lixo" and can_sell(stack.item_id)]


def sell_junk(player: "Player") -> Tuple[int, int]:
    """Vende toda a sucata (itens de qualidade pobre sem outra utilidade). Devolve (unidades, valor)."""
    units = earned = 0
    for stack in junk(player):
        units += stack.quantity
        earned += sell(player, stack, stack.quantity)
    return units, earned


# --------------------------------------------------------------------------- interface

def _ask_quantity(prompt: str, default: int, maximum: int) -> Optional[int]:
    raw = ui.ask(f"  {prompt} " + ui.style(f"(Enter = {default}, 0 cancela)", "gray") + f" {ui.sym('arrow')} ")
    if not raw:
        return default
    if not raw.isdigit():
        ui.echo(ui.style("  Quantidade inválida.", "gray"))
        return None
    value = int(raw)
    return min(value, maximum) if value > 0 else None


def run(session: "GameSession", shop_id: str) -> None:
    shop = get_shop(shop_id)
    player = session.player
    message = ""
    while True:
        screens.section(f"{shop['name'].upper()}  {ui.sym('dot')}  seu dinheiro: {format_money(player.copper)}")
        if message:
            ui.echo_lines(ui.wrap(message, screens.screen_width() - 4, "  "))
            ui.echo()
            message = ""
        scraps = junk(player)
        options = ["Comprar", "Vender"]
        if scraps:
            value = sum(stack.data["value"] * stack.quantity for stack in scraps)
            options.append(f"Vender toda a sucata ({sum(s.quantity for s in scraps)} itens por {format_money(value)})")
        choice = ui.choose(options, prompt="Negociar", cancel="Sair da loja")
        if choice is None:
            session.needs_redraw = True
            return
        if choice == 0:
            message = _buy_menu(player, shop_id)
        elif choice == 1:
            message = _sell_menu(player)
        else:
            units, earned = sell_junk(player)
            message = ui.style(f"Você vende {units} itens de sucata por {format_money(earned)}.", "bright_green")
        session.dirty = True


def _buy_menu(player: "Player", shop_id: str) -> str:
    stock = get_shop(shop_id)["stock"]
    labels = [f"{item_name(item_id)} — {ui.style(format_money(buy_price(shop_id, item_id)), 'bright_yellow')}"
              for item_id in stock]
    details = [(item_summary(item_id) + ". " if get_item(item_id).get("slot") or get_item(item_id).get("tool") else "")
               + get_item(item_id)["description"] for item_id in stock]
    choice = ui.choose(labels, prompt="Comprar", cancel="Voltar", details=details)
    if choice is None:
        return ""
    item_id = stock[choice]
    affordable = player.copper // buy_price(shop_id, item_id)
    if affordable <= 0:
        return ui.style("Você não tem dinheiro para isso.", "red")
    quantity = _ask_quantity("Quantos?", 1, affordable)
    if quantity is None:
        return ""
    try:
        paid = buy(player, shop_id, item_id, quantity)
    except ValueError as error:
        return ui.style(str(error), "red")
    return ui.style(f"Você compra {item_name(item_id, colored=False)} x{quantity} por {format_money(paid)}.",
                    "bright_green")


def _sell_menu(player: "Player") -> str:
    sellable = [stack for stack in player.inventory if can_sell(stack.item_id)]
    if not sellable:
        return "Você não tem nada que a quitandeira queira comprar."
    labels = [f"{stack.name()} x{stack.quantity} — {ui.style(format_money(stack.data['value']), 'bright_yellow')} cada"
              for stack in sellable]
    details = [item_summary(stack.item_id) if stack.data.get("slot") else "" for stack in sellable]
    choice = ui.choose(labels, prompt="Vender", cancel="Voltar", details=details)
    if choice is None:
        return ""
    stack = sellable[choice]
    quantity = stack.quantity
    if quantity > 1:
        chosen = _ask_quantity("Quantos?", quantity, quantity)
        if chosen is None:
            return ""
        quantity = chosen
    name = stack.name(colored=False)
    earned = sell(player, stack, quantity)
    return ui.style(f"Você vende {name} x{quantity} por {format_money(earned)}.", "bright_green")
