import feedparser
import asyncio
import logging
import schedule
import time
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Логування для відстеження помилок і подій
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Вказати токен Telegram
TOKEN = '7846084048:AAH5TLUctSLeeVo3liWh-rmB5KsLwWh1_X8'

# Чат ID групи та ID гілки для публікації новин
CHAT_ID = '-1002332086987'
THREAD_ID = '2'


# URL-адреси RSS-каналів
RSS_FEEDS = [
    'http://k.img.com.ua/rss/ua/web.xml',
    'https://itc.ua/ua/feed/',
    'https://hi-tech.ua/uk/tag/shtuchnyj-intelekt/feed/',
    #'https://rss.it.ua/feed.xml',          # IT новини
    #'https://rss.designnews.com/feed.xml'   # Новини дизайну
]

# Функція для збору новин із RSS-каналів
def get_news():
    news_list = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:1]:  # Обмеження до 1 новини
            title = entry.title
            link = entry.link
            news_list.append(f"{title}\n{link}")
    return news_list

# Функція для ручного надсилання новин користувачу, який викликає команду
async def send_news(update, context):
    news_list = get_news()
    for news in news_list:
        await update.message.reply_text(news)

# Функція для надсилання новин у гілку групи
async def post_news_to_group(update, context):
    news_list = get_news()
    for news in news_list:
        await context.bot.send_message(chat_id=CHAT_ID, text=news, message_thread_id=THREAD_ID)
    await update.message.reply_text("Новини успішно надіслані  у гілку групи!")

# Функція для автоматичного постингу новин у гілку групи
async def post_news_automatically(application):
    news_list = get_news()
    for news in news_list:
        await application.bot.send_message(chat_id=CHAT_ID, text=news, message_thread_id=THREAD_ID)

# Налаштування автоматичного постингу
def schedule_news_posting(application):
    async def scheduled_task():
        await post_news_automatically(application)

    schedule.every(2).minutes.do(lambda: asyncio.create_task(scheduled_task()))
    #schedule.every().day.at("00:02").do(lambda: asyncio.create_task(scheduled_task()))
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Головна функція для запуску бота та планувальника
def main():
    # Створення бота з використанням класу Application
    application = Application.builder().token(TOKEN).build()

    # Додаємо команду /news для ручного запиту новин
    application.add_handler(CommandHandler("news", send_news))

    # Додаємо команду /post_news для надсилання новин у групу
    application.add_handler(CommandHandler("post_news", post_news_to_group))

    # Запуск бота
    application.run_polling()

    # Запуск планувальника для автоматичного постингу новин
    schedule_news_posting(application)

if __name__ == '__main__':
    main()