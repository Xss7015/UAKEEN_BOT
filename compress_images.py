"""
compress_images.py — СЖАТИЕ ВСЕХ ФОТО В ПАПКЕ
Уменьшает размер фото без потери качества
"""

import os
from pathlib import Path
from PIL import Image
from config import IMAGES_DIR

# Настройки сжатия
MAX_WIDTH = 800
MAX_HEIGHT = 800
QUALITY = 85

def compress_image(file_path):
    """Сжимает одно фото"""
    try:
        img = Image.open(file_path)
        
        # Конвертируем в RGB (если PNG с прозрачностью)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Уменьшаем размер
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
        
        # Сохраняем с оптимизацией
        if file_path.suffix.lower() in ['.jpg', '.jpeg']:
            img.save(file_path, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
        elif file_path.suffix.lower() == '.png':
            img.save(file_path, 'PNG', optimize=True)
        else:
            img.save(file_path, optimize=True)
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {file_path.name} - {e}")
        return False

def compress_all_images():
    """Сжимает все фото в папке images/"""
    print("=" * 60)
    print("🖼️ СЖАТИЕ ФОТО")
    print("=" * 60)
    
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    compressed = 0
    total_size_before = 0
    total_size_after = 0
    
    for folder in IMAGES_DIR.iterdir():
        if not folder.is_dir():
            continue
        
        images = []
        for ext in extensions:
            images.extend(folder.glob(f"*{ext}"))
        
        if not images:
            continue
        
        print(f"\n📂 Папка: {folder.name} ({len(images)} фото)")
        
        for img in images:
            size_before = img.stat().st_size
            total_size_before += size_before
            
            if compress_image(img):
                size_after = img.stat().st_size
                total_size_after += size_after
                compressed += 1
                saved = (1 - size_after / size_before) * 100
                print(f"   ✅ {img.name}: {size_before//1024}KB → {size_after//1024}KB ({-saved:.0f}%)")
    
    print("\n" + "=" * 60)
    print("📊 ИТОГ:")
    print(f"   ✅ Сжато: {compressed} фото")
    print(f"   📦 До: {total_size_before//1024//1024} MB")
    print(f"   📦 После: {total_size_after//1024//1024} MB")
    print(f"   💾 Сэкономлено: {(total_size_before - total_size_after)//1024//1024} MB")
    print("=" * 60)

if __name__ == "__main__":
    compress_all_images()