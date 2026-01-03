from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from config import settings
from database import User, UserLanguage, get_db
from states import RegistrationStates
from keyboards import get_language_keyboard, get_main_menu_keyboard
from utils.validators import validate_email

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if user:
        # User already registered
        await message.answer(
            f"👋 Welcome back to {user.store_name or 'your store'}!",
            reply_markup=get_main_menu_keyboard(user.language.value)
        )
    else:
        # New user registration
        await message.answer(
            "👋 Welcome to Store Accounting Bot!\n"
            "Please enter your email to register:"
        )
        await state.set_state(RegistrationStates.waiting_for_email)


@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    
    if not validate_email(email):
        await message.answer("❌ Invalid email format. Please enter a valid email:")
        return
    
    db = next(get_db())
    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        await message.answer("❌ This email is already registered. Please use another email:")
        return
    
    await state.update_data(email=email)
    await message.answer(
        "🌐 Please select your language:",
        reply_markup=get_language_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_language)


@router.callback_query(F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    
    language_map = {
        "en": UserLanguage.ENGLISH,
        "ru": UserLanguage.RUSSIAN,
        "uk": UserLanguage.UKRAINIAN
    }
    
    language = language_map.get(lang_code, UserLanguage.ENGLISH)
    await state.update_data(language=language)
    
    texts = {
        "en": "🏪 Please enter your store name:",
        "ru": "🏪 Пожалуйста, введите название вашего магазина:",
        "uk": "🏪 Будь ласка, введіть назву вашого магазину:"
    }
    
    await callback.message.edit_text(texts.get(lang_code, texts["en"]))
    await state.set_state(RegistrationStates.waiting_for_store_name)


@router.message(RegistrationStates.waiting_for_store_name)
async def process_store_name(message: Message, state: FSMContext):
    store_name = message.text.strip()
    
    if len(store_name) < 2:
        await message.answer("❌ Store name is too short. Please enter a valid store name:")
        return
    
    data = await state.get_data()
    
    db = next(get_db())
    user = User(
        telegram_id=message.from_user.id,
        email=data['email'],
        language=data['language'],
        store_name=store_name
    )
    
    db.add(user)
    db.commit()
    
    welcome_texts = {
        "en": f"✅ Registration complete!\n"
              f"Welcome to {store_name}!\n"
              f"Email: {data['email']}\n"
              f"Language: English",
        "ru": f"✅ Регистрация завершена!\n"
              f"Добро пожаловать в {store_name}!\n"
              f"Email: {data['email']}\n"
              f"Язык: Русский",
        "uk": f"✅ Реєстрація завершена!\n"
              f"Ласкаво просимо до {store_name}!\n"
              f"Email: {data['email']}\n"
              f"Мова: Українська"
    }
    
    lang_code = data['language'].value
    await message.answer(
        welcome_texts.get(lang_code, welcome_texts["en"]),
        reply_markup=get_main_menu_keyboard(lang_code)
    )
    await state.clear()
