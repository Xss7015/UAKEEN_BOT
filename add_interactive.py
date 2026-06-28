#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
add_interactive.py — ИНТЕРАКТИВНОЕ ДОБАВЛЕНИЕ ТОВАРОВ
1. Показывает ВСЕ категории с количеством фото
2. Выбираешь категорию по номеру
3. Показывает ВСЕ фото в категории с номерами
4. Выбираешь фото по номерам (1,3,5,7) или all
5. Добавляет выбранные товары в категорию
"""

import os
import sqlite3
import re
from pathlib import Path
from config import IMAGES_DIR, DB_PATH

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

# ===== ВСЕ КАТЕГОРИИ =====
CATEGORY_MAP = {
    'dazmol': 'DAZMOL',
    'chopper': 'CHOPPER',
    'blender': 'BLENDER',
    'mikrovolnovka': 'MIKROVOLNOVKA',
    'pilesos': 'PILESOS VA OCHISTITELLAR',
    'fen va tarozzi': 'FEN VA TAROZZI',
    'aerogrill': 'AEROGRILL',
    'lon': 'LON',
    'steklo': 'STEKLO',
    'vaza': 'VAZA',
    'nabor': 'NABOR',
    'kazon': 'KAZON',
    'kastrylya': 'KASTRULYA',
    'chaynik': 'KERAMIK CHAYNIK',
    'koshik': 'KOSHIK/VILKA/CHOY KOSHIK',
    'uy iqlimi uchun': 'UY IQLIMI UCHUN',
    'razdelochnaya doska': 'RAZDELOCHNAYA DOSKA',
    'koshik vilka nabor': 'KOSHIK VILKA NABOR',
    'kanfetnitsa': 'KANFETNITSA',
    'bakal va krujka': 'BAKAL/KRUJKA',
    'kaskon': 'KASKON',
    'kastrulya nikel': 'KASTRULYA NIKEL',
    'kastrulya emal': 'KASTRULYA EMAL',
    'kastrulya blinitsa soteynik': 'KASTRULYA/BLINNITSA/SOTEYNIK',
    'zam zam': 'ZAMZAM',
    'veshalka': 'VESHALKA',
}

def get_category(folder_name: str) -> str:
    return CATEGORY_MAP.get(folder_name.lower(), folder_name.upper())

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def get_folders_with_photos():
    """Получить все папки с фото"""
    folders = []
    for folder in IMAGES_DIR.iterdir():
        if not folder.is_dir():
            continue
        if folder.name in ['categories', 'employees', 'news']:
            continue
        
        photos = []
        for ext in IMAGE_EXTENSIONS:
            photos.extend(folder.glob(f"*{ext}"))
        
        # Пропускаем папки с photo_ файлами (они уже обработаны)
        real_photos = [p for p in photos if not p.stem.startswith('photo_')]
        
        if real_photos:
            folders.append({
                'name': folder.name,
                'path': folder,
                'photos': real_photos,
                'count': len(real_photos)
            })
    return folders

def show_categories(folders):
    """Показать все категории с номерами"""
    print_header("📂 ВЫБЕРИТЕ КАТЕГОРИЮ")
    for i, f in enumerate(folders, 1):
        category = get_category(f['name'])
        print(f"   {i:2}. {category} ({f['count']} фото)")
    print(f"   {len(folders)+1:2}. 🚪 Выход")
    print("=" * 60)

def show_photos(folder, category):
    """Показать все фото в категории с номерами"""
    print_header(f"📸 ФОТО В КАТЕГОРИИ: {category}")
    print("   Введите номера через запятую (например: 1,3,5,7)")
    print("   Или введите 'all' для выбора всех")
    print("   Или '0' для отмены")
    print("-" * 60)
    
    for i, photo in enumerate(folder['photos'], 1):
        print(f"   {i:3}. {photo.name}")
    
    print("=" * 60)

def get_existing_names():
    """Получить все имена товаров из БД"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products")
        return [row[0] for row in cursor.fetchall()]

def parse_numbers(input_str: str, max_num: int) -> list:
    """Разобрать ввод номеров: 1,3,5-7,9"""
    if input_str.lower() == 'all':
        return list(range(1, max_num + 1))
    
    if input_str.lower() == '0':
        return []
    
    result = []
    # Удаляем пробелы и разбиваем по запятой
    parts = input_str.replace(' ', '').split(',')
    
    for part in parts:
        if not part:
            continue
        
        # Проверяем диапазон 5-7
        if '-' in part:
            try:
                start, end = part.split('-')
                start_num = int(start)
                end_num = int(end)
                for i in range(start_num, end_num + 1):
                    if 1 <= i <= max_num and i not in result:
                        result.append(i)
            except:
                continue
        else:
            try:
                num = int(part)
                if 1 <= num <= max_num and num not in result:
                    result.append(num)
            except:
                continue
    
    return sorted(result)

def add_products(folder, category, selected_indices):
    """Добавить выбранные товары в БД"""
    existing = get_existing_names()
    added = 0
    skipped = 0
    already_exists = 0
    
    print_header("📥 ДОБАВЛЕНИЕ ТОВАРОВ")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        for idx in selected_indices:
            photo = folder['photos'][idx - 1]
            name = photo.stem
            
            # Пропускаем служебные файлы
            if name.startswith('photo_') or name.startswith('news_'):
                print(f"   ⏭️ {name} — служебный файл (пропускаю)")
                skipped += 1
                continue
            
            if name in existing:
                print(f"   ⏭️ {name} — уже есть в БД (пропускаю)")
                already_exists += 1
                continue
            
            relative_path = f"{folder['name']}/{photo.name}"
            try:
                cursor.execute('''
                    INSERT INTO products (name, category, brand, price, color, description, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    name,
                    category,
                    "UAKEEN",
                    "",
                    "",
                    "",
                    relative_path
                ))
                added += 1
                print(f"   ✅ {name} — ДОБАВЛЕН в {category}")
            except Exception as e:
                print(f"   ❌ {name} — ошибка: {e}")
                skipped += 1
        
        conn.commit()
    
    print("-" * 60)
    print(f"   ✅ Добавлено: {added}")
    print(f"   ⏭️ Уже есть в БД: {already_exists}")
    print(f"   ⏭️ Пропущено: {skipped}")
    print("=" * 60)

def main():
    while True:
        clear_screen()
        print("\n" + "=" * 60)
        print("  📦 ИНТЕРАКТИВНОЕ ДОБАВЛЕНИЕ ТОВАРОВ")
        print("=" * 60)
        
        # Получаем папки с фото
        folders = get_folders_with_photos()
        
        if not folders:
            print("\n❌ Нет папок с фото в images/")
            print("📁 Положите фото в папки, например: images/dazmol/")
            input("\nНажмите Enter для выхода...")
            break
        
        # Показываем категории
        show_categories(folders)
        
        # Выбор категории
        try:
            choice = input("\n👉 Выберите номер категории: ").strip()
            if not choice:
                print("❌ Введите число!")
                input("Нажмите Enter...")
                continue
            
            # Проверяем, что введено число
            if not choice.isdigit():
                print("❌ Введите число, а не текст!")
                input("Нажмите Enter...")
                continue
            
            choice_int = int(choice)
            
            # Выход
            if choice_int == len(folders) + 1:
                print("\n👋 До свидания!")
                break
            
            # Проверка диапазона
            if choice_int < 1 or choice_int > len(folders):
                print(f"❌ Введите число от 1 до {len(folders)}!")
                input("Нажмите Enter...")
                continue
            
            selected_folder = folders[choice_int - 1]
            category = get_category(selected_folder['name'])
            
            # Показываем фото
            clear_screen()
            show_photos(selected_folder, category)
            
            # Выбор фото
            while True:
                choice2 = input("\n👉 Введите номера фото (через запятую) или 'all' или '0': ").strip()
                
                if choice2.lower() == '0':
                    break
                
                # Разбираем номера
                selected_indices = parse_numbers(choice2, len(selected_folder['photos']))
                
                if not selected_indices:
                    print("❌ Не выбрано ни одного фото! Попробуйте снова.")
                    continue
                
                # Подтверждение
                print(f"\n📌 Выбрано {len(selected_indices)} фото для категории {category}")
                for idx in selected_indices:
                    print(f"   • {selected_folder['photos'][idx - 1].name}")
                
                confirm = input("\n✅ Добавить? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    add_products(selected_folder, category, selected_indices)
                else:
                    print("❌ Отмена!")
                
                break
            
            input("\nНажмите Enter для продолжения...")
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            input("Нажмите Enter...")

if __name__ == "__main__":
    main()