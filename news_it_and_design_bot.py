import feedparser
from telegram import Bot
from telegram.ext import Updater, CommandHandler
import schedule
import time

# Вкажіть ваш токен Telegram
TOKEN = '7846084048:AAH5TLUctSLeeVo3liWh-rmB5KsLwWh1_X8'
bot = Bot(token=TOKEN)

# Чат ID групи, де будуть публікуватися новини
CHAT_ID = '-1002332086987'

# URL-адреси RSS-каналів
RSS_FEEDS = [
    'https://rss.it.ua/feed.xml',          # IT новини
    'https://rss.designnews.com/feed.xml'  # Новини дизайну
]

# Функція для збору новин із RSS-каналів
def get_news():
    news_list = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:  # Обмеження до 5 останніх новин
            title = entry.title
            link = entry.link
            news_list.append(f"{title}\n{link}")
    return news_list

# Функція для ручного надсилання новин користувачу, який викликає команду
def send_news(update, context):
    news_list = get_news()
    for news in news_list:
        update.message.reply_text(news)

# Функція для надсилання новин у групу
def post_news_to_group(update, context):
    news_list = get_news()
    for news in news_list:
        bot.send_message(chat_id=CHAT_ID, text=news)
    update.message.reply_text("Новини успішно надіслані у групу!")

# Функція для автоматичного постингу новин
def post_news_automatically():
    news_list = get_news()
    for news in news_list:
        bot.send_message(chat_id=CHAT_ID, text=news)

# Головна функція для запуску бота та планувальника
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Додаємо команду /news для ручного запиту новин користувачу
    dp.add_handler(CommandHandler("news", send_news))

    # Додаємо команду /post_news для надсилання новин у групу
    dp.add_handler(CommandHandler("post_news", post_news_to_group))

    # Налаштовуємо автоматичний постинг новин кожного дня о 9:00
    schedule.every().day.at("09:00").do(post_news_automatically)

    # Запускаємо бот
    updater.start_polling()

    # Цикл для планувальника
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()