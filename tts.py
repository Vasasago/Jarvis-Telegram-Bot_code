import os
import re
import time
from tkinter import messagebox

import customtkinter
import requests
import sounddevice as sd
import torch
from aiogram import types
from colorama import init
from num2t4ru import num2text

import create_bot
import logger
import soundfile as sf

init()

language = 'ru'
model_id = 'ru_v3'
sample_rate = 48000
put_accent = True
put_yo = True


model = None
device = torch.device('cpu')
local_file = 'model.pt'
url = 'https://models.silero.ai/models/tts/ru/v3_1_ru.pt'


def show_error_message(message):
    messagebox.showerror("Ошибка", message)


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def start_tts():
    global model

    def on_closing():
        if messagebox.askokcancel("Подтверждение", "Вы уверены, что хотите остановить установку Silero TTS?"):
            root.destroy()

    def download_url_with_progress(url, local_file, progress_bar, progress_label, remaining_label, speed_label,
                                   time_label):
        if not os.path.isfile(local_file):

            try:

                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))

                with open(local_file, 'wb') as f:
                    start_time = time.time()
                    downloaded_size = 0
                    prev_time = start_time

                    for data in response.iter_content(chunk_size=4096):
                        f.write(data)
                        downloaded_size += len(data)
                        progress = min(downloaded_size / total_size, 1.0)
                        progress_bar.set(progress)
                        progress_bar.update()
                        progress_label.configure(text=f"Прогресс: {progress * 100:.2f}%")

                        remaining_size = total_size - downloaded_size
                        remaining_label.configure(text=f"Осталось: {remaining_size / (1024 * 1024):.2f} MB")

                        curr_time = time.time()
                        elapsed_time = curr_time - start_time
                        speed = downloaded_size / (1024 * elapsed_time)
                        if speed <= 1024:
                            speed_label.configure(text=f"Скорость загрузки: {speed:.2f} KB/s")
                        else:
                            speed_mb = speed / 1024
                            speed_label.configure(text=f"Скорость загрузки: {speed_mb:.2f} MB/s")

                        if speed > 0:
                            remaining_time = remaining_size / (speed * 1024)
                            time_left = format_time(remaining_time)
                            time_label.configure(text=f"Оставшееся время: {time_left}")

                        prev_time = curr_time

                        root.update()

                        if progress == 1.0:
                            root.destroy()  # Закрыть окно после завершения загрузки

            except Exception as e:
                logger.logging_func(e)


        else:
            return

    try:
        model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
        model.to(device)

    except Exception:
        try:
            os.remove('model.pt')
        except:
            pass
        customtkinter.set_appearance_mode('dark')
        customtkinter.set_default_color_theme('dark-blue')

        root = customtkinter.CTk()
        root.title("Установка модели Silero TTS")
        root.geometry("400x100")
        root.resizable(False, False)
        root.iconbitmap("icons\\h.ico")

        progress_bar = customtkinter.CTkProgressBar(root, mode="determinate", width=300, progress_color='magenta3')
        progress_bar.place(x=50, y=10)

        progress_label = customtkinter.CTkLabel(root, text="Прогресс: 0%")
        progress_label.place(x=45, y=30)

        remaining_label = customtkinter.CTkLabel(root, text="Осталось: --")
        remaining_label.place(x=45, y=60)

        speed_label = customtkinter.CTkLabel(root, text="Скорость загрузки: --")
        speed_label.place(x=180, y=30)

        time_label = customtkinter.CTkLabel(root, text="Оставшееся время: --")
        time_label.place(x=180, y=60)

        root.protocol("WM_DELETE_WINDOW", on_closing)

        download_url_with_progress(url, local_file, progress_bar, progress_label, remaining_label, speed_label, time_label)

        root.mainloop()


# Переводим цифры в слова
def wrap_numbers(text):
    pattern = r'\d+'
    result = re.sub(pattern, lambda m: num2text(int(m.group(0))), text)
    return result


# Воспроизводим текст

def va_speak(what: str, voice: bool, speaker: str):
    if os.path.isfile(local_file) and model is not None:
        try:
            text = wrap_numbers(what)
            audio = model.apply_tts(text="..." + text + "...",
                                    speaker=speaker,
                                    sample_rate=sample_rate,
                                    put_accent=put_accent,
                                    put_yo=put_yo)

            if voice is True:
                # Сохранение аудио в файл
                with open('audio.mp3', 'w') as file:
                    file.close()

                sf.write('audio.mp3', audio, sample_rate)

                audio = types.InputFile('audio.mp3')
                return audio

            else:
                # Воспроизведение
                sd.play(audio, sample_rate * 1.05)

        except Exception as e:
            show_error_message(e)
            logger.logging_func(e)

    else:
        create_bot.console += f'\nОшибка: модель Silero TTS не установлена.\n\n'
        show_error_message(f'Модель Silero TTS не установлена.')
