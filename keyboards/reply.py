from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton
for_cmd_start = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = "Виртуальная карта"), KeyboardButton(text = "Мои бонусы")],
        [KeyboardButton(text = "Поддержка"), KeyboardButton(text = "О нас")],
        [KeyboardButton(text = "Новинки"), KeyboardButton(text = "Как получать больше бонусов?")],
        [KeyboardButton(text = "Приведи друга")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите раздел..."
)