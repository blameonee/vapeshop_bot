import aiosqlite
import asyncio

async def init_db():
    try:
        async with aiosqlite.connect("vape_shop.db") as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    tg_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    balance INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    referred_by INTEGER
                )
            """)
            
            # НОВАЯ ТАБЛИЦА: История операций
            await db.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    operation TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (tg_id)
                )
            """)
            
            await db.commit()
            print("✅ База данных и история успешно инициализированы")

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА при запуске базы данных: {e}")
        exit(1)

# Новая функция для добавления записи в историю
async def add_history_item(user_id: int, operation: str):
    async with aiosqlite.connect("vape_shop.db") as db:
        await db.execute(
            "INSERT INTO history (user_id, operation) VALUES (?, ?)",
            (user_id, operation)
        )
        await db.commit()

# Новая функция для получения истории
async def get_user_history(user_id: int):
    async with aiosqlite.connect("vape_shop.db") as db:
        async with db.execute(
            "SELECT operation, timestamp FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 10",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()

async def check_or_add_user(tg_id: int, username: str, full_name: str, start_bonus: int, ref_bonus: int, referrer_id: int = None):
    async with aiosqlite.connect("vape_shop.db") as db:
        cursor = await db.execute("SELECT tg_id FROM users WHERE tg_id = ?", (tg_id,))
        user = await cursor.fetchone()
        
        if user:
            return False 
        else:
            # Используем бонусы из аргументов (которые пришли из .env)
            initial_balance = start_bonus
            if referrer_id:
                initial_balance += ref_bonus

            await db.execute(
                "INSERT INTO users (tg_id, username, full_name, balance, referred_by) VALUES (?,?,?,?,?)",
                (tg_id, username, full_name, initial_balance, referrer_id)
            )
            
            # Сразу записываем в историю новичка
            await db.execute(
                "INSERT INTO history (user_id, operation) VALUES (?, ?)",
                (tg_id, f"✅ Регистрация: +{start_bonus}")
            )
            
            if referrer_id:
                # Начисляем рефереру
                await db.execute(
                    "UPDATE users SET balance = balance + ? WHERE tg_id = ?",
                    (ref_bonus, referrer_id)
                )
                # Записываем в историю реферера
                await db.execute(
                    "INSERT INTO history (user_id, operation) VALUES (?, ?)",
                    (referrer_id, f"👥 Бонус за друга: +{ref_bonus}")
                )
                # Доп. запись в историю новичка про бонус за переход
                await db.execute(
                    "INSERT INTO history (user_id, operation) VALUES (?, ?)",
                    (tg_id, f"🎁 Бонус за приглашение: +{ref_bonus}")
                )

            await db.commit()
            return True

async def get_user_balance(tg_id: int):
    async with aiosqlite.connect("vape_shop.db") as db:
        async with db.execute("SELECT balance FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
        

async def update_user_balance(tg_id: int, amount: int):
    async with aiosqlite.connect("vape_shop.db") as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE tg_id = ?",
            (amount, tg_id)
        )
        await db.commit()
        