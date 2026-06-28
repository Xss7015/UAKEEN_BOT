import sqlite3
from pathlib import Path
from config import IMAGES_DIR, DB_PATH

print("=" * 60)
print("🔄 ПОЛНАЯ ОЧИСТКА И ПЕРЕДОБАВЛЕНИЕ")
print("⚠️ ВСЕ ТОВАРЫ БУДУТ УДАЛЕНЫ И ДОБАВЛЕНЫ ЗАНОВО!")
print("=" * 60)

confirm = input("✅ Уверены? (введите 'ДА' для подтверждения): ").strip()
if confirm != 'ДА':
    print("❌ Отмена!")
    exit()

# 1. Удаляем все товары
print("\n1️⃣ Удаляю все товары из БД...")
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    deleted = cursor.rowcount
    conn.commit()
print(f"   ✅ Удалено: {deleted} товаров")

# 2. Сканируем папки и добавляем все фото
print("\n2️⃣ Добавляю все фото из папок...")

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

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

added = 0
skipped = 0

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    
    for folder in IMAGES_DIR.iterdir():
        if not folder.is_dir():
            continue
        if folder.name in ['categories', 'employees', 'news']:
            continue
        
        photos = []
        for ext in IMAGE_EXTENSIONS:
            photos.extend(folder.glob(f"*{ext}"))
        
        if not photos:
            continue
        
        category = get_category(folder.name)
        print(f"\n   📂 {folder.name} → {category} ({len(photos)} фото)")
        
        for img in photos:
            name = img.stem
            
            # Пропускаем служебные
            if name.startswith('photo_') or name.startswith('news_'):
                skipped += 1
                continue
            
            relative_path = f"{folder.name}/{img.name}"
            try:
                cursor.execute('''
                    INSERT INTO products (name, category, brand, price, color, description, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, category, "UAKEEN", "", "", "", relative_path))
                added += 1
                print(f"      ✅ {name}")
            except:
                skipped += 1
    
    conn.commit()

print("\n" + "=" * 60)
print("📊 ИТОГ:")
print(f"   ✅ Добавлено: {added}")
print(f"   ⏭️ Пропущено: {skipped}")
print("=" * 60)

# 3. Проверяем результат
print("\n3️⃣ Проверяю результат...")
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    print(f"   ✅ В БД теперь: {count} товаров")
print("=" * 60)