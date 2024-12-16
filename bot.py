from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import json
import pytz
from openpyxl import Workbook  # Для работы с Excel

# Словарь для хранения статистики сообщений
message_count = {}

# Список ID групп, в которых бот будет отслеживать сообщения
group_ids = {
    '-1001845256399', '-1001520209434', '-1001656540195',
    '-1001775046025', '-1001343504125', '-1001857285435',
    '-1001867637705', '-1002196532000', '-1001294018674',
    '-1002252347198', '-1001926464969'
}

# Список разрешенных пользователей
allowed_users = {785492955, 1782689461, 961325088, 1270457445}

# ID группы для отправки отчета
report_group_id = '-4564729970'

# Функция для сохранения данных в JSON
def save_to_json():
    with open('message_count.json', 'w', encoding='utf-8') as f:
        json.dump(message_count, f, ensure_ascii=False, indent=4)

# Функция для очистки данных
async def clear_data() -> None:
    save_to_json()
    message_count.clear()

async def count_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.first_name
    chat_id = str(update.message.chat.id)

    if chat_id in group_ids:
        if chat_id not in message_count:
            message_count[chat_id] = {
                'total_messages': 0,
                'users': {},
                'group_name': update.message.chat.title
            }

        message_count[chat_id]['total_messages'] += 1
        user_data = message_count[chat_id]['users'].setdefault(user_id, {'name': user_name, 'messages': 0})
        user_data['messages'] += 1

async def send_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        await update.message.reply_text("")
        return

    # Генерация Excel-отчета
    file_path = await generate_excel_report()

    # Отправка файла в Telegram
    await context.bot.send_document(chat_id=update.message.chat.id, document=open(file_path, 'rb'))

async def generate_excel_report() -> str:
    # Создаем новый Excel-файл
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Отчет"

    # Заголовки
    sheet.append(["Группа", "Всего сообщений", "Пользователь", "ID пользователя", "Сообщений"])

    # Заполняем данные
    for chat_id, data in message_count.items():
        group_name = data['group_name']
        total_messages = data['total_messages']
        for user_id, user_data in data['users'].items():
            sheet.append([group_name, total_messages, user_data['name'], user_id, user_data['messages']])

    # Сохраняем файл
    file_name = f"report_{datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')}.xlsx"
    workbook.save(file_name)

    return file_name

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    # Генерация Excel-отчета
    file_path = await generate_excel_report()

    # Отправка файла в Telegram
    await context.bot.send_document(chat_id=report_group_id, document=open(file_path, 'rb'))

    # Очистка данных
    await clear_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    await update.message.reply_text('Бот запущен! Используйте /report для получения отчета.')

def main() -> None:
    application = ApplicationBuilder().token("7686011006:AAGePIRZ_KGE-yww0zhlTUy5BNXQTnhdEAU").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", send_report))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_messages))

    # Запланировать отправку отчета в конце дня
    application.job_queue.run_daily(send_daily_report, time=datetime.time(hour=23, minute=59, tzinfo=pytz.timezone('Europe/Moscow')))

    application.run_polling()

if __name__ == '__main__':
    main()
