from typing import Final, Optional

from aiogram.types import InlineKeyboardMarkup

from CheckerBot.code.Achievement import AchGameCounter
from CheckerBot.code.Config import Config
from CheckerBot.code.Player import Player
from Field import Field, Cell, Figure

WHITE: Final[tuple[Figure, Figure]] = (Figure.white, Figure.white_queen)
BLACK: Final[tuple[Figure, Figure]] = (Figure.black, Figure.black_queen)

config: Final[Config] = Config.get()

BotBd = config.Bot_db


class Game:
    counter = 0

    def __init__(self, player1: Player, player2: Player):
        self.id: Final[int] = Game.counter
        Game.counter += 1

        ws = player1.get_skin() if player1.get_skin() is not None else 'white'
        bs = player2.get_skin() if player2.get_skin() is not None else 'black'

        self.field: Final[Field] = Field(self.id, white_skin=ws, black_skin=bs)
        self.players: list[Player, Player] = [player1, player2]  # белые, чёрные
        self.choosen_cell: Optional[str] = None
        self.old_cell: Optional[str] = None
        self.one_cut: Optional[str] = None
        self.move: int = 0
        self.win: int = -1
        self.ach_counter: AchGameCounter = AchGameCounter()

    def get_message(self) -> str:
        player1: str = f'{self.players[0].name} {self.field.white_skin["pawn"]}'
        player2: str = f'{self.players[1].name} {self.field.black_skin["pawn"]}'
        return f'{player1} vs {player2} \n' \
               f'Ход: {self.field.white_skin["whose"] if self.move == 0 else self.field.black_skin["whose"]}'

    def moving(self) -> list[str]:
        result = self.ach_counter.move(self.move)
        self.move = (self.move + 1) % 2

        if not self.can_move(self.move)[0]:
            self.win = (self.move + 1) % 2
            with BotBd as bd:
                if bd.game_exists(self.id):
                    bd.del_game(self.id)

        return result

    def get_board(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=self.field.get_keyboard(self.choosen_cell, self.old_cell))

    def check_click(self, player_id: int) -> bool:
        player = next(filter(lambda pl: pl.id == player_id, self.players))
        if self.players.index(player) != self.move:
            return False  # не ваш ход
        return True

    def get_cur_state(self) -> tuple[tuple[Figure, Figure], tuple[Figure, Figure]]:
        return (WHITE, BLACK) if self.move == 0 else (BLACK, WHITE)

    def click_handler(self, cell_id: str) -> tuple[bool, Optional[str | list[str]]]:
        cell = self.field.get_cell(cell_id)

        match cell.state, self.move:
            case (Figure.black | Figure.black_queen, 0) | (Figure.white | Figure.white_queen, 1):  # в чужую
                return False, None
            case (Figure.black | Figure.black_queen, 1) | (Figure.white | Figure.white_queen, 0):  # в свою
                self.choosen_cell = cell_id
                return True, None
            case Figure.null, 0 | 1:  # в пустую
                return self.move_attempt(cell_id)

    def move_attempt(self, cell_id: str) -> tuple[bool, Optional[str | list[str]]]:

        def procces(is_cut: bool, queen: bool = False, *dopresult: str) -> tuple[bool, list[str]]:
            cell.state = choosen.state
            choosen.state = Figure.null
            self.old_cell = self.choosen_cell

            achieves = [*dopresult]

            if is_cut:
                self.ach_counter.eaten_counter += 1

            if (not queen and is_cut and self.can_cut_down_one(cell)) or (queen and is_cut and self.can_queen_cut_down(cell)):
                self.choosen_cell = cell.get_id()
                self.one_cut = cell.get_id()
            else:
                self.choosen_cell = None
                achieves += self.moving()
                self.one_cut = None

            if cell.state is Figure.black and cell.number == 8:
                cell.state = Figure.black_queen
                self.ach_counter.counter_black_queen += 1
                if self.ach_counter.move_counter // 1 <= 10:
                    achieves.append('feet')

            elif cell.state is Figure.white and cell.number == 1:
                cell.state = Figure.white_queen
                self.ach_counter.counter_white_queen += 1
                if self.ach_counter.move_counter // 1 <= 10:
                    achieves.append('feet')

            return True, achieves

        cell = self.field.get_cell(cell_id)

        if self.choosen_cell is None:
            return False, None

        choosen = self.field.get_cell(self.choosen_cell)

        cut_down: bool = self.can_cut_down_all_pawn()
        queens_cut_down: bool = self.can_all_queen_cut_down()

        if not cut_down and not queens_cut_down:
            if ((choosen.state is Figure.white and cell.number == choosen.number - 1) or (choosen.state is Figure.black and cell.number == choosen.number + 1)) and abs(ord(cell.letter) - ord(choosen.letter)) == 1:  # обычный ход
                return procces(False)
            elif choosen.state in (Figure.white_queen, Figure.black_queen) and abs(ord(cell.letter) - ord(choosen.letter)) == abs(cell.number - choosen.number) and all(i.state is Figure.null for i in self.field.get_cells_between(cell, choosen)):
                return procces(False)

        else:
            if (self.one_cut is not None and choosen.get_id() == self.one_cut) or self.one_cut is None:
                if choosen.state is self.get_cur_state()[0][0]:
                    if abs(cell.number - choosen.number) == 2 and abs(ord(cell.letter) - ord(choosen.letter)) == 2:  # рубка
                        between = self.field.get_cell(f'{chr((ord(cell.letter) + ord(choosen.letter)) // 2)}{(cell.number + choosen.number) // 2}')
                        if between.state in self.get_cur_state()[1]:
                            if between.state is self.get_cur_state()[1][1]:
                                between.state = Figure.null
                                return procces(True, False, 'insight')
                            else:
                                between.state = Figure.null
                                return procces(True)
                elif choosen.state is self.get_cur_state()[0][1]:
                    cell_between = self.field.get_cells_between(cell, choosen)
                    count_color = lambda color: tuple(i.state.get_color() for i in cell_between).count(self.get_cur_state()[color][0].get_color())
                    if abs(ord(cell.letter) - ord(choosen.letter)) == abs(cell.number - choosen.number) and count_color(1) == 1 and count_color(0) == 0:
                        for i in cell_between:
                            i.state = Figure.null
                        return procces(True, queen=True)

                return False, 'Вы должны рубить!'

        return False, None

    def can_cut_down_all_pawn(self) -> bool:
        for cell in tuple(filter(lambda ce: ce.state is self.get_cur_state()[0][0], self.field.get_list_cells())):
            if self.can_cut_down_one(cell):
                return True
        return False

    def can_cut_down_one(self, cell: Cell, opponent: tuple[Figure, Figure] = None) -> bool:
        if opponent is None:
            opponent = self.get_cur_state()[1]
        for di in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            target = self.field.get_cell(f'{chr(ord(cell.letter) + di[0])}{cell.number + di[1]}')
            behind = self.field.get_cell(f'{chr(ord(cell.letter) + di[0] * 2)}{cell.number + di[1] * 2}')
            if target is None or behind is None:
                continue
            if target.state in opponent and behind.state is Figure.null:
                return True
        return False

    def can_all_queen_cut_down(self) -> bool:
        for cell in tuple(filter(lambda ce: ce.state is self.get_cur_state()[0][1], self.field.get_list_cells())):
            if self.can_queen_cut_down(cell):
                return True
        return False

    def can_queen_cut_down(self, cell: Cell, opponent: tuple[Figure, Figure] = None, team: tuple[Figure, Figure] = None) -> bool:
        if opponent is None:
            opponent = self.get_cur_state()[1]
        if team is None:
            team = self.get_cur_state()[0]
        for di in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            for i in range(1, 9):
                target = self.field.get_cell(f'{chr(ord(cell.letter) + di[0] * i)}{cell.number + di[1] * i}')
                behind = self.field.get_cell(f'{chr(ord(cell.letter) + di[0] * (i + 1))}{cell.number + di[1] * (i + 1)}')
                if target is None or behind is None:
                    break
                if target.state in team or behind.state in team:
                    break
                if target.state in opponent and behind.state in opponent:
                    break
                if target.state in opponent and behind.state is Figure.null:
                    return True
        return False

    def can_move(self, color: int) -> tuple[bool, Optional[bool]]:
        is_have_figures: bool = False
        for cell in tuple(filter(lambda c: c.state.get_color() == color, self.field.get_list_cells())):
            is_have_figures = True
            match cell.state:
                case Figure.white | Figure.black:
                    if self.can_cut_down_one(cell, opponent=WHITE if color == 1 else BLACK):
                        return True, None
                    one = self.field.get_cell(f'{chr(ord(cell.letter) - 1)}{cell.number + (1 if color == 1 else -1)}')
                    two = self.field.get_cell(f'{chr(ord(cell.letter) + 1)}{cell.number + (1 if color == 1 else -1)}')
                    if (one is not None and one.state is Figure.null) or (two is not None and two.state is Figure.null):
                        return True, None

                case Figure.white_queen | Figure.black_queen:
                    if self.can_queen_cut_down(cell, opponent=WHITE if color == 1 else BLACK, team=WHITE if color == 0 else BLACK):
                        return True, None
                    for di in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                        target = self.field.get_cell(f'{chr(ord(cell.letter) + di[0])}{cell.number + di[1]}')
                        if target is not None and target.state is Figure.null:
                            return True, None
        return False, is_have_figures
