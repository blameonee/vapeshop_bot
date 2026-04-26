import os
from dotenv import load_dotenv

from aiogram import Router, types, F
from aiogram.filters import CommandStart,CommandObject 
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from keyboards.reply import for_cmd_start
from keyboards.inline import for_cmd_ubout


from aiogram.types import FSInputFile


from database import check_or_add_user

load_dotenv()

UZ_ADMINA = os.getenv("ADMIN_USERNAME")
START_BONUS = int(os.getenv("START_BONUS", 100)) 
REFERRAL_BONUS = int(os.getenv("REFERRAL_BONUS", 50))

user_router = Router()

users_db = []



@user_router.message(CommandStart())
async def startt(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    args = command.args
    referrer_id = None
    if args and args.isdigit():
        potential_referrer = int(args)
        if potential_referrer != user_id:
            referrer_id = potential_referrer

    is_new_user = await check_or_add_user(
        tg_id= message.from_user.id,
        username= message.from_user.username,
        full_name=message.from_user.full_name,
        referrer_id=referrer_id
    )
    if is_new_user:
        welcome_text = (
            f"Рады видеть тебя в нашем вейп-шопе💨, {message.from_user.full_name}!\n"
            f"Лови на свой баланс {START_BONUS} бонусов💯\n"
        )

        if referrer_id:
            welcome_text += f"🎁 Плюс еще +{REFERRAL_BONUS} бонусов за переход по ссылке друга!\n"
            
        welcome_text += "В нашей системе лояльности 1 бонус = 1 рубль😊"
        
        await message.answer(welcome_text, reply_markup=for_cmd_start)
        
        # Опционально: уведомляем того, кто пригласил
        if referrer_id:
            try:
                # Нам нужен доступ к объекту bot, чтобы отправить сообщение другому юзеру
                await message.bot.send_message(
                    referrer_id, 
                    f"🎉 По твоей ссылке пришел новый друг! Тебе начислено {REFERRAL_BONUS} бонусов."
                )
                
            except Exception:
                pass # Если юзер заблокировал бота, просто игнорируем
    else:
        await message.answer(f"С возвращением, {message.from_user.first_name}! 👋")

@user_router.message(F.text == "Поддержка")
async def supp(message : types.Message):
    await message.answer(f"Для связи с поддержкой пишите сюда - {UZ_ADMINA}")


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
        f"<b>💰 Как накопить больше бонусов?</b>\n\n"
        f"В нашем шопе действует накопительная система:\n\n"
        f"1️⃣ <b>Покупки:</b> Получайте 5% кэшбэка с каждого чека на вашу карту.\n"
        f"2️⃣ <b>Друзья:</b> Приведите друга, и получите по бонусов оба после его первой покупки.\n"
        f"3️⃣ <b>Отзывы:</b> Оставьте отзыв в наших соцсетях и пришлите скриншот менеджеру — начислим {REFERRAL_BONUS} бонусов!\n"
        f"4️⃣ <b>Праздники:</b> В день рождения кэшбэк удваивается (10%)!\n\n"
        f"<i>* 1 бонус = 1 рубль. Бонусами можно оплатить до 30% стоимости покупки.</i>"
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

@user_router.message(F.text == "Приведи друга")
async def invite_friend(message: types.Message):
    user_id = message.from_user.id
    reflink = f"https://t.me/vapeshooops_bot?start={user_id}"
    text = (
        "<b>🤝 Программа «Приведи друга»</b>\n\n"
        "Отправь свою уникальную ссылку другу, и когда он зарегистрируется, "
        f"вы <b>оба</b> получите по {REFERRAL_BONUS} бонусов на баланс! 🎁\n\n"
        f"Твоя ссылка:\n<code>{reflink}</code>\n\n"
        "<i>Нажми на ссылку, чтобы скопировать её.</i>"
    )
    await message.answer(text, parse_mode="HTML")