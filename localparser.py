import pandas as pd
import re

# Пути к файлам
energy_drinks_path = './tables/energy_drinks.csv'
errors_path = './tables/errors.csv'
merged_output_path = './tables/merged_energy_drinks.csv'
unparsed_output_path = './tables/unparsed_errors.csv'

# Шаг 1: Чтение файла energy_drinks
try:
    energy_drinks_df = pd.read_csv(energy_drinks_path)
    print("Содержимое energy_drinks.csv:")
    print(energy_drinks_df.head())
except FileNotFoundError:
    print(f"Файл {energy_drinks_path} не найден.")
    energy_drinks_df = pd.DataFrame(columns=['id', 'name', 'model', 'rating', 'description', 'date'])

# Определяем последний ID
last_id = energy_drinks_df['id'].max() if not energy_drinks_df.empty else 0

# Шаг 2: Чтение файла errors как DataFrame
try:
    errors_df = pd.read_csv(errors_path, encoding='utf-8')
    print("Содержимое errors.csv:")
    print(errors_df.head())
except FileNotFoundError:
    print(f"Файл {errors_path} не найден.")
    errors_df = pd.DataFrame(columns=['message'])

# Проверка на наличие данных и корректный формат
if 'message' not in errors_df.columns:
    raise ValueError("Столбец 'message' не найден в файле errors.csv")

# Шаг 3: Парсинг данных из столбца 'message'
parsed_data = []
unparsed_data = []
current_id = last_id + 1

# Функции для поиска различных частей информации
def extract_section(text, section_name):
    match = re.search(f'{section_name}:\s*([^\n]*)', text)
    return match.group(1).strip() if match else ''

# Проход по каждой строке в DataFrame
for _, row in errors_df.iterrows():
    message = row['message']
    
    # Проверяем, что сообщение содержит данные
    if pd.notna(message) and len(message.strip()) > 0:
        name = extract_section(message, 'Название')
        rating = extract_section(message, 'Оценка')
        alt_rating = extract_section(message, 'Альтернативная оценка')
        description = extract_section(message, 'Описание')
        date = extract_section(message, 'Дата')
        
        # Проверяем, удалось ли распарсить основные части
        if name and rating and date:
            # Обрабатываем описание
            if alt_rating:
                description += f"\nАльтернативная оценка: {alt_rating}"
            
            # Добавляем данные в список
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
            # Если данные не удалось распарсить, проверяем на наличие "Название:" и добавляем в нераспарсенные
            if name:
                unparsed_data.append({"message": message})

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

# Шаг 5: Объединяем данные из energy_drinks и parsed_errors
if not parsed_errors_df.empty:
    merged_df = pd.concat([energy_drinks_df, parsed_errors_df], ignore_index=True)
else:
    merged_df = energy_drinks_df

# Шаг 6: Запись объединённых данных в новый CSV файл
merged_df.to_csv(merged_output_path, index=False, encoding='utf-8')
print(f"Данные успешно распарсены, объединены и сохранены в файл {merged_output_path}.")
