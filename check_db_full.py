import sqlite3
from pathlib import Path
from config import IMAGES_DIR, DB_PATH

print("=" * 60)
print("🔍 ПОЛНАЯ ДИАГНОСТИКА БД")
print("=" * 60)

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, image_path FROM products")
    rows = cursor.fetchall()
    
    print(f"\n📦 ВСЕГО ТОВАРОВ: {len(rows)}\n")
    
    valid = 0
    invalid = 0
    
    for row in rows:
        product_id, name, category, image_path = row
        
        # Проверяем путь
        if not image_path:
            print(f"❌ #{product_id} {name} — НЕТ ПУТИ К ФОТО")
            invalid += 1
            continue
        
        # Проверяем файл
        file_path = IMAGES_DIR / image_path
        if file_path.exists():
            print(f"✅ #{product_id} {name} ({category}) — ФОТО ЕСТЬ: {image_path}")
            valid += 1
        else:
            # Проверяем другие расширения
            found = False
            base = Path(image_path).stem
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                test_path = IMAGES_DIR / f"{base}{ext}"
                if test_path.exists():
                    print(f"⚠️ #{product_id} {name} — ФОТО НАЙДЕНО С ДРУГИМ РАСШИРЕНИЕМ: {test_path.name}")
                    found = True
                    break
            
            if not found:
                print(f"❌ #{product_id} {name} — ФАЙЛ НЕ НАЙДЕН: {image_path}")
                invalid += 1

print("\n" + "=" * 60)
print(f"📊 ИТОГ:")
print(f"   ✅ Валидных товаров: {valid}")
print(f"   ❌ Невалидных товаров: {invalid}")
print("=" * 60)