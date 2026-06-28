import time
import sqlite3
from pathlib import Path
from config import IMAGES_DIR, DB_PATH, WEBAPP_DIR

print("=" * 60)
print("🔍 ПРОВЕРКА ОПТИМИЗАЦИИ")
print("=" * 60)

# 1. Проверка БД
start = time.time()
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
print(f"✅ БД: {count} товаров ({(time.time()-start)*1000:.0f} мс)")

# 2. Проверка файлов
start = time.time()
images = list(IMAGES_DIR.glob("**/*.jpg")) + list(IMAGES_DIR.glob("**/*.png"))
print(f"✅ Фото: {len(images)} файлов ({(time.time()-start)*1000:.0f} мс)")

# 3. Проверка WebApp
start = time.time()
html = WEBAPP_DIR / "index.html"
if html.exists():
    size = html.stat().st_size / 1024
    print(f"✅ index.html: {size:.1f} KB ({(time.time()-start)*1000:.0f} мс)")
else:
    print("❌ index.html не найден!")

# 4. Проверка стилей
start = time.time()
css = WEBAPP_DIR / "style.css"
if css.exists():
    size = css.stat().st_size / 1024
    print(f"✅ style.css: {size:.1f} KB ({(time.time()-start)*1000:.0f} мс)")

# 5. Проверка скрипта
start = time.time()
js = WEBAPP_DIR / "script.js"
if js.exists():
    size = js.stat().st_size / 1024
    print(f"✅ script.js: {size:.1f} KB ({(time.time()-start)*1000:.0f} мс)")

print("=" * 60)
print("✅ Проверка завершена!")