import random
from typing import Literal, Final, Optional

from assessor import FieldAssessor, COLORS
from config import Config
from field import Field, Move

config: Final[Config] = Config.get()
BotBd = config.Bot_db
bot = config.bot


class VirtualPlayer:
    def __init__(self, color: Literal[0, 1]) -> None:
        self.color: Literal[0, 1] = color
        self._start_assess: float = -1_000_000
        self._actual_best_move: Optional[tuple[Move, float]] = None
        self._actual_moves: dict[Move, float] = {}
        self.excluded_di = None

    async def get_strongest_move(self, field: Field, depth: int = 4, one_cut: str = None) -> tuple[Move, bool]:
        assessor: FieldAssessor = FieldAssessor(field)
        all_moves, cut, _ = assessor.get_all_moves(self.color, one_cut, self.excluded_di)

        if len(all_moves) == 1:  # если в позиции только один ход, делаем его
            return all_moves[0], cut

        self._start_assess = assessor.pos_assesment(self.color)
        self._actual_moves = {move: -1_000_000 for move in all_moves}

        for move, new_field in self.get_final_moves(all_moves, self.color, cut, field):
            self.b(move, new_field, (self.color + 1) % 2, depth=depth)  # ищем сильнейший ход

        for move in self._actual_moves:
            print(move, self._actual_moves[move])
        print(''.ljust(10, '='))

        if len(set(self._actual_moves.values())) == 1:
            return random.choice(self._actual_moves), cut
        return max(self._actual_moves, key=self._actual_moves.get), cut

    def b(self, last_move: Move, field: Field, color: Literal[0, 1], depth: int, init_move: Move = None):
        if depth == 0:
            return
        assessor: FieldAssessor = FieldAssessor(field)
        assess: float = assessor.pos_assesment(self.color)
        all_moves, cut, _ = assessor.get_all_moves(color, excluded_di=self.excluded_di)

        start_move = last_move if init_move is None else init_move

        if self._actual_moves[start_move] - self._start_assess <= -200 and self._actual_moves[start_move] != -1_000_000:
            return  # слишком плохая позиция, даже не считаем её

        if color != self.color:  # если сейчас позиция после нашего хода
            if assess >= self._actual_moves[start_move]:
                self._actual_moves[start_move] = assess

            if assess - self._start_assess <= -50 and assess < max(self._actual_moves.values()):
                return  # слишком плохая позиция, даже не считаем её

            for move, new_field in sorted(self.get_final_moves(all_moves, color, cut, field), key=lambda t: FieldAssessor(t[1]).pos_assesment(color), reverse=True)[:2]:
                self.b(move, new_field, (color + 1) % 2, depth-1, start_move)

        else:
            if len(all_moves) == 0:
                self._actual_moves[start_move] = -1_000_000
                return

            for move, new_field in self.get_final_moves(all_moves, color, cut, field):
                self.b(move, new_field, (color + 1) % 2, depth - 1, start_move)

    def get_final_moves(self, moves: list[Move], color: int, cut: bool, field: Field, init_move: Move = None) -> list[tuple[Move, Field]]:
        result: list[tuple[Move, Field]] = []
        for move in moves:
            new_field: Field = Field(-1, setup_string=field.get_string())
            new_field.turn_without_check(move)
            new_assessor: FieldAssessor = FieldAssessor(new_field)

            start_move = move if init_move is None else init_move

            if cut:
                cuts = new_assessor.get_figure_cuts(new_field.get_cell(move.cwhere), opponent=COLORS[(color + 1) % 2], team=COLORS[color], excluded_di=self.excluded_di)
                if len(cuts) > 0:
                    result += self.get_final_moves(cuts, color, True, new_field, init_move=start_move)
                else:
                    result.append((start_move, new_field))
            else:
                result.append((start_move, new_field))

        return result
