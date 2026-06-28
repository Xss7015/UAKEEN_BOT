import sqlite3
from pathlib import Path
from config import IMAGES_DIR, DB_PATH

print("=" * 60)
print("🔍 ДИАГНОСТИКА")
print("=" * 60)

# 1. Проверяем папку images
print(f"\n📁 Папка images: {IMAGES_DIR}")
print(f"   Существует: {IMAGES_DIR.exists()}")

# 2. Проверяем содержимое
folders = [f for f in IMAGES_DIR.iterdir() if f.is_dir()]
print(f"\n📁 Папки в images/:")
for f in folders:
    print(f"   • {f.name}")

# 3. Проверяем фото в папке dazmol
dazmol_path = IMAGES_DIR / "dazmol"
if dazmol_path.exists():
    photos = list(dazmol_path.glob("*.jpg")) + list(dazmol_path.glob("*.png")) + list(dazmol_path.glob("*.jpeg"))
    print(f"\n📸 Фото в dazmol/: {len(photos)}")
    for p in photos[:5]:
        print(f"   • {p.name}")
else:
    print(f"\n❌ Папка dazmol не найдена!")

# 4. Проверяем БД
try:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"\n📦 Товаров в БД: {count}")
        
        cursor.execute("SELECT id, name, category, image_path FROM products LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   #{row[0]} {row[1]} ({row[2]}) — {row[3]}")
except Exception as e:
    print(f"\n❌ Ошибка БД: {e}")

print("\n" + "=" * 60)