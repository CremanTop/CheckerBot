from typing import Final, TypedDict


class SkinSet(TypedDict):
    """
    pawn: str \n
    queen: str \n
    choosen_pawn: str \n
    choosen_queen: str \n
    name: str \n
    """
    pawn: str
    queen: str
    choosen_pawn: str
    choosen_queen: str
    name: str


def __create_set(pawn: str, queen: str, c_pawn: str, c_queen: str, name: str) -> SkinSet:
    return {
        'pawn': pawn,
        'queen': queen,
        'choosen_pawn': c_pawn,
        'choosen_queen': c_queen,
        'name': name
    }


SKINS: Final[dict[str, SkinSet]] = {
    'white': __create_set('⚪', '🤍', '🔴', '❤', 'Белых⚪'),
    'black': __create_set('⚫', '🖤', '🔴', '❤', 'Чёрных⚫'),
    'animal': __create_set('🐭', '🐯', '🐹', '🦁', 'Животных🐭'),
    'moon': __create_set('🌑', '🌕', '🌚', '🌝', 'Лун🌚'),
    'food': __create_set('🍏', '🌮', '🍎', '🫔', 'Еды🍏'),
    'rain': __create_set('💧', '🌧', '💦', '🌩', 'Дождя💧'),
    'rock': __create_set('🪨', '⛰', '🗿', '🌋', 'Камней🗿')
    #'food': __create_set('', '', '', ''),
}