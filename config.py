import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

BOT_TOKEN = os.getenv("BOT_TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
ADMIN_IDS = os.getenv("ADMIN_ID", "0").split(',')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS if id.strip().isdigit()]

IMAGES_DIR = BASE_DIR / "images"
DB_PATH = BASE_DIR / "data" / "products.db"
WEBAPP_DIR = BASE_DIR / "webapp"

WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", os.environ.get("PORT", 8080)))
WEBAPP_URL = os.getenv("WEBAPP_URL", f"http://localhost:{WEB_PORT}")

IP_API_URL = os.getenv("IP_API_URL", "http://ip-api.com/json/")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")

IMAGES_DIR.mkdir(exist_ok=True)
DB_PATH.parent.mkdir(exist_ok=True)
WEBAPP_DIR.mkdir(exist_ok=True)
(WEBAPP_DIR / "images").mkdir(exist_ok=True)

def get_image_path(filename: str) -> Path:
    return IMAGES_DIR / filename

def image_exists(filename: str) -> bool:
    return get_image_path(filename).exists()

def get_image_path_by_model(model: str) -> str:
    extensions = ['.jpg', '.jpeg', '.png', '.webp']
    for ext in extensions:
        path = IMAGES_DIR / f"{model}{ext}"
        if path.exists():
            return f"{model}{ext}"
    return ""

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

print(f"✅ Конфигурация загружена:")
print(f"   - Режим: {ENVIRONMENT}")
print(f"   - Админы: {ADMIN_IDS}")
print(f"   - WebApp URL: {WEBAPP_URL}")
print(f"   - Папка фото: {IMAGES_DIR}")
print(f"   - Папка webapp: {WEBAPP_DIR}")
print(f"   - БД: {DB_PATH}")