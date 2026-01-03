from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.orm import Session

from database import get_db, User
from keyboards.builders import get_language_keyboard, get_main_menu_keyboard

router = Router()

def get_main_menu_text(language: str) -> str:
    texts = {
        'ru': """🏪 Добро пожаловать в StoreBot!

Выберите действие из меню ниже:""",
        'en': """🏪 Welcome to StoreBot!

Choose an action from the menu below:"""
    }
    return texts.get(language, texts['ru'])

@router.message(F.text.in_(["⚙️ Настройки", "⚙️ Settings"]))
async def settings_menu(message: Message):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    if user.language == 'ru':
        text = """⚙️ Настройки:

• Изменить язык
• Изменить название магазина
• Изменить email"""
    else:
        text = """⚙️ Settings:

• Change language
• Change store name
• Change email"""
    
    await message.answer(text)

@router.message(Command("language"))
async def cmd_language(message: Message):
    await message.answer(
        "🌍 Choose your language / Выберите язык:",
        reply_markup=get_language_keyboard()
    )
