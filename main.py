import os
import asyncpg
from telethon import TelegramClient
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных окружения из .env файла
load_dotenv()

# Ваши данные для авторизации
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
PRIVATE_CHANNEL_URL = os.getenv('PRIVATE_CHANNEL_URL')

# Создаем клиент Telethon с новым именем сессии
client = TelegramClient('session_name', API_ID, API_HASH)

# Функция для сохранения сообщения в базе данных
async def save_message_to_db(conn, message_id, chat_id, sender_id, text, date):
    query = '''
    INSERT INTO messages (message_id, chat_id, sender_id, text, date)
    VALUES ($1, $2, $3, $4, $5)
    '''
    # Преобразование даты в объект datetime
    if date:
        date = datetime.fromtimestamp(date.timestamp())
    else:
        date = datetime.now()  # Установите значение по умолчанию, если даты нет
    await conn.execute(query, message_id, chat_id, sender_id, text, date)

async def main():
    # Подключение к Telegram
    await client.start(phone=PHONE_NUMBER)

    # Подключение к базе данных PostgreSQL
    conn = await asyncpg.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME')
    )

    # Получаем объект канала
    channel = await client.get_entity(PRIVATE_CHANNEL_URL)

    # Получаем последние 300 сообщений из канала
    async for message in client.iter_messages(channel, limit=500):
        message_id = message.id
        chat_id = message.chat_id
        sender_id = message.sender_id if message.sender_id else None
        text = message.text
        date = message.date

        # Сохраняем сообщение в базе данных
        await save_message_to_db(conn, message_id, chat_id, sender_id, text, date)

    # Закрываем соединение с базой данных
    await conn.close()

    # Завершение работы с клиентом
    await client.disconnect()

# Запускаем клиента и выполняем функцию main
with client:
    client.loop.run_until_complete(main())
