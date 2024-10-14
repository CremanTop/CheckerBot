from typing import Final


class Player:
    def __init__(self, id: int, name: str) -> None:
        self.id: Final[int] = id
        self.name: Final[str] = name
