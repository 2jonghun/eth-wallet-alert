import json

class WalletStorage:
  def __init__(self):
    try:
      with open('./wallet_data.json', 'r', encoding='utf-8') as f:
        self.__wallets = json.load(f)
        f.close()
    except Exception as e:
      print(e)

  def get_wallet_name(self, chat_id):
    self.__wallet_names = self.__wallets[str(chat_id)].keys()
    return list(self.__wallet_names)
  
  def file_add_wallet(self, chat_id, wallet_name, wallet_adr):
    self.__wallets_keys = list(self.__wallets.keys())
    if chat_id not in self.__wallets_keys:
      self.__wallets[str(chat_id)] = {}
    self.__wallets[str(chat_id)][wallet_name] = wallet_adr
    if self.__file_write():
      return True
    else:
      return False
  
  def file_del_wallet(self, chat_id, wallet_name):
    del self.__wallets[str(chat_id)][wallet_name]
    if self.__file_write():
      return True
    else:
      return False

  def __get_wallets(self):
    try:
      with open('./wallet_data.json', 'r', encoding='utf-8') as f:
        self.__wallets = json.load(f)
        f.close()
    except Exception as e:
      print(e)
  
  def __file_write(self):
    try:
      with open('./wallet_data.json', 'w', encoding='utf-8') as f:
        json.dump(self.__wallets, f, indent=4)
        f.close()
      return True
    except Exception as e:
      print(e)
      return False