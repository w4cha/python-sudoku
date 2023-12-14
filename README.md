# SudokuSolver A program for solving and playing sudokus of varying sizes.
## Video Demo:
### Description:
The present project is a program writing using python that allows users
to solve 4x4, 9x9 and **some** 16x16 sudokus, which are latter saved to a
database as a string representation of the game so the user can latter
try and play the solved sudokus by themselves via a command line interface.
-----
### Project contents:
The elements of the folder containing this project are the following:
1. project.py:
This file contains the code from where users can interact with the program to
solve and play sudokus and read or write to the database where the sudokus
are stored.
2. sudoku_test.py:
Contains the code tests for some functions found on the project.py file.
3. sudoku.py:
Contains a self-made module that is used by project.py to solve the sudokus
of different sizes the user may enter into the program.
4. data.py:

This file contains the code for a self-made module that was created to pass
queries to the sqlite database that was used for this project.
5. requirement.txt:
Contains the list of third-party not built-in python modules used for this project.
6. input.txt:
This file is used by the program as a way for the user to introduce manually a sudoku
game by filling a template that is created in the file according to the sudoku size the
user specified (4 by 4 grid if the size was 4, 9 by 9 grid if the size was 9, and a 16 by 16
for a size 16 sudoku).
7. sudoku_table.db:
The sudoku_table.db file is where all sudokus solved for the first time are saved, each
row of the database contains the following information about a solved sudoku: A string
representation of the unsolved sudoku, a string representation of the solved sudoku,
the number of initial values present in the sudoku, a number generated by the sudoku.py
module that represents the relative difficulty of solving a sudoku, and the size of the sudoku.
A user can play a specific sudoku from this database by introducing the string representation
of the unsolved sudoku when asked what sudoku to play by the project.py file.
---
### Design consideration for a sudoku solver:
When it comes down to try and solve a sudoku (specially one of size 16) using a program,
an important consideration is that the number of possible values necessary to check,
try, and found a solution may end up being a big amount for the most difficult
sudokus (sudokus with a low value of initial number which means more values are needed
to be found), and thus the task may end up being a cpu-bound one where the speed of the
programing language of choice and its wide support for things like multithreading results
critical to found solutions under a reasonable amount of time for a user (an example was
a 16 by 16 sudoku which took close to 30 minutes to solve using python). For this reason,
I believe that this project was not the most ideal for a python
program.

Other design consideration that was tried to implement but ended up being a little too
difficult to code, was the use of more advanced pattern seeking techniques used by
real sudoku players to try and solve the more difficult sudokus. Some strategies I would have loved to
use
for the project were the following: The X/Y/Z Wings, The Swordfish, The Jellyfish,
etc.
---
### Credits:
Program designed and created by Lucas Folch C., from Quilpué, Chile, for the online
course CS50’s Introduction to Programming with Python 2023.