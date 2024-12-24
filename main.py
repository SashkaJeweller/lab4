import json
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Загрузка данных о мероприятиях из JSON файла
def load_events():
    with open('events.json', 'r', encoding='utf-8') as file:
        return json.load(file)


# Получение уникальных городов из мероприятий
def get_cities(events):
    return set(event['city'] for event in events)


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Привет! Я бот-афиша. Выберите город с помощью команды /city.")


# Обработчик команды /city
async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = load_events()
    cities = get_cities(events)

    keyboard = [[KeyboardButton(city) for city in cities]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите город:", reply_markup=reply_markup)


# Обработчик выбора города
async def handle_city_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_city = update.message.text
    events = load_events()

    # Фильтрация мероприятий по выбранному городу
    city_events = [event for event in events if event['city'].lower() == selected_city.lower()]

    if not city_events:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Извините, в городе '{selected_city}' нет запланированных мероприятий.")
        return

    message = f"Мероприятия в городе {selected_city}:\n\n"

    for event in city_events:
        message += (f"{event['title']} в {event['location']}\n"

                    f"Дата: {event['date']}\n"
                    f"Время: {event['time']}\n"
                    f"Описание: {event['description']}\n\n")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Основная функция
def main():
    # Создание экземпляра приложения
    application = ApplicationBuilder().token('8038163785:AAF1yZrtbSQXUEVoWamstjN_TP9SqhCZ5Ik').build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('city', city))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city_selection))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
