from aiogram.utils import exceptions
from aiogram import Dispatcher
from aiogram.types import Message

import create_bot
import logger


async def errors_handler(update: Message, exception: Exception):
    if isinstance(exception, exceptions.MessageNotModified):
        create_bot.console += f'\nОшибка: не удалось отредактировать сообщение.\n'
        logger.py_logger.error(f"{exception}\n\n")

    elif isinstance(exception, exceptions.NetworkError):
        create_bot.console += f'\nОшибка при попытке подключения к сети.\n'
        logger.py_logger.error(f"{exception}\n\n")

    else:
        create_bot.console += f'\nОшибка: {exception}\n'
        logger.py_logger.error(f"{exception}\n\n")

def register_exceptions(dispatcher: Dispatcher):
    dispatcher.register_errors_handler(errors_handler)