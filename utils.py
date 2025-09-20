import aiohttp
import os
from telegram import Update

def get_user_info(update: Update):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    message = update.effective_message
    timestamp = int(message.date.timestamp())
    first_name = user.first_name or ''
    last_name = user.last_name or ''
    full_name = f'{first_name} {last_name}'.strip()
    ava_str = f'{user.username or "no_username"}_{user_id}_{first_name[:2]}_{timestamp}'
    ava_url_cat = f'https://robohash.org/{ava_str}?set=set4'
    return {
        'chat_id': chat_id,
        'first_name': first_name,
        'full_name': full_name,
        'ava_url_cat': ava_url_cat,
        'user_id': user_id,
        'username': user.username,
        'timestamp': timestamp
    }

async def get_weather(lat: float, lon: float) -> str:
    token_weather = os.getenv('TOKEN_WEATHER')
    url = f'https://api.openweathermap.org/data/2.5/weather?APPID={token_weather}&lang=ru&units=metric&lat={lat}&lon={lon}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return 'Ошибка при получении данных о погоде'
                data = await resp.json()
    except Exception as e:
        return 'Ошибка соединения с сервером погоды.'
    
    try:
        city = data.get('name', 'Неизвестное место')
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        wind_speed = data['wind']['speed']
        if wind_speed < 5:
            wind_recom = 'Ветра почти нет, погода хорошая, ветра почти нет'
        elif wind_speed < 10:
            wind_recom = 'На улице немного ветрено, оденьтесь чуть теплее'
        elif wind_speed < 20:
            wind_recom = 'Сейчас на улице очень сильный ветер, будьте осторожны, выходя из дома'
        else:
            wind_recom = 'Не лучшее время, на улицу лучше не выходить'

        return (
            f'Сейчас в {city} {weather}\n'
            f'🌡 Температура: {temp}°C (Ощущается как {feels_like}°C)\n'
            f'💨 Скорость ветра: {wind_speed} м/с\n'
            f'{wind_recom}\n'
        )
    except Exception as e:
        return "Ошибка разбора данных о погоде."