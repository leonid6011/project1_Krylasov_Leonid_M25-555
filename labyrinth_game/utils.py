from .constants import ROOMS


def normalize(s: str) -> list[str]:
    return s.strip().lower().split() if s.strip() else []

def room_name(key: str) -> str:
    return key.replace("_", " ").title()

def describe_current_room(game_state: dict) -> None:
    #полное описание текущей комнаты и подсказки
    key = game_state["current_room"]
    room = ROOMS[key]

    print(f"\n== {room_name(key).upper()} ==")
    print(room["description"])

    #предметы
    if room["items"]:
        print("Заметные предметы:", ", ".join(room["items"]))

    #выходы
    if room["exits"]:
        exits = ", ".join(f"{d}->{room_name(nxt)}" for d, nxt in room["exits"].items())
        print("Выходы:", exits)

    #загадка
    if room["puzzle"] is not None:
        print("Кажется, здесь есть загадка (используйте команду solve)")
    
def solve_puzzle(game_state: dict) -> None:
    #решение обычной загадки в текущей комнате
    room_key = game_state["current_room"]
    room = ROOMS[room_key]
    puzzle = room.get("puzzle")
    if not puzzle:
        print("Загадки здесь нет.")
        return
    
    question, answer = puzzle
    print(question)
    user = input("Ваш ответ: ").strip().lower()

    if user == str(answer).strip().lower():
        print("Верно! Вы справились с загадкой.")
        #запретим решать одну и туже загадку дважды
        room["puzzle"] = None
        #награда игроку
        game_sate["player_inventory"].append("token")
    else:
        print("Неверно. Попробуйте снова.")

def attempt_open_treasure(game_state: dict) -> None:
    #открыть сундук ключем или кодом
    room_key = game_state["current_room"]
    room = ROOMS[room_key]

    if room_key != "treasure_room":
        print("Здесь нечего открывать.")
        return
    
    #сундук должен быть среди предметов комнаты
    if "treasure_chest" not in room.get("items", []):
        print("Сундук уже открыт.")
        return
    
    inv = game_state["player_inventory"]

    # 1. Есть ключ?
    if "treasure_key" in inv:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        room["items"].remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
        return
    
    # 2. Нет ключа, предложить ввести код из puzzle
    puzzle = room.get("puzzle")
    if not puzzle:
        print("Сундук заперт, и кода тут не найти.")
        return
    
    choice = input("Сундуе запрет... Ввести код? (да/нет) ").strip().lower()
    if choice not in {"да", "yes", "y"}:
        print("Вы отступаете от сундука.")
        return
    
    question, answer = puzzle
    print(question)
    code = input("Ваш ответ: ").strip().lower()

    if code == str(answer).strip().lower():
        print("Код верный! Замок щёлкнул. Сундук открыт!")
        room["items"].remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
    else:
        print("Код неверный.")

def show_help():
    print("\nДоступные команды:")
    print("  go <direction>  - перейти в направлении (north/south/east/west)")
    print("  look            - осмотреть текущую комнату")
    print("  take <item>     - поднять предмет")
    print("  use <item>      - использовать предмет из инвентаря")
    print("  inventory       - показать инвентарь")
    print("  solve           - попытаться решить загадку в комнате")
    print("  quit            - выйти из игры")
    print("  help            - показать это сообщение")