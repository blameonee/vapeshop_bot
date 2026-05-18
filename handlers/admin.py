import os
import hashlib
import qrcode
from dotenv import load_dotenv


from aiogram import Router, types, F
from aiogram.filters import CommandStart,CommandObject 
from aiogram.types import BufferedInputFile

admin_router = Router()

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

@admin_router.callback_query(F.data.statswith("add_"))
async def admin_add_points(callback:types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("У вас нет прав", show_alert=True)
        return
    data = callback.data.split("_")
    amount = int(data[1])
    target_id = int(data[2])
    from database import update_user_balance, add_history_item
    await update_user_balance(target_id, amount)
    await add_history_item(target_id, f"💰 Начислено админом: +{amount}")
    await callback.answer(f"Начислено {amount} бонусов!", show_alert=True)
    await callback.message.edit_text(f"✅ Успешно начислено {amount} бонусов пользователю {target_id}")
    try:
        await callback.bot.send_message(target_id, f"🎁 Вам начислено {amount} бонусов!")
    except:
        pass
    