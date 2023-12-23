"""libraries used by this program"""

import pandas as pd
import os
import re
import time
import platform
import copy
import sys
from pathlib import Path
from more_itertools import flatten, unique_to_each, duplicates_everseen
from colorama import Fore, Style, just_fix_windows_console
from math import sqrt, ceil


class Sudoku:
    """ class Sudoku it's responsable for making sure that
    a valid sudoku has been submitted before attempting to solve it"""
    read_input_from: str = str(Path(fr"{os.path.abspath(os.path.dirname(__file__))}\input.txt"))

    def __init__(self, sudoku_size: int | str | pd.DataFrame = 9, letters: bool = False, sudoku_color: bool = False):
        # set pandas values to allow the display of dataframes in console or as a string
        # for 16x16 sudokus
        pd.set_option("display.max_columns", 16)
        pd.set_option("display.max_rows", 16)
        pd.set_option("display.width", 120)
        self.sudoku: None | pd.DataFrame = None
        self.size = sudoku_size
        self.letters = letters
        self.color = sudoku_color
        self.unknown_values: dict[str: list[int]] = {}
        self.initial_values: dict[str: list[int]] = {}
        self.verified: bool = False
        if self.color and platform.system() == "Windows":
            # allows the display of colored string in a windows console
            just_fix_windows_console()

    @property
    def color(self) -> bool:
        return self._color

    @color.setter
    def color(self, value: bool) -> None:
        if isinstance(value, bool):
            self._color = value
        else:
            raise InputError("Expected type value for class Sudoku color argument of bool, "
                             f"\ninstead you set color to an argument of type {type(value)}.")

    @property
    def letters(self) -> bool:
        return self._letters

    @letters.setter
    def letters(self, value: bool) -> None:
        if isinstance(value, bool):
            self._letters = value
        else:
            raise InputError("Expected type value for class Sudoku letters argument of bool, "
                             f"\ninstead you set color to an argument of type {type(value)}.")

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int | str | pd.DataFrame) -> None:
        if isinstance(value, int):
            if value in (4, 9, 16):
                self._size = value
            else:
                raise InputError("Invalid value for class Sudoku size argument, "
                                 f"\nexpected values: 4, 9, 16 your value: {value}.")
        elif isinstance(value, str):
            if re.search("^(?:[1-4]|-){16}|(?:[1-9]|-){81}|(?:[1-9]|[a-g]|-){256}$",
                         value) is not None:
                self.size = int(sqrt(len(value)))
                game = self.__create_template()
                current_row = 1
                for count, sudo_value in enumerate(value, start=1):
                    if sudo_value != "-":
                        game.at[f"row{current_row}",
                                f"col{count-self.size*(current_row-1)}"] = self.tr(sudo_value)
                    if count % self.size == 0:
                        current_row += 1
                self.sudoku = game
            elif re.search(r"^(?:(?:(?:[1-4]{2}){0,4}\|){3}(?:[1-4]{2}){0,4}|(?:(?:[1-9]{2}){0,9}\|){8}"
                           "(?:[1-9]{2}){0,9}|(?:(?:(?:[1-9]|[a-g])"
                           r"{2}){0,16}\|){15}(?:(?:[1-9]|[a-g]){2}){0,16})$", value) is not None:
                self.size = len(value.split("|"))
                game_rows = value.split("|")
                game: pd.DataFrame = self.__create_template()
                for count, row in enumerate(game_rows):
                    if row:
                        row = tuple((row[val:val+2]) for val in range(0, len(row), 2))
                        for sudo_value in row:
                            game.at[f"row{count + 1}", f"col{self.tr(sudo_value[0])}"] = self.tr(sudo_value[1])
                self.sudoku = game
            else:
                raise InputError("Invalid value for class Sudoku size argument, "
                                 f"\nexpected a valid sudoku string your value: {value}.")
        elif isinstance(value, pd.DataFrame):
            df_shape = value.shape
            match df_shape:
                case (4, 4) | (9, 9) | (16, 16):
                    self._size = df_shape[0]
                    self.sudoku = value
                case _:
                    raise InputError("Invalid value for class Sudoku size argument, "
                                     "\nexpected a valid sudoku dataframe of shape (4, 4), "
                                     f"(9, 9) or (16, 16), got dataframe of shape {df_shape} instead.")
        else:
            raise InputError("Invalid value for class Sudoku size argument, "
                             f"\nexpected value of type int, str or dataframe, got value type: {type(value)}.")

    @classmethod
    def enter_game(cls, sudoku_df: int = 9) -> None:
        """class method enter_game, expects as argument sudoku_df of type int
            if sudoku_dg is int it just creates a template in the txt file from where sudokus are validated
            that the user has to complete with the initial game numbers."""
        class_game = cls(sudoku_df).__create_template()
        with open(Sudoku.read_input_from, "w") as new_game:
            new_game.write(str(class_game))
        os.startfile(Sudoku.read_input_from, "open")

    def read(self) -> pd.DataFrame:
        """Sudoku class public read method: once a sudoku is in place (txt file from where sudokus are read)
            this method validate the sudoku first by its format (dataframe str format); second that only has as initial
            values 1-4 (sudoku size 4x4), 1-9 (sudoku size 9x9) or 1-16 or 1-9a-f (sudoku size 16x16); third that
            the total amount of initial values it's at least 4, 17 or 55 depending on the sudoku size (4, 9 or 16) and
            finally that there are not two equal initial values in a row, column or quadrant of the sudoku.
            If valid this method returns a dataframe with the initial numbers else it raises an InputError"""
        initial_values: int = 0
        if self.sudoku is not None:
            with open(Sudoku.read_input_from, "w") as put_game:
                put_game.write(str(self.sudoku))
        else:
            self.sudoku: pd.DataFrame = self.__create_template()
        with open(Sudoku.read_input_from, "r") as get_game:
            new_game = tuple(sentences.strip().lower() for sentences in get_game.readlines() if sentences.strip())
        if len(new_game) != self.size + 1:
            raise InputError("Rows are missing or there are more than required "
                             "in your sudoku.")
        if new_game[0] != " ".join(tuple(f"col{val}" for val in range(1, self.size + 1))):
            raise InputError("Invalid column sudoku format.")
        for count, line in enumerate(new_game[1:], 1):
            if re.search(fr"^row{count}\s+([1-9]\s+|1[0-6]\s+|[a-g]\s+|-\s+){{{self.size - 1}}}"
                         "([1-9]|1[0-6]|[a-g]|-)$", line) is None:
                raise InputError("There are invalid characters in your sudoku.")
            values: list = line.split()[1:]
            values: zip = zip(values, list(val for val in range((count - 1) * self.size + 1,
                                                                self.size * count + 1)))
            values: list = [(self.tr(val[0]), val[1]) if val[0] in ("a", "b", "c", "d", "e", "f", "g")
                            else (val if "-" in val else (int(val[0]), val[1])) for val in values]
            if all(tuple(map(lambda val: val <= self.size, (val[0] for val in values if "-" not in val)))):
                for user_input, position in values:
                    row: int = position//self.size if position % self.size == 0 else position//self.size + 1
                    col: int = self.size if position % self.size == 0 else position % self.size
                    quadrant = int(sqrt(self.size)) * (ceil(row / sqrt(self.size)) - 1) + ceil(col / sqrt(self.size))
                    if user_input != "-":
                        initial_values += 1
                        self.sudoku.at[f"row{row}", f"col{col}"] = user_input
                        self.initial_values[f"{self.tr(row)}{self.tr(col)}{self.tr(quadrant)}"] = [user_input]
                    else:
                        self.unknown_values[f"{self.tr(row)}{self.tr(col)}{self.tr(quadrant)}"] \
                         = [val for val in range(1, self.size + 1)]
            else:
                fails = tuple(str(val[0]) for val in values if '-' not in val and val[0] > self.size)
                raise InputError(f"Max value for a sudoku starting numbers is {self.size} "
                                 f"\nbut at row {count} you entered: "
                                 f"{', '.join(fails)}.")
        # minimum number of initial values required for a sudoku to have a unique
        # solution at the time of the writing of this program
        min_vals: dict[int: int] = {4: 4, 9: 17, 16: 55}
        if initial_values >= min_vals[self.size]:
            self.__validate_sudoku()
            for entry in self.initial_values:
                to_remove = self.initial_values[entry][0]
                entry_kin = {key: value for key, value in self.unknown_values.items() if self._filtro(key, entry)}
                for child in entry_kin:
                    if to_remove in entry_kin[child]:
                        self.unknown_values[child].remove(to_remove)
            if self.letters and self.size > 9:
                self.sudoku = self._with_letters(self.sudoku)
            self.verified = True
            return self.sudoku
        else:
            raise InputError("The minimum amount of number to solve a sudoku of\n"
                             f"size {self.size} is {min_vals[self.size]} and your sudoku has {initial_values}.")

    def __create_template(self) -> pd.DataFrame:
        """ create_template private method generates a dataframe of dimensions according to the object size
            property """
        rows: list = [f"row{size}" for size in range(1, self.size + 1)]
        datos_tabla: dict = {}
        for a in range(1, self.size + 1):
            datos_tabla[f"col{a}"] = ["-"]
        return pd.DataFrame(data=datos_tabla, index=rows)

    def __check_game(self) -> dict | str:
        """ private method check_game scans the current game to check for number
            repetition inside a column row or quadrant and then returns say repetitions if any was found"""
        error_locations: dict[str:list | set] = {
            "rows": [], "cols": [],
            "quadrants": [], "total": set()
        }
        for size_category in tuple(self.tr(val) for val in range(1, self.size + 1)):
            for place, pattern in (("rows", 0),
                                   ("cols", 1), ("quadrants", 2)):
                locations: dict[str:list] = {key: val for key, val in self.initial_values.items()
                                             if key[pattern] == size_category}
                has_repetition: tuple = tuple(duplicates_everseen(locations.values()))
                if has_repetition:
                    for sub_error in has_repetition:
                        location: list = [key for key, value in locations.items() if value == sub_error]
                        current_len: int = len(error_locations["total"])
                        error_locations["total"] |= set(location)
                        if current_len != len(error_locations["total"]):
                            error_locations[place].extend([location[0]])
        return {key: value for key, value in error_locations.items() if value} if error_locations["total"] else "void"

    def __validate_sudoku(self) -> None:
        """ private method validate_sudoku generates human-readable messages base on the output
            of the check_game method and save the errors wih more detail inside a dictionary
            that can be access through the InputError class"""
        has_error: dict | str = self.__check_game()
        if isinstance(has_error, dict):
            error_log: list[dict[str: int | str]] = []
            messages: list = []
            for item in has_error:
                if item == "rows":
                    messages.extend([(f"input error at row{self.tr(value[0])}: "
                                      f"\ncan't have two or more equal "
                                      f"values ({self.__change(self.initial_values[value][0])}) in the same row.")
                                     for value in has_error["rows"]])
                elif item == "cols":
                    messages.extend([(f"input error at col{self.tr(value[1])}: "
                                      f"\ncan't have two or more equal "
                                      f"values ({self.__change(self.initial_values[value][0])}) in the same column.")
                                     for value in has_error["cols"]])
                elif item == "quadrants":
                    inicios = tuple(range(1, self.size, int(sqrt(self.size))))
                    quadrant: dict = {value: self.tr(value[2]) for value in has_error["quadrants"]}
                    for position in quadrant:
                        for count in range(len(inicios)):
                            if quadrant[position] - count in inicios:
                                text = [quadrant[position] - count,
                                        quadrant[position] - count + int(sqrt(self.size)) - 1,
                                        count * int(sqrt(self.size)) + 1,
                                        count * int(sqrt(self.size)) + int(sqrt(self.size))]
                                quadrant[position] = text
                                break
                    messages.extend([(f"input error between row{value[0]} -> row{value[1]} "
                                      f"and col{value[2]} -> col{value[3]}: \ncan't "
                                      f"have equal values ({self.__change(self.initial_values[key][0])}) "
                                      "in the same quadrant.") for key, value in quadrant.items()])
                else:
                    error_log.extend([{"row": self.tr(value[0]),
                                       "col": self.tr(value[1]),
                                       "invalid_value": self.__change(self.initial_values[value][0])}
                                      for value in has_error["total"]])
                    if not self.color:
                        for error in has_error["total"]:
                            self.sudoku.at[f"row{self.tr(error[0])}",
                                           f"col{self.tr(error[1])}"] \
                                = f">{self.__change(self.initial_values[error][0])}"
            error_log.sort(key=lambda x: x["row"] + x["col"])
            if self.letters and self.size > 9:
                self.sudoku = self._with_letters(self.sudoku)
            if self.color:
                raise InputError(*messages, game=self.__error_color(*has_error["total"]),
                                 values=error_log)
            raise InputError(*messages, game=str(self.sudoku), values=error_log)

    def __change(self, value: int | str) -> int | str:
        """ change private method modifies the functionality of the tr private method
            to acomodate to the necessities of the validate_sudoku method"""
        return self.tr(value) if self.letters and self.size > 9 and value > 9 else value

    @staticmethod
    def tr(value: int | str) -> int | str:
        """ tr static method coverts numeric values from int to str so
            numeric values greater than 10 can be represented as letters if required"""
        sudoku_key: dict[str: int] = {key: value for key, value in zip("123456789abcdefg", range(1, 17))}
        if converted := sudoku_key.get(value, False):
            return converted
        elif converted := {item: key for key, item in sudoku_key.items()}.get(value, False):
            return converted
        else:
            raise ValueError("Invalid argument value for tr function, expected a"
                             f" int from 1 to 16 or a str from a to g, got {value} instead.")

    def initial_numbers(self, row_col: bool = True) -> tuple:
        """ class Sudoku initial numbers public method: once a sudoku is validated (read public method) it returns
            either as a tuple of dicts or a tuple of tuples (depending on the row_col value)
            the sudoku initial numbers"""
        if row_col:
            return tuple({"row": self.tr(key[0]),
                          "col": self.tr(key[1]),
                          "value": val[0] if not self.letters else self.tr(val[0])}
                         for key, val in self.initial_values.items())
        else:
            return tuple(((int(self.tr(key[0])) - 1) * self.size + int(self.tr(key[1])),
                          val[0] if not self.letters else self.tr(val[0]))
                         for key, val in self.initial_values.items())

    def __error_color(self, *args: str) -> str:
        """ private method error_color allows the display of input errors (repetitions inside a row, col or quadrant)
            with a color user aid to a command line interface"""
        red_values = tuple((int(self.tr(item[0])) - 1) * self.size + int(self.tr(item[1])) for item in args)
        head: str = (f"{' ' * (len(str(self.size)) + 3)}"
                     f"{''.join(tuple(f' col{val}' for val in range(1, self.size + 1)))}\n")
        color_row = []
        for position in range(1, self.size ** 2 + 1):
            row = position // self.size if position % self.size == 0 else position // self.size + 1
            col = self.size if position % self.size == 0 else position % self.size
            row_col = self.sudoku.at[f"row{row}", f"col{col}"]
            if position in red_values:
                color_row.append(f"{' ' * (3 + len(str(col)) - len(str(row_col)))}"
                                 f"{Fore.RED}{row_col}{Style.RESET_ALL} ")
            else:
                color_row.append(f"{' ' * (3 + len(str(col)) - len(str(row_col)))}{row_col} ")
            if position % self.size == 0:
                row_table: str = f"row{row}{' ' * (3 - len(str(row)))}" if self.size > 9 else f"row{row} "
                row_table += "".join(color_row)
                head += row_table.strip()
                if position != self.size**2:
                    head += "\n"
                color_row.clear()
        return head

    def _with_letters(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """ private method with_letters change the sudoku cells grater than 9 to letters if the user
            has that option selected"""
        new_dataframe = dataframe.applymap(func=lambda x: self.tr(x) if x in tuple(range(10, self.size + 1)) else x)
        return new_dataframe

    @staticmethod
    def _filtro(child_location: str, current_location: str) -> bool:
        """ static private method filtro helps to find all the cells which possibilities are changed
            when a kin cell is also changed"""
        for index, num in enumerate(current_location):
            if num == child_location[index]:
                return True
        return False

    def __str__(self) -> str:
        if self.sudoku is not None:
            return str(self.sudoku)
        else:
            raise SudokuError("Can't call string method of class Sudoku before entering or "
                              "reading a valid sudoku game.")

    def __len__(self):
        return len(self.initial_values)


class Solution(Sudoku):
    """class solution it's a child of the Sudoku class and the one in charge
    of finding the sudoku solution"""

    def __init__(self, size: int | str | pd.DataFrame = 9, letter: bool = False,
                 color: bool = False):
        super().__init__(size, letter, color)
        self.alt_unknowns: list[tuple] = []
        self.solution_path: list[str] = []
        self.puzzle: None | pd.DataFrame = None
        self.time: None | float = None
        self.iterations: int = 1
        self.max_time: int | float = 10
        self.max_level: int = 30 if self.size == 4 else (5_000 if self.size == 9 else 1_400_000)

    def solve(self) -> pd.DataFrame:
        """ public method solve is in charge of taking the current sudoku and search a solution if
            there is any, this function may halt if the sudoku it's difficult enough to take more time
            than the current set max time, or if the sudoku is invalid (seemingly valid sudokus detected
            as such by this program may still be invalid and as such they will raise and error)
            if a solution is found a dataframe containing the solved sudoku is returned"""
        if self.sudoku is not None:
            if self.verified:
                self.puzzle = copy.deepcopy(self.sudoku)
            else:
                self.puzzle = copy.deepcopy(self.read())
        else:
            raise SudokuError("Can't call solve method of class Solution before entering a valid sudoku game")
        start_time: float = time.process_time()
        self.__put_values(self.unknown_values, method=0)
        if self.__end(self.unknown_values):
            end_time: float = time.process_time()
            self.time = end_time - start_time
            if self.letters and self.size > 9:
                self.puzzle: pd.DataFrame = self._with_letters(self.puzzle)
            return self.puzzle
        min_value: int = min(tuple(len(options) for options in self.unknown_values.values() if len(options) > 0))
        for possible_value in range(min_value - 1, min_value + self.size//2):
            if possible_value == min_value - 1:
                is_solved: bool = self.__possibility_compare(self.unknown_values, possible_value,
                                                             gen_safe=self.alt_unknowns, is_alt=False)
            else:
                is_solved: bool = self.__possibility_compare(self.unknown_values, possible_value, is_alt=False)
            if is_solved and self.__end(self.unknown_values):
                end_time: float = time.process_time()
                self.time: float = end_time - start_time
                if self.letters and self.size > 9:
                    self.puzzle: pd.DataFrame = self._with_letters(self.puzzle)
                return self.puzzle
        new_node = tuple(self.__next_node(item) for item in self.alt_unknowns)
        if "solved" in new_node:
            if self.__testing():
                end_time: float = time.process_time()
                self.time = end_time - start_time
                if self.letters and self.size > 9:
                    self.puzzle = self._with_letters(self.puzzle)
                return self.puzzle
        new_node = tuple(item for item in new_node if isinstance(item, tuple))
        if not new_node:
            raise InputError("Couldn't found a solution for your sudoku, initial numbers seem valid "
                             "\nbut the sudoku seems to be not.")
        running_time: float = time.time() + 60 * self.max_time
        while True:
            new_node = tuple(self.__next_node(val) for item in new_node for val in item)
            if "solved" in new_node:
                break
            new_node = tuple(item for item in new_node if isinstance(item, tuple))
            if not new_node:
                raise InputError("Couldn't found a solution for your sudoku, initial numbers seem valid "
                                 "\nbut the sudoku seems to be not.")
            elif time.time() > running_time:
                raise SudokuError("the program is taking more time to solve the sudoku "
                                  f"\nthan the current time limit: {self.max_time} minutes.\n"
                                  f"game string representation:\n"
                                  f"{self.stringify()['start'] if self.sudoku is not None else 'not available'}")
        if self.__testing():
            end_time: float = time.process_time()
            self.time = end_time - start_time
            if self.letters and self.size > 9:
                self.puzzle: pd.DataFrame = self._with_letters(self.puzzle)
            return self.puzzle
        else:
            raise SudokuError("unable to found a valid solution for your sudoku.")

    def found_values(self, row_col: bool = True) -> tuple:
        """ public method found_values returns the found values by the solve method and returns them as a dict
            containing the row, col and value of each or a tuple containing the position (1-16, 1-81 or 1-256 depending
            on the current sudoku size) and the value"""
        found: list = []
        initials = tuple(val[0] for val in self.initial_numbers(row_col=False))
        for position in range(1, self.size**2 + 1):
            if position not in initials:
                row: int = position // self.size if position % self.size == 0 else position // self.size + 1
                col: int = self.size if position % self.size == 0 else position % self.size
                value: int = self.puzzle.at[f"row{row}", f"col{col}"]
                if row_col:
                    found.append({"row": row, "col": col, "value": value})
                else:
                    found.append((position, value))
        return tuple(val for val in found)

    def extra_info(self, raw_level: bool = False) -> dict:
        """ public method extra_info returns as a dict the number of initials values (start_vals key),
            the solving time (solving_time key) and the relative difficulty (difficulty key) of the sudoku"""
        if not raw_level:
            level: float = (self.iterations if self.max_level == 0
                            else self.iterations / self.max_level) * 100
            return {
                "start_vals": self.__len__(),
                "solving_time": "0" if self.time is None else f"{self.time:.3f} seconds",
                "difficulty": f"{100 if level >= 100 else (1 if level <= 1 else int(level))}/100"
            }
        else:
            return {
                "start_vals": self.__len__(),
                "solving_time": "0" if self.time is None else f"{self.time:.3f} seconds",
                "difficulty": self.iterations
            }

    def stringify(self) -> dict:
        """ public method stringify return as a dict a string representation of the current sudoku, one
            containing the unsolved state of the sudoku (start key) and other with the solved state (end key)"""
        strings_: dict[str, str | None] = {}
        if self.sudoku is not None:
            rows_values = tuple("".join(tuple(self.tr(val) if isinstance(val, int) else val
                                              for val in self.sudoku.iloc[row])) for row in range(0, self.size))
            if len(self.initial_values) * 2 + self.size - 1 < self.size**2:
                sudoku_strings = []
                for row in rows_values:
                    numbers: zip = zip([self.tr(val) for val in range(1, self.size + 1)], row)
                    numbers: tuple = tuple("".join(val) for val in numbers if "-" not in val)
                    if numbers:
                        sudoku_strings.append("".join(numbers))
                    else:
                        sudoku_strings.append("")
                strings_["start"] = "|".join(sudoku_strings)
            else:
                strings_["start"] = "".join(rows_values)
        else:
            strings_["start"] = None
            # always like this 2-1----3-----2--
        if self.puzzle is not None:
            rows_values = tuple("".join(tuple(self.tr(val) if isinstance(val, int) else val
                                              for val in self.puzzle.iloc[row])) for row in range(0, self.size))
            strings_["end"] = "".join(rows_values)
        else:
            strings_["end"] = None
        return strings_

    @property
    def max_time(self) -> int:
        return self._max_time

    @max_time.setter
    def max_time(self, new_val: int | float) -> None:
        if isinstance(new_val, int | float) and 31 > new_val > 0:
            self._max_time = new_val
        else:
            raise InputError(f"Expected an int or float between 1 and 30 got {new_val} instead.")

    @property
    def max_level(self) -> int:
        return self._max_level

    @max_level.setter
    def max_level(self, new_val: int) -> None:
        if isinstance(new_val, int) and new_val > 0:
            self._max_level = new_val
        else:
            raise InputError(f"fExpected an int greater than 0 got {new_val} instead.")

    def __put_color(self) -> str:
        """ put_color private method displays the found values in color on a command line
        interfaces as a visual aid"""
        head: str = (f"{' ' * (len(str(self.size)) + 3)}"
                     f"{''.join(tuple(f' col{val}' for val in range(1, self.size + 1)))}\n")
        color_row = []
        white_values = tuple(val[0] for val in self.initial_numbers(row_col=False))
        for position in range(1, self.size**2 + 1):
            row = position // self.size if position % self.size == 0 else position // self.size + 1
            col = self.size if position % self.size == 0 else position % self.size
            row_col = self.puzzle.at[f"row{row}", f"col{col}"]
            if position not in white_values:
                color_row.append(f"{' ' * (3 + len(str(col)) - len(str(row_col)))}"
                                 f"{Fore.GREEN}{row_col}{Style.RESET_ALL} ")
            else:
                color_row.append(f"{' ' * (3 + len(str(col)) - len(str(row_col)))}{row_col} ")
            if position % self.size == 0:
                row_table: str = f"row{row}{' ' * (3 - len(str(row)))}" if self.size > 9 else f"row{row} "
                row_table += "".join(color_row)
                head += row_table.strip()
                if position != self.size**2:
                    head += "\n"
                color_row.clear()
        return head

    def __put_values(self, game_dict: dict, method: int, pick: int = 0, coord: str = "000 0") -> bool:
        """ private method put_values runs the alter_child private method on a loop until
            there are not any sudoku cell with only one possibility left (the cell is set to that possibility)
            or one of this possibility is an incorrect guess"""
        while True:
            if method != 2:
                current_pick = {key: value for key, value in game_dict.items() if len(value) == 1 and 0 not in value}
                if len(current_pick) != 0:
                    for answer in current_pick:
                        if method == 0:
                            self.puzzle.at[f"row{self.tr(answer[0])}", f"col{self.tr(answer[1])}"] \
                                = current_pick[answer][0]
                            if not self.__alter_child(game_dict, answer):
                                return False
                            self.iterations += 1
                        else:
                            if not self.__alter_child(game_dict, answer):
                                return False
                        break
                else:
                    break
            else:
                self.puzzle.at[f"row{self.tr(coord[0])}", f"col{self.tr(coord[1])}"] = pick
                if not self.__alter_child(game_dict, coord, pick, 1):
                    return False
                method -= method
        return True

    def __alter_child(self, game_dict: dict, position: str, pick: int = 0, mode: int = 0) -> bool:
        """ private method alter_child takes a sudoku cell set that cell to a possible value, delete that
            possibility as a valid choice for that cell and related cells while checking if the chose value
            was a valid guess"""
        if mode == 0:
            pick: int = game_dict[position][pick]
            game_dict[position]: list = [pick]
        else:
            if len(game_dict[position]) >= 2:
                game_dict[position]: list = [pick]
        new_sequence: dict[str:list] = {location: list_options for location, list_options in game_dict.items()
                                        if self._filtro(location, position) and pick in list_options}
        for list_locations in new_sequence:
            if len(new_sequence[list_locations]) > 1 or list_locations == position:
                game_dict[list_locations].remove(pick)
            else:
                game_dict[list_locations].extend([0, 0])
                return False
        return True

    def __possibility_compare(self, game_dict: dict,
                              option_len: int, gen_safe: list | None = None, is_alt: bool = True) -> bool:
        """ private method possibility_compare takes all the sudoku cells with an equal number of
            possible values and sort them, then takes one of the cells to test each of its possible values
            to see if any is a valid play, if there are no valid plays that branch dies out"""
        if gen_safe is not None:
            gen_safe.clear()
        len_values: list = [[key, value] for key, value in game_dict.items() if len(value) == option_len + 1]
        len_values.sort(key=lambda child_item: self.__get_info(child_item, game_dict), reverse=True)
        if is_alt:
            len_values = len_values[:1]
        for count, item in enumerate(len_values):
            for value in range(0, option_len + 1):
                alt_game = copy.deepcopy(game_dict)
                if self.__alter_child(alt_game, item[0], value):
                    self.__put_values(alt_game, 1)
                if len(tuple(filter(lambda value: 0 in value, alt_game.values()))) == 0:
                    if gen_safe is not None and count == 0:
                        self.iterations += 1
                        if is_alt:
                            gen_safe.append(f"{item[1][value]} {item[0]}")
                        else:
                            gen_safe.append((f"{item[1][value]} {item[0]}", None))
                    if self.__end(alt_game):
                        if is_alt:
                            self.solution_path.append(f"+{item[1][value]} {item[0]}")
                        else:
                            self.__put_values(game_dict, 2, item[1][value], item[0])
                        return True
        return False

    def __get_info(self, element: list, father_element: dict) -> int:
        """ private method get_info sort sudoku cells to determinate which one have possibilities
            that are present the most in their related cells"""
        usefulness: int = 0
        for option in father_element[element[0]]:
            usefulness += len({key: val for key, val in father_element.items()
                               if self._filtro(element[0], key) and option in val})
        return usefulness

    def __next_node(self, next_path: tuple):
        """ private method get next_node takes a branch created from the choice of a possible value
                    of a cell and create as many new branches as posible values the selected sudoku cell
                    inside the branch had"""
        if self.solution_path:
            return "void"
        next_gen: list = []
        for last_place in next_path[1:]:
            new_path = f"{next_path[0]}+{last_place}" if last_place is not None else next_path[0]
            self.solution_path.append(new_path)
            new_dict = self.__testing(return_alt=True)
            if isinstance(new_dict, dict):
                min_value = min(tuple(len(options) for options in new_dict.values() if len(options) > 0))
                new_path = self.__is_valid_game(new_dict, min_value, new_path)
                if new_path == "solved":
                    return new_path
                elif new_path == "void":
                    continue
            else:
                raise InputError("Couldn't found a solution for your sudoku, initial numbers seem valid "
                                 "\nbut the sudoku seems to be not.")
            min_value = min(tuple(len(options) for options in new_dict.values() if len(options) > 0))
            next_values: list = []
            is_solution = self.__possibility_compare(new_dict, min_value - 1, gen_safe=next_values)
            if is_solution:
                new_path += self.solution_path.pop(0)
                self.solution_path.append(new_path)
                return "solved"
            elif next_values:
                next_gen.append((new_path, *next_values))
        if next_gen:
            return tuple(next_gen)
        return "void"

    def __testing(self, return_alt: bool = False) -> bool | dict:
        """ private method testing checks if the chose combination of branches that hte program found
            is a solution for the sudoku"""
        duplicate_dict = copy.deepcopy(self.unknown_values)
        was_alter = re.findall(r"\*-([^+*]+)\*", self.solution_path[0])
        if was_alter:
            for finding in was_alter:
                val_to_change = finding.split("-")
                for change in val_to_change:
                    value, key = change.split()
                    if int(value) in duplicate_dict[key]:
                        duplicate_dict[key].remove(int(value))
            put_path = re.sub(r"\*-([^+*]+)\*", "", self.solution_path.pop(0))
            if "*" in put_path:
                put_path = re.sub(r"\*", "", put_path)
            self.solution_path.append(put_path)
        duplicate_game = copy.deepcopy(self.puzzle)
        solving_path = self.solution_path[0].split("+")
        for val_position in solving_path:
            contents = val_position.split()
            self.__put_values(duplicate_dict, 2, int(contents[0]), contents[1])
        if self.__end(duplicate_dict):
            return True
        self.solution_path.clear()
        self.puzzle = duplicate_game
        if return_alt:
            return duplicate_dict
        return False

    def __is_valid_game(self, current_option: dict, min_options: int, last_path: str) -> str:
        """ private method is_valid_game search for patterns inside the branches to see if they are
            valid games or not"""
        current_dict: dict[str:list] = {key: value for key, value
                                        in current_option.items() if len(value) == min_options}
        removed: set = set()
        for child in current_dict:
            for child_relation in range(0, 3):
                related_items: dict[str:list] = {key: value for key, value in current_option.items()
                                                 if key[child_relation] == child[child_relation] and value}
                is_case = list(filter(lambda num: num == current_dict[child], related_items.values()))
                # filter case 0) {[6, 8], [6, 8], [6, 15], [6, 8, 12]}
                # here  the third and forth entries must be 15 and 12 otherwise
                # the 2 first entries would end up with the same values making it invalid
                if len(is_case) == min_options and len(is_case) != len(related_items):
                    remove_conflicts: dict[str:list] = {key: sorted(list(set(item) - set(is_case[0])))
                                                        for key, item in related_items.items() if item != is_case[0]}
                    if remove_conflicts:
                        removed_vals = ""
                        for change in remove_conflicts:
                            if len(remove_conflicts[change]) > 1:
                                removed_vals += "-"
                                current_option[change]: list = remove_conflicts[change]
                                removed_vals += "-".join((f"{val} {change}" for val in is_case[0]))
                        if removed_vals:
                            removed.add(removed_vals)
                    remove_conflicts: dict[str:list] = {key: val for key, val in remove_conflicts.items()
                                                        if len(val) == 1}
                    if remove_conflicts:
                        for one_option in remove_conflicts:
                            current_option[one_option]: list = remove_conflicts[one_option]
                            if not self.__put_values(current_option, 1):
                                return "void"
                            else:
                                if not (tuple(filter(None, current_option.values()))):
                                    last_path += f"+{remove_conflicts[one_option][0]} {one_option}"
                                    if removed:
                                        last_path += f"*{''.join(removed)}*"
                                    self.solution_path.append(last_path)
                                    return "solved"
                                else:
                                    last_path += f"+{remove_conflicts[one_option][0]} {one_option}"
                        related_items = {key: value for key, value in current_option.items()
                                         if key[child_relation] == child[child_relation] and value}
                case_options = list(flatten(list(related_items.values())))
                # filter case 1) {[2,4], [2, 4], [2, 4]} 2) {[2, 4], [2, 4], [1, 3, 5], [3, 5], [1, 4], [1, 5]}
                if len(is_case) >= min_options + 1 or len(related_items) > len(set(case_options)):
                    return "void"
                elif len(related_items) == len(set(case_options)):
                    # filter case 2) {[2, 4], [2, 4], [7, 8], [2, 5], [5, 4]}
                    get_unique: list = unique_to_each(*related_items.values())
                    if tuple(filter(lambda group: len(group) > 1, get_unique)):
                        return "void"
                    else:
                        get_unique: tuple = tuple(flatten(get_unique))
                        if get_unique:
                            # filter case 3) {[2, 4], [2, 4], [7, 5], [2, 5], [5, 4]}
                            for val in get_unique:
                                is_case = tuple(key for key, value in related_items.items() if val in value)
                                if is_case:
                                    current_option[is_case[0]]: list = [val]
                                    if not self.__put_values(current_option, 1):
                                        return "void"
                                    else:
                                        if not(tuple(filter(None, current_option.values()))):
                                            last_path += f"+{val} {is_case[0]}"
                                            if removed:
                                                last_path += f"*{''.join(removed)}*"
                                            self.solution_path.append(last_path)
                                            return "solved"
                                        else:
                                            last_path += f"+{val} {is_case[0]}"
                            if removed:
                                last_path += f"*{''.join(removed)}*"
                            return last_path
        if removed:
            last_path += f"*{''.join(removed)}*"
        return last_path

    @staticmethod
    def __end(dict_game: dict[str: list]) -> bool:
        """ static private method end checks if the game has been solved"""
        return True if len(tuple(position for position in dict_game.values() if len(position) > 0)) == 0 else False

    def __str__(self) -> str:
        if self.puzzle is None and self.sudoku is None:
            raise SudokuError("Can't call string method of class Solution before entering or reading"
                              " a valid sudoku game.")
        elif self.puzzle is None:
            return str(self.sudoku)
        else:
            if self.color:
                return self.__put_color()
            else:
                return str(self.puzzle)


class SudokuError(Exception):
    """ class SudokuError gets raised if a method it's called before
    doing something before, when a solution for a sudoku cannot be found
    or when a sudoku has taken more time to solve than the set time limit"""
    def __init__(self, message: str):
        self.error = message

    @property
    def error(self) -> str:
        return self._error

    @error.setter
    def error(self, value) -> None:
        if isinstance(value, str):
            self._error = value
        else:
            raise ValueError("Invalid value for class SudokuError error argument "
                             f"\nexpected a str, got {type(value)} instead.")

    def __str__(self) -> str:
        return self.error


class InputError(ValueError):
    """ class InputError gets raised whenever there are invalid values
    inside the sudoku grid or there are not enough values, a Sudoku or Solution
    class parameter are not valid or when a sudoku that looks valid does not have
    a solution"""
    def __init__(self, *args: str, game: str | None = None, values: list | None = None):
        self.error = tuple(val for val in args)
        self.game = game
        self.values = values

    @property
    def error(self) -> tuple:
        return self._error

    @error.setter
    def error(self, value) -> None:
        if isinstance(value, tuple):
            if all(tuple(True if isinstance(val, str) else False for val in value)):
                self._error = value
            else:
                raise ValueError("Invalid contents for class InputError error argument expected a tuple with only"
                                 f"\nstrings, got {tuple(type(val) for val in value if not isinstance(val, str))} "
                                 f"instead.")
        else:
            raise ValueError("Invalid value for class InputError error argument expected a tuple "
                             f"\ngot {type(value)} instead.")

    @property
    def game(self) -> str | None:
        return self._game

    @game.setter
    def game(self, value) -> None:
        if isinstance(value, str):
            self._game = value
        else:
            self._game = None

    @property
    def values(self) -> list | None:
        return self._values

    @values.setter
    def values(self, value) -> None:
        if isinstance(value, list):
            self._values = value
        else:
            self._values = None

    def __str__(self) -> str:
        return "\n".join(self.error)


if __name__ == "__main__":
    try:
        sudo_size: str = input("Your sudoku size (4, 9 or 16) or valid sequence: ")
        proceed: str = "y"
        if sudo_size in ("4", "9", "16"):
            Sudoku.enter_game(sudoku_df=int(sudo_size))
            proceed: str = input(f"please enter your sudoku of size {sudo_size}"
                                 f"\nand then press y to confirm: ").lower().strip()
            sudo_size: int = int(sudo_size)
        if proceed == "y":
            use_color: str = input("Use color? y/n: ").lower().strip()
            use_color: bool = True if use_color == "y" else False
            try:
                sudoku_game = Solution(size=sudo_size, letter=False,
                                       color=use_color)
                if sudoku_game.size > 9:
                    use_letter: str = input("Use letters for numbers over 9? y/n: ").lower().strip()
                    use_letter: bool = True if use_letter == "y" else False
                    set_time: str = input("Set time limit to minutes (enter a number up to 30): ").strip()
                    if set_time.isnumeric():
                        sudoku_game.max_time = 5 if 30 < int(set_time) <= 0 else int(set_time)
                    else:
                        sudoku_game.max_time = 5
                    sudoku_game.letters = use_letter
                was_input_valid = sudoku_game.read()
                sudoku_game.solve()
            except (InputError, SudokuError) as fail:
                print(f"\n{str(fail)}\n")
                if isinstance(fail, InputError):
                    if fail.game is not None:
                        print(f"{fail.game}\n")
            else:
                print("\nThe game: ")
                print(f"\n{was_input_valid}\n")
                print("The solution: \n")
                print(f"{str(sudoku_game)}")
                string_val = sudoku_game.stringify()
                print(f"\nUnsolved game representation: {string_val['start']}")
                print(f"\nSolved game representation: {string_val['end']}\n")
                print(sudoku_game.extra_info(raw_level=True))
        sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        sys.exit("program execution aborted")
