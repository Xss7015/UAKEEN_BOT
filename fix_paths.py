import sqlite3
from config import DB_PATH

print("=" * 60)
print("🔧 ИСПРАВЛЕНИЕ ПУТЕЙ К ФОТО")
print("=" * 60)

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    
    # Получаем все товары
    cursor.execute("SELECT id, name, image_path FROM products")
    rows = cursor.fetchall()
    
    fixed = 0
    for row in rows:
        product_id, name, image_path = row
        if not image_path:
            continue
        
        # Если путь содержит папку (например pilesos/ZL-944.jpg)
        if '/' in image_path:
            new_path = image_path.split('/')[-1]
            cursor.execute("UPDATE products SET image_path = ? WHERE id = ?", (new_path, product_id))
            fixed += 1
            print(f"   🔄 #{product_id} {name}: {image_path} → {new_path}")
    
    conn.commit()

print(f"\n✅ Исправлено путей: {fixed}")
print("=" * 60)