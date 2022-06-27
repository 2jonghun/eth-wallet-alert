from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from WalletStorage import WalletStorage

class BotHandle(WalletStorage):

  RESTART, CHOICE, PROCESS, CHECK = range(4)
  reply_keyboard = [['Add wallet', 'Del wallet'], ['not yet','cancel']]

  def __init__(self, bot_token):
    super().__init__()
    self.bot_token = bot_token
    self.updater = Updater(token=self.bot_token, use_context=True)
    self.bot = self.updater.bot
    self.dp = self.updater.dispatcher

  def restart(self, update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text='choice process', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))

    return self.CHOICE

  def test(self, context):
    context.bot.send_message(chat_id=context.job.context, text='job queue testing')

  def start(self, update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text='choice process', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))
    context.job_queue.run_repeating(self.test, interval=60, context=chat_id)

    return self.CHOICE

  def choice(self, update, context):
    chat_id = update.message.chat_id
    chat_txt = update.message.text

    if chat_txt == 'Add wallet':
      update.message.reply_text('추가할 지갑 주소를 입력해주세요.')
      return self.PROCESS

    if chat_txt == 'Del wallet':
      wallet_keyboard = []
      wallet_names = self.get_wallet_name(chat_id)
      for name in wallet_names:
        wallet_keyboard.append([name])
      if wallet_keyboard == []:
        update.message.reply_text('등록된 지갑이 없습니다.', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))
        return ConversationHandler.END
      update.message.reply_text('제거할 지갑 이름을 선택해주세요.', reply_markup=ReplyKeyboardMarkup(wallet_keyboard, one_time_keyboard=True))
      return self.PROCESS
    
    return self.RESTART

  def add_wallet(self, update, context):
    global wallet_adr
    chat_id = update.message.chat_id
    wallet_adr = update.message.text

    update.message.reply_text(f'{wallet_adr}\n추가할 지갑의 이름을 입력해주세요.')
    return self.CHECK

  def check_name(self, update, context):
    chat_id = update.message.chat_id
    wallet_name = update.message.text

    if self.file_add_wallet(chat_id, wallet_name, wallet_adr):
      update.message.reply_text('추가완료.', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))
    else:
      update.message.reply_text('다시 시도해 주세요.', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))
    
    return self.RESTART


  def del_wallet(self, update, context):
    chat_id = update.message.chat_id
    req_del_wallet_name = update.message.text
    wallet_names = self.get_wallet_name(chat_id)

    if req_del_wallet_name in wallet_names:
      if self.file_del_wallet(chat_id, req_del_wallet_name):
        update.message.reply_text('제거완료.', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))
      else:
        update.message.reply_text('다시 시도해 주세요.', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))
    else:
      update.message.reply_text('지갑을 찾을 수 없습니다.', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))

    return self.RESTART

  def error_message(self, update, context):
    chat_txt = update.message.text
    update.message.reply_text(f'{chat_txt} 도중 에러발생 다시 시작해주세요.', reply_markup=ReplyKeyboardMarkup(self.reply_keyboard))
    return self.RESTART
    

  # 기타 메시지에 대한 챗봇의 답변 패턴
  def echo(self, update, context):
    chat_id = update.message.chat_id
    chat_txt = update.message.text

    if chat_txt == 'cancel':
      return self.RESTART


  # 챗봇 실행
  def main(self):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', self.start, pass_job_queue=True)],

        states={
            self.CHOICE: [MessageHandler(Filters.text, self.choice)],

            self.PROCESS: [MessageHandler(Filters.regex(r'0x'), self.add_wallet),
                        MessageHandler(Filters.text, self.del_wallet)],

            self.CHECK: [MessageHandler(Filters.text, self.check_name)],

            self.RESTART: [MessageHandler(Filters.text, self.restart)],
        },

        fallbacks=[MessageHandler(Filters.text, self.error_message)]
    )

    self.dp.add_handler(conv_handler)
    self.dp.add_handler(MessageHandler(Filters.text, self.echo))

    self.updater.start_polling()
    self.updater.idle()