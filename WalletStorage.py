import json

class WalletStorage:
  wallets = {}
  
  def __init__(self):
    try:
        with open('./wallet_data.json', 'r', encoding='utf-8') as f:
            wallet_data = json.load(f)
            self.wallets = wallet_data
            f.close()
    except Exception as e:
        print(e)
  
  def add_wallet(self, wallet_name, wallet_adr):
    try:
        self.wallets[wallet_name] = wallet_adr
        with open('./wallet_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.wallets, f, indent=4)
            f.close()
            return True
    except Exception as e:
      print(e)
      return False
  
  def del_wallet(self, wallet_name):
    try:
        del self.wallets[wallet_name]
        with open('./wallet_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.wallets, f, indent=4)
            f.close()
            return True
    except Exception as e:
      print(e)
      return False