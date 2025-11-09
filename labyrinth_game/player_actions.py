from .constants import ROOMS
from .utils import describe_current_room, random_event


def show_inventory(game_state: dict) -> None:
    inv = game_state["player_inventory"]
    if inv:
        print("Ваш инвентарь:", ", ".join(inv))
    else:
        print("Инвентарь пуст.")

def get_input(promt: str = "> ") -> str:
    try:
        return input(promt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры!")
        return "quit"

def move_player(game_state: dict, direction: str) -> None:
    #перемещение между комнатами по направлению (north/south/east/west)
    current = game_state["current_room"]
    exits = ROOMS[current].get("exits", {})

    if direction not in exits:
        print("Нельзя пойти в этом направлении.")
        return
    
    #проверяем возможность входа в комнату сокровищ
    if exits[direction] == "treasure_room":
        if "rusty_key" in game_state["player_inventory"]:
            print("Вы используете найденный ключ, чтобы открыть путь " \
            "в комнату сокровищ.")
        else:
            print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
            return

    new_room = exits[direction]
    game_state["current_room"] = new_room
    game_state["steps_taken"] += 1
    describe_current_room(game_state)

    random_event(game_state)

def take_item(game_state: dict, item_name: str) -> None:
    #нельзя поднимать сундук
    if item_name == "treasure_chest":
        print("Вы не можете поднять сундук, он слишком тяжёлый.")
        return

    #подобрать предмет если он есть в текущей комнате
    room_key = game_state["current_room"]
    room_items = ROOMS[room_key].get("items", [])

    if item_name in room_items:
        room_items.remove(item_name)
        game_state["player_inventory"].append(item_name)
        print(f"Вы подняли: {item_name}")
    else:
        print("Такого предмета здесь нет.")
    

def use_item(game_state: dict, item_name: str) -> None:
    #Используем предмет из инвенторя
    inv = game_state["player_inventory"]
    if item_name not in inv:
        print("У вас нет такого предмета.")
        return
    
    if item_name == "torch":
        print("Вы зажгли факел. Стало светлее.")
    elif item_name == "sword":
        print("Меч придает вам уверенности.")
    elif item_name == "bronze_box":
        if "rusty_key" not in inv:
            inv.append("rusty_key")
            print("Вы открыли бронзовую шкатулку и нашли ключ (rusty_key)!")
        else:
            print("Шкатулка пуста.")
    else:
        print("Вы не знаете, как использовать это предмет.")