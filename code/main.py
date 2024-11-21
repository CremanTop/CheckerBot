import asyncio
from typing import Final, Optional

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardButton, InlineKeyboardMarkup

from CheckerBot.code.achievement import get_achieve, Achievement, achievements
from CheckerBot.code.assessor import FieldAssessor
from CheckerBot.code.player import Player
from CheckerBot.code.skins import SkinSet, SKINS
from CheckerBot.code.virtualplayer import VirtualPlayer
from config import Config
from game import Game

config: Final[Config] = Config.get()

bot = config.bot
dp = config.dp
BotDB = config.Bot_db

games: list[Game] = []
game0 = Game(Player(0, '???'), Player(1, '???'))


async def get_game(callback, game_id: int) -> Optional[Game]:
    game = next(filter(lambda g: g.id == game_id, games), None)
    if game is None:
        await callback.answer('Игры с таким id не существует или она завершена')
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
    await message.answer(game0.get_message(), reply_markup=game0.get_board())


@dp.message(Command(commands=['skin']))
async def skin_command(message: Message):
    player_init(message.from_user.id)

    player_this: Player = Player(message.from_user.id, 'Name')
    skins_unlocked: list[str] = player_this.get_skins_unlocked()
    result: list[str] = []
    buttons: list[list[InlineKeyboardButton]] = []
    i = 1
    for ach in achievements:
        string: str = f'{i}) '
        lock: str = '✅' if ach.id in skins_unlocked else '❌'
        if ach.secret and ach.id not in skins_unlocked:
            string += '???'
        else:
            string += f'{ach.name}: {ach.descript[:-1]}'

        if ach.id == 'moon':
            string += f' ({player_this.get_wins()}/3)'

        string += f' - {lock}'
        result.append(string)

        if ach.id in skins_unlocked:
            skin = SKINS[ach.id]
            buttons.append([InlineKeyboardButton(text=f'{i}) {skin["name"]}', callback_data=f'skin_{ach.id}')])

        i += 1
    rejoin = '\n'.join(result)

    await message.answer(text=f'Вы можете получать новые скины, выполняя достижения! \n\nСписок достижений:\n{rejoin}', reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


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


async def move_reaction(callback: CallbackQuery, edit: bool, game: Game):
    if callback.inline_message_id is not None:
        kwargs = {'inline_message_id': callback.inline_message_id}
    elif callback.message.message_id is not None:
        kwargs = {'message_id': callback.message.message_id,
                  'chat_id': callback.message.chat.id}

    if edit:
        if game.win in (0, 1):
            game.id = -1
            await bot.edit_message_text(text=f'{game.screen_players()}Победа {game.field.white_skin["whose"] if game.win == 0 else game.field.black_skin["whose"]}!', reply_markup=game.get_board(), **kwargs)

            async with asyncio.TaskGroup() as tg:
                for i in (0, 1):
                    results: list[str] = []
                    player_i = game.players[i]
                    opponent = game.players[(i + 1) % 2]

                    have_figure_opponent: bool = False
                    if i == game.win:
                        _, have_figure_opponent = game.can_move((i + 1) % 2)
                        if not player_i.is_virtual():
                            player_i.win_increment()
                            if player_i.get_wins() >= 3:
                                results.append('moon')

                    results += game.ach_counter.end_game(i, i == game.win, have_figure_opponent=have_figure_opponent)
                    if opponent.id in (2130716911, 1906460474):
                        results.append('research')

                    if not player_i.is_virtual():
                        tg.create_task(achieve_handler(callback, player_i, results, False))
            games.remove(game)

        elif game.win == 2:
            game.id = -1
            async with asyncio.TaskGroup() as tg:
                for player in game.players:
                    if player.is_virtual():
                        continue
                    player.draw_increment()
                    if player.get_draws() >= 3:
                        tg.create_task(achieve_handler(callback, player, ['rock'], False))
            await bot.edit_message_text(text=f'{game.screen_players()}Ничья! 🤝', reply_markup=game.get_board(), **kwargs)
            games.remove(game)

        else:
            await bot.edit_message_text(text=game.get_message(), reply_markup=game.get_board(), **kwargs)

            while game.move == 1:
                vp = VirtualPlayer(1)
                vp.excluded_di = game.excluded_queen_direction
                move, cut = await vp.get_strongest_move(game.field, one_cut=game.one_cut)
                game.choosen_cell = move.cfrom
                await asyncio.sleep(0.4)
                game.move_attempt(move.cwhere)
                await bot.edit_message_text(text=game.get_message(), reply_markup=game.get_board(), **kwargs)
                if game.win != -1:
                    await move_reaction(callback, True, game)
    else:
        await callback.answer()


@dp.callback_query()
async def callback(callback: CallbackQuery):
    player_init(callback.from_user.id)

    if callback.data == 'null':
        await callback.answer()
        return

    board_id = callback.data[:callback.data.index('_')]
    cell_id = callback.data[callback.data.index('_') + 1:]

    if board_id == 'skin':
        Player(callback.from_user.id, callback.from_user.first_name).set_skin(cell_id)
        await bot.answer_callback_query(callback.id, text=f'Вы выбрали набор скинов\n{SKINS[cell_id]["name"]}', show_alert=True)
        return

    if board_id == '0':
        game = Game(Player(callback.from_user.id, callback.from_user.first_name), Player(-1, '???'))
        # game.field.load_from_string('ww0w,w0ww,0ww0,b000,00w0,b00b,bb0b,00bb')
        # game.field.load_from_string('0000,0000,b000,0W00,0b00,0000,0000,0000')
        games.append(game)
    else:
        game = await get_game(callback, int(board_id))
        if game is None:
            return

    if game.players[1].id == -1 and game.move == 1 and callback.from_user.id != game.players[0].id:
        player2: Player = Player(callback.from_user.id, callback.from_user.first_name)
        game.players = [game.players[0], player2]
        game.field.skin_update(player2.get_skin() if player2.get_skin() is not None else 'black')

    if not game.check_click(callback.from_user.id):
        if cell_id == 'draw':  # предлагать ничью можно только не в свой ход
            if (game.players[1] if game.players[0].id == callback.from_user.id else game.players[0]).is_virtual():
                await callback.answer('Нельзя предложить ничью боту.')
            else:
                game.is_draw_offered = not game.is_draw_offered
                await move_reaction(callback, True, game)
        else:
            await callback.answer('Сейчас не ваш ход!')
        return

    if cell_id == 'draw':  # а тут приём ничьи в свой ход
        if not game.is_draw_offered:
            await bot.answer_callback_query(callback.id, text='Отправить предложение ничьи можно только не в свой ход.', show_alert=True)
        else:
            game.win = 2
            await move_reaction(callback, True, game)
        return

    player = game.players[0] if game.players[0].id == callback.from_user.id else game.players[1]

    if cell_id == 'surrender':
        game.win = (game.players.index(player) + 1) % 2
        await move_reaction(callback, True, game)
        return

    edit: bool = True
    if game.choosen_cell != cell_id:
        if game.is_draw_offered:
            game.is_draw_offered = False
            await callback.answer('Вы отклонили предложение ничьи')
        result = game.click_handler(cell_id)
        edit = result[0]

        print(round(FieldAssessor(game.field).pos_assesment(0), 2))

        match result[1]:
            case str() as mes:
                await callback.answer(mes)
            case list() as achi_s:
                if not player.is_virtual():
                    await achieve_handler(callback, player, achi_s, True)
            case _:
                pass

    else:
        game.choosen_cell = None

    await move_reaction(callback, edit, game)


if __name__ == '__main__':
    # dp.middleware.setup(ThrottlingMiddleware(1))
    print('Бот запущен')
    dp.run_polling(bot, skip_updates=False)
