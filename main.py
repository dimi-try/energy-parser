import os
import re
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from dotenv import load_dotenv
import asyncio
import pandas as pd
from datetime import datetime

# Загрузка переменных окружения из .env файла
load_dotenv()

# Ваши данные для авторизации
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
PRIVATE_CHANNEL_URL = os.getenv('PRIVATE_CHANNEL_URL')

# Создаем уникальный файл сессии для каждого устройства
session_file = 'energy_session'

client = TelegramClient(session_file, API_ID, API_HASH)

# Пути к CSV-файлам
energy_drinks_path = './tables/energy_drinks.csv'
errors_path = './tables/errors.csv'

# Инициализация файлов с заголовками (если файл не существует)
if not os.path.exists(energy_drinks_path):
    pd.DataFrame(columns=['name', 'model', 'rating', 'description', 'date']).to_csv(energy_drinks_path, index=False)

if not os.path.exists(errors_path):
    pd.DataFrame(columns=['error_message']).to_csv(errors_path, index=False)

def parse_message(text):
    # Разбираем текст сообщения и извлекаем данные
    pattern = re.compile(r'Название:\s*(.*)\nОценка:\s*(.*)\n(?:Описание:\s*(.*)\n)?Дата:\s*(.*)')
    match = pattern.search(text)
    
    if match:
        full_name = match.group(1).strip()
        rating = match.group(2).strip()
        description = match.group(3).strip() if match.group(3) else ''
        date_str = match.group(4).strip()

        # Конвертируем строку с датой в объект datetime.date
        try:
            date = datetime.strptime(date_str, '%d.%m.%Y').date()
        except ValueError:
            print(f'Дата в неверном формате: {date_str}')
            return None

        # Разделяем название на модель и остальное
        parts = full_name.split(' ', 1)
        model = parts[0].strip()
        name = parts[1].strip() if len(parts) > 1 else ''

        print(f'Parsed data - Name: {name}, Model: {model}, Rating: {rating}, Description: {description}, Date: {date}')
        
        return name, model, rating, description, date
    else:
        # Если не удалось разобрать сообщение, возвращаем его как ошибку
        return text

async def ensure_authorized():
    if not await client.is_user_authorized():
        await client.send_code_request(PHONE_NUMBER)
        code = input('Please enter the code you received: ')
        try:
            await client.sign_in(PHONE_NUMBER, code)
        except SessionPasswordNeededError:
            password = input('Please enter your password: ')
            await client.sign_in(password=password)

async def main():
    try:
        async with client:
            await ensure_authorized()

            # Получаем объект канала
            channel = await client.get_entity(PRIVATE_CHANNEL_URL)

            # Получаем последние 10000 сообщений из канала
            async for message in client.iter_messages(channel, limit=10000):
                if message.text:
                    data = parse_message(message.text)
                    if data:
                        if isinstance(data, tuple):
                            # Сохраняем разобранное сообщение в energy_drinks.csv
                            name, model, rating, description, date = data
                            new_data = pd.DataFrame([{
                                'name': name,
                                'model': model,
                                'rating': rating,
                                'description': description,
                                'date': date
                            }])
                            new_data.to_csv(energy_drinks_path, mode='a', header=False, index=False)
                        else:
                            # Сохраняем ошибку в errors.csv
                            new_error = pd.DataFrame([{'error_message': data}])
                            new_error.to_csv(errors_path, mode='a', header=False, index=False)

            print(f'Данные успешно сохранены в {energy_drinks_path} и ошибки в {errors_path}.')
            await client.disconnect()
    except FloodWaitError as e:
        print(f'Flood wait error: please wait for {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)
        await main()
    except Exception as e:
        print(f'An error occurred: {e}')

# Запускаем клиента и выполняем функцию main
if __name__ == "__main__":
    asyncio.run(main())
