import logging
import time
import json
from BotHandle import BotHandle

with open('./config.json', 'r', encoding='utf-8') as f:
  config_data = json.load(f)
  bot_token = config_data['bot_token']
  f.close()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_log = logging.StreamHandler()
console_log.setLevel(logging.DEBUG)

file_log = logging.FileHandler(filename='bot.log')
file_log.setLevel(logging.WARNING)

logger.addHandler(console_log)
logger.addHandler(file_log)

BH = BotHandle(bot_token)

if __name__ == '__main__':
  BH.main()