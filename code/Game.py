from typing import Final, Optional

from aiogram.types import InlineKeyboardMarkup

from Field import Field, Cell, Figure

WHITE: Final[tuple[Figure, Figure]] = (Figure.white, Figure.white_queen)
BLACK: Final[tuple[Figure, Figure]] = (Figure.black, Figure.black_queen)


class Game:
    def __init__(self, player1: int, player2: int):
        self.field: Final[Field] = Field()
        self.players: tuple[int, int] = (player1, player2)
        self.choosen_cell: Optional[str] = None
        self.old_cell: Optional[str] = None
        self.one_cut: Optional[str] = None
        self.move: int = 0
        self.win: int = -1

    def moving(self) -> int:
        self.move = (self.move + 1) % 2

        if not self.can_move(self.move):
            self.win = (self.move + 1) % 2

        return self.move

    def get_board(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=self.field.get_keyboard(self.choosen_cell, self.old_cell))

    def check_click(self, player_id: int) -> bool:
        if self.players.index(player_id) != self.move:
            return False  # не ваш ход
        return True

    def get_cur_state(self) -> tuple[tuple[Figure, Figure], tuple[Figure, Figure]]:
        return (WHITE, BLACK) if self.move == 0 else (BLACK, WHITE)

    def click_handler(self, cell_id: str) -> tuple[bool, Optional[str]]:
        cell = self.field.get_cell(cell_id)

        match cell.state, self.move:
            case (Figure.black | Figure.black_queen, 0) | (Figure.white | Figure.white_queen, 1):  # в чужую
                return False, None
            case (Figure.black | Figure.black_queen, 1) | (Figure.white | Figure.white_queen, 0):  # в свою
                self.choosen_cell = cell_id
                return True, None
            case Figure.null, 0 | 1:  # в пустую
                return self.move_attempt(cell_id)

    def move_attempt(self, cell_id: str) -> tuple[bool, Optional[str]]:

        def procces(is_cut: bool, queen: bool = False) -> tuple[bool, Optional[str]]:
            cell.state = choosen.state
            choosen.state = Figure.null
            self.old_cell = self.choosen_cell

            if (not queen and is_cut and self.can_cut_down_one(cell)) or (queen and is_cut and self.can_queen_cut_down(cell)):
                self.choosen_cell = cell.get_id()
                self.one_cut = cell.get_id()
            else:
                self.choosen_cell = None
                self.moving()
                self.one_cut = None

            if cell.state is Figure.black and cell.number == 8:
                cell.state = Figure.black_queen
            elif cell.state is Figure.white and cell.number == 1:
                cell.state = Figure.white_queen

            return True, None

        cell = self.field.get_cell(cell_id)

        if self.choosen_cell is None:
            return False, None

        choosen = self.field.get_cell(self.choosen_cell)

        cut_down: bool = self.can_cut_down_all()
        queens_cat_down: bool = self.can_all_queen_cut_down()

        if not cut_down and not queens_cat_down:
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
                            between.state = Figure.null
                            return procces(True)
                elif choosen.state is self.get_cur_state()[0][1]:
                    if abs(ord(cell.letter) - ord(choosen.letter)) == abs(cell.number - choosen.number) and tuple(i.state.get_color() for i in self.field.get_cells_between(cell, choosen)).count(self.get_cur_state()[1][0].get_color()) == 1 and tuple(i.state.get_color() for i in self.field.get_cells_between(cell, choosen)).count(self.get_cur_state()[0][0].get_color()) == 0:
                        for i in self.field.get_cells_between(cell, choosen):
                            i.state = Figure.null
                        return procces(True, queen=True)

                return False, 'Вы должны рубить!'

        return False, None

    def can_cut_down_all(self) -> bool:
        cells = []
        for i in self.field.cells:
            cells += i
        for cell in tuple(filter(lambda ce: ce.state in self.get_cur_state()[0], cells)):
            if self.can_cut_down_one(cell):
                return True
        return False

    def can_cut_down_one(self, cell: Cell, opponent: tuple[Figure, Figure] = None) -> bool:
        if opponent is None:
            opponent = self.get_cur_state()[1]
        for neigh in ((self.field.get_cell(f'{chr(ord(cell.letter) - 1)}{cell.number - 1}'),
                       self.field.get_cell(f'{chr(ord(cell.letter) - 2)}{cell.number - 2}')),
                      (self.field.get_cell(f'{chr(ord(cell.letter) - 1)}{cell.number + 1}'),
                       self.field.get_cell(f'{chr(ord(cell.letter) - 2)}{cell.number + 2}')),
                      (self.field.get_cell(f'{chr(ord(cell.letter) + 1)}{cell.number + 1}'),
                       self.field.get_cell(f'{chr(ord(cell.letter) + 2)}{cell.number + 2}')),
                      (self.field.get_cell(f'{chr(ord(cell.letter) + 1)}{cell.number - 1}'),
                       self.field.get_cell(f'{chr(ord(cell.letter) + 2)}{cell.number - 2}')),
                      ):
            if neigh[0] is None or neigh[1] is None:
                continue
            if neigh[0].state in opponent and neigh[1].state is Figure.null:
                return True
        return False

    def can_all_queen_cut_down(self) -> bool:
        cells = []
        for i in self.field.cells:
            cells += i
        for cell in tuple(filter(lambda ce: ce.state is self.get_cur_state()[0][1], cells)):
            if self.can_queen_cut_down(cell):
                return True
        return False

    def can_queen_cut_down(self, cell: Cell, opponent: tuple[Figure, Figure] = None, team: tuple[Figure, Figure] = None) -> bool:
        if opponent is None:
            opponent = self.get_cur_state()[1]
        if team is None:
            team = self.get_cur_state()[0]
        directs = ((-1, -1),
                   (-1, 1),
                   (1, 1),
                   (1, -1))
        for di in directs:
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

    def can_move(self, color: int) -> bool:
        cells = []
        for i in self.field.cells:
            cells += i
        for cell in tuple(filter(lambda c: c.state.get_color() == color, cells)):
            match cell.state:
                case Figure.white | Figure.black:
                    if self.can_cut_down_one(cell, opponent=WHITE if color == 1 else BLACK):
                        return True
                    one = self.field.get_cell(f'{chr(ord(cell.letter) - 1)}{cell.number + (1 if color == 1 else -1)}')
                    two = self.field.get_cell(f'{chr(ord(cell.letter) + 1)}{cell.number + (1 if color == 1 else -1)}')
                    if (one is not None and one.state is Figure.null) or (two is not None and two.state is Figure.null):
                        return True

                case Figure.white_queen | Figure.black_queen:
                    if self.can_queen_cut_down(cell, opponent=WHITE if color == 1 else BLACK, team=WHITE if color == 0 else BLACK):
                        return True
                    for di in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                        target = self.field.get_cell(f'{chr(ord(cell.letter) + di[0])}{cell.number + di[1]}')
                        if target is not None and target.state is Figure.null:
                            return True
        return False
