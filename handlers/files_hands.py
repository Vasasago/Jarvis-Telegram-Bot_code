import os
from tkinter import messagebox

from aiogram import types, Dispatcher

import create_bot
import markups

import soundfile as sf

edit_msgs = []

script_path = create_bot.script_path
user_id = create_bot.user_id
output_file = create_bot.output_file

bot, dp = create_bot.create()

def copy_bot():
    global bot, dp
    bot, dp = create_bot.create()

def show_error_message(message):
    messagebox.showerror("Ошибка", message)


# Функция для сохранения файла
async def save_file(file_id, file_name, is_photo=False, is_video=False):
    script_path = create_bot.script_path
    try:
        all_path = os.path.join(script_path, 'downloads')

        if os.path.isdir(all_path):
            create_bot.script_path = script_path + '/downloads'

        elif script_path.split('/')[-1] == 'downloads':

            create_bot.script_path = script_path

        else:
            pass

        script_path = create_bot.script_path

        if is_photo:
            save_folder = script_path + '/photos'
        elif is_video:
            save_folder = script_path + '/videos'
        else:
            save_folder = script_path + '/documents'

        create_bot.console += f'Save file: {save_folder}\\{file_name}\n'

        os.makedirs(save_folder, exist_ok=True)  # Создание папки, если она не существует
        save_path = os.path.join(save_folder, file_name)

        file_path = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_path.file_path)

        with open(save_path, 'wb') as f:
            f.write(downloaded_file.read())
            return True

    except Exception as e:
        create_bot.console += f'\nОшибка при скачивании файла: {e}\n'
        show_error_message(f'Ошибка при скачивании файла: {e}')
        return False


# Обработчик документов
# @dp.message_handler(content_types=[types.ContentType.DOCUMENT, types.ContentType.PHOTO, types.ContentType.VIDEO])
async def handle_document(message: types.Message):
    script_path = create_bot.script_path
    user_id = create_bot.user_id

    if str(message.from_user.id) == str(user_id):
        file = None
        create_bot.edit_msg = await bot.send_message(chat_id=user_id, text=f'⏳ Идёт сохранение.')
        edit_msgs.append(create_bot.edit_msg)

        if message.document:
            file = message.document
        elif message.photo:
            file = message.photo
        elif message.video:
            file = message.video

        if message.photo:
            file_name = str(file[-1].file_id)[:20] + '.png'
            if await save_file(str(file[-1].file_id), file_name, is_photo=True):
                save_folder = script_path + '/photos'
                create_bot.edit_msg = edit_msgs.pop()
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text=f"✅ Файл '{file_name}' успешно сохранен по пути {save_folder}.")
            else:
                create_bot.edit_msg = edit_msgs.pop()
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='🫡При сохранении файла возникла ошибка. Подробнее читайте в Консоли.')

        elif message.video:
            file_name = str(file["file_id"])[:20] + '.mp4'
            if await save_file(file["file_id"], file_name, is_video=True):
                save_folder = script_path + '/videos'
                create_bot.edit_msg = edit_msgs.pop()
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text=f"✅ Файл '{file_name}' успешно сохранен по пути {save_folder}.")

            else:
                create_bot.edit_msg = edit_msgs.pop()
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='🫡При сохранении файла возникла ошибка. Подробнее читайте в Консоли.')

        else:
            file_name = file.file_name
            if await save_file(file.file_id, file_name):
                save_folder = script_path + '\\documents'
                create_bot.edit_msg = edit_msgs.pop()
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text=f"✅ Файл '{file_name}' успешно сохранен по пути {save_folder}.")

            else:
                create_bot.edit_msg = edit_msgs.pop()
                await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                            text='🫡При сохранении файла возникла ошибка. Подробнее читайте в Консоли.')

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


# распознавание голосовых сообщений
# @dp.message_handler(content_types=types.ContentType.VOICE)
async def voice_message_handler(message: types.Message):
    global output_file, user_id
    user_id = create_bot.user_id
    if str(message.from_user.id) == str(user_id):
        create_bot.edit_msg = await bot.send_message(chat_id=user_id, text=f'⏳ Идёт распознавание.')
        # # Получаем информацию о голосовом сообщении
        voice = message.voice
        voice_file = await voice.get_file()

        # Сохраняем голосовое сообщение на локальном устройстве
        input_file = 'file.wav'  # Путь для сохранения файла
        await voice_file.download(destination_file=input_file)

        # Определите желаемые параметры выходного аудиофайла
        output_format = 'WAV'
        output_sample_rate = 44100  # Частота дискретизации (в герцах)

        # Чтение исходного аудиофайла
        data, sample_rate = sf.read(input_file)

        # Конвертация аудиофайла
        converted_data = data.astype('float32')  # Приведение данных к нужному формату
        converted_sample_rate = output_sample_rate  # Изменение частоты дискретизации (при необходимости)

        # Запись конвертированного аудиофайла
        sf.write(output_file, converted_data, converted_sample_rate, format=output_format)

        create_bot.edit_msg = await bot.edit_message_text(chat_id=user_id, message_id=create_bot.edit_msg.message_id,
                                                          text='😜 Выберите язык распознавания:',
                                                          reply_markup=markups.langs_markup)

    else:
        await message.answer("❗ У вас нет доступа к этому боту!")


def message_handlers_files(dp: Dispatcher):
    try:
        dp.register_message_handler(handle_document, content_types=[types.ContentType.DOCUMENT, types.ContentType.PHOTO,
                                                                    types.ContentType.VIDEO])
        dp.register_message_handler(voice_message_handler, content_types=types.ContentType.VOICE)
    except:
        pass
