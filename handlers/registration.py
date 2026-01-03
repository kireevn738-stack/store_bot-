from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
import re

from database import get_db, User
from keyboards.builders import get_main_menu_keyboard, get_cancel_keyboard
from utils.validators import is_valid_email

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_store_name = State()

@router.message(F.text.in_(["🇷🇺 Русский", "🇬🇧 English"]))
async def process_language_selection(message: Message, state: FSMContext):
    language_map = {
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en"
    }
    
    language = language_map[message.text]
    
    await state.update_data(language=language)
    
    # Ask for email
    if language == 'ru':
        text = "📧 Пожалуйста, введите ваш email:"
        cancel_text = "❌ Отмена"
    else:
        text = "📧 Please enter your email:"
        cancel_text = "❌ Cancel"
    
    await message.answer(
        text,
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(RegistrationStates.waiting_for_email)

@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    if message.text == ("❌ Отмена" if language == 'ru' else "❌ Cancel"):
        await state.clear()
        await message.answer(
            "🚫 Регистрация отменена" if language == 'ru' else "🚫 Registration cancelled",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    email = message.text.strip()
    
    if not is_valid_email(email):
        error_text = "❌ Пожалуйста, введите корректный email:" if language == 'ru' else "❌ Please enter a valid email:"
        await message.answer(error_text)
        return
    
    # Check if email already exists
    db: Session = next(get_db())
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        error_text = "❌ Этот email уже зарегистрирован. Введите другой:" if language == 'ru' else "❌ This email is already registered. Enter another one:"
        await message.answer(error_text)
        return
    
    await state.update_data(email=email)
    
    # Ask for store name
    if language == 'ru':
        text = "🏪 Введите название вашего магазина:"
    else:
        text = "🏪 Enter your store name:"
    
    await message.answer(text)
    await state.set_state(RegistrationStates.waiting_for_store_name)

@router.message(RegistrationStates.waiting_for_store_name)
async def process_store_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    email = data.get('email')
    
    store_name = message.text.strip()
    
    if len(store_name) < 2:
        error_text = "❌ Название магазина должно содержать минимум 2 символа:" if language == 'ru' else "❌ Store name must be at least 2 characters:"
        await message.answer(error_text)
        return
    
    # Create user
    db: Session = next(get_db())
    
    user = User(
        telegram_id=message.from_user.id,
        email=email,
        language=language,
        store_name=store_name
    )
    
    db.add(user)
    db.commit()
    
    # Send success message
    if language == 'ru':
        success_text = f"""✅ Регистрация завершена!

🏪 Магазин: {store_name}
📧 Email: {email}

Теперь вы можете управлять своим магазином!"""
    else:
        success_text = f"""✅ Registration completed!

🏪 Store: {store_name}
📧 Email: {email}

Now you can manage your store!"""
    
    await message.answer(
        success_text,
        reply_markup=get_main_menu_keyboard(language)
    )
    
    await state.clear()
