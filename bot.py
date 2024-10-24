from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import datetime

# Словарь для хранения количества сообщений
message_count = {}

def count_messages(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    message_count[user_id] = message_count.get(user_id, 0) + 1

def send_report(context: CallbackContext) -> None:
    chat_id = context.job.context
    report = f"Количество сообщений за день:\n"
    for user_id, count in message_count.items():
        report += f"Пользователь {user_id}: {count} сообщений\n"
    context.bot.send_message(chat_id=chat_id, text=report)
    # Сбросить счетчик
    message_count.clear()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Бот запущен!')

def main() -> None:
    updater = Updater("7686011006:AAGePIRZ_KGE-yww0zhlTUy5BNXQTnhdEAU")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, count_messages))

    # Запланировать отправку отчета в конце дня
    job_queue = updater.job_queue
    job_queue.run_daily(send_report, time=datetime.time(hour=23, minute=59), context='-1001980493060')

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
