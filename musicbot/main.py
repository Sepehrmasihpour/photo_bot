import os

from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes , Updater

BOT_TOKEN= os.getenv("BOT_TOKEN")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def mp3_handler(update, context):

    pass

def main():
    Updater = Update("BOT_TOKEN", use_context=True)

 dp = Updater.dispatcher

mp3_filter = filters.document.mime_type('audio/mpeg')
    dp.add_handler(MessageHandler(mp3_filter, mp3_handler))


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token('BOT_TOKEN').build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()