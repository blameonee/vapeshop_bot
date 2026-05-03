import os
import time
import hashlib
import qrcode

from dotenv import load_dotenv

from io import BytesIO

from aiogram import Router, types, F
from aiogram.filters import CommandStart,CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import BufferedInputFile

from keyboards.reply import for_cmd_start
from keyboards.inline import for_cmd_ubout

from aiogram.types import FSInputFile

from database import check_or_add_user
from database import get_user_history

load_dotenv()

UZ_ADMINA = os.getenv("ADMIN_USERNAME")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
START_BONUS = int(os.getenv("START_BONUS", 100))
REFERRAL_BONUS = int(os.getenv("REFERRAL_BONUS", 50))

user_router = Router()

users_db = []

def get_dynamic_token(user_id):
    interval = int(time.time() // 600)
    secret_key = os.getenv("SECRET_KEY", "super_secret_vape_key")
    raw_str = f"{user_id}:{interval}:{secret_key}"
    return hashlib.md5(raw_str.encode()).hexdigest()[:8]


@user_router.message(CommandStart())
async def startt(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    args = command.args
    print(f"DEBUG: Получены аргументы: {args}")
    #__проверка для админа__
    if args and args.startswith("admin_check"):
        if user_id == ADMIN_ID:
            try:
                # 1. Разрезаем строку
                parts = args.split("_")
                
                # В строке "admin_check_ID_TOKEN" у нас 4 части
                if len(parts) == 4:
                    # Распаковываем: admin (0), check (1), ID (2), TOKEN (3)
                    _, _, target_id_str, received_token = parts
                    target_id = int(target_id_str)
                else:
                    await message.answer(f"❌ Неверный формат ссылки. Ждал 4 части, пришло {len(parts)}")
                    return
                
                # 2. Проверяем токен
                expected_token = get_dynamic_token(target_id)
                if received_token != expected_token:
                    await message.answer(f"❌ QR-код устарел или неверный!")
                    return

                # 3. Импорт и отправка клавиатуры
                try:
                    from keyboards.inline import get_admin_manage_kb
                    kb = get_admin_manage_kb(target_id)
                except ImportError as e:
                    await message.answer(f"❌ Ошибка импорта: {e}")
                    return

                await message.answer(
                    f"👤 <b>Управление клиентом</b>\n"
                    f"ID: <code>{target_id}</code>\n"
                    f"Статус: Проверка пройдена ✅",
                    reply_markup=kb,
                    parse_mode="HTML"
                )

            except Exception as e:
                print(f"ПОЛНАЯ ОШИБКА: {e}")
                await message.answer(f"❌ Произошла ошибка: {e}")
        else:
            await message.answer(f"🚫 Доступ запрещен. Ваш ID {user_id} не админ.")
        return # Важно! Завершаем работу старта здесь, чтобы не пошла рефералка
    referrer_id = None
    if args and args.isdigit():
        potential_referrer = int(args)
        if potential_referrer != user_id:
            referrer_id = potential_referrer

    is_new_user = await check_or_add_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        start_bonus=START_BONUS,
        ref_bonus=REFERRAL_BONUS,
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

from keyboards.inline import for_card_inline
@user_router.message(F.text == "Виртуальная карта")
async def virtual_card(message: types.Message):
    user_id = message.from_user.id
    balance = await get_user_balance(user_id)
    status = "Клиент 💨"

    if balance < (START_BONUS * 5):
        status = "Любитель пара 🔥"
    text = (
        f"<b>💳 ВАША КАРТА ЛОЯЛЬНОСТИ</b>\n"
        f"──────────────────\n"
        f"👤 <b>Имя:</b> {message.from_user.full_name}\n"
        f"✨ <b>Статус:</b> {status}\n"
        f"💰 <b>Баланс:</b> {balance} бонусов\n"
        f"──────────────────\n"
        f"<i>1 бонус = 1 рубль</i>"
    )
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=for_card_inline
        )



@user_router.callback_query(F.data == "show_history")
async def send_history(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    history_rows = await get_user_history(user_id)

    if not history_rows:
        await callback.message.answer("📜 Ваша история операций пока пуста.")
        return

    text = "<b>📜 Ваша история операций:</b>\n\n"

    for row in history_rows:

        operation, timestamp = row
        text += f"▫️ {operation} <i>({timestamp[:16]})</i>\n"

    await callback.message.answer(text, parse_mode="HTML")


@user_router.callback_query(F.data == "show_qr")
async def send_qr(callback: types.CallbackQuery):
    await callback.answer("Генерирую ваш QR-код")

    user_id = callback.from_user.id
    token = get_dynamic_token(user_id)

    qr_data = f"https://t.me/vapeshooops_bot?start=admin_check_{user_id}_{token}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    await callback.message.answer_photo(
        photo=BufferedInputFile(buffer.read(), filename=f"qr_{user_id}.png"),
        caption=(
            f"<b>📲 Ваш QR-код для кассы</b>\n\n"
            f"Покажите его сотруднику для начисления или списания бонусов.\n"
            f"Ваш ID: <code>{user_id}</code>"
        ),
        parse_mode="HTML"
    )