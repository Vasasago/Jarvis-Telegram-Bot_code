import os
from tkinter import messagebox

import keyboard
import openai
import requests
from aiogram import types, Dispatcher
from colorama import init

import create_bot
import logger
import markups
from create_bot import bot_version

user_id = create_bot.user_id
chatgpt_token = create_bot.chatgpt_token
script_path = create_bot.script_path
config = create_bot.config

openai.api_key = chatgpt_token

bot, dp = create_bot.create()

init()

def copy_bot():
    global bot, dp
    bot, dp = create_bot.create()


def show_error_message(message):
    messagebox.showerror("Ошибка", message)


async def add_downloads_folder(path):
    folder_name = os.path.basename(path)

    if folder_name == "downloads":
        return path
    else:
        downloads_path = os.path.join(path, "downloads")
        return downloads_path


def check_openai_token(token):
    try:
        url = 'https://api.openai.com/v1/dashboard/billing/subscription'
        headers = {
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url, headers=headers)

    except Exception:
        return False

    if response.status_code == 200:
        return True
    else:
        return False


# @dp.message_handler(commands=['start'])
async def start(message: types.Message):
    global user_id
    user_id = create_bot.user_id
    # Если есть User_id, ничего не делаем. Если нет - записываем в файл.
    if create_bot.user_id == '':
        config.set('tg-bot', 'user_id', f'{message.from_user.id}')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            user_id = message.from_user.id
            create_bot.user_id = user_id
            create_bot.console += f'User ID: {str(create_bot.user_id)}\n'

    if str(message.from_user.id) == str(user_id):
        await message.answer("🙋 *Добро пожаловать в бота для вашего личного ассистента Jarvis!*\n\n"
                             f"*Jarvis-Bot V{bot_version}*\n\n"
                             "_Доступные команды:_\n"
                             "🔸 /message \[текст] - отправить текст на ваш компьютер.\n"
                             "🔸 /voice \[текст] - прислать голосовое сообщение с вашим текстом.\n"
                             "🔸 /audio \[текст] - озвучить текст на вашем компьютере.\n"
                             "🔸 /dalle \[текст] - сгенерировать изображение.\n"
                             "🔸 /link \[ссылка] - открыть ссылку в браузере.\n\n"
                             "_Доступные изменения:_\n"
                             "🔸 /set\_cmd\_path \[путь] - изменить путь к командам.\n"
                             "🔸 /set\_downloads\_path \[путь] - изменить путь к загрузкам.\n"
                             "🔸 /set\_gpt\_token \[токен] - изменить токен OpenAI.\n\n"
                             "_При выборе файла в проводнике бота:_\n"
                             "🔸 Запуск файла в приложении по-умолчанию.\n"
                             "🔸 Скачивание файла.",
                             reply_markup=markups.main_inline, parse_mode="Markdown")

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# @dp.message_handler(commands=['message'])
async def message_com(message: types.Message):
    global user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text.replace('/message', "").lstrip() == '':
            await message.answer("❗ Текст не был введён!", reply_markup=markups.main_inline)

        else:
            keyboard.write(message.text.replace('/message', "").lstrip())
            await message.answer("✅ Текст отправлен!", reply_markup=markups.main_inline)

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# @dp.message_handler(commands=['voice'])
async def voice_com(message: types.Message):
    global user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text.replace('/voice', "").lstrip() == '':
            await message.answer("❗ Текст не был введён!", reply_markup=markups.main_inline)

        else:
            create_bot.console += f'voice: {message.text.replace("/voice", "").lstrip()}\n'

            create_bot.edit_msg = await bot.send_message(chat_id=user_id, text='🗣 Выберите голос для озвучки:',
                                                         reply_markup=markups.voice_markup)

            create_bot.text_to_speech = message.text.replace('/voice', "").lstrip()

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# @dp.message_handler(commands=['audio'])
async def audio_com(message: types.Message):
    global user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text.replace('/audio', "").lstrip() == '':
            await message.answer("❗ Текст не был введён!", reply_markup=markups.main_inline)

        else:
            create_bot.console += f'audio: {message.text.replace("/audio", "").lstrip()}\n'

            create_bot.edit_msg = await bot.send_message(chat_id=user_id, text='🗣 Выберите голос для озвучки:',
                                                         reply_markup=markups.audio_markup)

            create_bot.text_to_speech = message.text.replace('/audio', "").lstrip()

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# @dp.message_handler(commands=['dalle'])
async def send_image(message: types.Message):
    global user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text.replace('/dalle', "").lstrip() != '':
            create_bot.edit_msg = await message.answer("⏳ Ваш запрос отправлен.")
            create_bot.console += f'DALL-E: {message.text.replace("/dalle", "").lstrip()}\n'
            try:
                response = openai.Image.create(
                    prompt=message.text.replace('/dalle', "").lstrip(),
                    n=1,
                    size="1024x1024",
                )
                await message.answer_photo(response["data"][0]["url"])
                await bot.delete_message(chat_id=user_id, message_id=create_bot.edit_msg.message_id)

            except openai.error.TryAgain as e:
                create_bot.console += f'\nОшибка dall-e: {e}\n'
                show_error_message(f'Ошибка dall-e: {e}')
                logger.logging_func(e)

                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='🫡Не удалось выполнить запрос. Попробуйте снова.')

            # Обработка других исключений openai.error
            except Exception as e:
                create_bot.console += f'\nОшибка dall-e: {e}\n'
                show_error_message(f'Ошибка dall-e: {e}')
                logger.logging_func(e)

                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='🫡Не удалось выполнить запрос. Подробнее читайте в Консоли.')

        else:
            await message.answer("❗ Запрос не найден.")

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# @dp.message_handler(commands=['set_cmd_path'])
async def set_cmd_path(message: types.Message):
    global user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text.replace('/set_cmd_path', "").lstrip() == '':
            await bot.send_message(chat_id=user_id, text=f'❗ Путь не найден.')

        else:
            path = message.text.replace('/set_cmd_path', "").lstrip()
            # Проверка, есть ли папка commands в конце пути
            all_path = os.path.join(path, 'commands')
            if os.path.isdir(all_path):
                create_bot.console += f'set_cmd_path: {path}\\commands.\n'

                create_bot.root_folder = path + '\\commands'
                config.set('tg-bot', 'commands_folder', f'{create_bot.root_folder}')

                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                await bot.send_message(chat_id=user_id, text=f'✅ Путь обновлён.\nНовый путь: {create_bot.root_folder}')

            elif path.split('\\')[-1] == 'commands':

                create_bot.console += f'set_cmd_path: {path}.\n'

                create_bot.root_folder = path
                config.set('tg-bot', 'commands_folder', f'{create_bot.root_folder}')

                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                await bot.send_message(chat_id=user_id, text=f'✅ Путь обновлён.\nНовый путь: {create_bot.root_folder}')

            else:
                if os.path.exists(path):
                    await message.answer("❗ Папка commands отсутствует в указанном пути.")

                else:
                    await message.answer("❗ Указанный путь не существует.")

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# @dp.message_handler(commands=['set_gpt_token'])
async def set_gpt_token(message: types.Message):
    global chatgpt_token, user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text.replace('/set_gpt_token', "").lstrip() == '':
            await bot.send_message(chat_id=user_id, text=f'❗ Токен не найден.')

        else:
            token = message.text.replace('/set_gpt_token', "").lstrip()
            if check_openai_token(token):
                create_bot.console += f'set_gpt_token: {token}\n'

                create_bot.chatgpt_token = token
                chatgpt_token = create_bot.chatgpt_token
                config.set('tg-bot', 'chatgpt_token', f'{chatgpt_token}')

                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                await bot.send_message(chat_id=user_id, text=f'✅ Токен обновлён.\nНовый токен: {chatgpt_token}')
            else:
                await message.answer("❗ Токен недействителен.")

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# @dp.message_handler(commands=['set_downloads_path'])
async def set_downloads_path(message: types.Message):
    global user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text.replace('/set_downloads_path', "").lstrip() == '':
            await bot.send_message(chat_id=user_id, text=f'❗ Путь не найден.')

        else:
            path = message.text.replace('/set_downloads_path', "").lstrip()

            if path.split('\\')[-1] == 'downloads':
                create_bot.console += f'set_downloads_path: {path}\n'

                create_bot.script_path = path

                config.set('tg-bot', 'downloads_path', f'{await add_downloads_folder(create_bot.script_path)}')

                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                await bot.send_message(chat_id=user_id,
                                       text=f'✅ Путь к загрузкам обновлён.\nНовый путь: {create_bot.script_path}')

            else:
                create_bot.console += f'set_downloads_path: {path}\\downloads.\n'

                create_bot.script_path = path + '\\downloads'
                config.set('tg-bot', 'downloads_path', f'{await add_downloads_folder(create_bot.script_path)}')

                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                await bot.send_message(chat_id=user_id, text=f'✅ Путь к загрузкам обновлён.\nНовый путь:'
                                                             f' {create_bot.script_path}')

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


def commands_handlers_messages(dp: Dispatcher):
    try:
        dp.register_message_handler(start, commands=['start'])
        dp.register_message_handler(message_com, commands=['message'])
        dp.register_message_handler(voice_com, commands=['voice'])
        dp.register_message_handler(audio_com, commands=['audio'])
        dp.register_message_handler(send_image, commands=['dalle'])
        dp.register_message_handler(set_cmd_path, commands=['set_cmd_path'])
        dp.register_message_handler(set_gpt_token, commands=['set_gpt_token'])
        dp.register_message_handler(set_downloads_path, commands=['set_downloads_path'])
    except:
        pass
