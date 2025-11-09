#!/usr/bin/env python3

from .constants import COMMANDS
from .player_actions import get_input, move_player, show_inventory, take_item, use_item
from .utils import (
    attempt_open_treasure,
    describe_current_room,
    normalize,
    show_help,
    solve_puzzle,
)

game_state = {
        'player_inventory': [], # Инвентарь игрока
        'current_room': 'entrance', # Текущая комната
        'game_over': False, # Значения окончания игры
        'steps_taken': 0 # Количество шагов
  }

def process_command(game_state: dict, command: str) -> None:
    #парсер ввода и обработка действия
    parts = normalize(command)
    if not parts:
        return
    
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""
    
    #возможность ходить просто направлениям
    if command in ["north", "south", "east", "west"]:
        move_player(game_state, command)
        return

    match cmd:
        case "look":
            describe_current_room(game_state)
        case "inventory" | "inv":
            show_inventory(game_state)
        case "go":
            if not arg:
                print("Куда идти? (north/south/east/west)")
            else:
                move_player(game_state, arg)
        case "take":
            if not arg:
                print("Что взять?")
            else:
                take_item(game_state, arg)
        case "use":
            if not arg:
                print("Что использовать?")
            else:
                use_item(game_state, arg)
        case "solve":
            if game_state["current_room"] == "treasure_room":
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)
        case "help":
            show_help(COMMANDS)
        case "quit" | "exit":
            game_state["game_over"] = True
        case _:
            print("Неизвестная комманда.")

def main() -> None:
    print("Добро пожаловать в Лабиринт сокровищ!")
    describe_current_room(game_state)

    while not game_state['game_over']:
        user_cmd = get_input("=> ")
        process_command(game_state, user_cmd)

if __name__ == "__main__":
    main()