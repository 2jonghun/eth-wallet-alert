import telepot
import time
import json
from WalletStorage import WalletStorage

with open('./config.json', 'r', encoding='utf-8') as f:
  config_data = json.load(f)
  bot_token = config_data['bot_token']
  f.close()