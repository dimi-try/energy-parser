import os
import re
import asyncpg
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Загрузка переменных окружения из .env файла
load_dotenv()

# Ваши данные для авторизации
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
DATABASE_URL = os.getenv('DATABASE_URL')
PRIVATE_CHANNEL_URL = os.getenv('PRIVATE_CHANNEL_URL')

# Создаем уникальный файл сессии для каждого устройства
session_file = 'energy_session'

client = TelegramClient(session_file, API_ID, API_HASH)

async def create_tables(conn):
    # Создаем таблицы, если они не существуют
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS energy_drinks (
            id SERIAL PRIMARY KEY,
            name TEXT,
            model TEXT NOT NULL,
            rating TEXT NOT NULL,
            description TEXT,
            date DATE NOT NULL
        )
    ''')

    await conn.execute('''
        CREATE TABLE IF NOT EXISTS brands (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')

async def save_energy_drink_to_db(conn, name, model, rating, description, date):
    # Вставляем данные об энергетике
    await conn.execute('''
        INSERT INTO energy_drinks (name, model, rating, description, date)
        VALUES ($1, $2, $3, $4, $5)
    ''', name, model, rating, description, date)

    # Вставляем или обновляем бренд
    await conn.execute('''
        INSERT INTO brands (name) VALUES ($1)
        ON CONFLICT (name) DO NOTHING
    ''', model)

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
            # Если формат даты неверен, можно обработать исключение
            print(f'Дата в неверном формате: {date_str}')
            return None

        # Разделяем название на модель и остальное
        parts = full_name.split(' ', 1)
        model = parts[0].strip()
        name = parts[1].strip() if len(parts) > 1 else ''

        return name, model, rating, description, date
    return None

async def ensure_authorized():
    if not await client.is_user_authorized():
        # Не авторизован, нужно авторизоваться
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
            
            # Подключаемся к базе данных
            conn = await asyncpg.connect(DATABASE_URL)
            await create_tables(conn)

            # Получаем объект канала
            channel = await client.get_entity(PRIVATE_CHANNEL_URL)

            # Получаем последние 100 сообщений из канала
            async for message in client.iter_messages(channel, limit=10000):
                if message.text:
                    data = parse_message(message.text)
                    if data:
                        name, model, rating, description, date = data
                        await save_energy_drink_to_db(conn, name, model, rating, description, date)

            # Завершение работы с клиентом
            await client.disconnect()
            await conn.close()
    except FloodWaitError as e:
        print(f'Flood wait error: please wait for {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)
        await main()
    except Exception as e:
        print(f'An error occurred: {e}')

# Запускаем клиента и выполняем функцию main
if __name__ == "__main__":
    asyncio.run(main())
