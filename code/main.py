from typing import Final, Optional

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from CheckerBot.code.Player import Player
from Config import Config
from Game import Game

config: Final[Config] = Config.get()

bot = config.bot
dp = config.dp

games: list[Game] = []
game0 = Game(Player(0, '???'), Player(1, '???'))


async def get_game(callback, game_id: int) -> Optional[Game]:
    game = next(filter(lambda g: g.id == game_id, games), None)
    if game is None:
        await callback.answer('Игры с таким id не существует')
        await bot.edit_message_text(text='Ошибка', inline_message_id=callback.inline_message_id)
        return
    return game


# 2130716911 я
# 802878496 Макс
# 1906460474 Богдан


@dp.message(Command(commands=['start']))
async def start_command(message: Message):
    print(message.from_user.id)
    #await message.answer(game.get_message(), reply_markup=game.get_board())


# @dp.message_reaction()
# async def react(message: MessageReactionUpdated):
#     await message.bot.send_message(message.chat.id, '444')


@dp.inline_query()
async def inline(callback: InlineQuery):
    await callback.answer([
        InlineQueryResultArticle(id='1',
                                 title='Доска игровая будет',
                                 input_message_content=InputTextMessageContent(message_text=game0.get_message()),
                                 reply_markup=game0.get_board())
    ])


@dp.callback_query()
async def callback(callback: CallbackQuery):
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

        if result[1] is not None:
            await callback.answer(result[1])

    else:
        game.choosen_cell = None

    if edit:
        if game.win != -1:
            await bot.edit_message_text(text=f'Победа {game.field.white_skin["name"] if game.win == 0 else game.field.black_skin["name"]}!', inline_message_id=callback.inline_message_id)
        else:
            await bot.edit_message_text(text=game.get_message(), inline_message_id=callback.inline_message_id, reply_markup=game.get_board())
    else:
        await callback.answer()


if __name__ == '__main__':
    # dp.middleware.setup(ThrottlingMiddleware(1))
    print('Бот запущен')
    dp.run_polling(bot, skip_updates=False)
