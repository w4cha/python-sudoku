import sqlite3
from sqlite3 import Error
import csv
from typing import Generator


class Database:
    """ lass Database is used to read, write and download .db files that used the sqlite3 engine"""
    def __init__(self, db_path: str):
        self.db = db_path
        self.connection = self.start_connection()

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, val):
        if isinstance(val, str):
            self._db = val
        else:
            raise DatabaseError("expected value for database connection is a"
                                f" string but got {type(val)} instead")

    def start_connection(self) -> sqlite3.connect:
        """ start_connection method check if is possible to establish a connection from the current
        database location"""
        try:
            return sqlite3.connect(self.db)
        except Error as fail:
            raise DatabaseError(f"the next sqlite3 error was raised: {fail}")

    def write_db(self, values: str | tuple | list | dict, many: bool = False) -> None:
        """ write_db method allows writing (values argument) to a db file with the option to submit
        multiple writing queries (many method argument checks for this option)"""
        try:
            if many:
                con_obj = self.connection.cursor()
                con_obj.executemany(*self.check_query(values))
            else:
                con_obj = self.connection.cursor()
                con_obj.execute(*self.check_query(values))
            self.connection.commit()
        except Error as fail:
            raise DatabaseError(f"the next sqlite3 error was raised: {fail}")

    def read_db(self, entries: str | tuple, as_row: bool = False) -> Generator:
        """ read_db method is a generator that give access to the information requested
        from the user query (entries argument), the as_row argument gives the option to
        return the asked rows info to be returned as a dictionary where the keys are
        the name of the columns"""
        try:
            if as_row:
                self.connection.row_factory = sqlite3.Row
            con_obj = self.connection.cursor()
            con_obj.execute(*self.check_query(entries))
            while True:
                fetch_rows = con_obj.fetchmany(20)
                if not fetch_rows:
                    break
                else:
                    for item in fetch_rows:
                        yield item
        except Error as fail:
            raise DatabaseError(f"the next sqlite3 error was raised: {fail}")

    @staticmethod
    def check_query(sql_query: str | tuple | list | dict) -> tuple:
        """ static method check_query make sure the format of the submitted queries (sql_query) correspond
        to what the program requires"""
        match sql_query:
            case [str(query), tuple(arguments) | list(arguments)] | (str(query), tuple(arguments) | list(arguments)) | \
                 {"query": str(query), "args": tuple(arguments)}:
                return query, arguments
            case str(sql_query):
                return sql_query,
            case _:
                raise DatabaseError("invalid structure for executable query expected "
                                    "str, list[str, tuple | list], tuple[str, tuple | list] or "
                                    "dict like {query: str, args: tuple}, "
                                    f"got {sql_query} instead.")

    def csv_(self, read_val: str, output: str, delimiter: str = ",") -> None:
        """ csv_ method allows to download the solicited entries  (read_val argument)
        to a csv file (output argument) the user can specify the separator using the
        delimiter argument"""
        try:
            con_obj = self.connection.cursor()
            con_obj.execute(*self.check_query(read_val))
            with open(output, "w") as csv_file:
                csv_write = csv.writer(csv_file, delimiter=delimiter)
                csv_write.writerow([row[0] for row in con_obj.description])
                csv_write.writerows(con_obj)
        except Error as fail:
            raise DatabaseError(f"the next sqlite3 error was raised: {fail}")

    def close(self) -> None:
        """ close method close the current connection to the db file"""
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()


class DatabaseError(Exception):
    """ class DatabaseError is raised when any sqlite3.Error is raised"""
    def __init__(self, message: str = ""):
        self.error = message

    def __str__(self):
        return self.error
