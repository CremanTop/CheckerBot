from typing import Final, TypedDict


class SkinSet(TypedDict):
    """
    pawn: str\n
    queen: str\n
    choosen_pawn: str\n
    choosen_queen: str\n
    """
    pawn: str
    queen: str
    choosen_pawn: str
    choosen_queen: str


def __create_set(pawn: str, queen: str, c_pawn: str, c_queen: str) -> SkinSet:
    return {
        'pawn': pawn,
        'queen': queen,
        'choosen_pawn': c_pawn,
        'choosen_queen': c_queen
    }


SKINS: Final[dict[str, SkinSet]] = {
    'white': __create_set('⚪', '🤍', '🔴', '❤'),
    'black': __create_set('⚫', '🖤', '🔴', '❤'),
    'animal': __create_set('🐭', '🐯', '🐹', '🦁'),
    'moon': __create_set('🌑', '🌕', '🌚', '🌝'),
    'food': __create_set('🍏', '🌮', '🍎', '🫔'),
    'rain': __create_set('💧', '🌧', '💦', '🌩'),
    'rock': __create_set('🪨', '⛰', '🗿', '🌋')
    #'food': __create_set('', '', '', ''),
}