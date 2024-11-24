from typing import Final, Literal, Optional
from field import Field, Figure, Cell, WHITE, BLACK, Move


COLORS: Final = (WHITE, BLACK)


class FieldAssessor:
    def __init__(self, field: Field) -> None:
        self.field: Field = field

    def pos_assesment(self, color: Literal[0, 1]) -> float:
        PAWN_VALUE: Final[int] = 10
        QUEEN_VALUE: Final[int] = 65
        CELL_BONUS: Final[tuple[tuple[float, ...], ...]] = (
            (1.2 , 1.2, 1.2, 1.2 ),
            (1.15, 1.2, 1.2, 1.15),
            (1.15, 1.2, 1.2, 1.15),
            (1   , 1.2, 1.2, 1   ),
            (1   , 1.2, 1.2, 1   ),
            (1   , 1  , 1  , 1   ),
            (1   , 1  , 1  , 1   ),
            (1   , 1  , 1  , 1   ),
        )
        Y_BONUS: Final[tuple[int]] = tuple(range(1, 9))

        result: float = 0

        PLUSMINUS: Final = (1, -1), (-1, 1)
        pm: tuple[int, int] = PLUSMINUS[color]

        for n_i in range(8):
            line_num = self.field.cells[n_i]
            for l_j in range(4):
                cell = line_num[l_j]
                match cell.state:
                    case Figure.white:
                        result += pm[0] * PAWN_VALUE * CELL_BONUS[n_i][l_j] * Y_BONUS[n_i] / 2.2
                    case Figure.black:
                        result += pm[1] * PAWN_VALUE * CELL_BONUS[7 - n_i][l_j] * Y_BONUS[7 - n_i] / 2.2
                    case Figure.white_queen:
                        result += pm[0] * QUEEN_VALUE
                    case Figure.black_queen:
                        result += pm[1] * QUEEN_VALUE
                    case _:
                        pass
        return result

    def _get_pawn_cuts(self, cell: Cell, opponent: tuple[Figure, Figure]) -> list[Move]:
        moves: list[Move] = []
        for di in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            target = self.field.get_cell(f'{chr(ord(cell.letter) + di[0])}{cell.number + di[1]}')
            behind = self.field.get_cell(f'{chr(ord(cell.letter) + di[0] * 2)}{cell.number + di[1] * 2}')
            if target is None or behind is None:
                continue
            if target.state in opponent and behind.state is Figure.null:
                moves.append(Move(cell.get_id(), behind.get_id()))
        return moves

    def _get_pawn_moves(self, cell: Cell, color: Literal[0, 1]) -> list[Move]:
        moves: list[Move] = []
        one = self.field.get_cell(f'{chr(ord(cell.letter) - 1)}{cell.number + (1 if color == 1 else -1)}')
        two = self.field.get_cell(f'{chr(ord(cell.letter) + 1)}{cell.number + (1 if color == 1 else -1)}')
        if one is not None and one.state is Figure.null:
            moves.append(Move(cell.get_id(), one.get_id()))
        if two is not None and two.state is Figure.null:
            moves.append(Move(cell.get_id(), two.get_id()))
        return moves

    def can_cut_down_one(self, cell: Cell, opponent: tuple[Figure, Figure]) -> bool:
        return len(self._get_pawn_cuts(cell, opponent)) > 0

    def _get_queen_cuts(self, cell: Cell, opponent: tuple[Figure, Figure], team: tuple[Figure, Figure], field: Field = None, excluded_di: Optional[tuple[int, int]] = None) -> list[Move]:
        moves: list[Move] = []
        if field is None:
            field = self.field
        for di in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            if di == excluded_di:
                continue
            moves_in_direction: list[Move] = []
            for i in range(1, 9):
                target = field.get_cell(f'{chr(ord(cell.letter) + di[0] * i)}{cell.number + di[1] * i}')
                if target is None:
                    break
                if target.state in team:  # дальше не идём, через своих прыгать не можем
                    break
                if target.state in opponent:  # нашли противника, если за ним окажется пустая, срубим
                    continue

                cells_between: tuple[Cell] = field.get_cells_between(cell, target)
                count_color = lambda color: tuple(ce.state.get_color() for ce in cells_between).count(color)
                num_oppo = count_color(opponent[0].get_color())
                num_team = count_color(team[0].get_color())

                if target.state is Figure.null and num_oppo == 1 and num_team == 0:  # если клетка пустая, а между ней и стартовой только один противник и нет тиммейтов
                    moves_in_direction.append(Move(cell.get_id(), target.get_id()))

            new_moves_in_direction: list[Move] = []
            if len(moves_in_direction) > 1:
                for move in moves_in_direction:  # перебираем клетки, на которые можно встать после срубки
                    m_cell: Cell = field.get_cell(move.cwhere)
                    new_field: Field = Field(-1, setup_string=field.get_string())
                    new_field.turn_without_check(move)
                    if len(self._get_queen_cuts(m_cell, opponent, team, new_field, (-di[0], -di[1]))) > 0:
                        new_moves_in_direction.append(move)  # если на новой клетке можно срубить кого-то ещё, то обязательно вставать именно на неё
            if len(new_moves_in_direction) > 0:
                moves += new_moves_in_direction
            else:
                moves += moves_in_direction

        return moves

    def _get_queen_moves(self, cell: Cell) -> list[Move]:
        moves: list[Move] = []
        for di in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            for i in range(1, 9):
                target = self.field.get_cell(f'{chr(ord(cell.letter) + di[0] * i)}{cell.number + di[1] * i}')
                if target is None:
                    break
                if target.state is not Figure.null:
                    break
                else:
                    moves.append(Move(cell.get_id(), target.get_id()))
        return moves

    def can_queen_cut_down(self, cell: Cell, opponent: tuple[Figure, Figure] = None, team: tuple[Figure, Figure] = None, excluded_di: Optional[tuple[int, int]] = None) -> bool:
        return len(self._get_queen_cuts(cell, opponent, team, excluded_di=excluded_di)) > 0

    def get_figure_cuts(self, cell: Cell, opponent: tuple[Figure, Figure], team: tuple[Figure, Figure] = None, excluded_di: Optional[tuple[int, int]] = None) -> list[Move]:
        match cell.state.get_rang():
            case 0:  # пешка
                return self._get_pawn_cuts(cell, opponent)
            case 1:  # дамка
                return self._get_queen_cuts(cell, opponent, team, excluded_di=excluded_di)

    def get_figure_moves(self, cell: Cell) -> list[Move]:
        match cell.state.get_rang():
            case 0:  # пешка
                return self._get_pawn_moves(cell, cell.state.get_color())
            case 1:  # дамка
                return self._get_queen_moves(cell)

    def get_all_moves(self, color: Literal[0, 1], one_cut: Optional[str] = None, excluded_di: Optional[tuple[int, int]] = None) -> tuple[list[Move], bool, bool]:
        moves: list[Move] = []

        is_have_figures: bool = False  # посмотрим, остались ли фигуры
        cut: bool = False  # если кто-то может рубить, то рубить должны все

        if one_cut is None:
            cells: tuple[Cell] = tuple(filter(lambda ce: ce.state.get_color() == color, self.field.get_list_cells()))
        else:
            cells: tuple[Cell] = (self.field.get_cell(one_cut),)
            cut = True  # нас есть фигура, которой мы рубили в этом ходу, мы должны ходить только ей и только рубить

        for cell in cells:
            is_have_figures = True

            cut_moves = self.get_figure_cuts(cell, opponent=COLORS[(color + 1) % 2], team=COLORS[color], excluded_di=excluded_di)
            if len(cut_moves) > 0:  # если может рубить
                if not cut:
                    cut = True  # теперь рубить будут все
                    moves = cut_moves  # старые ходы становятся недопустимыми
                else:
                    moves += cut_moves
            elif not cut:  # рубить не может, но сейчас не обязательно
                moves += self.get_figure_moves(cell)
        # print(moves)
        return moves, cut, is_have_figures
