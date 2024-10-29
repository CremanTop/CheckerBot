from typing import Final, Optional

from CheckerBot.code.Achievement import achievements, get_achieve
from CheckerBot.code.Config import Config

config: Final[Config] = Config.get()
BotBd = config.Bot_db


class Player:
    def __init__(self, id: int, name: str) -> None:
        self.id: Final[int] = id
        self.name: Final[str] = name

    def __get_bin(self) -> str:
        with BotBd as bd:
            num: int = bd.get_skins(self.id)
        return bin(num)[2:].zfill(10)  # получаем двоичку из бд '00110'

    def get_skin(self) -> Optional[str]:
        with BotBd as bd:
            skin: str = bd.get_choosen_skin(self.id)
        return skin

    def set_skin(self, skin: Optional[str]) -> None:
        with BotBd as bd:
            bd.set_choosen_skin(self.id, skin)

    def get_wins(self) -> int:
        with BotBd as bd:
            win: int = bd.get_wins(self.id)
        return win

    def win_increment(self) -> None:
        with BotBd as bd:
            bd.win_increment(self.id)

    def get_skins_unlocked(self) -> list[str]:
        bin01: str = self.__get_bin()
        skins = [achieve.id for achieve in achievements]
        result = []
        for i in range(len(skins)):
            if bin01[i] == '1':
                result.append(skins[i])
        return result

    def achieve_complete(self, a_id: str):
        achieve = get_achieve(a_id)
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
