import logging

with open('logs_from_bot.log', 'w') as file:
    file.write('Start bot!\n\n')

# Настройка базового логирования
logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler('logs_from_bot.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(file_handler)


def logging_func(error):
    logger.info(error)
