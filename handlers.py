import aiohttp
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import os
from dotenv import load_dotenv
from utils import get_user_info, get_weather
import logging

logger = logging.getLogger(__name__)

load_dotenv()
token_weather = os.getenv('TOKEN_WEATHER')

async def say_hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    text = update.message.text
    logger.info(f'Получено сообщение: `{text}` от пользователя {user_info}')

    if text == 'Сгенерируй аватар':
        try:
            await context.bot.send_photo(
                chat_id=user_info['chat_id'],
                photo=user_info['ava_url_cat']
            )
            logger.info(f'Отправлен аватар пользователю {user_info['user_id']}')
        except Exception as e:
            logger.error(f'Ошибка при отправке аватара: {e}')
            await context.bot.send_message(
                chat_id=user_info['chat_id'],
                text='Ошибка при отправке аватара 😿'
            )
    elif text == 'Мой ID':
        await context.bot.send_message(
            chat_id=user_info['chat_id'],
            text=f'Ваш Telegram user ID: {user_info['user_id']}'
        )
        logger.info('ID отправлен пользователю')

    elif text == 'Погода сегодня':
        logger.info('Запрошена погода.')
        await request_location(update, context)
    elif text == 'Фото котика':
        logger.info('Запрошено фото котика.')
        await send_cat_photo(update, context)
    elif text.lower().startswith('рандом') or text.lower().startswith('случ'):
        logger.info('Запрошено рандомное число.')
        await send_random_digit(update, context, user_info)
    else:
        await context.bot.send_message(
            chat_id=user_info['chat_id'],
            text=f'{user_info['first_name']}, как твои дела?\n'
                 f'Твои данные:\n'
                 f'ID: {user_info['user_id']}\n'
                 f'Юзернейм: @{user_info['username']}'
        )
        logger.warning(f'Неопознанная команда: {text}')

async def wake_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    button = ReplyKeyboardMarkup([
        ['Фото котика', 'Сгенерируй аватар'],
        ['Мой ID', 'Рандомное число'],
        ['Погода сегодня']
    ], resize_keyboard=True)
    await context.bot.send_message(
        chat_id=user_info['chat_id'],
        text=f'Привет {user_info['username']}, спасибо, что присоединился!',
        reply_markup=button
    )
    logger.info(f'Пользователь {user_info['username']} получил основное меню')

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    await context.bot.send_message(
        chat_id=user_info['chat_id'],
        text=f'Ваш Telegram user ID: {user_info['user_id']}'
    )
    logger.info(f'Пользователь {user_info['user_id']} запросил свой ID')

async def request_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    location_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton('Отправить координаты 📍', request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await context.bot.send_message(
        chat_id=user_info['chat_id'],
        text='Пожалуйста, поделитесь своей геолокацией:',
        reply_markup=location_keyboard
    )
    logger.info('Запрос координат у пользователя')

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    if location is None:
        await update.message.reply_text('Локация не получена, попробуйте снова отправить координаты.')
        logger.warning('Не получена локация от пользователя')
        return
    latitude = location.latitude
    longitude = location.longitude
    context.user_data['location'] = (latitude, longitude)
    try:
        weather_report = await get_weather(latitude, longitude)
        logger.info(f'Погода успешно получена для координат: {latitude}, {longitude}')
    except Exception as e:
        weather_report = 'Ошибка при получении данных о погоде.'
        logger.error(f'Ошибка при запросе погоды: {e}')
    await update.message.reply_text(weather_report)
    main_menu = ReplyKeyboardMarkup(
        [
            ['Фото котика', 'Сгенерируй аватар'],
            ['Мой ID', 'Рандомное число'],
            ['Погода сегодня']
        ],
        resize_keyboard=True
    )
    await update.message.reply_text('🙂', reply_markup=main_menu)

async def send_cat_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    breed_id = 'beng'
    url = f'https://api.thecatapi.com/v1/images/search?breed_ids={breed_id}'
    logger.info('Запрос фото котика')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and 'url' in data[0]:
                        cat_url = data[0]['url']
                    elif data:
                        cat_url = data[0].get('url')
                    else:
                        cat_url = None
                else:
                    cat_url = None
    except Exception as e:
        cat_url = None
        logger.error(f'Ошибка при получении котика: {e}')

    if cat_url:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=cat_url,
            caption='Вот котик бенгальской породы😺:'
        )
        logger.info('Отправлено фото котика')
    else:
        await context.bot.send_message(chat_id=chat_id, text='Не удалось получить фото котика нужной породы 😿')
        logger.warning('Не удалось отправить фото котика')

async def send_random_digit(update: Update, context: ContextTypes.DEFAULT_TYPE, user_info):
    url = 'https://www.randomnumberapi.com/api/v1.0/random?min=1&max=100&count=1'
    logger.info('Запрос рандомного числа через API')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and data:
                        rand_num = data[0]
                        text = f'Ваше случайное число: {rand_num}'
                        logger.info(f'Отправлено число: {rand_num}')
                    else:
                        text = 'Ошибка: API не вернул число!'
                        logger.warning('API не вернул случайное число')
                else:
                    text = 'Ошибка при получении случайного числа!'
                    logger.error(f'Ошибка HTTP при запросе randomnumberapi: статус {resp.status}')
    except Exception as e:
        text = 'Ошибка соединения с сервисом случайных чисел!'
        logger.error(f'Ошибка соединения с randomnumberapi: {e}')
    await context.bot.send_message(chat_id=user_info['chat_id'], text=text)
