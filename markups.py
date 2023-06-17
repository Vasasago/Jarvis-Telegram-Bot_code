import configparser

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import os

import logger

commands_btns = []
commands = {}

config = configparser.ConfigParser()  # Создание конфига


def open_commands():
    def get_folder_names(directory):
        try:
            folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
            return folders

        except Exception as e:
            logger.logging_func(e)

    config.read('config.ini')
    folder_path = config.get('tg-bot', 'commands_folder')
    folders = get_folder_names(folder_path)

    if folders:

        folder_btns = [InlineKeyboardButton(f'{folder}', callback_data=f'folder:{folder}') for folder in folders]

    else:
        folder_btns = []

    commands_btns.clear()

    for btn in folder_btns:
        commands_btns.append(btn)

    inline_folders = InlineKeyboardMarkup(row_width=2).add(*commands_btns)

    return inline_folders


def open_folder(folder_name):
    def get_exe_files(directory):
        try:
            exe_files = [file for file in os.listdir(directory) if file.endswith('.exe')]
            return exe_files

        except Exception as e:
            logger.logging_func(e)

    config.read('config.ini')
    folder_path = config.get('tg-bot', 'commands_folder')

    folder_path = os.path.join(folder_path, folder_name)
    subfolder_path = os.path.join(folder_path, 'ahk')
    exe_files = get_exe_files(subfolder_path)

    if exe_files:
        exe_btns = [InlineKeyboardButton(file, callback_data=f'file:{file}') for file in exe_files]

    else:
        exe_btns = []

    commands_btns.clear()

    for btn in exe_btns:
        commands_btns.append(btn)

    inline_files = InlineKeyboardMarkup(row_width=2).add(*commands_btns)

    return inline_files


f = [InlineKeyboardButton('≡ F1 ≡', callback_data='f1'), InlineKeyboardButton('≡ F2 ≡', callback_data='f2'),
     InlineKeyboardButton('≡ F3 ≡', callback_data='f3'), InlineKeyboardButton('≡ F4 ≡', callback_data='f4'),
     InlineKeyboardButton('≡ F5 ≡', callback_data='f5'), InlineKeyboardButton('≡ F6 ≡', callback_data='f6'),
     InlineKeyboardButton('≡ F7 ≡', callback_data='f7'), InlineKeyboardButton('≡ F8 ≡', callback_data='f8'),
     InlineKeyboardButton('≡ F9 ≡', callback_data='f9'), InlineKeyboardButton('≡ F10 ≡', callback_data='f10'),
     InlineKeyboardButton('≡ F11 ≡', callback_data='f11'), InlineKeyboardButton('≡ F12 ≡', callback_data='f12')]

keys = [InlineKeyboardButton('Space', callback_data='space'),
        InlineKeyboardButton('Enter', callback_data='enter'),
        InlineKeyboardButton('Esc', callback_data='esc'),
        InlineKeyboardButton('Windows', callback_data='win'),
        InlineKeyboardButton('Backspace', callback_data='backspace'),
        InlineKeyboardButton('Shift', callback_data='shift'),
        InlineKeyboardButton('Ctrl', callback_data='ctrl'),
        InlineKeyboardButton('Alt', callback_data='alt'),
        InlineKeyboardButton('Left', callback_data='left'),
        InlineKeyboardButton('Right', callback_data='right'),
        InlineKeyboardButton('Up', callback_data='up'),
        InlineKeyboardButton('Down', callback_data='down')]

keyboard_inline = InlineKeyboardMarkup(row_width=4).add(*f, *keys)

main_btns = [KeyboardButton('🤖 Команды Jarvis'),
             KeyboardButton('⌨ Клавиатура'),
             KeyboardButton('📂 Проводник'),
             KeyboardButton('🖥 Программы'),
             KeyboardButton('🛠 Управление ботом')]

main_inline = ReplyKeyboardMarkup(resize_keyboard=True).add(*main_btns)

service_btns = [InlineKeyboardButton('🖥 Запустить голосового Jarvis', callback_data='start_voice_jarvis'),
                InlineKeyboardButton('📴 Выключить бота', callback_data='off'),
                InlineKeyboardButton('♻ Перезагрузить бота', callback_data='reboot'),
                InlineKeyboardButton('📂 Открыть папку с ботом', callback_data='bot_path'),
                InlineKeyboardButton('⬇ Скачать лог', callback_data='log')]

service_markup = InlineKeyboardMarkup(row_width=1).add(*service_btns)

voice_speakers = [InlineKeyboardButton('👨‍🦱 ‍Айдар', callback_data='voice-0'),
                  InlineKeyboardButton('🧑 Байя', callback_data='voice-1'),
                  InlineKeyboardButton('👩 Ксения 1', callback_data='voice-2'),
                  InlineKeyboardButton('👩‍🦰 Ксения 2', callback_data='voice-3'),
                  InlineKeyboardButton('👨‍🦰 Евгений', callback_data='voice-4')]

voice_markup = InlineKeyboardMarkup(row_width=1).add(*voice_speakers)

audio_speakers = [InlineKeyboardButton('👨‍🦱 ‍Айдар', callback_data='audio-0'),
                  InlineKeyboardButton('🧑 Байя', callback_data='audio-1'),
                  InlineKeyboardButton('👩 Ксения 1', callback_data='audio-2'),
                  InlineKeyboardButton('👩‍🦰 Ксения 2', callback_data='audio-3'),
                  InlineKeyboardButton('👨‍🦰 Евгений', callback_data='audio-4')]

audio_markup = InlineKeyboardMarkup(row_width=1).add(*audio_speakers)

languages = [InlineKeyboardButton('🇷🇺 Русский', callback_data='RU-ru'),
             InlineKeyboardButton('🇺🇦 Украинский', callback_data='UK-uk'),
             InlineKeyboardButton('🇺🇸 Английский', callback_data='EN-en')]

langs_markup = InlineKeyboardMarkup(row_width=1).add(*languages)

script_file_btns = [InlineKeyboardButton('🖥 Запустить', callback_data='run'),
                    InlineKeyboardButton('📲 Скачать', callback_data='download'),
                    InlineKeyboardButton('🗑 Удалить', callback_data='delete'),
                    InlineKeyboardButton('◀ Назад', callback_data='back_explorer')]

script_file_markup = InlineKeyboardMarkup(row_width=1).add(*script_file_btns)


open_lnk_btn = InlineKeyboardButton('📂 Открыть папку', callback_data='open_lnk')

open_lnk_markup = InlineKeyboardMarkup(row_width=1).add(open_lnk_btn)
