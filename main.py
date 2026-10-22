import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "SIZNING_BOT_TOKENINGIZ"

# Asosiy menyu
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Testlar"), KeyboardButton(text="📊 Javoblari")],
        [KeyboardButton(text="ℹ️ Biz haqimizda")]
    ],
    resize_keyboard=True
)

# Bekor qilish tugmasi (kod kiritishdan chiqib ketish uchun)
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
    resize_keyboard=True
)

# Holatlar (FSM)
class TestState(StatesGroup):
    waiting_for_code = State()

# Test kodlari bazasi 
# (Bu yerda '224' kodi maxfiy kanaldan olingan Word faylining file_id raqamiga bog'lanadi)
TEST_DATABASE = {
    "224": {
        "title": "Oksidlar mavzusi",
        "file_id": "BQACAgIAAxkBAAIC... (shu yerga Telegram beradigan fayl ID yoziladi)"
    },
    "225": {
        "title": "Kislotalar mavzusi",
        "file_id": "BQACAgIAAxkBAAIC... (boshqa fayl ID)"
    }
}

dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n"
        "<b>\"Kimyo sirlari\"</b> botiga xush kelibsiz. Marhamat, bo'limni tanlang:",
        reply_markup=main_keyboard
    )

# 1. "Testlar" bosilganda bot kod so'raydi
@dp.message(F.text == "📝 Testlar")
async def ask_for_code(message: Message, state: FSMContext):
    await state.set_state(TestState.waiting_for_code)
    await message.answer(
        "📝 Videosdagi test kodini kiriting (masalan: <b>224</b>):\n\n"
        "<i>(Kod yuborishni to'xtatish uchun pastdagi tugmani bosing)</i>",
        reply_markup=cancel_keyboard,
        parse_mode=ParseMode.HTML
    )

# Bekor qilish
@dp.message(F.text == "❌ Bekor qilish")
async def cancel_process(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_keyboard)

# 2. Obunachi yuborgan kodni qabul qilib, Word faylni tashlab berish
@dp.message(TestState.waiting_for_code)
async def check_test_code(message: Message, state: FSMContext, bot: Bot):
    code = message.text.strip()
    
    if code in TEST_DATABASE:
        test_info = TEST_DATABASE[code]
        await message.answer(f"✅ Topildi! <b>{test_info['title']}</b> testi yuborilmoqda...", parse_mode=ParseMode.HTML)
        
        # Maxfiy kanaldagi Word faylni obunachiga yuboramiz (file_id orqali)
        # Eslatma: Kanaldagi faylni yuborish uchun bot o'sha maxfiy kanalga ADMIN qilingan bo'lishi kerak!
        try:
            await bot.send_document(
                chat_id=message.chat.id,
                document=test_info["file_id"],
                caption=f"📚 <b>{test_info['title']}</b> testining Word varianti.\n"
                        "\"Kimyo sirlari\" kanali uchun maxsus!"
            )
        except Exception as e:
            await message.answer("⚠️ Faylni yuborishda xatolik yuz berdi. Iltimos, admin bilan bog'laning.")
            
        await state.clear()
        await message.answer("Boshqa bo'limni tanlashingiz mumkin:", reply_markup=main_keyboard)
    else:
        await message.answer("❌ Bunday kod topilmadi! Iltimos, to'g'ri kod kiriting (masalan: 224) yoki bekor qiling.")

# "Biz haqimizda" va "Javoblari"
@dp.message(F.text == "ℹ️ Biz haqimizda")
async def about(message: Message):
    await message.answer("ℹ️ <b>\"Kimyo sirlari\"</b> kanali va boti — kimyo fanini oson o'rganish uchun!")

@dp.message(F.text == "📊 Javoblari")
async def answers(message: Message):
    await message.answer("📊 Test javoblarini ko'rish uchun ham maxsus kod kerak bo'lsa, shu tartibda qo'shishimiz mumkin.")
