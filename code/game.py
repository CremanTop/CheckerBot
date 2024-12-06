from typing import Final, Optional, Literal

from aiogram.types import InlineKeyboardMarkup

from achievement import AchGameCounter
from config import Logger
from assessor import FieldAssessor
from field import Field, Figure, WHITE, BLACK
from player import Player


class Game:
    counter = 0

    def __init__(self, player1: Player, player2: Player, bot_color: Literal[0, 1] = -1):
        self.id: int = Game.counter
        Game.counter += 1

        ws = player1.get_skin() if player1.get_skin() is not None else 'white'
        bs = player2.get_skin() if player2.get_skin() is not None else 'black'

        self.field: Final[Field] = Field(self.id, white_skin=ws, black_skin=bs)
        self.players: list[Player, Player] = [player1, player2]  # белые, чёрные
        self.choosen_cell: Optional[str] = None
        self.old_cell: Optional[str] = None
        self.one_cut: Optional[str] = None
        self.excluded_queen_direction: Optional[tuple[int, int]] = None
        self.move: Literal[0, 1] = 0
        self.win: int = -1
        self.ach_counter: AchGameCounter = AchGameCounter()
        self.assessor: FieldAssessor = FieldAssessor(self.field)
        self.logger: Logger = Logger(True, self.id)
        self.is_draw_offered: bool = False
        self.with_bot: Literal[-1, 0, 1] = bot_color  # -1 - игра с игроком, 0 - бот за белых, 1 - бот за чёрных

        self.logger.info('Игра создана.')

    def screen_players(self) -> str:
        player1: str = f'{self.players[0].name} {self.field.white_skin["pawn"]}'
        player2: str = f'{self.players[1].name} {self.field.black_skin["pawn"]}'
        return f'{player1} vs {player2}\n'

    def get_message(self) -> str:
        draw: str = '\nПредложена ничья 🤝' if self.is_draw_offered else ''
        return self.screen_players() + f'Ход: {self.field.white_skin["whose"] if self.move == 0 else self.field.black_skin["whose"]}{draw}'

    def moving(self) -> list[str]:
        result = self.ach_counter.move(self.move)
        self.move = (self.move + 1) % 2

        if not self.can_move(self.move)[0]:
            self.win = (self.move + 1) % 2

        return result

    def get_board(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=self.field.get_keyboard(self.choosen_cell, self.old_cell, self.win != -1))

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

        def procces(is_cut: bool, *dopresult: str) -> tuple[bool, list[str]]:
            cell.state = choosen.state
            choosen.state = Figure.null
            self.old_cell = self.choosen_cell

            achieves = [*dopresult]

            if is_cut:
                self.ach_counter.eaten_counter += 1

            if cell.state.get_rang() == 1:
                di1 = 1 if ord(choosen.letter) > ord(cell.letter) else -1
                di2 = 1 if choosen.number > cell.number else -1
                self.excluded_queen_direction = (di1, di2)

            if is_cut and len(self.assessor.get_figure_cuts(cell, self.get_cur_state()[1], self.get_cur_state()[0], self.excluded_queen_direction)) != 0:
                self.choosen_cell = cell.get_id()
                self.one_cut = cell.get_id()

            else:
                self.choosen_cell = None
                achieves += self.moving()
                self.one_cut = None
                self.excluded_queen_direction = None

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

        all_moves, cut, _ = self.assessor.get_all_moves(self.move, self.one_cut, self.excluded_queen_direction)
        if len(tuple(filter(lambda move: move.cfrom == choosen.get_id() and move.cwhere == cell.get_id(), all_moves))) > 0:
            queen: bool = choosen.state is self.get_cur_state()[0][1]

            betweens = self.field.get_cells_between(choosen, cell)
            dop = None
            for bet in betweens:
                if not queen and bet.state is self.get_cur_state()[1][1]:
                    dop = 'insight'
                bet.state = Figure.null

            if dop is None:
                return procces(cut)
            else:
                return procces(cut, dop)
        else:
            if self.can_cut_down_all_pawn() or self.can_all_queen_cut_down():
                return False, 'Вы должны рубить!'
            else:
                return False, None

    def can_cut_down_all_pawn(self) -> bool:
        for cell in tuple(filter(lambda ce: ce.state is self.get_cur_state()[0][0], self.field.get_list_cells())):
            if self.assessor.can_cut_down_one(cell, self.get_cur_state()[1]):
                return True
        return False

    def can_all_queen_cut_down(self) -> bool:
        for cell in tuple(filter(lambda ce: ce.state is self.get_cur_state()[0][1], self.field.get_list_cells())):
            if self.assessor.can_queen_cut_down(cell, self.get_cur_state()[1], self.get_cur_state()[0], self.excluded_queen_direction):
                return True
        return False

    def can_move(self, color: Literal[0, 1]) -> tuple[bool, Optional[bool]]:
        moves, _, is_have_figures = self.assessor.get_all_moves(color, excluded_di=self.excluded_queen_direction)
        return len(moves) > 0, is_have_figures
