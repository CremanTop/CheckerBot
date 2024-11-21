from dataclasses import dataclass
from typing import Callable, Final


@dataclass
class Achievement:
    id: str
    name: str
    descript: str
    secret: bool


achievements: Final[tuple[Achievement, ...]] = (
    Achievement('animal', 'Геноцид', 'Съешьте не менее трёх фигур за ход.', False),
    Achievement('moon', 'Троекратное "Ура"', 'Выиграйте три раза.', False),
    Achievement('food', 'Званый ужин', 'Съешьте фигуры противника 3 хода подряд.', False),
    Achievement('rain', 'Двоевластие', 'Создайте не менее двух дамок за игру.', False),
    Achievement('rock', 'Паритет', 'Сыграйте в ничью три раза.', False),
    Achievement('insight', 'Чем больше шкаф', 'Съешьте дамку пешкой.', False),
    Achievement('tool', 'Крестьянская революция', 'Выиграйте, не создавая дамок за игру.', False),
    Achievement('key', 'Разделяй и властвуй', 'Выиграйте, не оставив противнику ходов.', False),
    Achievement('feet', 'Карьерный рост', 'Создайте дамку не позже десятого хода.', False),
    Achievement('research', 'Здравствуй, Нео', 'Сыграйте с создателем.', True),
)


class AchGameCounter:
    def __init__(self) -> None:
        self.eaten_counter: int = 0  # прибавлять при съедении фигуры
        self.counter_moves_when_white_chopping: int = 0
        self.counter_moves_when_black_chopping: int = 0
        self.counter_white_queen: int = 0  # прибавлять при создании дамки
        self.counter_black_queen: int = 0  # прибавлять при создании дамки
        self.move_counter: float = 1

    def move(self, color: int) -> list[str]:
        result: list[str] = []

        if color == 0:
            if self.eaten_counter == 0:
                self.counter_moves_when_white_chopping = 0
            else:
                self.counter_moves_when_white_chopping += 1
                if self.counter_moves_when_white_chopping >= 3:
                    result.append('food')
        else:
            if self.eaten_counter == 0:
                self.counter_moves_when_black_chopping = 0
            else:
                self.counter_moves_when_black_chopping += 1
                if self.counter_moves_when_black_chopping >= 3:
                    result.append('food')

        if self.eaten_counter >= 3:
            result.append('animal')

        self.move_counter += 0.5
        self.eaten_counter = 0

        return result

    def end_game(self, color: int, win: bool, have_figure_opponent: bool = False) -> list[str]:
        result: list[str] = []
        if (color == 0 and self.counter_white_queen >= 2) or (color == 1 and self.counter_black_queen >= 2):
            result.append('rain')

        if win:
            if (color == 0 and self.counter_white_queen == 0) or (color == 1 and self.counter_black_queen == 0):
                result.append('tool')
            if have_figure_opponent:
                result.append('key')

        return result


get_achieve: Final[Callable[[str], Achievement]] = lambda a_id: next(filter(lambda ach: ach.id == a_id, achievements), None)
