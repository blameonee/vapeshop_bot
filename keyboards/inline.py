from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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