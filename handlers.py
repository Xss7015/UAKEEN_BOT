import logging
import json
import aiohttp
from datetime import datetime
from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

from config import get_image_path, image_exists, is_admin, IMAGES_DIR, WEBAPP_URL, IP_API_URL, ADMIN_IDS, WEBAPP_DIR, BASE_DIR
from database import db
from keyboards import get_main_menu, get_admin_menu, get_complaint_actions, get_complaints_list_btn, get_news_list_btn
logger = logging.getLogger(__name__)

class Handlers:
    def __init__(self, dp):
        self.dp = dp
        self.admin_states = {}
        self.webapp_available = WEBAPP_URL.startswith("https://")
        self.news_dir = WEBAPP_DIR / "images" / "news"
        self.news_dir.mkdir(parents=True, exist_ok=True)
        self._register_handlers()

    def _register_handlers(self):
        # ===== КОМАНДЫ =====
        self.dp.message.register(self.start_cmd, Command("start"))
        self.dp.message.register(self.cancel_cmd, Command("cancel"))
        
        # ===== ОБЫЧНЫЕ КНОПКИ =====
        self.dp.message.register(self.back_to_main, F.text == "🔙 Asosiy menyuga")
        
        if not self.webapp_available:
            self.dp.message.register(self.show_categories_fallback, F.text == "🛍️ Mahsulotlar")
        
        self.dp.message.register(self.show_chopper, F.text == "⚡ Chopper")
        
        # ===== INLINE CALLBACK =====
        self.dp.callback_query.register(self.inline_main_menu, F.data == "main_menu")
        self.dp.callback_query.register(self.inline_admin_panel, F.data == "admin_panel")
        self.dp.callback_query.register(self.inline_back_to_main, F.data == "back_to_main")
        
        # ===== АДМИН КНОПКИ =====
        self.dp.message.register(self.admin_panel, F.text == "👑 Admin panel")
        self.dp.message.register(self.admin_add_product, F.text == "📥 Mahsulot qo'shish")
        self.dp.message.register(self.admin_view_products, F.text == "📋 Barcha mahsulotlar")
        self.dp.message.register(self.admin_edit_product, F.text == "✏️ Mahsulotni tahrirlash")
        self.dp.message.register(self.admin_delete_product, F.text == "🗑️ Mahsulotni o'chirish")
        self.dp.message.register(self.admin_delete_all, F.text == "💥 Barcha mahsulotlarni o'chirish")
        self.dp.message.register(self.admin_users, F.text == "👥 Foydalanuvchilar")
        self.dp.message.register(self.admin_user_stats, F.text == "📊 Statistika")
        self.dp.message.register(self.admin_complaints, F.text == "⚠️ Shikoyatlar")
        self.dp.message.register(self.admin_add_news, F.text == "📰 Yangilik qo'shish")
        self.dp.message.register(self.admin_news_list, F.text == "📋 Yangiliklar ro'yxati")
        
        # ===== WEBAPP DATA =====
        self.dp.message.register(self.handle_webapp_data, F.web_app_data)
        
        # ===== ОБРАБОТКА ФОТО/ВИДЕО ОТ АДМИНА =====
        self.dp.message.register(self.handle_admin_news_photo, F.photo)
        self.dp.message.register(self.handle_admin_news_video, F.video)
        self.dp.message.register(self.handle_admin_all_text, F.text)
        
        # ===== INLINE КОЛБЭКИ =====
        self.dp.callback_query.register(self.back_to_categories_callback, F.data == "back_to_categories")
        self.dp.callback_query.register(self.back_to_products_callback, F.data == "back_to_products")
        self.dp.callback_query.register(self.add_to_cart_callback, F.data.startswith("add_to_cart_"))
        self.dp.callback_query.register(self.fav_callback, F.data.startswith("fav_"))
        
        # ===== АДМИН INLINE КОЛБЭКИ =====
        self.dp.callback_query.register(self.admin_delete_callback, F.data.startswith("admin_delete_"))
        self.dp.callback_query.register(self.admin_edit_callback, F.data.startswith("admin_edit_"))
        self.dp.callback_query.register(self.admin_back_to_list, F.data == "admin_back_to_list")
        self.dp.callback_query.register(self.admin_complaint_action, F.data.startswith("complaint_"))
        self.dp.callback_query.register(self.admin_delete_news_callback, F.data.startswith("news_delete_"))
        
        # ===== INLINE АДМИН КОЛБЭКИ =====
        self.dp.callback_query.register(self.inline_admin_add_product, F.data == "admin_add_product")
        self.dp.callback_query.register(self.inline_admin_view_products, F.data == "admin_view_products")
        self.dp.callback_query.register(self.inline_admin_edit_product, F.data == "admin_edit_product")
        self.dp.callback_query.register(self.inline_admin_delete_product, F.data == "admin_delete_product")
        self.dp.callback_query.register(self.inline_admin_delete_all, F.data == "admin_delete_all")
        self.dp.callback_query.register(self.inline_admin_users, F.data == "admin_users")
        self.dp.callback_query.register(self.inline_admin_stats, F.data == "admin_user_stats")
        self.dp.callback_query.register(self.inline_admin_complaints, F.data == "admin_complaints")
        self.dp.callback_query.register(self.inline_admin_add_news, F.data == "admin_add_news")
        self.dp.callback_query.register(self.inline_admin_news_list, F.data == "admin_news_list")

    # ============================================================
    # INLINE МЕНЮ
    # ============================================================
    
    async def inline_main_menu(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        await callback.message.delete()
        await callback.message.answer(
            "👋 *Asosiy menyu:*",
            parse_mode="Markdown",
            reply_markup=get_main_menu(user_id)
        )
        await callback.answer()

    async def inline_back_to_main(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        await callback.message.delete()
        await callback.message.answer(
            "👋 *Asosiy menyu:*",
            parse_mode="Markdown",
            reply_markup=get_main_menu(user_id)
        )
        await callback.answer()

    async def inline_admin_panel(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Sizda ruxsat yo'q!", show_alert=True)
            return
        
        await callback.message.delete()
        await self._admin_panel_text(callback.message, user_id)
        await callback.answer()

    # ============================================================
    # INLINE АДМИН ФУНКЦИИ
    # ============================================================
    
    async def inline_admin_add_product(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_add_product(callback.message)
        await callback.answer()

    async def inline_admin_view_products(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_view_products(callback.message)
        await callback.answer()

    async def inline_admin_edit_product(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_edit_product(callback.message)
        await callback.answer()

    async def inline_admin_delete_product(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_delete_product(callback.message)
        await callback.answer()

    async def inline_admin_delete_all(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_delete_all(callback.message)
        await callback.answer()

    async def inline_admin_users(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_users(callback.message)
        await callback.answer()

    async def inline_admin_stats(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_user_stats(callback.message)
        await callback.answer()

    async def inline_admin_complaints(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_complaints(callback.message)
        await callback.answer()

    async def inline_admin_add_news(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_add_news(callback.message)
        await callback.answer()

    async def inline_admin_news_list(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_news_list(callback.message)
        await callback.answer()

    # ============================================================
    # ПОЛУЧЕНИЕ IP
    # ============================================================
    
    async def get_ip_location(self, ip: str = None) -> dict:
        try:
            url = f"{IP_API_URL}{ip}" if ip else IP_API_URL
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'success':
                            return {
                                'ip': data.get('query'),
                                'country': data.get('country'),
                                'countryCode': data.get('countryCode'),
                                'city': data.get('city'),
                                'region': data.get('regionName'),
                                'timezone': data.get('timezone'),
                                'isp': data.get('isp'),
                                'lat': data.get('lat'),
                                'lon': data.get('lon')
                            }
        except Exception as e:
            logger.error(f"IP ошибка: {e}")
        return {}

    # ============================================================
    # START
    # ============================================================
    
    async def start_cmd(self, message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
    
        ip_data = await self.get_ip_location()
        db.add_user(user_id, username, first_name, last_name, ip_data)
    
        logger.info(f"👤 Новый: {first_name} (@{username}) | ID: {user_id}")
    
    # ✅ Убрали упоминание кнопки Mahsulotlar
        text = (
            f"👋 *Assalomu alaykum, {first_name}!*\n\n"
            f"*UAKEEN O'zbekiston* do'koniga xush kelibsiz!"
        )
        
        reply_markup = get_main_menu(user_id)
        await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)

    # ============================================================
    # ОТМЕНА И НАЗАД
    # ============================================================
    
    async def cancel_cmd(self, message: types.Message):
        user_id = message.from_user.id
        if user_id in self.admin_states:
            del self.admin_states[user_id]
            await message.answer("❌ Amal bekor qilindi!", reply_markup=get_main_menu(user_id))
        else:
            await message.answer("Hech qanday faol amal yo'q.")

    async def back_to_main(self, message: types.Message):
        user_id = message.from_user.id
        await message.answer("✅ *Asosiy menyu:*", parse_mode="Markdown", reply_markup=get_main_menu(user_id))

    async def show_categories_fallback(self, message: types.Message):
        categories = db.get_all_categories()
        if not categories:
            await message.answer("📭 *Hozircha mahsulotlar yo'q!*", parse_mode="Markdown")
            return
        text = "📂 *Kategoriyalar:*\n\n" + "\n".join([f"• {cat} - {len(db.get_products_by_category(cat))} ta" for cat in categories])
        await message.answer(text, parse_mode="Markdown")

    async def show_chopper(self, message: types.Message):
        await message.answer("⚡ *Chopper bo'limi*\n\nBu bo'lim hozircha ishlab chiqilmoqda.\nTez orada mahsulotlar paydo bo'ladi!", parse_mode="Markdown")

    # ============================================================
    # WEBAPP DATA
    # ============================================================
    
    async def handle_webapp_data(self, message: types.Message):
        try:
            data = json.loads(message.web_app_data.data)
            if data.get('action') == 'complaint':
                await self._handle_complaint(message, data)
        except Exception as e:
            logger.error(f"WebApp xatolik: {e}")
            await message.answer("❌ Xatolik yuz berdi!")

    async def _handle_complaint(self, message: types.Message, data: dict):
        employee_id = data.get('employee_id')
        employee_name = data.get('employee_name')
        user_id = data.get('user_id')
        user_name = data.get('user_name', 'Foydalanuvchi')
        username = data.get('username', '')
        complaint_text = data.get('text', '')
        
        if not complaint_text:
            await message.answer("❌ Shikoyat matni kiritilmadi!")
            return
        if len(complaint_text) > 500:
            await message.answer("❌ Shikoyat 500 belgidan oshmasligi kerak!")
            return
        
        complaint_id = db.add_complaint(user_id, user_name, username, employee_id, employee_name, complaint_text)
        
        admin_text = (
            f"⚠️ *YANGI SHIKOYAT!* #{complaint_id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Xodim:* {employee_name}\n"
            f"🆔 *Xodim ID:* {employee_id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Foydalanuvchi:* {user_name}\n"
            f"🆔 *User ID:* {user_id or 'Nomalum'}\n"
            f"📱 *Username:* @{username if username else 'Nomalum'}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 *Shikoyat matni:*\n{complaint_text}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 *Vaqt:* {db.get_complaint_time(complaint_id)}"
        )
        
        keyboard = get_complaint_actions(complaint_id)
        
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        chat_id=admin_id,
                        text=admin_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки админу {admin_id}: {e}")
            await message.answer("✅ Shikoyatingiz yuborildi! Tez orada ko'rib chiqamiz.")
        else:
            await message.answer("⚠️ Admin topilmadi!")

    # ============================================================
    # АДМИН ПАНЕЛЬ
    # ============================================================
    
    async def admin_panel(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("⛔ Sizda ruxsat yo'q!")
            return
        await self._admin_panel_text(message, user_id)

    async def _admin_panel_text(self, message: types.Message, user_id: int):
        users_count = db.get_users_count()
        products_count = db.get_products_count()
        complaints_count = db.get_complaints_count()
        stats = db.get_user_stats()
    
        news_file = WEBAPP_DIR / "news.json"
        news_count = 0
        if news_file.exists():
            try:
                with open(news_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    news_count = len(data.get('news', []))
            except:
                pass
    
        countries_text = ""
        if stats['countries']:
             countries_text = "\n\n🌍 *Mamlakatlar:*\n"
             for country, count in stats['countries'][:5]:
                 countries_text += f"   • {country or 'Nomalum'}: {count} ta\n"
    
        await message.answer(
            f"👑 *Admin panel*\n\n"
            f"📊 *Statistika:*\n"
            f"   • 👥 Foydalanuvchilar: {users_count}\n"
            f"   • 📦 Mahsulotlar: {products_count}\n"
            f"   • ⚠️ Shikoyatlar: {complaints_count}\n"
            f"   • 📰 Yangiliklar: {news_count}{countries_text}\n\n"
            f"Amalni tanlang:",
            parse_mode="Markdown",
            reply_markup=get_admin_menu()  # ✅ ИСПРАВЛЕНО!
        )

    # ============================================================
    # АДМИН: НОВОСТИ
    # ============================================================
    
    async def admin_add_news(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("⛔ Sizda ruxsat yo'q!")
            return
        
        await message.answer(
            "📰 *Yangi yangilik qo'shish*\n\n"
            "1️⃣ *Rasm yoki video yuboring*\n"
            "2️⃣ *Keyin matn yozing*\n\n"
            "📌 Bekor qilish: `/cancel`",
            parse_mode="Markdown"
        )
        self.admin_states[user_id] = {"action": "add_news", "step": "waiting_media"}

    async def handle_admin_news_photo(self, message: types.Message):
        user_id = message.from_user.id
        
        if not is_admin(user_id) or user_id not in self.admin_states:
            return
        if self.admin_states[user_id].get("action") != "add_news":
            return
        
        try:
            photo = message.photo[-1]
            file = await message.bot.get_file(photo.file_id)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_{timestamp}.jpg"
            file_path = self.news_dir / filename
            
            await message.bot.download_file(file.file_path, file_path)
            
            self.admin_states[user_id]["media_path"] = filename
            self.admin_states[user_id]["media_type"] = "photo"
            self.admin_states[user_id]["step"] = "waiting_text"
            
            await message.answer(
                "✅ *Rasm qabul qilindi!*\n\n✏️ Endi matn yozing:\n📌 `/cancel`",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Rasm yuklash xatolik: {e}")
            await message.answer("❌ Rasm yuklashda xatolik!")

    async def handle_admin_news_video(self, message: types.Message):
        user_id = message.from_user.id
        
        if not is_admin(user_id) or user_id not in self.admin_states:
            return
        if self.admin_states[user_id].get("action") != "add_news":
            return
        
        try:
            video = message.video
            file = await message.bot.get_file(video.file_id)
            
            if file.file_size > 50 * 1024 * 1024:
                await message.answer("❌ Video 50MB dan oshmasligi kerak!")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_{timestamp}.mp4"
            file_path = self.news_dir / filename
            
            await message.bot.download_file(file.file_path, file_path)
            
            self.admin_states[user_id]["media_path"] = filename
            self.admin_states[user_id]["media_type"] = "video"
            self.admin_states[user_id]["step"] = "waiting_text"
            
            await message.answer(
                "✅ *Video qabul qilindi!*\n\n✏️ Endi matn yozing:\n📌 `/cancel`",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Video yuklash xatolik: {e}")
            await message.answer("❌ Video yuklashda xatolik!")

    async def handle_admin_all_text(self, message: types.Message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text.startswith("/") or not is_admin(user_id) or user_id not in self.admin_states:
            return
        
        state = self.admin_states[user_id]
        if state.get("action") != "add_news" or state.get("step") != "waiting_text":
            return
        
        media_path = state.get("media_path", "")
        media_type = state.get("media_type", "photo")
        
        if not media_path:
            await message.answer("❌ Avval rasm/video yuboring!")
            return
        
        file_path = self.news_dir / media_path
        if not file_path.exists():
            await message.answer(f"❌ Fayl topilmadi: {media_path}")
            return
        
        # Разбираем текст (если есть | — разделяем)
        if "|" in text:
            parts = text.split("|")
            title = parts[0].strip()
            description = " | ".join(parts[1:]).strip()
        else:
            title = text
            description = "Yangilik"
        
        if len(title) < 3:
            title = f"Yangilik #{datetime.now().strftime('%H%M')}"
            description = text
        
        # Путь к фото
        if media_type == "photo":
            image_url = f"/webapp/images/news/{media_path}"
            video_url = ""
        else:
            image_url = ""
            video_url = f"/webapp/images/news/{media_path}"
        
        # Сохраняем в news.json
        news_file = WEBAPP_DIR / "news.json"
        news_data = {"news": []}
        if news_file.exists():
            try:
                with open(news_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
            except:
                pass
        
        new_id = max([n.get('id', 0) for n in news_data.get('news', [])] or [0]) + 1
        new_news = {
            "id": new_id,
            "type": media_type,
            "title": title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": description,
            "image": image_url,
            "video": video_url
        }
        
        news_data["news"].insert(0, new_news)
        
        with open(news_file, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        
        await message.answer(
            f"✅ *Yangilik qo'shildi!* #{new_id}\n\n"
            f"📌 *Sarlavha:* {title}\n"
            f"📝 *Tavsif:* {description}\n"
            f"📸 *Turi:* {'🖼️ Rasm' if media_type == 'photo' else '🎬 Video'}",
            parse_mode="Markdown"
        )
        
        del self.admin_states[user_id]
        logger.info(f"📰 Yangilik: {title} (ID: {new_id})")

    # ============================================================
    # АДМИН: СПИСОК НОВОСТЕЙ
    # ============================================================
    
    async def admin_news_list(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("⛔ Ruxsat yo'q!")
            return
        
        news_file = WEBAPP_DIR / "news.json"
        if not news_file.exists():
            await message.answer("📭 Yangiliklar yo'q!")
            return
        
        try:
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            news_list = data.get('news', [])
        except:
            await message.answer("❌ Xatolik!")
            return
        
        if not news_list:
            await message.answer("📭 Yangiliklar yo'q!")
            return
        
        keyboard = get_news_list_btn(news_list[:10])
        text = f"📰 *Yangiliklar:* (jami: {len(news_list)})\n\n"
        for n in news_list[:10]:
            icon = "🖼️" if n.get('type') == 'photo' else "🎬"
            text += f"{icon} #{n['id']} - {n['title']}\n   📅 {n['date']}\n\n"
        
        if len(news_list) > 10:
            text += f"... va yana {len(news_list) - 10} ta"
        
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

    async def admin_delete_news_callback(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
            return
        
        news_id = int(callback.data.split("_")[-1])
        news_file = WEBAPP_DIR / "news.json"
        
        if not news_file.exists():
            await callback.answer("❌ Topilmadi!", show_alert=True)
            return
        
        try:
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            news_list = data.get('news', [])
            removed = False
            for i, n in enumerate(news_list):
                if n.get('id') == news_id:
                    # Удаляем файл
                    if n.get('image'):
                        img_path = self.news_dir / n['image'].split('/')[-1]
                        if img_path.exists():
                            img_path.unlink()
                    if n.get('video'):
                        video_path = self.news_dir / n['video'].split('/')[-1]
                        if video_path.exists():
                            video_path.unlink()
                    del news_list[i]
                    removed = True
                    break
            
            if removed:
                data['news'] = news_list
                with open(news_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                await callback.message.delete()
                await callback.message.answer(f"✅ Yangilik #{news_id} o'chirildi!")
                await callback.answer("✅ O'chirildi!")
            else:
                await callback.answer("❌ Topilmadi!", show_alert=True)
                
        except Exception as e:
            logger.error(f"Xatolik: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # АДМИН: ПОЛЬЗОВАТЕЛИ
    # ============================================================
    
    async def admin_users(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        
        users = db.get_all_users()
        if not users:
            await message.answer("👥 Foydalanuvchilar yo'q!")
            return
        
        text = f"👥 *Foydalanuvchilar:* (jami: {len(users)})\n\n"
        for u in users[:20]:
            name = u['first_name'] or "Ismsiz"
            username = f"@{u['username']}" if u['username'] else "Yo'q"
            location = ""
            if u.get('city') or u.get('country'):
                location = f"📍 {u.get('city', '?')}, {u.get('country', '?')}"
            elif u.get('ip_address'):
                location = f"🌐 {u.get('ip_address')}"
            
            text += f"• {name} ({username})\n  👤 ID: {u['id']}\n"
            if location:
                text += f"  {location}\n"
            text += f"  📅 Tashrif: {u['visits_count']}\n\n"
            
            if len(text) > 3500:
                await message.answer(text, parse_mode="Markdown")
                text = ""
        if text:
            await message.answer(text, parse_mode="Markdown")

    # ============================================================
    # АДМИН: СТАТИСТИКА
    # ============================================================
    
    async def admin_user_stats(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        
        stats = db.get_user_stats()
        text = f"📊 *Statistika:*\n\n👥 *Jami:* {stats['total']} ta\n\n"
        
        if stats['countries']:
            text += "🌍 *Mamlakatlar:*\n"
            for country, count in stats['countries'][:10]:
                text += f"   • {country or 'Nomalum'}: {count} ta\n"
        
        if stats['cities']:
            text += "\n🏙️ *Shaharlar:*\n"
            for city, count in stats['cities'][:10]:
                text += f"   • {city or 'Nomalum'}: {count} ta\n"
        
        await message.answer(text, parse_mode="Markdown")

    # ============================================================
    # АДМИН: ЖАЛОБЫ
    # ============================================================
    
    async def admin_complaints(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        
        complaints = db.get_all_complaints()
        if not complaints:
            await message.answer("📭 Shikoyatlar yo'q!")
            return
        
        text = f"⚠️ *Shikoyatlar:* (jami: {len(complaints)})\n\n"
        for c in complaints[:10]:
            status_emoji = "🟡" if c['status'] == 'pending' else "🟢"
            text += f"{status_emoji} #{c['id']} - {c['employee_name']}\n   👤 {c['user_name']} | 📅 {c['created_at'][:16]}\n   📝 {c['text'][:50]}...\n\n"
        
        if len(complaints) > 10:
            text += f"\n... va yana {len(complaints) - 10} ta"
        
        await message.answer(text, parse_mode="Markdown", reply_markup=get_complaints_list_btn())

    async def admin_complaint_action(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
            return
        
        parts = callback.data.split('_')
        action = parts[1]
        complaint_id = int(parts[2])
        
        if action == 'resolve':
            db.resolve_complaint(complaint_id)
            await callback.message.edit_text(callback.message.text + "\n\n✅ *Hal qilindi!*", parse_mode="Markdown")
            await callback.answer("✅ Hal qilindi!")
        elif action == 'delete':
            db.delete_complaint(complaint_id)
            await callback.message.delete()
            await callback.answer("🗑️ O'chirildi!")
        elif action == 'view':
            complaint = db.get_complaint(complaint_id)
            if complaint:
                text = (
                    f"⚠️ *Shikoyat #{complaint['id']}*\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 *Xodim:* {complaint['employee_name']}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 *Foydalanuvchi:* {complaint['user_name']}\n"
                    f"📱 *Username:* @{complaint['username'] or 'Nomalum'}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📝 *Matn:*\n{complaint['text']}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📅 *Vaqt:* {complaint['created_at']}\n"
                    f"📊 *Holat:* {'🟡 Kutilmoqda' if complaint['status'] == 'pending' else '🟢 Hal qilindi'}"
                )
                await callback.message.answer(text, parse_mode="Markdown")
            await callback.answer()

    # ============================================================
    # АДМИН: ТОВАРЫ
    # ============================================================
    
    async def admin_add_product(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        
        images = list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png")) + list(IMAGES_DIR.glob("*.jpeg"))
        images_text = "\n".join([f"   • {img.name}" for img in images]) if images else "   ❌ Rasm yo'q"
        
        await message.answer(
            f"📥 *Mahsulot qo'shish*\n\n"
            f"📸 *Rasmlar:*\n{images_text}\n\n"
            f"✏️ Format: `Model | Kategoriya | Brend`\n"
            f"*Misol:* `ZL-813B | DAZMOL | UAKEEN`\n\n"
            f"📌 `/cancel`",
            parse_mode="Markdown"
        )
        self.admin_states[user_id] = {"action": "add_product", "step": "waiting_for_data"}

    async def admin_view_products(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        
        products = db.get_all_products()
        if not products:
            await message.answer("📭 Mahsulotlar yo'q!")
            return
        
        text = "📋 *Barcha mahsulotlar:*\n\n"
        for p in products:
            img = "📸" if p['image_path'] else "❌"
            text += f"#{p['id']} {img} *{p['name']}*\n   📂 {p['category']} | 🏷 {p['brand']}\n\n"
            if len(text) > 3500:
                await message.answer(text, parse_mode="Markdown")
                text = ""
        if text:
            await message.answer(text, parse_mode="Markdown")

    async def admin_edit_product(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        await message.answer("✏️ *Tahrirlash*\n\nID kiriting:\n*Misol:* `1`\n\n📌 `/cancel`", parse_mode="Markdown")
        self.admin_states[user_id] = {"action": "edit_product", "step": "waiting_for_id"}

    async def admin_delete_product(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        await message.answer("🗑️ *O'chirish*\n\nID kiriting:\n*Misol:* `1`\n\n📌 `/cancel`", parse_mode="Markdown")
        self.admin_states[user_id] = {"action": "delete_product", "step": "waiting_for_id"}

    async def admin_delete_all(self, message: types.Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        await message.answer("⚠️ *DIQQAT!*\n\nBarcha mahsulotlarni o'chirish?\n\nTasdiqlash: `HA`\n📌 `/cancel`", parse_mode="Markdown")
        self.admin_states[user_id] = {"action": "delete_all", "step": "waiting_for_confirm"}

    # ============================================================
    # АДМИН: ВВОД
    # ============================================================
    
    async def handle_admin_input(self, message: types.Message):
        user_id = message.from_user.id
        
        if message.text.startswith("/") or not is_admin(user_id) or user_id not in self.admin_states:
            return
        
        state = self.admin_states[user_id]
        text = message.text.strip()
        
        if state["action"] == "add_product" and state["step"] == "waiting_for_data":
            parts = [p.strip() for p in text.split("|")]
            if len(parts) == 1:
                model, category, brand = parts[0], "DAZMOL", "UAKEEN"
            elif len(parts) >= 3:
                model, category, brand = parts[0], parts[1].upper(), parts[2]
            else:
                await message.answer("❌ `Model | Kategoriya | Brend`", parse_mode="Markdown")
                return
            
            image_path = self._get_image_path_by_model(model)
            if db.add_product({"name": model, "category": category, "brand": brand, "price": "", "color": "", "description": "", "image_path": image_path}):
                await message.answer(f"✅ *Qo'shildi!*\n📌 {model}\n📂 {category}\n🏷 {brand}\n📸 {'✅' if image_path else '❌'}", parse_mode="Markdown")
            else:
                await message.answer("❌ Xatolik!")
            del self.admin_states[user_id]
            return
        
        if state["action"] == "delete_product" and state["step"] == "waiting_for_id":
            if not text.isdigit():
                await message.answer("❌ ID raqam!")
                return
            product_id = int(text)
            product = db.get_product_by_id(product_id)
            if not product:
                await message.answer(f"❌ #{product_id} topilmadi!")
                return
            db.delete_product(product_id)
            await message.answer(f"✅ #{product_id} '{product['name']}' o'chirildi!")
            del self.admin_states[user_id]
            return
        
        if state["action"] == "delete_all" and state["step"] == "waiting_for_confirm":
            if text.upper() == "HA":
                db.delete_all_products()
                await message.answer("💥 *Barcha mahsulotlar o'chirildi!*", parse_mode="Markdown")
            else:
                await message.answer("❌ Bekor qilindi!")
            del self.admin_states[user_id]
            return
        
        if state["action"] == "edit_product" and state["step"] == "waiting_for_id":
            if not text.isdigit():
                await message.answer("❌ ID raqam!")
                return
            product_id = int(text)
            product = db.get_product_by_id(product_id)
            if not product:
                await message.answer(f"❌ #{product_id} topilmadi!")
                return
            await message.answer(
                f"✏️ *Mahsulot #{product_id}*\n\n"
                f"Joriy: {product['name']} | {product['category']} | {product['brand']}\n\n"
                f"Yangi: `Model | Kategoriya | Brend`\n"
                f"📌 `/cancel`",
                parse_mode="Markdown"
            )
            self.admin_states[user_id] = {"action": "edit_product_confirm", "step": "waiting_for_data", "product_id": product_id}
            return
        
        if state["action"] == "edit_product_confirm" and state["step"] == "waiting_for_data":
            product_id = state["product_id"]
            parts = [p.strip() for p in text.split("|")]
            if len(parts) >= 3:
                model, category, brand = parts[0], parts[1].upper(), parts[2]
            else:
                await message.answer("❌ `Model | Kategoriya | Brend`", parse_mode="Markdown")
                return
            image_path = self._get_image_path_by_model(model)
            if db.update_product(product_id, {"name": model, "category": category, "brand": brand, "price": "", "color": "", "description": "", "image_path": image_path}):
                await message.answer(f"✅ *Mahsulot #{product_id} yangilandi!*", parse_mode="Markdown")
            else:
                await message.answer("❌ Xatolik!")
            del self.admin_states[user_id]
            return

    # ============================================================
    # CALLBACKS
    # ============================================================
    
    async def back_to_categories_callback(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await callback.message.answer("📂 *Kategoriyani tanlang:*", parse_mode="Markdown", reply_markup=category_menu)
        await callback.answer()

    async def back_to_products_callback(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await callback.answer()

    async def add_to_cart_callback(self, callback: types.CallbackQuery):
        product_id = callback.data.split("_")[-1]
        product = db.get_product_by_id(int(product_id))
        if product:
            await callback.answer(f"✅ {product['name']} savatga qo'shildi!", show_alert=True)
        else:
            await callback.answer("❌ Topilmadi", show_alert=True)

    async def fav_callback(self, callback: types.CallbackQuery):
        await callback.answer("⭐ Sevimlilarga qo'shildi!", show_alert=True)

    async def admin_delete_callback(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
            return
        product_id = int(callback.data.split("_")[-1])
        product = db.get_product_by_id(product_id)
        if product:
            db.delete_product(product_id)
            await callback.message.delete()
            await callback.message.answer(f"✅ Mahsulot #{product_id} o'chirildi!")
            await callback.answer("✅ O'chirildi!")
        else:
            await callback.answer("❌ Topilmadi", show_alert=True)

    async def admin_edit_callback(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
            return
        product_id = int(callback.data.split("_")[-1])
        product = db.get_product_by_id(product_id)
        if not product:
            await callback.answer("❌ Topilmadi", show_alert=True)
            return
        await callback.message.delete()
        await callback.message.answer(
            f"✏️ *Mahsulot #{product_id}*\n\n"
            f"Joriy: {product['name']} | {product['category']} | {product['brand']}\n\n"
            f"Yangi: `Model | Kategoriya | Brend`\n"
            f"📌 `/cancel`",
            parse_mode="Markdown"
        )
        self.admin_states[user_id] = {"action": "edit_product_confirm", "step": "waiting_for_data", "product_id": product_id}
        await callback.answer()

    async def admin_back_to_list(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await self.admin_view_products(callback.message)
        await callback.answer()

    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ
    # ============================================================
    
    def _get_image_path_by_model(self, model: str) -> str:
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        for ext in extensions:
            path = IMAGES_DIR / f"{model}{ext}"
            if path.exists():
                return f"{model}{ext}"
        return ""