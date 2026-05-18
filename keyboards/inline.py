from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


for_cmd_ubout = InlineKeyboardMarkup(
    inline_keyboard= [
        [
            InlineKeyboardButton(text = "Наш канал",callback_data = 'channel', url= "https://t.me/napaslavandossss")
        ]
    ]
)


for_card_inline = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📱 QR-код", callback_data="show_qr"),
        InlineKeyboardButton(text="📜 История", callback_data="show_history")
    ]
])

def get_admin_manage_kb(target_id):
    builder = InlineKeyboardBuilder()
    # Записываем действие и ID клиента в callback_data
    builder.button(text="+50 бонусов", callback_data=f"add_50_{target_id}")
    builder.button(text="+100 бонусов", callback_data=f"add_100_{target_id}")
    builder.button(text="Списать 100", callback_data=f"sub_100_{target_id}")
    builder.adjust(2)
    return builder.as_markup()