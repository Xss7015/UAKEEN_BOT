from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import is_admin, WEBAPP_URL

WEBAPP_URL_FIXED = f"{WEBAPP_URL}?startapp=uakeen&ngrok-skip-browser-warning=true"

# ===== ТОЛЬКО INLINE КНОПКИ (НИКАКИХ КНОПОК ВНИЗУ) =====

def get_main_menu(user_id: int = None):
    """Asosiy menyu — ТОЛЬКО Admin panel (кнопка Mahsulotlar от BotFather)"""
    buttons = []
    
    # ✅ Только Admin panel (для админов)
    if user_id and is_admin(user_id):
        buttons.append(InlineKeyboardButton(text="👑 Admin panel", callback_data="admin_panel"))
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None

def get_admin_menu():
    """Admin panel — Inline кнопки"""
    buttons = [
        InlineKeyboardButton(text="📥 Mahsulot qo'shish", callback_data="admin_add_product"),
        InlineKeyboardButton(text="📋 Barcha mahsulotlar", callback_data="admin_view_products"),
        InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="admin_edit_product"),
        InlineKeyboardButton(text="🗑️ O'chirish", callback_data="admin_delete_product"),
        InlineKeyboardButton(text="💥 Barchasini o'chirish", callback_data="admin_delete_all"),
        InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_user_stats"),
        InlineKeyboardButton(text="⚠️ Shikoyatlar", callback_data="admin_complaints"),
        InlineKeyboardButton(text="📰 Yangilik qo'shish", callback_data="admin_add_news"),
        InlineKeyboardButton(text="📋 Yangiliklar ro'yxati", callback_data="admin_news_list"),
        InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main")
    ]
    
    keyboard = []
    for i in range(0, len(buttons), 2):
        keyboard.append(buttons[i:i+2])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ===== КНОПКИ ДЛЯ КАРТОЧЕК (INLINE) =====

def get_back_to_categories_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Kategoriyalarga qaytish", callback_data="back_to_categories")]
        ]
    )

def get_product_detail_btn(product_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛒 Savatga", callback_data=f"add_to_cart_{product_id}"),
                InlineKeyboardButton(text="⭐ Sevimlilarga", callback_data=f"fav_{product_id}")
            ],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_products")]
        ]
    )

def get_complaint_actions(complaint_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Hal qilindi", callback_data=f"resolve_{complaint_id}"),
                InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_{complaint_id}")
            ],
            [InlineKeyboardButton(text="📖 Batafsil", callback_data=f"view_{complaint_id}")]
        ]
    )

def get_complaints_list_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Barcha shikoyatlar", callback_data="complaints_list")]
        ]
    )

def get_news_list_btn(news_list):
    buttons = []
    for n in news_list[:10]:
        icon = "🖼️" if n.get('type') == 'photo' else "🎬"
        buttons.append([InlineKeyboardButton(
            text=f"{icon} #{n['id']} - {n['title'][:20]}",
            callback_data=f"news_delete_{n['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)