import pandas as pd
import re

# Пути к файлам
energy_drinks_path = './tables/energy_drinks.csv'
errors_path = './tables/errors.csv'
merged_output_path = './tables/data.csv'
unparsed_output_path = './tables/unparsed_errors.csv'

# Шаг 1: Чтение файла energy_drinks
try:
    energy_drinks_df = pd.read_csv(energy_drinks_path)
    print("Содержимое energy_drinks.csv:")
    print(energy_drinks_df.head())
except FileNotFoundError:
    print(f"Файл {energy_drinks_path} не найден.")
    # Создаем пустой DataFrame с нужными столбцами, включая 'id'
    energy_drinks_df = pd.DataFrame(columns=['id', 'name', 'model', 'rating', 'description', 'date'])

# Добавляем столбец 'id', если его нет в таблице
if 'id' not in energy_drinks_df.columns:
    energy_drinks_df['id'] = range(1, len(energy_drinks_df) + 1)

# Определяем последний ID
last_id = energy_drinks_df['id'].max() if not energy_drinks_df.empty else 0

# Шаг 2: Чтение файла errors как DataFrame
try:
    errors_df = pd.read_csv(errors_path, encoding='utf-8')
    print("Содержимое errors.csv:")
    print(errors_df.head())
except FileNotFoundError:
    print(f"Файл {errors_path} не найден.")
    errors_df = pd.DataFrame(columns=['error_message'])

# Проверка на наличие данных и корректный формат
if 'error_message' not in errors_df.columns:
    raise ValueError("Столбец 'error_message' не найден в файле errors.csv")

# Шаг 3: Парсинг данных из столбца 'error_message'
parsed_data = []
unparsed_data = []
current_id = last_id + 1

# Функция для извлечения секции текста с учетом многострочного описания
def extract_section(text, section_name):
    # Поиск с учетом регистра и многострочности
    match = re.search(rf'{section_name}:\s*(.*?)(?=\n\S+:|$)', text, re.DOTALL)
    return match.group(1).strip() if match else ''

# Проход по каждой строке в DataFrame
for _, row in errors_df.iterrows():
    message = row['error_message']
    
    # Проверяем, что сообщение содержит данные
    if pd.notna(message) and len(message.strip()) > 0:
        name = extract_section(message, 'Название')
        rating = extract_section(message, 'Оценка')
        description = extract_section(message, 'Описание')
        date = extract_section(message, 'Дата')
        
        # # Вывод для отладки
        # print(f"Message: {message}")
        # print(f"Extracted Name: {name}")
        # print(f"Extracted Rating: {rating}")
        # print(f"Extracted Description: {description}")
        # print(f"Extracted Date: {date}")
        
        # Проверяем, удалось ли распарсить основные части
        if name and rating and date:
            parsed_data.append({
                "id": current_id,
                "name": name,
                "model": name,  # В данном случае название и модель совпадают
                "rating": rating,
                "description": description,
                "date": date
            })
            current_id += 1
        else:
            # Добавляем в нераспарсенные
            unparsed_data.append({"error_message": message})


# Проверка результатов парсинга
parsed_errors_df = pd.DataFrame(parsed_data)
unparsed_errors_df = pd.DataFrame(unparsed_data)
print("Распарсенные данные из errors.csv:")
print(parsed_errors_df.head())
print("Нераспарсенные данные из errors.csv:")
print(unparsed_errors_df.head())

# Шаг 4: Запись нераспарсенных данных в новый CSV файл
if not unparsed_errors_df.empty:
    unparsed_errors_df.to_csv(unparsed_output_path, index=False, encoding='utf-8')
    print(f"Нераспарсенные данные сохранены в файл {unparsed_output_path}.")

# Шаг 5: Объединение данных из energy_drinks и parsed_errors
if not parsed_errors_df.empty:
    merged_df = pd.concat([energy_drinks_df, parsed_errors_df], ignore_index=True)
else:
    merged_df = energy_drinks_df

# Применение изменений перед записью в CSV

# 1. Разделение name и model (если в model больше одного слова, отделяем первое слово)
def split_name_model(row):
    model_words = row['model'].split()
    if len(model_words) > 1:
        # Если в модели больше одного слова, разделяем
        row['model'] = model_words[0]  # Первое слово остаётся в model
        row['name'] = ' '.join(model_words[1:])  # Остальные слова переносятся в name
    return row

merged_df = merged_df.apply(split_name_model, axis=1)

# 2. Оставляем только числовое значение рейтинга
merged_df['rating'] = merged_df['rating'].apply(lambda x: re.match(r'\d+(\.\d+)?', x).group() if re.match(r'\d+(\.\d+)?', x) else x)

# 3. Приводим дату к формату YYYY-MM-DD
def fix_date(date):
    if re.match(r'\d{2}\.\d{2}\.\d{4}', date):
        return pd.to_datetime(date, format='%d.%m.%Y').strftime('%Y-%m-%d')
    elif re.match(r'\d{2}\.\d{2}\.\d{2}', date):
        return pd.to_datetime(date, format='%d.%m.%y').strftime('%Y-%m-%d')
    return date

merged_df['date'] = merged_df['date'].apply(fix_date)

# Определяем порядок столбцов
column_order = ['id', 'name', 'model', 'rating', 'description', 'date']

# Применяем порядок столбцов
merged_df = merged_df.reindex(columns=column_order)

# Шаг 6: Запись объединённых данных в новый CSV файл
merged_df.to_csv(merged_output_path, index=False, encoding='utf-8')
print(f"Данные успешно распарсены, изменены и сохранены в файл {merged_output_path}.")
