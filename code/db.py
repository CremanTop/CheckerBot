import sqlite3
from sqlite3 import Connection, Cursor


class BotDB:
    """ОБЯЗАТЕЛЬНО ИСПОЛЬЗОВАТЬ ЧЕРЕЗ WITH!!!"""
    def __init__(self, db_file: str) -> None:
        self.db_file = db_file

    def __enter__(self):
        """Открываем соединение"""
        self.__conn: Connection = sqlite3.connect(self.db_file)
        self.__cursor: Cursor = self.__conn.cursor()
        return self

    def __exit__(self, etype, evalue, traceback):
        """Закрываем соединение"""
        self.__conn.commit()
        self.__conn.close()

    def get_users(self) -> list[tuple[int, int]]:
        result: Cursor = self.__cursor.execute("SELECT * FROM `users`")
        return result.fetchall()

    def user_exists(self, user_id: int) -> bool:
        """Проверяем, есть ли юзер в базе"""
        result: Cursor = self.__cursor.execute("SELECT `id` FROM `users` WHERE `id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def add_user(self, user_id: int, skins_num: int) -> None:
        """Добавляем юзера в базу"""
        self.__cursor.execute("INSERT INTO `users` (`id`, `skins_unlocked`) VALUES (?, ?)", (user_id, skins_num))

    def del_user(self, user_id: int) -> None:
        self.__cursor.execute("DELETE FROM `users` WHERE `id` = ?", (user_id,))

    def get_skins(self, user_id: int) -> int:
        result: Cursor = self.__cursor.execute("SELECT `skins_unlocked` FROM `users` WHERE `id` = ?", (user_id,))
        return result.fetchone()[0]

    def set_skins(self, user_is: int, skins: int) -> None:
        self.__cursor.execute("UPDATE `users` SET `skins_unlocked` = ? WHERE `id` = ?", (skins, user_is))

    def add_game(self, game_id: int, player1: int, player2: int, move: int, figures: str) -> None:
        self.__cursor.execute("REPLACE INTO `games` (`id`, `player1`, `player2`, `move`, `figures`) VALUES (?, ?, ?, ?, ?)", (game_id, player1, player2, move, figures))

    def del_game(self, game_id: int) -> None:
        self.__cursor.execute("DELETE FROM `games` WHERE `id` = ?", (game_id,))

    def game_exists(self, game_id: int) -> bool:
        result: Cursor = self.__cursor.execute("SELECT `id` FROM `games` WHERE `id` = ?", (game_id,))
        return bool(len(result.fetchall()))

    def get_game(self, game_id: int) -> list[tuple[int, int, int, int, str]]:
        result: Cursor = self.__cursor.execute("SELECT * FROM `games` WHERE `id` = ?", (game_id,))
        return result.fetchone()[0]

    # def get_wins(self, user_id: int) -> int:
    #     """Достаём колиество побед"""
    #     result: Cursor = self.cursor.execute("SELECT `num_wins` FROM `users` WHERE `id` = ?", (user_id,))
    #     return result.fetchone()[0]
    #
    # def set_wins(self, user_id: int, wins: int) -> None:
    #     """Устанавливаем количество побед"""
    #     self.cursor.execute("UPDATE `users` SET `num_wins` = ? WHERE `id` = ?", (wins, user_id))
    #     self.conn.commit()
