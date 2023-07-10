import configparser

import psutil
import requests
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import os

from bs4 import BeautifulSoup

import create_bot
import logger

commands_btns = []
commands = {}

config = configparser.ConfigParser()  # Создание конфига


def open_commands() -> InlineKeyboardMarkup:
    def get_folder_names(directory: str) -> list:
        try:
            folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
            return folders

        except Exception as e:
            logger.py_logger.error(f"{e}\n\n")

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


def open_folder(folder_name: str) -> InlineKeyboardMarkup:
    def get_exe_files(directory):
        try:
            exe_files = [file for file in os.listdir(directory) if file.endswith('.exe')]
            return exe_files

        except Exception as e:
            logger.py_logger.error(f"{e}\n\n")

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


main_btns = [KeyboardButton('🤖 Команды Jarvis'),
             KeyboardButton('🖥 Компьютер'),
             KeyboardButton('🛠 Управление ботом')]

main_inline = ReplyKeyboardMarkup(resize_keyboard=True).add(*main_btns)


pc_btns = [InlineKeyboardButton('📊 Показатели пк', callback_data='pc_control'),
           InlineKeyboardButton('💿 Программы', callback_data='programs'),
           InlineKeyboardButton('📂 Проводник', callback_data='explorer'),
           InlineKeyboardButton('💻 Команды Windows', callback_data='commands_windows'),
           InlineKeyboardButton('💽 Диспетчер задач', callback_data='tasks'),
           InlineKeyboardButton('⌨️ Клавиатура', callback_data='keyboard'),
           InlineKeyboardButton('🐁 Мышь', callback_data='mouse'),]

pc_markup = InlineKeyboardMarkup(row_width=2).add(*pc_btns)


update_pc_control_btn = InlineKeyboardButton('♻️ Обновить', callback_data='pc_control')
back_to_pc_markup_btn = InlineKeyboardButton('◀ Назад', callback_data='back_pc')

back_to_pc_markup = InlineKeyboardMarkup(row_width=1).add(update_pc_control_btn, back_to_pc_markup_btn)


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

keyboard_inline = InlineKeyboardMarkup(row_width=4).add(*f, *keys, back_to_pc_markup_btn)


mouse_btns = [
    InlineKeyboardButton('вверх 10', callback_data='up_10'),
    InlineKeyboardButton('вниз 10', callback_data='down_10'),
    InlineKeyboardButton('влево 10', callback_data='left_10'),
    InlineKeyboardButton('вправо 10', callback_data='right_10'),

    InlineKeyboardButton('вверх 100', callback_data='up_100'),
    InlineKeyboardButton('вниз 100', callback_data='down_100'),
    InlineKeyboardButton('влево 100', callback_data='left_100'),
    InlineKeyboardButton('вправо 100', callback_data='right_100'),

    InlineKeyboardButton('ЛКМ', callback_data='left_0'),
    InlineKeyboardButton('ПКМ', callback_data='right_0'),
]

Mouse_markup = InlineKeyboardMarkup(row_width=2).add(*mouse_btns, back_to_pc_markup_btn)


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

open_lnk_markup = InlineKeyboardMarkup(row_width=1).add(open_lnk_btn, back_to_pc_markup_btn)


close_dialog_btn = InlineKeyboardButton('✖ Закончить диалог', callback_data='close_dialog')

gpt_markup = InlineKeyboardMarkup(row_width=1).add(close_dialog_btn)


open_link_btn = InlineKeyboardButton('🌐 Открыть ссылку', callback_data='open_link')

open_link_markup = InlineKeyboardMarkup(row_width=1).add(open_link_btn)


commands_windows_btns1 = [
    InlineKeyboardButton('Выключить пк', callback_data='shutdown_pc'),
    InlineKeyboardButton('Отмена выключения', callback_data='cancel_shutdown_pc.exe'),
    InlineKeyboardButton('Заблокировать пк', callback_data='block_pc.exe'),
    InlineKeyboardButton('Спящий режим', callback_data='sleep_pc.exe'),
    InlineKeyboardButton('Перезагрузка', callback_data='reboot_pc.exe'),
    InlineKeyboardButton('Буфер обмена', callback_data='clipboard.exe'),
    InlineKeyboardButton('Очистить корзину', callback_data='empty_trash.exe'),
    InlineKeyboardButton('Диспетчер задач', callback_data='task_manager.exe'),
    InlineKeyboardButton('Открыть настройки', callback_data='open_settings.exe'),
    InlineKeyboardButton('Закрыть настройки', callback_data='close_settings.exe'),
    InlineKeyboardButton('Свернуть все окна', callback_data='roll_up_windows.exe'),
    InlineKeyboardButton('Свернуть текущее окно', callback_data='minimize_current_window.exe'),
    InlineKeyboardButton('Текущее окно на весь экран', callback_data='maximize_current_window.exe'),
    InlineKeyboardButton('Сменить раскладку', callback_data='change_language.exe'),
    InlineKeyboardButton('Сделать скриншот', callback_data='screenshot.exe'),
    InlineKeyboardButton('Открыть загрузки', callback_data='open_downloads.exe'),
]

commands_windows_btns2 = [
    InlineKeyboardButton('Звук', callback_data='mute_volume.exe'),
    InlineKeyboardButton('Звук на минимум', callback_data='min_volume.exe'),
    InlineKeyboardButton('Сделать тише', callback_data='sound_down.exe'),
    InlineKeyboardButton('Сделать громче', callback_data='sound_up.exe'),
    InlineKeyboardButton('Громкость 20', callback_data='set_sound_20.exe'),
    InlineKeyboardButton('Громкость 50', callback_data='set_sound_50.exe'),
    InlineKeyboardButton('Громкость 80', callback_data='set_sound_80.exe'),
    InlineKeyboardButton('Громкость 100', callback_data='set_sound_100.exe'),
    InlineKeyboardButton('Переключить на динамики', callback_data='switch_to_speakers.exe'),
    InlineKeyboardButton('Переключить на наушники', callback_data='switch_to_headphones.exe'),
]

go_next = InlineKeyboardButton('➡️ Следующая страница', callback_data='next')
go_back = InlineKeyboardButton('⬅️ Предыдущая страница', callback_data='back')


def commands_windows(page: int) -> InlineKeyboardMarkup:
    commands_windows_markup = InlineKeyboardMarkup(row_width=2)
    if page == 0:
        commands_windows_markup.add(*commands_windows_btns1, go_next, back_to_pc_markup_btn)
    else:
        commands_windows_markup.add(*commands_windows_btns2, go_back, back_to_pc_markup_btn)

    return commands_windows_markup


def get_running_applications() -> list:
    running_apps = []

    # Получение списка всех запущенных процессов
    for proc in psutil.process_iter(['name', 'username']):
        try:
            proc_info = proc.as_dict(attrs=['name', 'username', 'exe'])
            proc_name = proc_info['name']
            proc_username = proc_info['username']
            proc_exe = proc_info['exe']

            # Проверка на системные программы и фоновые процессы
            if proc_username and proc_exe and proc_name not in running_apps:
                running_apps.append(proc_name)  # Добавление названия процесса в массив running_apps
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return running_apps


def tasks() -> list:
    running_apps = get_running_applications()

    running_apps_btns = [InlineKeyboardButton(app_name, callback_data=app_name) for app_name in running_apps]
    running_apps_markup = InlineKeyboardMarkup(row_width=2).add(*running_apps_btns, back_to_pc_markup_btn)

    return [running_apps_btns, running_apps_markup]


def searching_films(page=1) -> tuple:
    buttons = []

    create_bot.page_films = page

    # URL-адрес для перехода
    url = f'https://hd.erfilm.cfd/page/{page}/'

    response = requests.get(url)

    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Найти все элементы с классом "th-item"
    th_items = soup.find_all(class_='th-item')

    # Обработать каждый блок
    for th_item in th_items:
        th_in = th_item.find(class_='th-in')
        link = th_in['href']
        title = th_in.find(class_='th-title').get_text(strip=True)

        if len(link.replace('https://hd.erfilm.cfd/', '')) < 66:
            buttons.append(InlineKeyboardButton(title, callback_data=link.replace('https://hd.erfilm.cfd/', '')))


    films_markup = InlineKeyboardMarkup(row_width=2)
    films_markup.add(*buttons)

    # Добавить кнопки "Вперед" и "Назад"
    if page == 1:
        films_markup.add(InlineKeyboardButton('➡️ Вперед', callback_data='next_film'))
    else:
        films_markup.add(InlineKeyboardButton('⬅️ Назад', callback_data='prev_film'),
                         InlineKeyboardButton('➡️ Вперед', callback_data='next_film'))

    return films_markup, page
