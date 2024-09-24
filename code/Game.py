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
        self.move: int = 0

    def moving(self) -> int:
        self.move = (self.move + 1) % 2
        return self.move

    def get_board(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=self.field.get_keyboard(self.choosen_cell, self.old_cell))

    def check_click(self, player_id: int) -> bool:
        if self.players.index(player_id) != self.move:
            return False  # не ваш ход
        return True

    def click_handler(self, cell_id: str) -> tuple[bool, Optional[str]]:
        cell = self.field.get_cell(cell_id)

        match cell.state, self.move:
            case (Figure.black | Figure.black_queen, 0) | (Figure.white | Figure.white_queen, 1):  # в чужую
                if self.choosen_cell is None:
                    return False, None
                else:
                    self.choosen_cell = None
                    return True, None
            case (Figure.black | Figure.black_queen, 1) | (Figure.white | Figure.white_queen, 0):  # в свою
                self.choosen_cell = cell_id
                return True, None
            case Figure.null, 0 | 1:  # в пустую
                return self.move_attempt(cell_id)

    def move_attempt(self, cell_id: str) -> tuple[bool, Optional[str]]:

        def procces() -> None:
            cell.state = choosen.state
            choosen.state = Figure.null
            self.old_cell = self.choosen_cell
            self.choosen_cell = None
            self.moving()

            if cell.state is Figure.black and cell.number == 8:
                cell.state = Figure.black_queen
            elif cell.state is Figure.white and cell.number == 1:
                cell.state = Figure.white_queen

        cell = self.field.get_cell(cell_id)

        if self.choosen_cell is None:
            return False, None

        choosen = self.field.get_cell(self.choosen_cell)

        cut_down: bool = self.can_cut_down()

        if not cut_down:
            if ((choosen.state is Figure.white and cell.number == choosen.number - 1) or (choosen.state is Figure.black and cell.number == choosen.number + 1)) and abs(ord(cell.letter) - ord(choosen.letter)) == 1:  # обычный ход
                procces()
                return True, None

        else:
            if abs(cell.number - choosen.number) == 2 and abs(ord(cell.letter) - ord(choosen.letter)) == 2:  # рубка
                between = self.field.get_cell(f'{chr((ord(cell.letter) + ord(choosen.letter)) // 2)}{(cell.number + choosen.number) // 2}')
                if (between.state in BLACK and choosen.state in WHITE) or (between.state in WHITE and choosen.state in BLACK):
                    procces()
                    between.state = Figure.null
                    return True, None
            return False, 'Вы должны рубить!'

        return False, None

    def can_cut_down(self) -> bool:
        print(f'{self.move=}')
        cur_state: tuple[tuple, tuple] = (WHITE, BLACK) if self.move == 0 else (BLACK, WHITE)
        print(cur_state)
        cells = []
        for i in self.field.cells:
            cells += i
        for cell in tuple(filter(lambda ce: ce.state in cur_state[0], cells)):
            print(cell)
            for neigh in ((self.field.get_cell(f'{chr(ord(cell.letter) - 1)}{cell.number - 1}'), self.field.get_cell(f'{chr(ord(cell.letter) - 2)}{cell.number - 2}')),
                          (self.field.get_cell(f'{chr(ord(cell.letter) - 1)}{cell.number + 1}'), self.field.get_cell(f'{chr(ord(cell.letter) - 2)}{cell.number + 2}')),
                          (self.field.get_cell(f'{chr(ord(cell.letter) + 1)}{cell.number + 1}'), self.field.get_cell(f'{chr(ord(cell.letter) + 2)}{cell.number + 2}')),
                          (self.field.get_cell(f'{chr(ord(cell.letter) + 1)}{cell.number - 1}'), self.field.get_cell(f'{chr(ord(cell.letter) + 2)}{cell.number - 2}')),
                          ):
                if neigh[0] is None or neigh[1] is None:
                    continue
                if neigh[0].state in cur_state[1] and neigh[1].state is Figure.null:
                    return True
        return False







