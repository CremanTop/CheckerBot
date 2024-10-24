from dataclasses import dataclass
from typing import Final

from CheckerBot.code.Config import Config

config: Final[Config] = Config.get()
BotBd = config.Bot_db


@dataclass
class Achievement:
    id: str
    name: str
    descript: str
    secret: bool


achievements: tuple[Achievement, ...] = (
    Achievement('animal', '', 'Сделайте что-то', False),
    Achievement('moon', '', '', False),
    Achievement('food', '', '', False),
    Achievement('rain', '', '', False),
    Achievement('rock', '', '', False),
    Achievement('insight', '', '', False),
    Achievement('tool', '', '', False),
    Achievement('key', '', '', False),
    Achievement('feet', '', '', False),
    Achievement('research', '', '', False),
)


class Player:
    def __init__(self, id: int, name: str) -> None:
        self.id: Final[int] = id
        self.name: Final[str] = name

    def __get_bin(self) -> str:
        with BotBd as bd:
            num: int = bd.get_skins(self.id)
        return bin(num)[2:].zfill(10)  # получаем двоичку из бд '00110'

    def get_skins_unlocked(self) -> list[str]:
        bin01: str = self.__get_bin()
        skins = [achieve.id for achieve in achievements]
        result = []
        for i in range(len(skins)):
            if bin01[i] == '1':
                result.append(skins[i])
        return result

    def achieve_complete(self, a_id: str):
        achieve = next(filter(lambda ach: ach.id == a_id, achievements), None)
        if achieve is None:
            return

        index: int = achievements.index(achieve)
        bin01: str = self.__get_bin()
        bin01 = bin01[:index] + '1' + bin01[index + 1:]

        with BotBd as bd:
            bd.set_skins(self.id, int(bin01, 2))

    def commit_skin(self, bin01: str) -> None:
        with BotBd as bd:
            bd.set_skins(self.id, int(bin01, 2))
