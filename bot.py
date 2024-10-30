from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import datetime

# Словарь для хранения статистики сообщений
message_count = {}

# Список ID групп, в которых бот будет отслеживать сообщения
group_ids = {'-1002196532000','-1001775046025','-1001343504125','-1001294018674','-1001656540195','-1001867637705','-1001857285435','-1002196532000'}  # Замените на ваши ID групп

# Список разрешенных пользователей
allowed_users = {123456789, 987654321}  # Замените на ID разрешенных пользователей

# ID группы для отправки отчета
report_group_id = '-4564729970'  # Замените на ваш ID группы

async def count_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.first_name  # Получаем имя пользователя
    chat_id = str(update.message.chat.id)

    # Убедимся, что сообщение пришло из одной из указанных групп
    if chat_id in group_ids:
        # Инициализируем данные группы, если они отсутствуют
        if chat_id not in message_count:
            message_count[chat_id] = {'total_messages': 0, 'users': {}}

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
    await update.message.reply_text(report)

async def generate_report() -> str:
    report = f"Отчет на {datetime.datetime.now().strftime('%Y-%m-%d')}:\n"
    
    if not message_count:
        report += "Нет данных для отчета.\n"
    else:
        for chat_id, data in message_count.items():
            # Получаем информацию о группе
            group_name = "Неизвестная группа"  # Заглушка, если название не будет получено
            report += f"\nСтатистика для группы '{group_name}':\n"
            report += f"Всего сообщений: {data['total_messages']}\n"
            for user_id, user_data in data['users'].items():
                report += f"Пользователь {user_data['name']} (ID: {user_id}) - {user_data['messages']} сообщений\n"
    
    return report

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    report = await generate_report()
    await context.bot.send_message(chat_id=report_group_id, text=report)

async def clear_data() -> None:
    # Очищаем данные в конце дня
    message_count.clear()

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
    application.job_queue.run_daily(send_daily_report, time=datetime.time(hour=23, minute=59))

    application.run_polling()

if __name__ == '__main__':
    main()
