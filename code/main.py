import asyncio
from typing import Final, Optional

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from CheckerBot.code.Achievement import get_achieve, Achievement
from CheckerBot.code.Player import Player
from CheckerBot.code.Skins import SkinSet, SKINS
from Config import Config
from Game import Game

config: Final[Config] = Config.get()

bot = config.bot
dp = config.dp
BotDB = config.Bot_db

games: list[Game] = []
game0 = Game(Player(0, '???'), Player(1, '???'))


async def get_game(callback, game_id: int) -> Optional[Game]:
    game = next(filter(lambda g: g.id == game_id, games), None)
    if game is None:
        await callback.answer('Игры с таким id не существует')
        await bot.edit_message_text(text='Ошибка', inline_message_id=callback.inline_message_id)
        return
    return game


def get_achievement_message(achieves: list[str]) -> str:
    result: str = f'Получен{"о" if len(achieves) == 1 else "ы"} достижени{"е" if len(achieves) == 1 else "я"}!\n'
    for ach_id in achieves:
        achieve: Achievement = get_achieve(ach_id)
        skin: SkinSet = SKINS[achieve.id]
        result += f'{achieve.name}{skin["emoji"]}: {achieve.descript}\n\n'

    return result[:-2]


def player_init(user_id: int):
    with BotDB as db:
        if not db.user_exists(user_id):
            db.add_user(user_id, 0)


async def achieve_handler(callback: CallbackQuery, player: Player, achi_s: list[str], only: bool) -> None:
    achi_s = list(set(achi_s) - set(player.get_skins_unlocked()))
    if len(achi_s) == 0:
        return

    text = get_achievement_message(achi_s)

    for res in achi_s:
        player.achieve_complete(res)

    if only:
        await callback.answer(text)
    await bot.send_message(player.id, text=text)


@dp.message(Command(commands=['start']))
async def start_command(message: Message):
    player_init(message.from_user.id)
    print(message.from_user.id)
    #await message.answer(game.get_message(), reply_markup=game.get_board())


# @dp.message_reaction()
# async def react(message: MessageReactionUpdated):
#     await message.bot.send_message(message.chat.id, '444')


@dp.inline_query()
async def inline(callback: InlineQuery):
    player_init(callback.from_user.id)
    await callback.answer([
        InlineQueryResultArticle(id='1',
                                 title='Доска игровая будет',
                                 input_message_content=InputTextMessageContent(message_text=game0.get_message()),
                                 reply_markup=game0.get_board())
    ])


@dp.callback_query()
async def callback(callback: CallbackQuery):
    player_init(callback.from_user.id)

    if callback.data == 'null':
        await callback.answer()
        return

    board_id = callback.data[:callback.data.index('_')]
    cell_id = callback.data[callback.data.index('_') + 1:]

    if board_id == '0':
        game = Game(Player(callback.from_user.id, callback.from_user.first_name), Player(-1, '???'))
        games.append(game)
    else:
        game = await get_game(callback, int(board_id))
        if game is None:
            return

    if game.players[1].id == -1 and game.move == 1 and callback.from_user.id != game.players[0].id:
        game.players = [game.players[0], Player(callback.from_user.id, callback.from_user.first_name)]

    if not game.check_click(callback.from_user.id):
        await callback.answer('Сейчас не ваш ход!')
        return

    edit: bool = True
    if game.choosen_cell != cell_id:
        result = game.click_handler(cell_id)
        edit = result[0]

        match result[1]:
            case str() as mes:
                await callback.answer(mes)
            case list() as achi_s:
                player = game.players[0] if game.players[0].id == callback.from_user.id else game.players[1]
                await achieve_handler(callback, player, achi_s, True)
            case _:
                pass

    else:
        game.choosen_cell = None

    if edit:
        if game.win != -1:
            await bot.edit_message_text(text=f'Победа {game.field.white_skin["whose"] if game.win == 0 else game.field.black_skin["whose"]}!', inline_message_id=callback.inline_message_id)

            async with asyncio.TaskGroup() as tg:
                for i in (0, 1):
                    results: list[str] = []
                    player_i = game.players[i]
                    opponent = game.players[(i + 1) % 2]

                    have_figure_opponent: bool = False
                    if i == game.win:
                        _, have_figure_opponent = game.can_move((i + 1) % 2)
                        player_i.win_increment()
                        if player_i.get_wins() >= 3:
                            results.append('moon')

                    results += game.ach_counter.end_game(i, i == game.win, have_figure_opponent=have_figure_opponent)
                    with BotDB as bbd:
                        if opponent.id in [admin[0] for admin in bbd.get_users()[:2]]:
                            results.append('research')

                    tg.create_task(achieve_handler(callback, player_i, results, False))
        else:
            await bot.edit_message_text(text=game.get_message(), inline_message_id=callback.inline_message_id, reply_markup=game.get_board())
    else:
        await callback.answer()


if __name__ == '__main__':
    # dp.middleware.setup(ThrottlingMiddleware(1))
    print('Бот запущен')
    with BotDB as bd:
        for user in bd.get_users():
            print(user)
            player = Player(user[0], 're')
            print(player.get_skins_unlocked())
    dp.run_polling(bot, skip_updates=False)
