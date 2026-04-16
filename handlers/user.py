from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from keyboards.reply import for_cmd_start
from keyboards.inline import for_cmd_ubout

from aiogram.types import FSInputFile

uz_admina = '@geopaoa'


user_router = Router()

users_db = []


from database import check_or_add_user #импорт нашей функции
@user_router.message(CommandStart())
async def startt(message: types.Message):
    is_new_user = await check_or_add_user(
        tg_id= message.from_user.id,
        username= message.from_user.username,
        full_name=message.from_user.full_name
    )
    if is_new_user:
        await message.answer(
            f"Рады видеть тебя в нашем вейп-шопе💨, {message.from_user.full_name}!\n"
            f"Лови на свой баланс 100 бонусов💯\n"
            f"В нашей системе лояльности 1 бонус = 1 рубль😊\n"
        )
    else:
        await message.answer(f"С возвращением, {message.from_user.first_name}! Рады тебя снова видеть. 👋")

@user_router.message(F.text == "Поддержка")
async def supp(message : types.Message):
    await message.answer(f"Для связи с поддержкой пишите сюда - {uz_admina}")


@user_router.message(F.text == "О нас")
async def about_us(message : types.Message):
    # Используем тройные кавычки, тогда \n ставить не нужно — перенос будет там, где ты нажал Enter
    text = (
        "<b>💨 О нашем Vape Shop</b>\n\n"
        "Мы — команда энтузиастов, которые знают о паре всё!\n"
        "Наша цель — привозить только качественные девайсы.\n\n"
        "<b>Почему выбирают нас?</b>\n"
        "✅ Только оригинальная продукция.\n"
        "✅ Система лояльности.\n\n"
        "📍 Наш адрес: г. Хабаровск, ул. Даунов\n"
        "⏰ Работаем для вас: ежедневно с 10:00 до 22:00.\n\n"
        "Залетай в гости, у нас всегда дымно! ✌️"
    )

    await message.answer(
        text,
        reply_markup=for_cmd_ubout,
        parse_mode="HTML" # МЕНЯЕМ НА HTML
    )

@user_router.message(F.text == "Как получать больше бонусов?")
async def bonus_info(message: types.Message):
    text = (
        "<b>💰 Как накопить больше бонусов?</b>\n\n"
        "В нашем шопе действует накопительная система:\n\n"
        "1️⃣ <b>Покупки:</b> Получайте 5% кэшбэка с каждого чека на вашу карту.\n"
        "2️⃣ <b>Друзья:</b> Приведите друга, и получите по 100 бонусов оба после его первой покупки.\n"
        "3️⃣ <b>Отзывы:</b> Оставьте отзыв в наших соцсетях и пришлите скриншот менеджеру — начислим 50 бонусов!\n"
        "4️⃣ <b>Праздники:</b> В день рождения кэшбэк удваивается (10%)!\n\n"
        "<i>* 1 бонус = 1 рубль. Бонусами можно оплатить до 30% стоимости покупки.</i>"
    )

    await message.answer(text, parse_mode="HTML")

@user_router.message(F.text == "Новинки")
async def news(message: types.Message):
    photo_file = FSInputFile("media/bot_photo.png")
    caption = (
        "<b>🔥 КВАДРАТНЫЕ НОВИНКИ ЭТОЙ НЕДЕЛИ!</b>\n\n"
        "📦 <b>POD-системы:</b>\n"
        "— XROS 4 (новые расцветки) — 2800₽\n"
        "— Vaporesso LUXE Q2 — 2400₽\n\n"
        "🧪 <b>Жидкости:</b>\n"
        "— Husky Premium (Double Ice) — 550₽\n"
        "— Maxwell's (Shoria) — 600₽\n\n"
        "⚡️ <i>Успей забрать, пока всё в наличии!</i>"
    )
    await message.answer_photo(
        photo=photo_file, # Указываем файл картинки
        caption=caption, # Указываем текст
        parse_mode="HTML",
    )

from database import get_user_balance
@user_router.message(F.text == "Мои бонусы")
async def my_balance(message:types.Message):
    user_id = message.from_user.id
    user_balance = await get_user_balance(user_id)
    await message.answer(f"{message.from_user.first_name}, на вашем балансе сейчас {user_balance} бонусов!")
