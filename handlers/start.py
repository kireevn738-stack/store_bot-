from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy.orm import Session
from database import get_db, User
from keyboards.builders import get_language_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    db: Session = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if user:
        # User exists, show main menu
        from handlers.language import get_main_menu_text
        await message.answer(
            get_main_menu_text(user.language),
            reply_markup=get_main_menu_keyboard(user.language)
        )
    else:
        # New user, ask for language
        await message.answer(
            "🌍 Please choose your language / Пожалуйста, выберите ваш язык:",
            reply_markup=get_language_keyboard()
        )
