import json
import sqlite3
from pathlib import Path
from aiohttp import web
from config import WEBAPP_DIR, DB_PATH, IMAGES_DIR

class WebServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.runner = None

    def setup_routes(self):
        # HTML
        self.app.router.add_get('/', self.serve_index)
        self.app.router.add_get('/index.html', self.serve_index)
        self.app.router.add_get('/products.html', self.serve_products)
        self.app.router.add_get('/employees.html', self.serve_employees_html)
        
        # CSS + JS (с кэшированием)
        self.app.router.add_get('/style.css', self.serve_css)
        self.app.router.add_get('/script.js', self.serve_js)
        
        # JSON
        self.app.router.add_get('/categories.json', self.serve_categories)
        self.app.router.add_get('/employees.json', self.serve_employees)
        self.app.router.add_get('/news.json', self.serve_news)
        
        # API
        self.app.router.add_get('/api/products', self.get_products)
        self.app.router.add_get('/api/products/{category}', self.get_products_by_category)
        
        # ✅ СТАТИКА С КЭШИРОВАНИЕМ
        self.app.router.add_static('/images', str(IMAGES_DIR), append_version=True)
        self.app.router.add_static('/webapp/images', str(WEBAPP_DIR / 'images'), append_version=True)

    # ===== СТРАНИЦЫ С КЭШИРОВАНИЕМ =====
    async def serve_index(self, request):
        file_path = WEBAPP_DIR / 'index.html'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Cache-Control': 'public, max-age=3600',
                'Content-Type': 'text/html'
            })
        return web.Response(text="<h1>404</h1>", content_type='text/html')

    async def serve_products(self, request):
        file_path = WEBAPP_DIR / 'products.html'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Cache-Control': 'public, max-age=3600',
                'Content-Type': 'text/html'
            })
        return web.Response(text="<h1>404</h1>", content_type='text/html')

    async def serve_employees_html(self, request):
        file_path = WEBAPP_DIR / 'employees.html'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Cache-Control': 'public, max-age=3600',
                'Content-Type': 'text/html'
            })
        return web.Response(text="<h1>404</h1>", content_type='text/html')

    async def serve_css(self, request):
        file_path = WEBAPP_DIR / 'style.css'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Content-Type': 'text/css',
                'Cache-Control': 'public, max-age=86400'  # 24 часа
            })
        return web.Response(text="", content_type='text/css')

    async def serve_js(self, request):
        file_path = WEBAPP_DIR / 'script.js'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Content-Type': 'application/javascript',
                'Cache-Control': 'public, max-age=86400'  # 24 часа
            })
        return web.Response(text="", content_type='application/javascript')

    # ===== JSON С КЭШИРОВАНИЕМ =====
    async def serve_categories(self, request):
        file_path = WEBAPP_DIR / 'categories.json'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Content-Type': 'application/json',
                'Cache-Control': 'public, max-age=3600'
            })
        return web.json_response({"categories": []})

    async def serve_employees(self, request):
        file_path = WEBAPP_DIR / 'employees.json'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Content-Type': 'application/json',
                'Cache-Control': 'public, max-age=3600'
            })
        return web.json_response({"employees": []})

    async def serve_news(self, request):
        file_path = WEBAPP_DIR / 'news.json'
        if file_path.exists():
            return web.FileResponse(file_path, headers={
                'Content-Type': 'application/json',
                'Cache-Control': 'public, max-age=3600'
            })
        return web.json_response({"news": []})

    # ===== API С КЭШИРОВАНИЕМ =====
    async def get_products(self, request):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, category, brand, price, color, description, image_path FROM products")
                rows = cursor.fetchall()
                products = [dict(row) for row in rows]
                return web.json_response(products, headers={
                    'Cache-Control': 'public, max-age=300'  # 5 минут
                })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def get_products_by_category(self, request):
        category = request.match_info.get('category', '').lower()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, category, brand, price, color, description, image_path FROM products WHERE LOWER(category) = ?",
                    (category,)
                )
                rows = cursor.fetchall()
                products = [dict(row) for row in rows]
                return web.json_response(products, headers={
                    'Cache-Control': 'public, max-age=300'
                })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def start(self):
        import os
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        port = int(os.environ.get("PORT", 8080))
        site = web.TCPSite(self.runner, host='0.0.0.0', port=port)
        await site.start()
        print(f"✅ Веб-сервер запущен на порту {port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            print("🛑 Веб-сервер остановлен")

web_server = WebServer()