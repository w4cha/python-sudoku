from project import _valid_play, _solve, _read, _save_game
from pathlib import Path
from sudoku import Solution
import os


def test__valid_play():
    """ test that a valid play is detected:
    the size parameter is not entered by the user but is stored in the
    database where games are stored, so is always going to be 4, 9 or 16
    if the function valid play returns a not empty list then the play was valid
    """
    valid_inputs: dict = {"111": 4, "333": 9, "abc": 16, "976": 9, "ggg": 16,
                          "424": 4, "1c9": 16, "c92": 16, "39f": 16, "251": 16}
    for play, size in valid_inputs.items():
        assert len(_valid_play(play, size)) != 0


def test__valid_play_2():
    """ test that an invalid play is detected:
    the size parameter is not entered by the user but is stored in the
    database where games are stored, so is always going to be 4, 9 or 16
    if the function valid play return an empty list then the play was not valid
    """
    invalid_inputs: dict = {"191": 4, "335": 4, "97a": 9, "f76": 9, "gg16": 16,
                            "4241": 4, "1c1": 4, "c92": 9, ".---78f": 16, "000": 9,
                            "not valid": 4, "test56\n": 16}
    for play, size in invalid_inputs.items():
        assert len(_valid_play(play, size)) == 0


def test__save_game():
    """ test saving an already saved game in the database:
    trying to save and already solve game should return false meaning that the game was not saved
    """
    saved_game: tuple = ("INSERT INTO sudokus (start_str, end_str, "
                         "init_vals, difficulty, size) VALUES (?, ?, ?, ?, ?)",
                         ("456379ced4e7|4aa8d3|233f8ga1bbccddg5|263c445e7897ba|3b425f6a8ea6b8e9fg|1c255869b3cb|"
                          "143a47829fb9d6ec|6b7ccde3f2|1d467g84bccffb|153372c6|224e7b8ad5e4f8|2453a9de|17caedf6g9|"
                          "1829324b96acg7|87c2ffg4|367d94dbeag8",
                          "2b85a39cdf6e471gg7da21fb98543ec6e3f9746g21bcd8a516c4e58d7ga3fb9231b2fa4ec68579gdc5ed8976"
                          "g23baf4148a7gd32fe916c5b6g9f5bc1a47d832eda7618g4e5cf92b35f38de29ba46g17c921e6cba3dg7548f"
                          "b4gc375f1928e6da7c41bge853fa2d69892b4fa36cdg15e7ad5396178be2cgf4fe6gc2d54719ba38",
                          96, 3970, 16))

    db_file = str(Path(fr"{os.path.abspath(os.path.dirname(__file__))}\sudoku_table.db"))
    assert not _save_game(saved_game, db_file, test=True)


def test__save_game_2():
    """ test saving a new game to the database:
    trying to save a not registered game too difficult to be solved, if the function
    _save_game returns true then the game was saved (the optional test argument for
    the _save_game function if set to True prevents the writing to the database of this test)
    """
    saved_game: tuple = ("INSERT INTO sudokus (start_str, end_str, "
                         "init_vals, difficulty, size) VALUES (?, ?, ?, ?, ?)",
                         ("49a3g2|5f8c9geag8|2445a9|8abdgf|38gg|65|1a3fgc|6d79a4f7|5g8e|"
                          "2544a7cbd1edf9|43a1d5f4|5a8f|1f3g98bage|6174d2f5|189cbg|697783f1",
                          "no solution available just an example",
                          55, 1_000_000, 16))

    db_file = str(Path(fr"{os.path.abspath(os.path.dirname(__file__))}\sudoku_table.db"))
    # by passing true as an argument the game is not saved if the function is used during a test
    assert _save_game(saved_game, db_file, test=True)


def test__read():
    """ test the detection of valid sudoku string sequences with invalid initial value positions:
    check if sudoku has repeated values inside a row, column or a grid or
    if the function _read returns a str (error message) then the game has invalid
    placement in this case
    """
    sequence_with_invalid_placement: dict = {
                  "row_col_quadrant_4": "34-3-3244132424-",
                  "row_4": "3--3--244131-24-",
                  "col_4": "241323-44-12-24-",
                  "quadrant_4": "-4-34----132--2-",
                  "row_col_quadrant_9": "45678912|9978986769|5678|3434|7856|982415|766689|453419|11",
                  "row_9": "2239|186378|1436458193|496288|475692|29325391|1164|2733576889|55667198",
                  "col_9": "2239|186376|1436458193|496288|475692|29325391|1864|2633576889|55667193",
                  "quadrant_9": "162239|186376|1436458193|496288|475692|29325391|1164|2133576889|55667198",
                  "row_col_quadrant_16": "3a4e547d87b1dbe9ff|1c518b99a6efgd|193g4b6cc7e3gf|2d475583cge1|297bacbdc7fe|"
                                         "4d71a9b3|244877c2d8f3|1b8e9gb5c8dde7|17264f58bb|1a5c7f95g8|38598g9dccd7g5|"
                                         "324g567a9fb9c4|275adef4|3c497e96a2bgga|2g6294becb|1593aaf1",
                  "row_16": "3a4e5a7d87b1dbe9f6|1c518b99a6eagd|193g4b6ccae3gf|2d475583cge1|297bacbdc6fe|4d71a9b3|"
                            "244877c2daf3|1b8e9gb5c8dde7|17264f58bb|1a5c7f95gc|38598g9dccd7g5|324g567a9fb9c4|"
                            "27def4|3c497e96a2bgga|2g6294becb|1593aaf1",
                  "col_16": "3g4e547d87b1dbe9f6|1c518b99a6eagd|193g4b6ccae3gf|2d475583cge1|297bacbdc6fe|4d71a9b3|"
                            "244877c2daf3|1b8e9gb5c8dde7|17264f58bd|1a5c7f95g8|38598gccd7g5|324g567a9fb9c4|"
                            "275adef4|3c497e96a2bgga|2g6294becb|1593aaf1",
                  "quadrant_16": "3a4e547d87b1dbe9f6|1c518b99eag6|193g4b6ccae3gf|475583cge1|297bacbdc6fe|4d71a9b3|"
                                 "2d77c2daf3|1b8e9gb5c8dde7|17264f58bb|1a5c7f95g8|38598g9dccd7g5|324g567a9fb9c4|"
                                 "275adef4|3c497e96a2bgga|2g6294becb|1593aaf1"
    }

    for sequence in sequence_with_invalid_placement:
        assert isinstance(_read(sequence), str)


def test__read_2():
    """ test that the sudoku string sequence has not enough initial values encoded:
    checks that the game has at least certain amount of initial numbers so a game does
    not have multiple solutions, for a 4 by 4 sudoku you need at least 4 initials values for it
    to not have multiple solution (not a real sudoku), for a 9 by 9 the amount is 17 and for a
    16 by 16 the least amount of initial numbers someone has created a valid sudoku with is 55
    if the function _read returns a str (error message) then the game does not have enough initial
    numbers in this case to be valid
    """
    multiple_solutions_sudokus: list = [
        "2334|||",
        "147895|23|47|2286|5574|51|466387|1542|11",
        "49a3g2|5f8c9gea|2445a9|8abdgf|38gg|65|1a3fgc|6d79a4f7|5g8e|2544a7cbd1edf9|43a1d5f4|5a8f|1f3g98bage|"
        "6174d2f5|189cbg|697783f1",
    ]
    for sequence in multiple_solutions_sudokus:
        assert isinstance(_read(sequence), str)


def test__read_3():
    """ test the detection of invalid sudoku string representations:
    check that the program (_read function) returns an
    error message (a string) if the user enters an invalid game sequence
    representation"""
    invalid_sequences: list = [
        "Hi How are You",
        "1677168898834523877337569812346523447865985631768755",
        "-432-3---1-442-0",
        "23768cf9|2a365g728bc5ee|19387fa3bgccgb|1e2c4475abf8|bbc8dffa|"
        "7h839dbad9e4|3b5862bfedf3|325a94c9|425764bdc3g1|1765ddfc|4a5c7b96a7dge8g4"
        "|1b6a7d98begf|2b3c6deaf5g8|1g6f79a4b6e7fe|4d53b8cffg|54788eb7cddce2",
        "---5-1279|95--863-4|-74-92-8-|--945--2-|735-29-6-|--8-63597|86----74-|--327--56|-27--4-3-",
        "-2|41|1243|1344",
        "243542|34|22|13",
        "223|186376|1436458193|496288|475692|29325391|1164|2633576889|55667198"
    ]
    for sequence in invalid_sequences:
        assert isinstance(_read(sequence), str)


def test__solve():
    """ test that a valid sudoku string with no solution is detected:
    raise error if sudoku has valid initial values but down the line the sudoku turns out to be
    invalid (the distribution of the initial values cause the sudoku to become unsolvable)
    only example at the moment: 164372|378499||132246|8897|11|235467|2573|59
    if the function _solve fails in generating a solution then a str is returned (error message)
    """
    assert isinstance(_solve(Solution(size="164372|378499||132246|8897|11|235467|2573|59"), max_time=0.1), str)


def test__solve_2():
    """ test that a valid sudoku string that is too difficult for this program is detected
    check that the program stop after an amount of time (minutes) if the sudoku is too difficult and takes
    too long to solve
    This is the string representation of a 16 by 16 sudoku with only 55 starting values few enough to make
    this sudoku unsolvable for this program with the current method since it would end taking too much time
    (no solution even after more than one hour running the program) and memory usage
    49a3g2|5f8c9geag8|2445a9|8abdgf|38gg|65|1a3fgc|6d79a4f7|5g8e|2544a7cbd1edf9|43a1d5f4|5a8f|1f3g98bage|
    6174d2f5|189cbg|697783f1
    if the _solve function can find a solution in the given time a tuple is returned with the game
    info otherwise a string is returned with the error message raised by the program
    """
    assert isinstance(_solve(Solution(size="49a3g2|5f8c9geag8|2445a9|8abdgf|38gg|65|1a3fgc|6d79a4f7|5g8e|"
                                           "2544a7cbd1edf9|43a1d5f4|5a8f|1f3g98bage|6174d2f5|189cbg|"
                                           "697783f1"), max_time=0.1), str)


def test__solve_3():
    """ test that different sizes sudokus are correctly solved (4, 9, 16 the only supported sizes):
    if a solution is found then the _solve function returns a tuple with info about the game and the solution,
    in this case the solution returned is represented by a string
    """
    sudoku_and_solution = {
        "-3411-3232-44--3": "2341143232144123",
        "12233441|||": "2341142332144132",
        "---5-127995--863-4-74-92-8---945--2-735-29-6---"
        "8-6359786----74---327--56-27--4-3-": "38654127995278631417439268561945"
                                              "7823735829461248163597861935742493278156527614938",
        "253244|5771||4862|1376|2945|113653|8899|17": "652481937834679152971325864467812"
                                                      "593315794628298563471186937245523146789749258316",
        "3a4b5269aceffdge|14496c7g96a2d8eaf7|259abfcef9gb|47|13226e84b5egf6|57637aadb4d1g9|114c6f8gb8|1b3879d7fe|"
        "667488bdcgdb|1d3e4382b9c7|29425g7f98e1g3|1a28377c859ba6d4e9g2|1e2334a7g5|5eb6daf2|"
        "3546627b8ffg|2g566487b3gf": "g1ab29634c785fde4ef95cgd62b38a71253d4871agfec69b86c7faeb591d243g329a8ed47"
                                     "15bfg6c5fge73a6cd421b89176cbf2gea89354dbd84159c3fg672eafc15964823dgbea7d4e"
                                     "3ab12f597g8c669b2g7fe84acd153a87g3dc5b6e149f2e341cg8a972f6db5cbdfe139g865a7"
                                     "247a56d2bf1ec493g89g286457db3aec1f",
        "213942869gbb|1c2835729ec3e1ga|276g9ac4f2|1d2a4b64c6g8|3d98a2c9eb|265a6badb5|475cbfcbf4g5|112g9cd8eff9ge"
        "|2d3fa9b8e4|1a5275849bbgcfd7ed|1e25365da4b3c7dafc|436988cce6fg|328ca6dee3gg|4a7793acbdd2|6a79dc"
        "|16295bagf5": "31928ca6g5bdfe74c8547d2bef93g16af7e69g31a8c4b52ddagbf4e571269c3843dfg51782e96bac86ceabf9"
                       "4d5g321792a7c86e13fbdg451gb543d2c76a8f9ebdfg37ca698514e2ac192654begf7d83e568d1gf2437a9cb2"
                       "473e9b8da1c56gf7b215f4c96a8e3dg5f4a6e7g3cd128b9ge8d1a935b42c7f6693cb28dfg7e4a51"
    }
    for problem, solution in sudoku_and_solution.items():
        program_solution: tuple[str, dict, dict] = _solve(Solution(size=problem), max_time=0.2)
        assert program_solution[2]["end"] == solution
