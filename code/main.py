from typing import Final

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from Config import Config
from Game import Game

config: Final[Config] = Config.get()

bot = config.bot
dp = config.dp

games: list[Game] = [game := Game(1906460474, 1906460474)]


# 2130716911

@dp.message(Command(commands=['start']))
async def start_command(message: Message):
    print(message.from_user.id)
    await message.answer('AAa', reply_markup=game.get_board())


# @dp.message_reaction()
# async def react(message: MessageReactionUpdated):
#     await message.bot.send_message(message.chat.id, '444')

@dp.callback_query()
async def callback(callback: CallbackQuery):
    if callback.data == 'null':
        await callback.answer()
        return

    # if not game.check_click(callback.from_user.id):
    #     await callback.answer('Сейчас не ваш ход!')
    #     return

    edit: bool = True
    if game.choosen_cell != callback.data:
        result = game.click_handler(callback.data)
        edit = result[0]

        if result[1] is not None:
            await callback.answer(result[1])

    else:
        game.choosen_cell = None

    if edit:
        await callback.message.edit_reply_markup(reply_markup=game.get_board())
    else:
        await callback.answer()


if __name__ == '__main__':
    # dp.middleware.setup(ThrottlingMiddleware(1))
    print('Бот запущен')
    dp.run_polling(bot, skip_updates=False)
