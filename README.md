# Парсер из закрытого Телеграм канала для Backend приложения "Топ энергетиков"

## 🚀 О проекте

Этот репозиторий содержит приложение "Топ энергетиков", разработанное на **Python** с использованием **Telethon** и **Alembic**.

## 💻 Технологии

[![Технологии](https://skillicons.dev/icons?i=py)](https://skillicons.dev)

## 📂 Структура проекта

```sh
ergy-parser/
│
├── .env                # Переменные окружения
├── .gitignore          # Исключаемые файлы
├── README.md           # Документация
├── tables/
│   ├── merged_energy_drinks.csv    # Полученные данные (конечный материал, который может получиться только после отработки алгоритма)
│
├── main.py             # Точка входа приложения (забирает данные из сообщений и преобразовывает в csv)
├── localparser.py      # Точка входа FastAPI
├── requirements.txt    # Зависимости проекта
├── venv/               # Виртуальное окружение
```

---

## ⚡ Установка и запуск

### 1️⃣ Подготовка окружения

#### Установка зависимостей
```bash
pip install -r requirements.txt
```

#### Создание и активация виртуального окружения
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

#### Подготовка .env
Переименуйте .env.sample в .env и вставьте в него свои значения

### 2️⃣ Настройка и запуск Backend

#### Получение данных из Телеграм канала

Просто выполните следующую команду — она заберет все данные из сообщений в тгк и преобразует в csv (./tables/energy_drinks.csv):
```bash
python main.py
```

#### Преобразование полученных данных 

Преобразование полученных данных в понятный, для backend приложения "Топ энергетиков", вид (./tables/merged_energy_drinks.csv)
```bash
python localparser.py
```

---

## 📌 Требования для данных из канала

#### Сообщения в каналах могут быть только такого вида:
```
Название: Название
Оценка: 0/10
Описание: Описание
Дата: dd.MM.YYYY
```
#### Пример:
1. ![image](https://github.com/user-attachments/assets/5499c358-7c84-4ffb-8ea7-23d8805d35e7)
2. ![image](https://github.com/user-attachments/assets/e18f6916-e233-422f-9e78-9dcc73d0ce6f)
3. ![image](https://github.com/user-attachments/assets/2a4f509f-f7f8-4b81-a1d6-89cd6e59b988)

>Если сообщения не распарсились на этапе получения данных, то они запишутся в ./tables/errors.csv.

>Если сообщения не распарсились на этапе преобразования данных, то они запишутся в ./tables/unparsed_errors.csv.

---

## 🛠 Полезные команды

### Просмотр установленных зависимостей
```bash
pip list
```

### Сохранение зависимостей
```bash
pip freeze > requirements.txt
```

### Удаление всех зависимостей
```bash
pip uninstall -y -r requirements.txt
```
