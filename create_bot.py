import configparser
import os
import sys

import requests
from aiogram import Bot, Dispatcher

import logger


bot_version = '3.2.0'  # Версия бота

bot_token = None  # Токен бота
chatgpt_token = None  # Токен OpenAI
root_folder = ''  # Команды
user_id = None  # ID пользователя
script_path = ''  # Путь к боту

gpt_model = 'gpt-3.5-turbo'  # Модель GPT
commands_folder_out = ''  # путь к папке с командами
commands_dict = {}  # Команды
inline_folders = []  # Кнопки с папками
folders_names = {}  # Имена папок
drives_in = []  # Кнопки дисков
names_drives = []  # Имена дисков
current_path = ''  # Текущий путь
max_tokens = 4097  # Токены ChatGPT
page_number = 0  # Страница проводника
pages = 0  # Всего страниц
output_file = 'file.wav'  # Имя перекодированного файла
edit_msg = None  # Сообщение для редактирования
text_to_speech = ''  # Текст для озвучки
speaker = ['aidar', 'baya', 'kseniya', 'xenia', 'eugene']  # Голоса для озвучки
text_to_gpt = ''  # Текст запроса к GPT
file_name = ''  # Имя текущего файла
page_films = 1


description = "_Доступные команды:_\n" \
              "🔸 /message \[текст] - отправить текст на ваш компьютер.\n" \
              "🔸 /voice \[текст] - прислать голосовое сообщение с вашим текстом.\n" \
              "🔸 /audio \[текст] - озвучить текст на вашем компьютере.\n" \
              "🔸 /dalle \[текст] - сгенерировать изображение.\n" \
              "🔸 /film \[текст (не обязательно)] - получить фильм (список фильмов) для просмотра.\n" \
              "🔸 /math \[текст] - сделать математический расчет.\n\n" \
              "_Доступные изменения:_\n" \
              "🔸 /set\_cmd\_path \[путь] - изменить путь к командам.\n" \
              "🔸 /set\_downloads\_path \[путь] - изменить путь к загрузкам.\n" \
              "🔸 /set\_gpt\_token \[токен] - изменить токен OpenAI.\n\n" \
              "_При выборе файла в проводнике бота:_\n" \
              "🔸 Запуск файла в приложении по-умолчанию.\n" \
              "🔸 Скачивание файла.\n\n" \
              "_Чтобы открыть ссылку на пк, просто отправьте ее боту без каких-либо команд_\n\n" \
              "_Для управления мышью напишите:_\n" \
              "🔸 Движение: (вверх, вниз, вправо, влево) + [число пикселей]\n" \
              "🔸 Нажатие: лкм, пкм."


flag = False

console = ''

bot = None
dp = None

config = configparser.ConfigParser()  # Создание конфига

# Проверяем, существует ли файл "config.txt"
if not os.path.isfile("config.ini"):
    # Если файл не существует, создаем его
    with open("config.ini", "w") as file:
        pass

# Проверяем, пустой ли файл "config.txt"
if os.stat("config.ini").st_size == 0:
    # Если файл пустой, запрашиваем у пользователя необходимую информацию
    bot_token = ''
    chatgpt_token = ''
    root_folder = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\commands'
    script_path = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\downloads'

    config.add_section('tg-bot')

    config.set('tg-bot', 'bot_token', f'{bot_token}')
    config.set('tg-bot', 'chatgpt_token', f'{chatgpt_token}')
    config.set('tg-bot', 'commands_folder', f'{root_folder}')
    config.set('tg-bot', 'downloads_path', f'{script_path}')
    config.set('tg-bot', 'user_id', '')

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    config.read('config.ini')

    bot_token = config.get('tg-bot', 'bot_token')
    chatgpt_token = config.get('tg-bot', 'chatgpt_token')
    root_folder = config.get('tg-bot', 'commands_folder')
    user_id = config.get('tg-bot', 'user_id')
    script_path = config.get('tg-bot', 'downloads_path')

else:

    config.read('config.ini')

    bot_token = config.get('tg-bot', 'bot_token')
    chatgpt_token = config.get('tg-bot', 'chatgpt_token')
    root_folder = config.get('tg-bot', 'commands_folder')
    user_id = config.get('tg-bot', 'user_id')
    script_path = config.get('tg-bot', 'downloads_path')


os.makedirs(os.path.dirname(os.path.abspath(sys.argv[0])) + '\\lnk', exist_ok=True)


# Проверка токена бота перед созданием экземпляра
def check_bot_token(token):
    try:
        url = f'https://api.telegram.org/bot{token}/getMe'
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return True
        else:
            return False

    except Exception as e:
        logger.py_logger.error(f"{e}\n\n")
        return False

def create():
    global bot, dp
    # Создаем экземпляр бота и диспетчера
    if check_bot_token(bot_token):
        from aiogram.contrib.fsm_storage.memory import MemoryStorage
        bot = Bot(token=bot_token)
        dp = Dispatcher(bot, storage=MemoryStorage())

        return bot, dp
    else:
        return None, None