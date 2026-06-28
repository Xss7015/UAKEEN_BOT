import sqlite3
from typing import List, Dict, Optional
from config import DB_PATH

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _init_db(self):
        """Создаем все таблицы если их нет"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    brand TEXT,
                    price TEXT,
                    color TEXT,
                    description TEXT,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    ip_address TEXT,
                    country TEXT,
                    city TEXT,
                    region TEXT,
                    timezone TEXT,
                    isp TEXT,
                    first_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    visits_count INTEGER DEFAULT 1
                )
            ''')
            
            # Таблица корзины
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            ''')
            
            # Таблица избранного
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    UNIQUE(user_id, product_id)
                )
            ''')
            
            # ✅ ТАБЛИЦА ЖАЛОБ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    user_name TEXT,
                    username TEXT,
                    employee_id INTEGER,
                    employee_name TEXT,
                    text TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            ''')
            
            # Проверяем и добавляем новые колонки если их нет
            self._add_columns_if_not_exists(cursor)
            
            conn.commit()

    def _add_columns_if_not_exists(self, cursor):
        """Добавляет новые колонки в таблицу users если их нет"""
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_columns = ['ip_address', 'country', 'city', 'region', 'timezone', 'isp']
        for col in new_columns:
            if col not in columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")

    # ============================================================
    # ПОЛЬЗОВАТЕЛИ
    # ============================================================
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, ip_data: Dict = None):
        """Добавить или обновить пользователя с IP и локацией"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            existing = cursor.fetchone()
            
            ip = ip_data.get('ip') if ip_data else None
            country = ip_data.get('country') if ip_data else None
            city = ip_data.get('city') if ip_data else None
            region = ip_data.get('regionName') if ip_data else None
            timezone = ip_data.get('timezone') if ip_data else None
            isp = ip_data.get('isp') if ip_data else None
            
            if existing:
                cursor.execute('''
                    UPDATE users 
                    SET last_visit = CURRENT_TIMESTAMP, 
                        visits_count = visits_count + 1,
                        ip_address = COALESCE(?, ip_address),
                        country = COALESCE(?, country),
                        city = COALESCE(?, city),
                        region = COALESCE(?, region),
                        timezone = COALESCE(?, timezone),
                        isp = COALESCE(?, isp)
                    WHERE id = ?
                ''', (ip, country, city, region, timezone, isp, user_id))
            else:
                cursor.execute('''
                    INSERT INTO users (
                        id, username, first_name, last_name, 
                        ip_address, country, city, region, timezone, isp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name, 
                      ip, country, city, region, timezone, isp))
            
            conn.commit()

    def get_all_users(self) -> List[Dict]:
        """Получить всех пользователей с локацией"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, first_name, last_name, 
                       ip_address, country, city, region, timezone, isp,
                       first_visit, last_visit, visits_count
                FROM users ORDER BY last_visit DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_users_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, first_name, last_name, 
                       ip_address, country, city, region, timezone, isp,
                       first_visit, last_visit, visits_count
                FROM users WHERE id = ?
            ''', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_stats(self) -> Dict:
        """Получить статистику по пользователям"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT country, COUNT(*) FROM users 
                WHERE country IS NOT NULL AND country != ''
                GROUP BY country ORDER BY COUNT(*) DESC
            ''')
            countries = cursor.fetchall()
            
            cursor.execute('''
                SELECT city, COUNT(*) FROM users 
                WHERE city IS NOT NULL AND city != ''
                GROUP BY city ORDER BY COUNT(*) DESC LIMIT 10
            ''')
            cities = cursor.fetchall()
            
            return {
                'total': total,
                'countries': countries,
                'cities': cities
            }

    # ============================================================
    # ТОВАРЫ
    # ============================================================
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category.lower() == 'all':
                cursor.execute("SELECT * FROM products ORDER BY id")
            else:
                cursor.execute(
                    "SELECT * FROM products WHERE LOWER(category) = LOWER(?) ORDER BY id",
                    (category,)
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_all_products(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY id")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_product(self, data: Dict) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO products (name, category, brand, price, color, description, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('name', ''),
                    data.get('category', ''),
                    data.get('brand', ''),
                    data.get('price', ''),
                    data.get('color', ''),
                    data.get('description', ''),
                    data.get('image_path', '')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка добавления товара: {e}")
            return False

    def update_product(self, product_id: int, data: Dict) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE products 
                    SET name = ?, category = ?, brand = ?, price = ?, color = ?, description = ?, image_path = ?
                    WHERE id = ?
                ''', (
                    data.get('name', ''),
                    data.get('category', ''),
                    data.get('brand', ''),
                    data.get('price', ''),
                    data.get('color', ''),
                    data.get('description', ''),
                    data.get('image_path', ''),
                    product_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка обновления: {e}")
            return False

    def delete_product(self, product_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False

    def delete_all_products(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products")
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def get_products_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            return cursor.fetchone()[0]

    def get_all_categories(self) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
            rows = cursor.fetchall()
            return [row[0] for row in rows if row[0]]

    def search_products(self, query: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            search = f"%{query}%"
            cursor.execute('''
                SELECT * FROM products 
                WHERE name LIKE ? OR brand LIKE ? OR category LIKE ? OR description LIKE ?
                ORDER BY name
            ''', (search, search, search, search))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # ============================================================
    # КОРЗИНА
    # ============================================================
    
    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
                    (user_id, product_id)
                )
                existing = cursor.fetchone()
                
                if existing:
                    new_qty = existing[1] + quantity
                    cursor.execute(
                        "UPDATE cart SET quantity = ? WHERE id = ?",
                        (new_qty, existing[0])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                        (user_id, product_id, quantity)
                    )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка добавления в корзину: {e}")
            return False

    def get_cart(self, user_id: int) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.product_id, c.quantity, p.name, p.price, p.brand, p.image_path
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
                ORDER BY c.created_at DESC
            ''', (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM cart WHERE user_id = ? AND product_id = ?",
                    (user_id, product_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка удаления из корзины: {e}")
            return False

    def clear_cart(self, user_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка очистки корзины: {e}")
            return False

    # ============================================================
    # ИЗБРАННОЕ
    # ============================================================
    
    def add_to_favorites(self, user_id: int, product_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)",
                    (user_id, product_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка добавления в избранное: {e}")
            return False

    def remove_from_favorites(self, user_id: int, product_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
                    (user_id, product_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка удаления из избранного: {e}")
            return False

    def get_favorites(self, user_id: int) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT f.id, f.product_id, p.name, p.price, p.brand, p.image_path
                FROM favorites f
                JOIN products p ON f.product_id = p.id
                WHERE f.user_id = ?
                ORDER BY f.created_at DESC
            ''', (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def is_favorite(self, user_id: int, product_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM favorites WHERE user_id = ? AND product_id = ?",
                (user_id, product_id)
            )
            return cursor.fetchone() is not None

    # ============================================================
    # ✅ ЖАЛОБЫ (НОВЫЕ МЕТОДЫ)
    # ============================================================
    
    def add_complaint(self, user_id: str, user_name: str, username: str, 
                      employee_id: int, employee_name: str, text: str) -> int:
        """Добавить жалобу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO complaints (user_id, user_name, username, employee_id, employee_name, text)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, user_name, username, employee_id, employee_name, text))
            conn.commit()
            return cursor.lastrowid

    def get_all_complaints(self) -> List[Dict]:
        """Получить все жалобы"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM complaints ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_complaint(self, complaint_id: int) -> Optional[Dict]:
        """Получить жалобу по ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM complaints WHERE id = ?
            ''', (complaint_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_complaints_count(self) -> int:
        """Количество активных жалоб (pending)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'pending'")
            return cursor.fetchone()[0]

    def get_all_complaints_count(self) -> int:
        """Общее количество жалоб"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM complaints")
            return cursor.fetchone()[0]

    def resolve_complaint(self, complaint_id: int) -> bool:
        """Отметить жалобу как решенную"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE complaints SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (complaint_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def delete_complaint(self, complaint_id: int) -> bool:
        """Удалить жалобу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def get_complaint_time(self, complaint_id: int) -> str:
        """Получить время создания жалобы"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT created_at FROM complaints WHERE id = ?
            ''', (complaint_id,))
            row = cursor.fetchone()
            return row[0] if row else ''


# ===== СОЗДАЕМ ЭКЗЕМПЛЯР =====
db = Database()