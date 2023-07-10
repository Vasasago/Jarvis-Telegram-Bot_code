from io import BytesIO

import requests
from PIL import Image
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup

def search(url: str):
    response = requests.get(url)

    # Создать объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Извлечь название из тега h1
    h1_tag = soup.find('h1')
    title = h1_tag.get_text(strip=True).replace('смотреть онлайн', '')

    # Извлечь описание из тега div с классом "fdesc"
    fdesc_div = soup.find(class_='fdesc')
    description = fdesc_div.get_text(strip=True)

    if len(description) > 500:
        description = description[:500]

    # Извлечь ссылку на картинку из тега img
    image_div = soup.find(class_='fleft-img fx-first').find(class_='fleft-img-in').find(class_='fposter img-wide')
    image_url = 'https://hd.erfilm.cfd/' +  image_div.img['src']


    open_url = InlineKeyboardButton('Смотреть на текущем устройстве', url=url)
    open_pc = InlineKeyboardButton('Смотреть на пк', callback_data='open_link')
    open_markup = InlineKeyboardMarkup(row_width=1).add(open_url, open_pc)

    response = requests.get(image_url)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    image.save(title, "PNG")

    return title, description, open_markup

