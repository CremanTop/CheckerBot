from typing import Final, TypedDict


class SkinSet(TypedDict):
    """
    pawn: str \n
    queen: str \n
    choosen_pawn: str \n
    choosen_queen: str \n
    whose: str \n
    name: str \n
    """
    pawn: str
    queen: str
    choosen_pawn: str
    choosen_queen: str
    whose: str
    name: str


def __create_set(pawn: str, queen: str, c_pawn: str, c_queen: str, whose: str, name: str) -> SkinSet:
    return {
        'pawn': pawn,
        'queen': queen,
        'choosen_pawn': c_pawn,
        'choosen_queen': c_queen,
        'whose': whose,
        'name': name
    }


SKINS: Final[dict[str, SkinSet]] = {
    'white': __create_set('⚪', '🤍', '🔴', '❤', 'Белых⚪', 'Белые⚪'),
    'black': __create_set('⚫', '🖤', '🔴', '❤', 'Чёрных⚫', 'Чёрные⚫'),
    'animal': __create_set('🐭', '🐯', '🐹', '🦁', 'Животных🐭', 'Животные🐭'),
    'moon': __create_set('🌑', '🌕', '🌚', '🌝', 'Лун🌚', 'Луны🌚'),
    'food': __create_set('🍏', '🌮', '🍎', '🫔', 'Еды🍏', 'Еда🍏'),
    'rain': __create_set('💧', '🌧', '💦', '🌩', 'Дождя💧', 'Дождь💧'),
    'rock': __create_set('🪨', '⛰', '🗿', '🌋', 'Камней🗿', 'Камни🗿'),
    'insight': __create_set('⚪', '👁️‍', '🔵', '🧿', 'Прозрения⚪', 'Прозрение👁️'),
    'tool': __create_set('🔨', '🗡️', '🛠️', '⚔', 'Инструментов войны🗡️', 'Инструменты войны🗡️'),
    'key': __create_set('🔓', '🔑', '🚪', '🗝️', 'Ключей к победе🔓', 'Ключ к победе🔓'),
    'feet': __create_set('🦵', '🦿', '💪', '🦾', 'Ног в руках🦵', 'Ноги в руки🦵'),
    'research': __create_set('🦠', '🔬', '⭐', '🔭', 'Изучения🦠', 'Изучение🦠'),
    #'food': __create_set('', '', '', '', ''),
}