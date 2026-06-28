import json
from pathlib import Path
from config import WEBAPP_DIR

categories = [
    "MAISHIY TEXNIKA",
    "PILESOS VA OCHISTITELLAR",
    "DAZMOL",
    "UY IQLIMI UCHUN",
    "FEN VA TAROZZI",
    "MIKROVOLNOVKA",
    "RAZDELOCHNAYA DOSKA",
    "AEROGRILL",
    "LON",
    "STEKLO",
    "BAKAL/KRUJKA",
    "BLENDER",
    "VAZA",
    "VESHALKA",
    "ZAKRIVALKA",
    "ZAMZAM",
    "NABOR",
    "KAZON",
    "KANFETNITSA",
    "KASKON",
    "KASTRULYA NIKEL",
    "KASTRULYA EMAL",
    "KASTRULYA/BLINNITSA/SOTEYNIK",
    "KERAMIK CHAYNIK",
    "KONFETNITSA",
    "KOSHIK/VILKA/CHOY KOSHIK",
    "PACHKALIY",
    "KOSHIK VILKA NABOR"
]

data = {
    "categories": [
        {"name": cat, "description": " "} for cat in categories
    ]
}

file_path = WEBAPP_DIR / "categories.json"
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ categories.json обновлён! Добавлено {len(categories)} категорий.")