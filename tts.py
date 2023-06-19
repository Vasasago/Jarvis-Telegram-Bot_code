import os
import re
import time
from tkinter import messagebox

import customtkinter
import numpy as np
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

is_run = True


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def start_tts():
    global model, is_run

    def download_url_with_progress(url, local_file, progress_bar, progress_label, remaining_label, speed_label,
                                   time_label):
        global model
        if not os.path.isfile(local_file):
            try:
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))

                with open(local_file, 'wb') as f:
                    start_time = time.time()
                    downloaded_size = 0
                    prev_time = start_time

                    for data in response.iter_content(chunk_size=4096):
                        if is_run:
                            f.write(data)
                            downloaded_size += len(data)
                            progress = min(downloaded_size / total_size, 1.0)
                            progress_bar.set(progress)
                            try:
                                progress_bar.update()
                            except:
                                pass
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

                            try:
                                root.update()
                            except:
                                pass

                            if progress == 1.0:
                                root.destroy()  # Закрыть окно после завершения загрузки
                                return

                        else:
                            root.destroy()
                            return

            except Exception as e:
                logger.logging_func(e)
                root.destroy()

        else:
            root.destroy()
            return

    if os.path.isfile(local_file):
        size = os.path.getsize(local_file)
    else:
        size = 0

    if size < 61896251:
        try:
            os.remove('model.pt')
        except:
            pass

        try:
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

            def on_closing():
                global is_run
                if messagebox.askokcancel("Подтверждение",
                                          "Вы уверены, что хотите остановить установку Silero TTS?"):
                    is_run = False

            root.protocol("WM_DELETE_WINDOW", on_closing)

            download_url_with_progress(url, local_file, progress_bar, progress_label, remaining_label, speed_label, time_label)

            root.wait_window()
            return
        except:
            pass

    return


# Переводим цифры в слова
def wrap_numbers(text):
    pattern = r'\d+'
    result = re.sub(pattern, lambda m: num2text(int(m.group(0))), text)
    return result


# Воспроизводим текст


def split_text(text, max_length):
    if len(text) <= max_length:
        return [text]

    words = text.split()
    fragments = []
    current_fragment = ""

    for word in words:
        if len(current_fragment) + len(word) + 1 <= max_length:  # +1 for space
            if current_fragment:
                current_fragment += " "
            current_fragment += word
        else:
            fragments.append(current_fragment)
            current_fragment = word

    if current_fragment:
        fragments.append(current_fragment)

    return fragments


def va_speak(what: str, voice: bool, speaker: str):
    global model

    if os.path.isfile(local_file):
        size = os.path.getsize(local_file)
    else:
        size = 0

    if os.path.isfile(local_file) and size == 61896251:
        model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
        model.to(device)

    if os.path.isfile(local_file) and model is not None:
        try:
            text_fragments = split_text(what, 1000)
            audio_fragments = []

            for fragment in text_fragments:
                text = wrap_numbers(fragment)
                audio = model.apply_tts(text="..." + text + "...",
                                        speaker=speaker,
                                        sample_rate=sample_rate,
                                        put_accent=put_accent,
                                        put_yo=put_yo)
                audio_fragments.append(audio)

            audio_combined = np.concatenate(audio_fragments)

            if voice is True:
                # Сохранение аудио в файл
                with open('audio.mp3', 'w') as file:
                    file.close()

                sf.write('audio.mp3', audio_combined, sample_rate)

                audio_combined = types.InputFile('audio.mp3')
                return audio_combined

            else:
                # Воспроизведение
                sd.play(audio_combined, sample_rate * 1.05)

        except Exception as e:
            logger.logging_func(e)

    else:
        create_bot.console += f'\nОшибка: модель Silero TTS не установлена.\n\n'
