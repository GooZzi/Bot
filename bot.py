from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import json
import pytz  # Не забудьте установить pytz, если он еще не установлен

# Словарь для хранения статистики сообщений
message_count = {}

# Список ID групп, в которых бот будет отслеживать сообщения
group_ids = {
    '-1001845256399','-1001520209434','-1001656540195',
    '-1001775046025','-1001343504125','-1001857285435',
    '-1001867637705','-1002196532000','-1001294018674',
    '-1002252347198','-1001926464969'
}  # Замените на ваши ID групп

# Список разрешенных пользователей
allowed_users = {785492955, 1782689461, 961325088, 1270457445}  # Замените на ID разрешенных пользователей

# ID группы для отправки отчета
report_group_id = '-4564729970'  # Замените на ваш ID группы

# Функция для сохранения данных в JSON
def save_to_json():
    with open('message_count.json', 'w', encoding='utf-8') as f:
        json.dump(message_count, f, ensure_ascii=False, indent=4)

# Функция для очистки данных
async def clear_data() -> None:
    save_to_json()  # Сохраняем текущие данные в файл перед очисткой
    message_count.clear()

async def count_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.first_name  # Получаем имя пользователя
    chat_id = str(update.message.chat.id)

    # Убедимся, что сообщение пришло из одной из указанных групп
    if chat_id in group_ids:
        # Инициализируем данные группы, если они отсутствуют
        if chat_id not in message_count:
            message_count[chat_id] = {
                'total_messages': 0,
                'users': {},
                'group_name': update.message.chat.title  # Сохраняем название группы
            }

        # Увеличиваем общее количество сообщений в группе
        message_count[chat_id]['total_messages'] += 1

        # Инициализируем данные пользователя, если они отсутствуют
        user_data = message_count[chat_id]['users'].setdefault(user_id, {'name': user_name, 'messages': 0})
        
        # Увеличиваем счетчик сообщений для пользователя
        user_data['messages'] += 1

async def send_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        await update.message.reply_text("")
        return

    report = await generate_report()
    await send_long_message(context, update.message.chat.id, report)

async def generate_report() -> str:
    report = f"Отчет на {datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')}:\n"
    
    if not message_count:
        report += "Нет данных для отчета.\n"
    else:
        for chat_id, data in message_count.items():
            # Получаем информацию о группе
            group_name = data['group_name']  # Используем сохраненное название группы
            report += f"\nСтатистика для группы '{group_name}':\n"
            report += f"Всего сообщений: {data['total_messages']}\n"
            for user_id, user_data in data['users'].items():
                report += f"Пользователь {user_data['name']} (ID: {user_id}) - {user_data['messages']} сообщений\n"
    
    return report

async def send_long_message(context, chat_id, text):
    max_length = 4096  # Максимальная длина сообщения в Telegram
    for i in range(0, len(text), max_length):
        await context.bot.send_message(chat_id=chat_id, text=text[i:i + max_length])

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    report = await generate_report()
    await send_long_message(context, report_group_id, report)
    await clear_data()  # Очищаем данные после отправки отчета

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        await update.message.reply_text("")
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
