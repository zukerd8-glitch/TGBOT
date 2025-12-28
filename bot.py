from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)

# --------------------------------------------------
# 🔴 ЗАМЕНИ MESSAGE_ID ПОСТОВ В КАНАЛЕ
# --------------------------------------------------
POSTS = {
    "pack_1": 10,   # ← message_id поста в канале
    "pack_2": 20    # ← message_id поста в канале
}

# --------------------------------------------------
# КЛАВИАТУРЫ
# --------------------------------------------------
def main_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    for code in POSTS:
        kb.add(
            InlineKeyboardButton(
                text=f"📦 {code}",
                callback_data=f"get_{code}"
            )
        )
    return kb


def check_subscription_keyboard(code):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text="✅ Я подписался",
            callback_data=f"check_{code}"
        )
    )
    return kb


admin_keyboard = InlineKeyboardMarkup()
admin_keyboard.add(
    InlineKeyboardButton("➕ Добавить пост", callback_data="add_post")
)

# --------------------------------------------------
# ПРОВЕРКА ПОДПИСКИ
# --------------------------------------------------
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

# --------------------------------------------------
# /start
# --------------------------------------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "📂 Выберите набор файлов:",
        reply_markup=main_keyboard()
    )

# --------------------------------------------------
# ПОЛУЧЕНИЕ ФАЙЛОВ
# --------------------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("get_"))
async def get_files(callback: types.CallbackQuery):
    code = callback.data.replace("get_", "")

    if not await is_subscribed(callback.from_user.id):
        await callback.message.answer(
            "🔒 Для доступа подпишитесь на канал и нажмите кнопку ниже.",
            reply_markup=check_subscription_keyboard(code)
        )
        return

    await send_post(callback.message, code)

# --------------------------------------------------
# ПРОВЕРКА ПОДПИСКИ
# --------------------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def check_subscription(callback: types.CallbackQuery):
    code = callback.data.replace("check_", "")

    if await is_subscribed(callback.from_user.id):
        await send_post(callback.message, code)
    else:
        await callback.answer(
            "❌ Подписка не найдена",
            show_alert=True
        )

# --------------------------------------------------
# ОТПРАВКА ПОСТА ИЗ КАНАЛА
# --------------------------------------------------
async def send_post(message, code: str):
    if code not in POSTS:
        await message.answer("❌ Набор файлов не найден")
        return

    await bot.copy_message(
        chat_id=message.chat.id,
        from_chat_id=config.CHANNEL_ID,
        message_id=POSTS[code]
    )

# --------------------------------------------------
# АДМИН-ПАНЕЛЬ
# --------------------------------------------------
@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer(
            "⚙️ Админ-панель",
            reply_markup=admin_keyboard
        )

# --------------------------------------------------
# ДОБАВЛЕНИЕ ПОСТА
# --------------------------------------------------
@dp.callback_query_handler(lambda c: c.data == "add_post")
async def add_post(callback: types.CallbackQuery):
    await callback.message.answer(
        "📌 Отправь сообщение в формате:\n"
        "`код message_id`\n\n"
        "Пример:\n`pack_3 45`",
        parse_mode="Markdown"
    )
    dp.register_message_handler(save_post)

async def save_post(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return

    try:
        code, msg_id = message.text.split()
        POSTS[code] = int(msg_id)
        await message.answer("✅ Пост добавлен")
    except:
        await message.answer("❌ Ошибка формата")

    dp.message_handlers.unregister(save_post)

# --------------------------------------------------
# ЗАПУСК (Render-compatible)
# --------------------------------------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
