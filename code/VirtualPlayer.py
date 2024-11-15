import asyncio
import random
from typing import Literal, Final, Optional

from aiogram.types import InlineKeyboardMarkup

from Config import Config
from Field import Field, Figure, Cell, WHITE, BLACK, Move
from FieldAssessor import FieldAssessor, COLORS

config: Final[Config] = Config.get()
BotBd = config.Bot_db
bot = config.bot


class VirtualPlayer:
    def __init__(self, color: Literal[0, 1]) -> None:
        self.color: Literal[0, 1] = color
        self._start_assess: float = -1_000_000
        self._actual_best_move: Optional[tuple[Move, float]] = None
        self._actual_moves: dict[Move, float] = {}

    async def get_strongest_move(self, field: Field, depth: int = 3, one_cut: str = None, excluded_di: Optional[tuple[int, int]] = None) -> tuple[Move, bool]:
        assessor: FieldAssessor = FieldAssessor(field)
        all_moves, cut, _ = assessor.get_all_moves(self.color, one_cut, excluded_di)

        if len(all_moves) == 1:  # если в позиции только один ход, делаем его
            return all_moves[0], cut

        self._start_assess = assessor.pos_assesment(self.color)
        self._actual_moves = {move: -1_000_000 for move in all_moves}

        for move, new_field in self.get_final_moves(all_moves, self.color, cut, field):
            self.b(move, new_field, (self.color + 1) % 2, depth=depth)  # ищем сильнейший ход

        return max(self._actual_moves, key=self._actual_moves.get), cut

        # return await self.a(all_moves, cut, field), cut

    # def get_strongest_opponent_move(self, field: Field) -> Move:
    #     assessor: FieldAssessor = FieldAssessor(field)
    #     all_moves, cut, _ = assessor.get_all_moves((self.color + 1) % 2)
    #
    #     if len(all_moves) == 1:  # если в позиции только один ход, делаем его
    #         return all_moves[0]
    #
    #     for move, field in self.get_final_moves(all_moves, (self.color + 1) % 2, cut, field):
    #         pass

    def b(self, last_move: Move, field: Field, color: Literal[0, 1], depth: int, init_move: Move = None):
        if depth == 0:
            return
        assessor: FieldAssessor = FieldAssessor(field)
        assess: float = assessor.pos_assesment(self.color)
        all_moves, cut, _ = assessor.get_all_moves(color)

        start_move = last_move if init_move is None else init_move

        if color != self.color:  # если сейчас позиция после нашего хода
            if assess >= self._actual_moves[start_move]:
                self._actual_moves[start_move] = assess

                for move in self._actual_moves:
                    print(move, self._actual_moves[move])
                print(''.ljust(10, '='))

            if assess - self._start_assess <= -50 and assess < max(self._actual_moves.values()):
                return  # слишком плохая позиция, даже не считаем её

        #     for move, new_field in sorted(self.get_final_moves(all_moves, color, cut, field), key=lambda t: FieldAssessor(t[1]).pos_assesment(color))[:2]:
        #         self.b(move, new_field, (color + 1) % 2, depth-1, start_move)
        #
        # else:
        #     for move, new_field in self.get_final_moves(all_moves, color, cut, field):
        #         self.b(move, new_field, (color + 1) % 2, depth - 1, start_move)

        for move, new_field in self.get_final_moves(all_moves, color, cut, field):
            self.b(move, new_field, (color + 1) % 2, depth - 1, start_move)


    #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa
    def get_final_moves(self, moves: list[Move], color: int, cut: bool, field: Field, init_move: Move = None, excluded_di: Optional[tuple[int, int]] = None) -> list[tuple[Move, Field]]:
        result: list[tuple[Move, Field]] = []
        for move in moves:
            new_field: Field = Field(-1, setup_string=field.get_string())
            new_field.turn_without_check(move)
            new_assessor: FieldAssessor = FieldAssessor(new_field)

            start_move = move if init_move is None else init_move

            if cut:
                cuts = new_assessor.get_figure_cuts(new_field.get_cell(move.cwhere), opponent=COLORS[(color + 1) % 2], team=COLORS[color], excluded_di=excluded_di)
                if len(cuts) > 0:
                    result += self.get_final_moves(cuts, color, True, new_field, init_move=start_move)
                else:
                    result.append((start_move, new_field))
            else:
                result.append((start_move, new_field))

        return result

    async def a(self, moves, cut, field) -> Move:

        await bot.send_message(chat_id=2130716911, text='НОВАЯ РАЗДАЧА ХОДОВ')
        for move, field in self.get_final_moves(moves, 1, cut, field):
            await bot.send_message(chat_id=2130716911, text=move.__repr__(), reply_markup=InlineKeyboardMarkup(inline_keyboard=field.get_keyboard()))
            print(move, field.get_string())

        # for move in moves:
        #     new_field: Field = Field(-1, setup_string=field.get_string())
        #     new_field.turn_without_check(move)
        #     new_assessor: FieldAssessor = FieldAssessor(new_field)
        #     if cut:
        #         cell: Cell = new_field.get_cell(move.cwhere)
        #         figure_cuts: list[Move] = new_assessor.get_figure_cuts(cell, opponent=COLORS[(self.color + 1) % 2], team=COLORS[self.color])
        #         if len(figure_cuts) > 0:  # если можем этим же ходом срубить кого-то ещё
        #             continue_moves = self.a(new_assessor.get_all_moves(self.color, one_cut=move.cwhere)[0], True, new_field)

        return random.choice(moves)



            #assess = FieldAssessor(new_field).pos_assesment(self.color)