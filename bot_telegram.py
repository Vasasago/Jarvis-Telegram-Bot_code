import asyncio

from aiogram.utils import executor
import create_bot
import logger
import markups

from handlers import callbacks_messages_hands, files_hands, commands_hands, exceptions_hands, state_shutdown

bot, dp = create_bot.create()

bot_loop = asyncio.new_event_loop()

# При старте
async def on_startup(dp):
    user_id = create_bot.user_id
    if user_id != '':
        create_bot.console += 'Start polling...\n'
        await bot.send_message(chat_id=user_id, text="✅ Бот запущен!", reply_markup=markups.main_inline)
        create_bot.flag = True
        start_register_handlers()
    else:
        create_bot.console += '\nUser id не найден.\nНажмите /start, чтобы добавить ID.\n'
        create_bot.flag = True
        start_register_handlers()


# При отключении
async def on_shutdown(dp):
    user_id = create_bot.user_id
    create_bot.console += 'Stop polling...\n'
    await bot.send_message(chat_id=user_id, text="📴 Бот отключен!")
    create_bot.flag = False


# Вызов регистраторов хендлеров
def start_register_handlers():
    if create_bot.flag:
        commands_hands.copy_bot()
        callbacks_messages_hands.copy_bot()
        files_hands.copy_bot()

        state_shutdown.states(dp)
        commands_hands.commands_handlers_messages(dp)
        files_hands.message_handlers_files(dp)
        callbacks_messages_hands.callbacks_messages_handlers(dp)
        exceptions_hands.register_exceptions(dp)


# Остановка поллинга
def stop_bot():
    try:
        dp.stop_polling()
        bot_loop.stop()
        create_bot.flag = False

    except Exception as e:
        logger.py_logger.error(f"{e}\n\n")


# Начало поллинга
def start():
    global dp, bot

    bot, dp = create_bot.create()

    try:
        # Если бот создан, запускаем поллинг
        if bot is not None and dp is not None:
            asyncio.set_event_loop(bot_loop)
            bot_loop.create_task(executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown, timeout=30))
            bot_loop.run_forever()

            create_bot.flag = True
    except Exception as e:
        logger.py_logger.error(f"{e}\n\n")