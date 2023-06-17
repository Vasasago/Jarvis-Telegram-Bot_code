import asyncio

from aiogram.utils import executor
import create_bot
import markups

from handlers import callbacks_messages_hands, files_hands, commands_hands

user_id = create_bot.user_id
bot, dp = create_bot.create()


async def on_startup(dp):
    global user_id, bot
    user_id = create_bot.user_id
    if user_id != '':
        create_bot.console += 'Бот запущен!\n'
        await bot.send_message(chat_id=user_id, text="✅ Бот запущен!", reply_markup=markups.main_inline)
        create_bot.flag = True
        run_bot()
    else:
        create_bot.console += '\nChat id не найден.\nНажмите /start, чтобы добавить ID.\n'
        create_bot.flag = True
        run_bot()


async def on_shutdown(dp):
    create_bot.console += 'Бот отключен!\n'
    await bot.send_message(chat_id=user_id, text="📴 Бот отключен!")
    create_bot.flag = False


def run_bot():
    if create_bot.flag:
        commands_hands.commands_handlers_messages(dp)
        files_hands.message_handlers_files(dp)
        callbacks_messages_hands.callbacks_messages_handlers(dp)
    else:
        pass


new_loop = asyncio.new_event_loop()


def start_bot():
    global dp, bot
    try:
        bot, dp = create_bot.create()
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, timeout=10)
    except:
        pass

def stop_bot():
    global dp, new_loop
    try:
        dp.stop_polling()
        new_loop.stop()
        create_bot.flag = False
    except:
        pass

def start():
    global new_loop
    try:
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(start_bot())
        create_bot.flag = True
    except:
        pass
