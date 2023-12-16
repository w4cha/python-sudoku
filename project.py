import sys
import os
import time
import re
import pandas as pd
from colorama import Fore, Style, Back, just_fix_windows_console
import platform
from pathlib import Path
from sudoku import Sudoku, Solution, InputError, SudokuError
from data import Database


def _read(game_value: str) -> tuple | str:
    """_read function get input from the user and checks that is a valid sudoku
    returning an error message if is not valid otherwise it returns a tuple with the game
    generated from the input and a sudoku solution object"""
    try:
        if game_value.isnumeric() and len(game_value) <= 2:
            read_game: Solution = Solution(size=int(game_value), letter=False, color=True)
            was_valid: pd.DataFrame = read_game.read()
        else:
            read_game: Solution = Solution(size=game_value, letter=False, color=True)
            was_valid: pd.DataFrame = read_game.read()
    except InputError as error_contents:
        if error_contents.game is not None:
            return f"\n{error_contents}\n{error_contents.game}\n"
        else:
            return str(error_contents)

    else:
        return str(was_valid), read_game


def _solve(game_object: Solution, max_time: float = 3) -> tuple | str:
    game_object.max_time = max_time
    """ function _read accepts a sudoku solution object and a max_time optional parameter as arguments
    (defines the time limit the program has to solve a sudoku before returning a time out error) 
    and returns a tuple from the solution object with additional information about the solved game"""
    try:
        game_object.solve()
    except (InputError, SudokuError) as error:
        return str(error)
    else:
        return str(game_object), game_object.extra_info(raw_level=True), game_object.stringify()


def _choose_game(choose_value: str, db_path: str) -> int | tuple:
    """ function _choose_game accept as arguments choose_value (str from the user)
    and a valid path like str where the database with the sudokus is located and return 0 if no games
    where found (if the user game is not in the database or there are no games) or a tuple with the game
    info if something is found"""
    if choose_value.isnumeric() and len(choose_value) <= 2:
        new_query = f"SELECT * FROM sudokus WHERE size = {choose_value} ORDER BY random() LIMIT 1"
    elif "-" in choose_value and len(choose_value) <= 3:
        new_query = f"SELECT * FROM sudokus WHERE size NOT IN ({choose_value[1:]}) ORDER BY random() LIMIT 1"
    elif choose_value == "all":
        new_query = f"SELECT * FROM sudokus ORDER BY random() LIMIT 1"
    else:
        new_query = (f"SELECT * FROM sudokus WHERE start_str = ?", [choose_value])
    with Database(db_path=db_path) as read_entry:
        for posible_game in read_entry.read_db(entries=new_query, as_row=True):
            return Sudoku(sudoku_size=posible_game["start_str"]), Sudoku(sudoku_size=posible_game["end_str"])
        return 0


def _play(games: tuple[Sudoku, Sudoku]) -> None:
    """ function _play allows the user to play a game from the solved games' database, accepts as arguments a tuple
    with two Sudoku object inside it one the game selected by the user and the other the game solution that it's
    used to know if the user input is part of it"""
    starting_place, ending_place = games
    print("\nTo start solving enter a valid play, the format of a valid play is:\n"
          "first the row, then the column and finally the value to enter, each\n"
          "value can't be bigger than the sudoku size and if it's bigger than 9\n"
          "use letters to represent it (a for 10, b for 11 and so on\n"
          "Example: agb, a95, 978, 432, ggg, are all valid plays, while\n"
          "fgh, fgg4, 14135, 9a6 (if sudoku size is 9), 453 (if sudoku size if 4)\n"
          "are all invalid.\n"
          "To stop playing enter 000.")
    starting_place.read()
    ending_place.read()
    print("\n", starting_place, "\n")
    board = str(starting_place)
    star_val = set("".join(list(map(Solution.tr, val.values()))) for val in starting_place.initial_numbers())
    end_val = set("".join(list(map(Solution.tr, val.values()))) for val in ending_place.initial_numbers())
    valid_moves: list = list(end_val - star_val)
    right_answers: list = []
    if platform.system() == "Windows":
        just_fix_windows_console()
    while True:
        new_play = input("next move (000 to quit game): ").strip().lower()
        if new_play != "000":
            move: list = _valid_play(new_play, starting_place.size)
            if move:
                if new_play in valid_moves:
                    valid_moves.remove(new_play)
                    right_answers.append(move)
                    board = _add_color(values=right_answers, object_=board)
                    print("\n", board)
                    if not valid_moves:
                        print("Game solved.")
                        return
                elif new_play[0:-1] in [val[0:-1] for val in valid_moves]:
                    board = _add_color(values=[move], object_=board, right=False)
                    print("\n", board)

                else:
                    print("You are trying to make a move on an already solved place,\n"
                          "please try another move.")
            else:
                print("Enter a valid move.")
        else:
            return


def _add_color(values: list, object_: str, right: bool = True) -> str:
    """ function _add_color is responsable for adding color to the current sudoku
    the user is playing (on a command line interface), adding red on the sudoku if
    the user input is not part of the game solution and green if it is, as arguments this function
    accepts a list of values to be colored, a str that is the current game being played and a bool value
    use to know if the lis of values are correct or incorrect plays
    """
    game_rows = [item.split()[1:] for item in object_.split("\n") if item][1:]
    for to_change in values:
        game_rows[to_change[0] - 1][to_change[1] - 1] = Fore.GREEN + str(to_change[2]) + \
                                                        Style.RESET_ALL if right \
                                                        else Fore.RED + str(to_change[2]) + Style.RESET_ALL
    head = f"{' ' * (len(str(len(game_rows))) + 3)}"
    head += f"{''.join([f' col{val}' for val in range(1, len(game_rows) + 1)])}\n"
    for count, row in enumerate(game_rows, 1):
        head += f"row{count}{' ' * (3 - len(str(count)))}" if len(game_rows) > 9 else f"row{count} "
        for step, val_item in enumerate(row, 1):
            head += _item_format(val_item, step)
        head += "\n"
    return head


def _item_format(item: str, position: int) -> str:
    """ function _item_format accepts as arguments a str that is the  value inside
    a cell of the current game and an int that is the position of that cell inside a row
    and used them to properly format the game when is printed, the new format cell value
    is returned as a str"""
    if len(item) > 2:
        number = re.search(r"m([1-9]|1[0-6])\x1b", item)[1]
        return f"{' ' * (3 + len(str(position)) - len(number))}{item} "
    else:
        return f"{' ' * (3 + len(str(position)) - len(item))}{item} "


def _valid_play(play_input: str, sudoku_size: int) -> list:
    """ function _valid_play accepts as argument a str that is the user input and an int that represents
    the size of the current played game to then return an empty list if the user input doesn't have
    the format of a valid sudoku play (not an incorrect play just not a valid one) and returns a list with the
    coordinates to find that cell inside the current game (to latter verify if the play was an incorrect or correct
    answer) if the play was valid"""
    current_size = {4: "^[1-4]{3}$", 9: "^[1-9]{3}$", 16: "^(?:[1-9]|[a-g]){3}$"}
    if re.search(current_size[sudoku_size], play_input) is not None:
        return [Solution.tr(coord) for coord in play_input]
    else:
        return []


def _save_game(query: tuple, database_location: str, test: bool = False) -> bool:
    """function _save_game accepts a tuple as an argument and loads the game info into a db file
    checking before if the entry has not being already submitted, so there are not two sudokus
    with the same solution in the database"""
    is_present: tuple = ("SELECT end_str FROM sudokus WHERE end_str = ?", [query[1][1]])
    with Database(db_path=database_location) as add_entry:
        if not next(add_entry.read_db(entries=is_present), False):
            if not test:
                add_entry.write_db(values=query)
            return True
        return False


def main(db_file=str(Path(fr"{os.path.abspath(os.path.dirname(__file__))}\sudoku_table.db"))) -> None:
    """ function main accepts as is only argument a path like str where the database used by
    this program to save and read sudoku games is located and the purpose of the function is
    to serve as a main menu from where the user can solve and play game being by calling all the other functions in
    this file directly or indirectly"""
    print(f"{Back.LIGHTRED_EX}{Fore.BLACK}Welcome "
          f"to {Fore.LIGHTMAGENTA_EX}S{Fore.BLACK}udoku{Fore.LIGHTMAGENTA_EX}S{Fore.BLACK}olver{Style.RESET_ALL}")
    while True:
        play_or_solve = input("\nEnter p to play or s to solve, anything else to exit: ").lower().strip()
        if play_or_solve == "s":
            while True:
                game_size_or_sequence = input("\nEnter a valid game size or sequence, "
                                              "n to go back: ").lower().strip()
                if game_size_or_sequence in ("4", "9", "16"):
                    Sudoku.enter_game(sudoku_df=int(game_size_or_sequence))
                    time.sleep(3)
                    proceed = input("\nEnter your game, when rady enter y to "
                                    "proceed, anything else to go back: ").lower().strip()
                    if proceed != "y":
                        break
                elif game_size_or_sequence == "n":
                    break
                new_game = _read(game_size_or_sequence)
                if isinstance(new_game, str):
                    print(new_game)
                else:
                    print(f"\n{new_game[0]}\n")
                    solution: tuple = _solve(new_game[1])
                    if isinstance(solution, tuple):
                        info_labels: tuple = ("game starting values", "game solving time",
                                              "game difficulty", "game start id", "game solution id")
                        game_info = list(f"{val[0]}: {val[1]}" for val in
                                         zip(info_labels, (solution[1] | solution[2]).values()))
                        print(f"{solution[0]}\n",
                              *game_info,
                              sep="\n")
                        new_query: tuple = ("INSERT INTO sudokus (start_str, end_str, "
                                            "init_vals, difficulty, size) VALUES (?, ?, ?, ?, ?)",
                                            (solution[2]["start"], solution[2]["end"],
                                             solution[1]["start_vals"], solution[1]["difficulty"], new_game[1].size))
                        if _save_game(new_query, db_file):
                            print("\nnew game added to database, copy the start id or "
                                  "solution id if you want to play it")
                    else:
                        print(solution)
        elif play_or_solve == "p":
            while True:
                random_or_id = input("\nEnter r to choose a random game, enter "
                                     "a valid id or n to go back: ").lower().strip()
                if random_or_id == "n":
                    break
                elif random_or_id == "r":
                    while True:
                        all_sizes = input("\nEnter from what sizes (4, 9 or 16) to choose randomly,\n"
                                          "for all sizes enter all for one sizes enter the numbers,\n"
                                          "to select from all except one size enter minus next to\n"
                                          "excluded size(eg. -16 to elect randomly from 4 and"
                                          " 9 only) and to go back enter anything else: ").strip().lower()
                        if all_sizes in ["4", "9", "16", "all", "-4", "-9", "-16"]:
                            while True:
                                present_game: tuple[Solution, Solution] = _choose_game(all_sizes, db_file)
                                if present_game != 0:
                                    print("\n" + str(present_game[0]) + "\n")
                                    confirm = input("Choose this sudoku or get another?"
                                                    "\n(y to confirm, n to choose again, "
                                                    "anything else to go back): ").strip().lower()
                                    if confirm == "y":
                                        _play(present_game)
                                        break
                                    elif confirm != "n":
                                        break
                                else:
                                    print("\nno games where found, unable to play.")
                        else:
                            break
                else:
                    present_game: tuple[Solution, Solution] = _choose_game(random_or_id, db_file)
                    if present_game != 0:
                        _play(present_game)
                    else:
                        print("\ngame not found, try to solve it first if you want to add it to the play list.")
        else:
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        sys.exit("program execution aborted")
