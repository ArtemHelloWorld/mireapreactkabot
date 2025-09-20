import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers import wake_up, say_hi, my_id, handle_location

def run_bot():
    load_dotenv()
    token = os.getenv('TOKEN')
    if not token:
        raise EnvironmentError("Не найдена обязательная переменная окружения: TOKEN")
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', wake_up))
    app.add_handler(CommandHandler('myID', my_id))
    app.add_handler(MessageHandler(filters.TEXT, say_hi))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.run_polling()
