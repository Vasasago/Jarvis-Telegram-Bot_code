import logging

with open('logs_from_bot.log', 'w', encoding='utf-8') as file:
    file.write('Start bot!\n\n')

# Настройка базового логирования
logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler('logs_from_bot.log', encoding='utf-8')
formatter = logging.Formatter('\n%(asctime)s - %(name)s\nLevel: %(levelname)s\nFile: %(filename)s\nFunc: %(funcName)s\nLine: %(lineno)d\nMessage: %(message)s\n')
file_handler.setFormatter(formatter)
py_logger = logging.getLogger()
py_logger.addHandler(file_handler)