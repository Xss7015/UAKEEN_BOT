import sqlite3
from pathlib import Path
from config import IMAGES_DIR, DB_PATH

print("=" * 60)
print("🔍 ДИАГНОСТИКА ТОВАРОВ")
print("=" * 60)

# 1. Проверяем БД
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, image_path FROM products")
    rows = cursor.fetchall()
    
    print(f"\n📦 Товаров в БД: {len(rows)}")
    for row in rows:
        print(f"   #{row[0]} {row[1]} ({row[2]})")
        print(f"      📸 {row[3]}")
        # Проверяем файл
        if row[3]:
            file_path = IMAGES_DIR / row[3]
            if file_path.exists():
                print(f"      ✅ Файл существует")
            else:
                print(f"      ❌ ФАЙЛ НЕ НАЙДЕН!")
        else:
            print(f"      ❌ НЕТ ПУТИ К ФОТО!")

print("\n" + "=" * 60)

# 2. Проверяем папки
print("\n📁 ПАПКИ В IMAGES:")
for folder in IMAGES_DIR.iterdir():
    if folder.is_dir():
        photos = list(folder.glob("*.jpg")) + list(folder.glob("*.png")) + list(folder.glob("*.jpeg"))
        print(f"   📂 {folder.name}: {len(photos)} фото")