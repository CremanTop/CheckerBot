from enum import Enum
from typing import Final, Optional, Literal

from aiogram.types import InlineKeyboardButton

from CheckerBot.code.Skins import SkinSet, SKINS

alp: Final[str] = 'abcdefgh'


class Figure(Enum):
    null = '•'
    white = '⚪'
    black = '⚫'
    white_queen = '🤍'
    black_queen = '🖤'

    choosen = '🔴'
    choosen_queen = '❤'
    old_move = '📍'

    def get_color(self) -> int:
        match self:
            case self.white | self.white_queen:
                return 0
            case self.black | self.black_queen:
                return 1
            case _:
                return -1

    def get_skin_type(self, choosen: bool) -> Literal['pawn', 'queen', 'choosen_pawn', 'choosen_queen']:
        match self, choosen:
            case self.white | self.black, False:
                return 'pawn'
            case self.white_queen | self.black_queen, False:
                return 'queen'
            case self.white | self.black, True:
                return 'choosen_pawn'
            case self.white_queen | self.black_queen, True:
                return 'choosen_queen'


class Cell:
    def __init__(self, let: str, num: int, figure: Figure = Figure.null) -> None:
        self.letter: str = let
        self.number: int = num
        self.state: Figure = figure

    def get_id(self) -> str:
        return f'{self.letter}{self.number}'

    def __str__(self):
        return self.get_id()


class Field:
    def start_setup(self) -> None:
        lines = []

        for i in range(8, 0, -1):
            line = []
            for n in range(1, 9, 2):
                if i % 2 != 0:
                    n -= 1
                cell = Cell(alp[n], i)

                if i > 5:
                    cell.state = Figure.white
                elif i < 4:
                    cell.state = Figure.black

                line.append(cell)
            lines.append(line)
        self.cells = lines

    def skin_update(self, black_skin: str = 'black'):
        if self.white_skin is not SKINS[black_skin]:
            self.black_skin: SkinSet = SKINS[black_skin]
        else:
            self.black_skin: SkinSet = SKINS['black']

    def __init__(self, game_id: int, white_skin: str = 'white', black_skin: str = 'black', setup_string: str = None) -> None:
        self.cells: list[list[Cell]] = None
        self.id: Final[int] = game_id

        self.white_skin: Final[SkinSet] = SKINS[white_skin]
        self.black_skin = None
        self.skin_update(black_skin)

        if setup_string is None:
            self.start_setup()
        else:
            self.load_from_string(setup_string)

    def get_list_cells(self) -> list[Cell]:
        cells: list[Cell] = []
        for i in self.cells:
            cells += i
        return cells

    def get_cell(self, cell_id: str) -> Optional[Cell]:
        let, num = cell_id[0], cell_id[1]
        if num.isdigit():
            num = int(num)
        else:
            return None
        if let not in alp or num not in range(1, 9):
            return None

        return self.cells[8 - num][alp.index(let) // 2]

    def get_cells_between(self, first: Cell, second: Cell) -> tuple[Cell, ...]:
        step1 = 1 if ord(first.letter) < ord(second.letter) else -1
        step2 = 1 if first.number < second.number else -1
        return tuple(self.get_cell(f'{let}{num}') for let, num in zip(
            (chr(j) for j in range(ord(first.letter) + step1, ord(second.letter), step1)),
            range(first.number + step2, second.number, step2)
            )
        )

    def get_keyboard(self, choosen_cell: str = None, old_cell: str = None) -> list[list[InlineKeyboardButton]]:
        def get_fig_skin(figure: Figure, choosen: bool) -> str:
            skin_set: SkinSet = self.white_skin if figure.get_color() == 0 else self.black_skin
            if figure.get_skin_type(choosen) is None:
                return str(figure.value)
            return skin_set[figure.get_skin_type(choosen)]

        keyboard = []
        for line, i in zip(self.cells, range(8)):
            u_line = []
            for cell in line:

                button = InlineKeyboardButton(text=get_fig_skin(cell.state, cell.get_id() == choosen_cell), callback_data=f'{self.id}_{cell.get_id()}')
                if cell.get_id() == old_cell:
                    button = InlineKeyboardButton(text=str(Figure.old_move.value), callback_data=f'{self.id}_{cell.get_id()}')

                if i % 2 != 0:
                    u_line.append(button)
                u_line.append(InlineKeyboardButton(text=' ', callback_data='null'))
                if i % 2 == 0:
                    u_line.append(button)
            keyboard.append(u_line)
        keyboard.append([InlineKeyboardButton(text='Сдаться', callback_data=f'{self.id}_surrender'), InlineKeyboardButton(text='Предложить ничью', callback_data=f'{self.id}_draw')])
        return keyboard

    def get_string(self) -> str:
        string = ''
        for line in self.cells:
            for cell in line:
                match cell.state:
                    case Figure.white:
                        result = 'w'
                    case Figure.black:
                        result = 'b'
                    case Figure.white_queen:
                        result = 'W'
                    case Figure.black_queen:
                        result = 'B'
                    case _:
                        result = '0'
                string += result
            string += ','
        return string[:-1]

    def load_from_string(self, string: str):
        num = 8
        let = (('b', 'd', 'f', 'h'), ('a', 'c', 'e', 'g'))
        lines = []
        COUN = 0
        for lo in string.split(','):
            line = []
            coun = 0
            for ch in lo:
                cell = Cell(let[COUN][coun], num)
                coun += 1
                match ch:
                    case '0':
                        cell.state = Figure.null
                    case 'w':
                        cell.state = Figure.white
                    case 'W':
                        cell.state = Figure.white_queen
                    case 'b':
                        cell.state = Figure.black
                    case 'B':
                        cell.state = Figure.black_queen
                line.append(cell)
            COUN = (COUN + 1) % 2
            num -= 1
            lines.append(line)
        self.cells = lines
