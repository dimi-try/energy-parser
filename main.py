import os
from telethon import TelegramClient
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Ваши данные для авторизации
API_ID = os.getenv('API_ID')  # Ваш API_ID
API_HASH = os.getenv('API_HASH')  # Ваш API_HASH
PHONE_NUMBER = os.getenv('PHONE_NUMBER')  # Ваш номер телефона для авторизации

# Создаем клиент Telethon
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    # Подключение к Telegram
    await client.start(phone=PHONE_NUMBER)

    # Приватная ссылка или ID канала
    private_channel_url = os.getenv('PRIVATE_CHANNEL_URL')  # Приватная ссылка на ваш канал
    
    # Получаем объект канала
    channel = await client.get_entity(private_channel_url)

    # Получаем последние 100 сообщений из канала
    async for message in client.iter_messages(channel, limit=100):
        print(f"ID: {message.id} | Текст сообщения: {message.text}")

    # Завершение работы с клиентом
    await client.disconnect()

# Запускаем клиента и выполняем функцию main
with client:
    client.loop.run_until_complete(main())
