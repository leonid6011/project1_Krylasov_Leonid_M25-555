import math

from .constants import EVENT_PROBABILITY, RANDOM_EVENT, RANDOM_SEED_OFFSET, ROOMS


def normalize(s: str) -> list[str]:
    """Преобразование команд"""
    return s.strip().lower().split() if s.strip() else []

def room_name(key: str) -> str:
    """Для вывода названий комнат"""
    return key.replace("_", " ").title()

def describe_current_room(game_state: dict) -> None:
    """Полное описание текущей комнаты и подсказки"""
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

def attempt_open_treasure(game_state: dict) -> None:
    """Открыть сундук ключем или кодом"""
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
    
    choice = input("Сундук запрет... Ввести код? (да/нет) ").strip().lower()
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

def show_help(commands: dict) -> None:
    """Вывод доступных команд"""
    print("\nДоступные команды:")
    for cmd, desc in commands.items():
        print(f"{cmd:<16} - {desc}")    

def pseudo_random(seed: int, modulo: int) -> int:
    """Детерменированный псевдослучайный генератор на синусе"""
    x = math.sin(seed * 12.9898) * 43758.5453
    frac = x - math.floor(x)
    return int(frac * modulo)

def trigger_trap(game_state: dict) -> None:
    """Срабатывание ловушки"""
    print("Ловушка активирована! Пол стал дрожжать...")
    inv = game_state["player_inventory"]

    if inv:
        #берем случайный предмет и теряем его
        indx = pseudo_random(game_state["steps_taken"], len(inv))
        lost = inv.pop(indx)
        print(f"Вы теряете предмет: {lost}.")
    else:
        #пустой инвентарь - шанс поражения в игре
        roll = pseudo_random(game_state["steps_taken"], EVENT_PROBABILITY)
        if  roll < 3:
            print("Удар пришелся слишком сильно... Вы падаете в пропасть. " \
            "Игра окончена.")
            game_state["game_over"] = True
        else:
            print("Вы едва удержались на ногах и уцелели.")

def random_event(game_state: dict) -> None:
    """Небольшие случайные события после перемещения игрока"""
    #сначала определяем будет ли событие вообще
    if pseudo_random(game_state["steps_taken"], EVENT_PROBABILITY) != 0:
        return
    
    #выбираем одно из трех событий
    pick = pseudo_random(game_state["steps_taken"] + RANDOM_SEED_OFFSET, RANDOM_EVENT)
    room_key = game_state["current_room"]
    room = ROOMS[room_key]
    inv = game_state["player_inventory"]

    if pick == 0:
        #1 сценарий - монетка
        print("Вы замечаете на полу монетку.")
        room.setdefault("items", []).append("coin")

    elif pick == 1:
        # 2 сценарий - шорох
        print("Слышен странный шорох где-то рядом...")
        if "sword" in inv:
            print("Вы крепче сжимаете меч - шорох отступает.")
    
    else:
         #3 сценарий - проверка ловушки при отсутствии факела
         if room_key == "trap_room" and "torch" not in inv:
            print("Опасно без света в этой комнате!")
            trigger_trap(game_state)

def solve_puzzle(game_state: dict) -> None:
    """Решение обычной загадки в текущей комнате"""
    room_key = game_state["current_room"]
    room = ROOMS[room_key]
    puzzle = room.get("puzzle")

    if not puzzle:
        print("Загадки здесь нет.")
        return
    
    question, correct = puzzle
    print(question)
    user = input("Ваш ответ: ").strip().lower()

    #допускаем альтернативный вариант ответа
    if user == str(correct).lower() or (str(correct) == "10" and user == "десять"):
        print("Верно! Вы справились с загадкой.")
        room["puzzle"] = None

        #разная награда в зависимости от комнаты
        if room_key == "hall":
            reward = "coin_hall"
        elif room_key == "library":
            reward = "coin_library"
        elif room_key == "trap_room":
            reward = "treasure_key"

        game_state["player_inventory"].append(reward)
        print(f"Вы получили {reward}!")
    else:
        print("Неверно. Попробуйте снова.")
        #если это ловушка то активируем её
        if room_key == "trap_room":
            trigger_trap(game_state)
