import math
import os
import subprocess
import sys
import tempfile
import webbrowser
from tkinter import messagebox
from urllib.parse import urlparse

import keyboard
import openai
import psutil
from PIL import ImageGrab
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import create_bot
import logger
import markups
import tts
import speech_recognition as sr

max_tokens = create_bot.max_tokens
text_to_gpt = create_bot.text_to_gpt
output_file = create_bot.output_file
current_path = create_bot.current_path
page_number = create_bot.page_number
pages = create_bot.pages
drives_in = create_bot.drives_in
user_id = create_bot.user_id
names_drives = create_bot.names_drives
bot_version = create_bot.bot_version
gpt_model = create_bot.gpt_model
folders_names = create_bot.folders_names
root_folder = create_bot.root_folder
text_to_speech = create_bot.text_to_speech

name_folder = ''

bot, dp = create_bot.create()

recognizer = sr.Recognizer()


def copy_bot():
    global bot, dp
    bot, dp = create_bot.create()


def show_error_message(message):
    messagebox.showerror("Ошибка", message)


async def explore_disks(update=False):
    global user_id
    user_id = create_bot.user_id
    # Получаем список дисков, записываем в drives_in и создаём инлайн - кнопки
    drives = psutil.disk_partitions()
    drives_in.clear()

    for drive in drives:
        try:
            drive_usage = psutil.disk_usage(drive.mountpoint)

            if drive_usage.total > 0:
                drives_in.append(InlineKeyboardButton(drive.device, callback_data=drive.device))

        except Exception:
            pass

    drives_markup = InlineKeyboardMarkup(row_width=2).add(*drives_in)

    if update is False:
        create_bot.edit_msg = await bot.send_message(chat_id=user_id, text=f'📂 Проводник\n💿 Выберите диск:',
                                                     reply_markup=drives_markup)

    else:
        await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                    text=f'📂 Проводник\n💿 Выберите диск:',
                                    reply_markup=drives_markup)

    names_drives.clear()

    for name in drives_in:
        names_drives.append(name['callback_data'])


async def description():
    global user_id
    user_id = create_bot.user_id
    await bot.send_message(chat_id=user_id,
                           text=f"*Jarvis-Bot V{bot_version}*\n\n"
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
                           reply_markup=markups.service_markup, parse_mode="Markdown")


def is_url(text):
    parsed = urlparse(text)
    return parsed.scheme and parsed.netloc


# Обработчик текста
# @dp.message_handler()
async def messages(message: types.Message):
    global max_tokens, text_to_gpt, current_path, user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        if message.text == '🤖 Команды Jarvis':
            await bot.send_message(chat_id=user_id, text='📂 Выберите папку:',
                                   reply_markup=markups.open_commands())
        elif message.text == '⌨ Клавиатура':
            await bot.send_message(chat_id=user_id, text='⌨ Клавиатура\nВыберите действие:',
                                   reply_markup=markups.keyboard_inline)

        elif message.text == '📂 Проводник':
            await explore_disks()

        elif message.text == '🛠 Управление ботом':
            await description()

        elif message.text == '🖥 Программы':
            current_path = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\lnk'
            result = await explorer_func(number='', query_id='0')

            if result is not None and pages >= 1:
                folder, buttons = result
                await bot.send_message(chat_id=user_id, text=f'🖥 Программы:',
                                       reply_markup=buttons)

            else:
                await bot.send_message(chat_id=user_id, text=f'🖥 В данной папке нет программ.'
                                                             f' Добавьте их ярлыки или сами программы'
                                                             f' в папку lnk по этому пути:\n'
                                                             f'{current_path}', reply_markup=markups.open_lnk_markup)

        elif is_url(message.text):
            create_bot.console += f'link: {message.text}\n'
            await message.answer("✅ Ссылка отправлена!", reply_markup=markups.main_inline)
            webbrowser.open(url=message.text)

        else:
            create_bot.edit_msg = await message.answer("⏳ Ваш запрос отправлен.")

            response = '🤖 Jarvis:\n'

            max_tokens = int(max_tokens - len(text_to_gpt) * 1.3)

            if max_tokens <= 0:
                text_to_gpt = message.text + '.'
                max_tokens = int(max_tokens - len(text_to_gpt) * 1.3)
                response += '❗ Достигнут лимит токенов. История была очищена.\n'

            close_dialog_btn = InlineKeyboardButton('✖ Закончить диалог', callback_data='close_dialog')
            gpt_markup = InlineKeyboardMarkup(row_width=1).add(close_dialog_btn)

            try:
                create_bot.console += f'ChatGPT: {message.text}.\n'

                completion = openai.ChatCompletion.create(model=gpt_model,
                                                          messages=[{"role": "user", "content": text_to_gpt},
                                                                    {"role": "user", "content": message.text + '.'}])

                response += completion.choices[0].message.content

                text_to_gpt += ('\n' + message.text + '.' + '\n' + response)

                create_bot.edit_msg = await bot.edit_message_text(chat_id=user_id,
                                                                  message_id=create_bot.edit_msg.message_id,
                                                                  text=response, reply_markup=gpt_markup)

                response = ''

            except openai.error.TryAgain as e:
                create_bot.console += f'\nОшибка gpt: {e}\n\n'
                show_error_message(f'\nОшибка gpt: {e}')
                logger.logging_func(e)

                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='🫡Не удалось выполнить запрос. Попробуйте снова.')

            # Обработка других исключений openai.error
            except Exception as e:
                create_bot.console += f'\nОшибка gpt: {e}\n\n'
                show_error_message(f'\nОшибка gpt: {e}')

                logger.logging_func(e)

                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='🫡Не удалось выполнить запрос. Подробнее читайте в Консоли.')

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


async def recognition(lang):
    global output_file, user_id
    user_id = create_bot.user_id

    create_bot.edit_msg = await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                                      text=f'⏳ Идёт распознавание.')

    if lang == 'RU-ru':
        lang_sticker = '🇷🇺'
    elif lang == 'UK-uk':
        lang_sticker = '🇺🇦'
    else:
        lang_sticker = '🇺🇸'

    try:
        with sr.AudioFile(output_file) as audio:
            audio_data = recognizer.record(audio)
            text = recognizer.recognize_google(audio_data, language=lang)
            create_bot.console += f'speech to text: {text}\n'

            await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                        text=f'📝{lang_sticker}Распознанный текст:\n{text}.')

    except sr.exceptions.UnknownValueError:
        create_bot.console += '\nОшибка при распознавании голосового сообщения.\n\n'
        show_error_message('Ошибка при распознавании голосового сообщения.')

        await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                    text=f'🫡При распознавании возникла ошибка.')

    except Exception as e:
        create_bot.console += f'\nОшибка при распознавании голосового сообщения: {e}\n\n'
        show_error_message(f'\nОшибка при распознавании голосового сообщения: {e}')

    os.remove(output_file)


# Проводник: переходим по пути и генерируем Inline кнопки с названиями папок и файлов
async def explorer_func(number, page=1, items_per_page=20, query_id=''):
    global current_path, name_folder, page_number, pages, user_id
    user_id = create_bot.user_id

    page_number = page

    if number == '':  # Если имя папки не задано
        for name in names_drives:
            if current_path.replace('\\', '') in name.replace('\\', ''):
                current_path = current_path.replace('\\', '') + '\\'
                break
            else:
                current_path = current_path
                break

    elif current_path in names_drives:  # Если директория корневая (начало одного из дисков)
        name = folders_names.get(number)
        current_path += f'{name}'
    else:
        name = folders_names.get(number)
        current_path += f'\\{name}'

    try:
        direct = os.listdir(current_path)  # Получаем список папок по пути

        folders = []

        for folder in direct:
            if folder[0] != '.' and folder[0] != '$':
                folders.append(folder)

        create_bot.console += f'directory: {current_path} page: {page_number}\n'

        # Рассчитываем начальный и конечный индексы для текущей страницы
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page

        pages = math.ceil((len(folders) / items_per_page))

        inline_folders = []
        folders_names.clear()

        i = 0

        # Создаем список с Inline-кнопками только для элементов на текущей странице
        for folder in folders[start_index:end_index]:
            if query_id == '0' or 'lnk' in folder or ' - Ярлык.lnk' in folder:
                name_folder = folder.replace('.lnk', '').replace('.exe', '')

            elif folder.lower() == 'пользователи' or folder.lower() == '%1$d пользователей':
                name_folder = 'Users'

            else:
                name_folder = folder

            if len(name_folder) > 20:
                name_folder = name_folder[:10] + '...' + name_folder[-10:]

            inline_folders.append(InlineKeyboardButton(f'{name_folder}', callback_data=str(i)))
            folders_names[str(i)] = folder
            i += 1

        folders_markup = InlineKeyboardMarkup(row_width=2).add(*inline_folders)

        # Добавляем кнопки для переключения между страницами
        previous_button = InlineKeyboardButton('◀ Предыдущая страница', callback_data='previous_page')
        next_button = InlineKeyboardButton('Следующая страница ▶', callback_data='next_page')

        if page == 1 and pages > 1:
            folders_markup.row(next_button)
        elif end_index >= len(folders) and pages > 1:
            folders_markup.row(previous_button)
        elif pages <= 1:
            pass
        else:
            folders_markup.row(previous_button, next_button)

        if query_id != '0':
            if current_path in names_drives:
                go_back_to_drives = InlineKeyboardButton('◀ К дискам', callback_data='back_to_drives')
                folders_markup.row(go_back_to_drives)
            else:
                go_back_to_drives = InlineKeyboardButton('◀ К дискам', callback_data='back_to_drives')
                go_back_explorer = InlineKeyboardButton('◀ Назад', callback_data='back_explorer')
                folders_markup.row(go_back_explorer, go_back_to_drives)

        if query_id != '0':
            await bot.answer_callback_query(callback_query_id=query_id)

        return current_path, folders_markup  # Возвращаем путь и Маркапы

    except PermissionError as e:
        create_bot.console += f'\nОшибка explorer_func: {e}\n\n'
        show_error_message(f'Ошибка explorer_func: {e}')
        logger.logging_func(e)

        await bot.answer_callback_query(callback_query_id=query_id, text="❗ Отказано в доступе.", show_alert=True)
        current_path = os.path.dirname(current_path)

    except FileNotFoundError as e:
        create_bot.console += f'\nОшибка explorer_func: {e}\n\n'
        show_error_message(f'Ошибка explorer_func: {e}')
        logger.logging_func(e)

        await bot.answer_callback_query(callback_query_id=query_id, text="❗ Устройство не найдено.", show_alert=True)
        await explore_disks(True)

    except Exception as e:
        create_bot.console += f'\nОшибка explorer_func: {e}\n\n'
        show_error_message(f'Ошибка explorer_func: {e}')
        logger.logging_func(e)

        await bot.answer_callback_query(callback_query_id=query_id, text="❗ Произошла ошибка.", show_alert=True)
        await explore_disks(True)


# Обработчик CallBacks
# @dp.callback_query_handler()
async def handle_callback(callback_query: types.CallbackQuery):
    global current_path, page_number, pages, text_to_gpt, file_name, user_id
    user_id = create_bot.user_id

    if str(callback_query.from_user.id) == str(user_id):

        command = callback_query.data
        names_dict = {}

        def read_text_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                return lines

            except Exception as e:
                logger.logging_func(e)

        def scan_folders(root_folder):
            exe_files = {}
            for foldername, subfolders, filenames in os.walk(root_folder):
                if foldername.endswith("ahk"):
                    for filename in filenames:
                        if filename.endswith(".exe"):
                            exe_path = os.path.join(foldername, filename)
                            exe_files[filename] = exe_path
            return exe_files

        folders = os.listdir(root_folder)

        if folders:
            for foldername, subfolders, filenames in os.walk(root_folder):
                for filename in filenames:
                    if filename == "names.txt":
                        file_path = os.path.join(foldername, filename)
                        lines = read_text_file(file_path)
                        if lines:
                            for line in lines:
                                line = line.strip()
                                names_dict[line.split(':')[1]] = line.split(':')[0]

        exe_files = scan_folders(root_folder)

        if command.startswith('folder:'):
            await bot.answer_callback_query(callback_query.id)
            folder_name = command.split(':')[1]
            subfolder_path = os.path.join(root_folder, folder_name, 'ahk')
            exe_files = scan_folders(subfolder_path)

            if exe_files:
                global files
                files = []
                files.clear()
                for filename in exe_files.keys():
                    for key, val in names_dict.items():
                        if str(filename.split('.')[0]) == key:
                            files.append(InlineKeyboardButton(val, callback_data=filename))
                        elif str(filename.split('.')[0]) not in names_dict.keys():
                            if InlineKeyboardButton(filename, callback_data=filename) not in files:
                                files.append(InlineKeyboardButton(filename, callback_data=filename))

                inline_files = InlineKeyboardMarkup(row_width=2).add(*files, InlineKeyboardButton('🔙 Вернуться назад',
                                                                                                  callback_data=
                                                                                                  'commands'))
                await bot.edit_message_text(chat_id=user_id,
                                            message_id=callback_query.message.message_id,
                                            text=f'📂 Текущая папка: {folder_name}.\nВыберите действие:',
                                            reply_markup=inline_files)
            else:
                await bot.edit_message_text(chat_id=user_id,
                                            message_id=callback_query.message.message_id,
                                            text='✖ В данной папке нет файлов.', reply_markup=markups.open_commands())

        if command == 'commands':
            await bot.answer_callback_query(callback_query.id)
            await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                        text='📂 Выберите папку:', reply_markup=markups.open_commands())

        if command in names_drives:
            current_path = command
            try:
                result = await explorer_func(number='', query_id=callback_query.id)

                if result is not None:
                    folder, buttons = result
                    if pages >= 1:
                        await bot.edit_message_text(chat_id=user_id,
                                                    message_id=callback_query.message.message_id,
                                                    text=f'📂 Проводник\n📃 Страница:\n{page_number}'
                                                         f' из {pages}\n➡ Текущий путь: {folder}', reply_markup=buttons)

                    else:
                        go_back_explorer = InlineKeyboardButton('◀ Назад', callback_data='back_explorer')
                        folders_markup = InlineKeyboardMarkup(row_width=1).add(go_back_explorer)
                        await bot.edit_message_text(chat_id=user_id,
                                                    message_id=callback_query.message.message_id,
                                                    text=f'📂 Проводник\n➡ Текущий путь:\n{folder}\n'
                                                         f'✖ В данной папке нет файлов.', reply_markup=folders_markup)
                else:
                    pass

            except Exception:
                pass

        if command == 'next_page':
            page_number = page_number + 1

            result = await explorer_func(number='', page=page_number, query_id=callback_query.id)

            if result is not None:
                folder, buttons = result
                await bot.edit_message_text(chat_id=user_id,
                                            message_id=callback_query.message.message_id,
                                            text=f'📂 Проводник\n📃 Страница: {page_number}'
                                                 f' из {pages}\n➡ Текущий путь:\n{folder}', reply_markup=buttons)

        if command == 'previous_page':
            page_number = page_number - 1

            result = await explorer_func(number='', page=page_number, query_id=callback_query.id)

            if result is not None:
                folder, buttons = result
                await bot.edit_message_text(chat_id=user_id,
                                            message_id=callback_query.message.message_id,
                                            text=f'📂 Проводник\n📃 Страница: {page_number}'
                                                 f' из {pages}\n➡ Текущий путь:\n{folder}', reply_markup=buttons)

        if command in folders_names.keys():
            if os.path.isdir(current_path + f'\\{folders_names.get(command)}'):
                try:
                    create_bot.console += f'folder: {folders_names.get(command)}\n'

                    result = await explorer_func(number=command, query_id=callback_query.id)

                    if result is not None:
                        folder, buttons = result
                        if pages >= 1:
                            await bot.edit_message_text(chat_id=user_id,
                                                        message_id=callback_query.message.message_id,
                                                        text=f'📂 Проводник\n📃 Страница: {page_number}'
                                                             f' из {pages}\n➡ Текущий путь:\n{folder}',
                                                        reply_markup=buttons)

                        else:
                            go_back_explorer = InlineKeyboardButton('◀ Назад', callback_data='back_explorer')
                            folders_markup = InlineKeyboardMarkup(row_width=1).add(go_back_explorer)
                            await bot.edit_message_text(chat_id=user_id,
                                                        message_id=callback_query.message.message_id,
                                                        text=f'📂 Проводник\n➡ Текущий путь:\n{folder}\n'
                                                             f'✖ В данной папке нет файлов.',
                                                        reply_markup=folders_markup)

                except Exception as e:
                    if current_path not in names_drives:
                        index = current_path.rfind('\\')
                        if index != -1:
                            current_path = current_path[:index]
                            result = await explorer_func(number='', query_id=callback_query.id)

                            if result is not None:
                                folder, buttons = result
                                await bot.edit_message_text(chat_id=user_id,
                                                            message_id=callback_query.message.message_id,
                                                            text=f'📂 Проводник\n🫡Не удалось открыть папку.\n📃 Страница:'
                                                                 f' {page_number} из {pages}\n➡ Текущий путь:\n{folder}',
                                                            reply_markup=buttons)

                                create_bot.console += f'\nОшибка при попытке открыть папку: {e}\n\n'
                                show_error_message(f'Ошибка при попытке открыть папку: {e}')
                                logger.logging_func(e)

                            else:
                                pass

            else:
                file_name = folders_names.get(command)
                if current_path == os.path.dirname(os.path.abspath(sys.argv[0])) + '\\lnk':

                    create_bot.console += f'subprocess: {current_path}\\{file_name}\n'

                    subprocess.run(['start', '', current_path + f'\\{file_name}'], shell=True)
                    await bot.answer_callback_query(callback_query_id=callback_query.id,
                                                    text="✅ Выполнено!", show_alert=False)

                else:
                    current_path = current_path + '\\' + file_name
                    if os.path.exists(current_path):
                        create_bot.edit_msg = await bot.edit_message_text(chat_id=user_id,
                                                                          message_id=callback_query.message.message_id,
                                                                          text=f'➡ Текущий путь:\n{current_path}'
                                                                               + '\n📂 Выберите действие:',
                                                                          reply_markup=markups.script_file_markup)
                    else:
                        await bot.answer_callback_query(callback_query_id=callback_query.id,
                                                        text="❗ Устройство не найдено.", show_alert=True)
                        await explore_disks(True)

        if command == 'run':
            create_bot.console += f'subprocess: {current_path}\n'

            subprocess.run(['start', '', current_path], shell=True)

            await bot.answer_callback_query(callback_query_id=callback_query.id,
                                            text="✅ Выполнено!", show_alert=False)

        if command == 'download':
            current_path = os.path.dirname(current_path)
            result = await explorer_func(number='', query_id=callback_query.id)
            if result is not None:
                folder, buttons = result
                try:
                    create_bot.edit_msg = await bot.edit_message_text(chat_id=user_id,
                                                                      message_id=callback_query.message.message_id,
                                                                      text='⏳ Идёт загрузка файла.')

                    file_path_name = ''

                    for name in names_drives:
                        if current_path in name:
                            file_path_name = current_path + f'{file_name}'
                            break
                        else:
                            file_path_name = current_path + f'\\{file_name}'
                            break

                    with open(file_path_name, 'rb') as file:
                        create_bot.console += f'upload file: {file_name}\n'
                        await bot.send_document(chat_id=user_id, document=file)
                        create_bot.edit_msg = await bot.send_message(chat_id=user_id,
                                                                     text=f'📂 Проводник\n📃 Страница: {page_number}'
                                                                          f' из {pages}\n➡ Текущий путь:\n{folder}',
                                                                     reply_markup=buttons)

                except Exception as e:
                    await bot.edit_message_text(chat_id=user_id,
                                                message_id=create_bot.edit_msg.message_id,
                                                text='🫡При загрузке файла возникла ошибка.'
                                                     ' Подробнее читайте в Консоли.')
                    create_bot.edit_msg = await bot.send_message(chat_id=user_id,
                                                                 text=f'📂 Проводник\n📃 Страница: {page_number}'
                                                                      f' из {pages}\n➡ Текущий путь:\n{folder}',
                                                                 reply_markup=buttons)

                    create_bot.console += f'\nОшибка handle_callback (попытка отправить файл): {e}\n\n'
                    show_error_message(f'Ошибка handle_callback (попытка отправить файл): {e}')

            else:
                pass

        if command == 'delete':
            create_bot.console += f'delete: {current_path}\n'

            os.remove(current_path)

            await bot.answer_callback_query(callback_query_id=callback_query.id,
                                            text="✅ Файл удален!", show_alert=False)


        if command == 'back_to_drives' or command == 'back_explorer':
            try:
                if command == 'back_explorer':
                    current_path = os.path.dirname(current_path)
                    result = await explorer_func(number='', query_id=callback_query.id)

                    if result is not None:
                        folder, buttons = result
                        await bot.edit_message_text(chat_id=user_id,
                                                    message_id=callback_query.message.message_id,
                                                    text=f'📂 Проводник\n📃 Страница: {page_number}'
                                                         f' из {pages}\n➡ Текущий путь:\n{folder}',
                                                    reply_markup=buttons)

                    else:
                        pass

                else:
                    await explore_disks(True)

            except Exception as e:
                create_bot.console += f'\nОшибка при попытке вернуться на директорию выше: {e}\n\n'
                show_error_message(f'Ошибка при попытке вернуться на директорию выше: {e}')
                logger.logging_func(e)
                await explore_disks(True)

        if command == 'open_lnk':
            await bot.answer_callback_query(callback_query.id)
            lnk_path = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\lnk'
            os.system(f"explorer.exe {lnk_path}")

        if command == 'bot_path':
            current_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            result = await explorer_func(number='', query_id=callback_query.id)

            if result is not None:
                folder, buttons = result
                await bot.edit_message_text(chat_id=user_id,
                                            message_id=callback_query.message.message_id,
                                            text=f'📂 Проводник\n📃 Страница: {page_number}'
                                                 f' из {pages}\n➡ Текущий путь:\n{folder}', reply_markup=buttons)

        if command == 'log':
            await bot.answer_callback_query(callback_query.id)
            await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
            await bot.send_message(chat_id=user_id, text=f'⏳ Идет загрузка лога.')
            create_bot.console += f'download log-file\n'
            with open('logs_from_bot.log', 'rb') as log_file:
                await bot.send_document(chat_id=user_id, document=log_file)

            await description()

        if command == 'start_voice_jarvis':
            await bot.answer_callback_query(callback_query.id)
            create_bot.edit_msg = await bot.send_message(chat_id=user_id, text='🖥 Запускаю голосового Jarvis...')

            try:
                subprocess.Popen('start-voice-jarvis.exe')
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='✅ Голосовой Jarvis запущен.')

            except Exception:
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='❗ Не удалось запустить голосового Jarvis. Убедитесь,'
                                                 ' что в папке бота присутствует файл start-voice-jarvis.exe.')

        if command == 'off':
            await bot.answer_callback_query(callback_query.id)
            await bot.send_message(chat_id=user_id, text='📴 Выключение...')
            subprocess.Popen('off.exe')

        if command == 'reboot':
            await bot.answer_callback_query(callback_query.id)
            await bot.send_message(chat_id=user_id, text='♻ Перезагрузка...')
            subprocess.Popen('reboot.exe')

        if command == 'RU-ru' or command == 'UK-uk' or command == 'EN-en':
            await bot.answer_callback_query(callback_query_id=callback_query.id)
            await recognition(command)

        if command == 'close_dialog':
            try:
                await bot.answer_callback_query(callback_query_id=callback_query.id)
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text=create_bot.edit_msg.text, reply_markup=None)
                text_to_gpt = ''
                await bot.send_message(chat_id=user_id, text='✅ Вы закончили диалог.')
            except Exception:
                pass

        def what_speaker(cmd):
            name_speaker = create_bot.speaker[int(cmd.split('-')[1])]

            if name_speaker == 'aidar':
                return 'Айдар'

            elif name_speaker == 'baya':
                return 'Байя'

            elif name_speaker == 'kseniya':
                return 'Ксения 1'

            elif name_speaker == 'xenia':
                return 'Ксения 2'

            else:
                return 'Евгений'

        if command.split('-')[0] == 'voice':
            await bot.answer_callback_query(callback_query_id=callback_query.id)
            await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                        text=f"✅ Текст отправлен!\n🗣 Голос: {what_speaker(command)}.")

            try:
                await bot.send_voice(chat_id=user_id,
                                     voice=tts.va_speak(what=create_bot.text_to_speech,
                                                        voice=True, speaker=create_bot.speaker[int(command.split('-')[1])]))

                os.remove('audio.mp3')
            except Exception as e:
                logger.logging_func(e)

        if command.split('-')[0] == 'audio':
            await bot.answer_callback_query(callback_query_id=callback_query.id)
            await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                        text=f"✅ Текст отправлен!\n🗣 Голос: {what_speaker(command)}.")

            tts.va_speak(what=create_bot.text_to_speech, voice=False,
                         speaker=create_bot.speaker[int(command.split('-')[1])])

        async def keyboard_press(btn):
            if command == btn.callback_data:
                await bot.answer_callback_query(callback_query.id)
                create_bot.console += f'keyboard press: {command}\n'
                keyboard.press_and_release(command)

        for btn1, btn2 in zip(markups.keys, markups.f):
            await keyboard_press(btn1)
            await keyboard_press(btn2)

        for key, val in exe_files.items():
            if command == key:
                await bot.answer_callback_query(callback_query_id=callback_query.id,
                                                text="✅ Выполнено!", show_alert=False)
                if command == 'screenshot.exe':
                    create_bot.console += ('subprocess: {}\\{}\n'.format(val.split("\\")[-3], command))

                    create_bot.edit_msg = await bot.edit_message_text(chat_id=user_id,
                                                                      message_id=create_bot.edit_msg.message_id,
                                                                      text='⏳ Идёт загрузка скриншота.')

                    path = tempfile.gettempdir() + 'screenshot.png'
                    screenshot = ImageGrab.grab()
                    screenshot.save(path, 'PNG')
                    subprocess.Popen(val)

                    await bot.send_document(chat_id=user_id, document=open(path, 'rb'))
                    await bot.delete_message(chat_id=user_id, message_id=create_bot.edit_msg.message_id)
                    await bot.send_message(chat_id=user_id, text='📂 Выберите папку:',
                                           reply_markup=markups.open_commands())

                else:
                    create_bot.console += 'subprocess: {}\\{}\n'.format(val.split("\\")[-3], command)
                    subprocess.Popen(val)

    else:
        await bot.send_message(chat_id=user_id, text="❗ У вас нет доступа к этому боту!")


def callbacks_messages_handlers(dp: Dispatcher):
    try:
        dp.register_message_handler(messages)
        dp.register_callback_query_handler(handle_callback)
    except:
        pass
