import logging
import time
import json
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from WalletStorage import WalletStorage

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

WS = WalletStorage()

CHOICE, PROCESS, CHECK = range(3)
reply_keyboard = [['Add wallet', 'Del wallet'], ['not yet','cancel']]

def test(context):
  context.bot.send_message(chat_id=context.job.context, text='job queue testing')

def start(update, context):
  chat_id = update.message.chat_id
  context.bot.send_message(chat_id=chat_id, text='choice process', reply_markup=ReplyKeyboardMarkup(reply_keyboard))
  context.job_queue.run_repeating(test, interval=5, context=chat_id)

  return CHOICE

def choice(update, context):
  chat_id = update.message.chat_id
  chat_txt = update.message.text

  if chat_txt == 'Add wallet':
    update.message.reply_text('추가할 지갑 주소를 입력해주세요.')
    return PROCESS

  if chat_txt == 'Del wallet':
    wallet_keyboard = []
    wallet_names = WS.get_wallet_name(chat_id)
    for name in wallet_names:
      wallet_keyboard.append([name])
    update.message.reply_text('제거할 지갑 이름을 선택해주세요.', reply_markup=ReplyKeyboardMarkup(wallet_keyboard, one_time_keyboard=True))
    return PROCESS
  
  return ConversationHandler.END

def add_wallet(update, context):
  global wallet_adr
  chat_id = update.message.chat_id
  wallet_adr = update.message.text

  update.message.reply_text('추가할 지갑의 이름을 입력해주세요.')
  return CHECK

def check_name(update, context):
  chat_id = update.message.chat_id
  wallet_name = update.message.text

  if WS.add_wallet(chat_id, wallet_name, wallet_adr):
    update.message.reply_text('추가완료.')
  else:
    update.message.reply_text('다시 시도해 주세요.')
  
  return ConversationHandler.END


def del_wallet(update, context):
  chat_id = update.message.chat_id
  req_del_wallet_name = update.message.text
  wallet_names = WS.get_wallet_name(chat_id)

  if req_del_wallet_name in wallet_names:
    if WS.del_wallet(chat_id, req_del_wallet_name):
      update.message.reply_text('제거완료.')
    else:
      update.message.reply_text('다시 시도해 주세요.')
  else:
    update.message.reply_text('지갑을 찾을 수 없습니다.')

  return ConversationHandler.END

def error_message(update, context):
  chat_txt = update.message.text
  update.message.reply_text(f'chat_txt 도중 에러발생 다시 시작해주세요.')
  return ConversationHandler.END
  

# 기타 메시지에 대한 챗봇의 답변 패턴
def echo(update, context):
  chat_id = update.message.chat_id
  chat_txt = update.message.text

  if chat_txt == 'cancel':
    return ConversationHandler.END


# 챗봇 실행
def main():
  updater = Updater(token=bot_token, use_context=True)
  bot = updater.bot
  dp = updater.dispatcher

  conv_handler = ConversationHandler(
      entry_points=[CommandHandler('start', start, pass_job_queue=True)],

      states={
          CHOICE: [MessageHandler(Filters.text, choice)],

          PROCESS: [MessageHandler(Filters.regex(r'0x'), add_wallet),
                      MessageHandler(Filters.text, del_wallet)],

          CHECK: [MessageHandler(Filters.text, check_name)],
      },

      fallbacks=[MessageHandler(Filters.text, error_message)]
  )

  dp.add_handler(conv_handler)
  dp.add_handler(MessageHandler(Filters.text, echo))

  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()