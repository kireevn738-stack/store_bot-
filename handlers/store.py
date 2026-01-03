from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from database import get_db, User

router = Router()

class StoreStates(StatesGroup):
    changing_name = State()
    changing_email = State()

@router.message(F.text.in_(["🏪 Мой магазин", "🏪 My Store"]))
async def store_info(message: Message):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    if user.language == 'ru':
        text = f"""🏪 Информация о магазине:

📋 Название: {user.store_name}
📧 Email: {user.email}
🌍 Язык: {'🇷🇺 Русский' if user.language == 'ru' else '🇬🇧 English'}
📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}

Всего товаров: {len(user.products)}
Всего заказов: {len(user.orders)}"""
    else:
        text = f"""🏪 Store Information:

📋 Name: {user.store_name}
📧 Email: {user.email}
🌍 Language: {'🇷🇺 Russian' if user.language == 'ru' else '🇬🇧 English'}
📅 Registration date: {user.created_at.strftime('%d.%m.%Y')}

Total products: {len(user.products)}
Total orders: {len(user.orders)}"""
    
    await message.answer(text)
