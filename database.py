import aiosqlite
import asyncio

async def init_db():
    try:
        async with aiosqlite.connect("vape_shop.db") as db:
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
            await db.commit()
            print("✅ База данных успешно инициализирована")

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА при запуске базы данных: {e}")
        # Можно даже принудительно остановить программу,
        # так как без базы бот работать не сможет
        exit(1)

if __name__ == "__main__":
    asyncio.run(init_db)


async def check_or_add_user(tg_id: int,username: str, full_name: str,referrer_id:int = None):
    async with aiosqlite.connect("vape_shop.db") as db:
        cursor = await db.execute("SELECT tg_id FROM users WHERE tg_id = ?", (tg_id,))
        user = await cursor.fetchone()
        if user: #проверка пользовалетля в БД
            return False #пользователь есть
        else:
            initial_balance = 100 
            if referrer_id:
                initial_balance += 50

             
            await db.execute(
                "INSERT INTO users (tg_id, username,full_name,balance,referred_by) VALUES (?,?,?,?,?)", #Пользователя нет
                (tg_id,username,full_name,initial_balance,referrer_id)
            )
            if referrer_id:
                await db.execute(
                    "UPDATE users SET balance = balance + 50 WHERE tg_id = ?",
                    (referrer_id,)
                )
            await db.commit() #это как обычный коммит - сохранение изменений в БД
            return True #пользователь новый
        
async def get_user_balance(tg_id: int):
    async with aiosqlite.connect("vape_shop.db") as db:
        cursor = await db.execute("SELECT balance FROM users WHERE tg_id = ?",(tg_id,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        return 0