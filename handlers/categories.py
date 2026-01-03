from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from database import get_db, User, Category
from keyboards.builders import (
    get_main_menu_keyboard, get_cancel_keyboard,
    get_categories_keyboard
)

router = Router()

class CategoryStates(StatesGroup):
    adding_name = State()
    editing_name = State()

@router.message(F.text.in_(["📁 Категории", "📁 Categories"]))
async def categories_menu(message: Message):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    if user.language == 'ru':
        if not categories:
            text = "📁 У вас пока нет категорий.\n\nЧтобы добавить категорию, нажмите 'Добавить категорию'"
        else:
            text = f"📁 Ваши категории ({len(categories)}):\n\n"
            for idx, category in enumerate(categories, 1):
                product_count = len(category.products)
                text += f"{idx}. {category.name} ({product_count} товаров)\n"
    else:
        if not categories:
            text = "📁 You have no categories yet.\n\nTo add a category, click 'Add category'"
        else:
            text = f"📁 Your categories ({len(categories)}):\n\n"
            for idx, category in enumerate(categories, 1):
                product_count = len(category.products)
                text += f"{idx}. {category.name} ({product_count} products)\n"
    
    await message.answer(
        text,
        reply_markup=get_categories_keyboard(categories, user.language)
    )

@router.callback_query(F.data == "add_category")
async def add_category_callback(callback: CallbackQuery, state: FSMContext):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    if not user:
        return
    
    if user.language == 'ru':
        text = "📝 Введите название категории:"
        cancel_text = "❌ Отмена"
    else:
        text = "📝 Enter category name:"
        cancel_text = "❌ Cancel"
    
    await callback.message.answer(
        text,
        reply_markup=get_cancel_keyboard(user.language)
    )
    await state.set_state(CategoryStates.adding_name)
    await state.update_data(language=user.language)
    await callback.answer()

@router.message(CategoryStates.adding_name)
async def process_category_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    if message.text == ("❌ Отмена" if language == 'ru' else "❌ Cancel"):
        await state.clear()
        await message.answer(
            "🚫 Добавление категории отменено" if language == 'ru' else "🚫 Category addition cancelled",
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    category_name = message.text.strip()
    
    if len(category_name) < 2:
        error_text = "❌ Название должно содержать минимум 2 символа:" if language == 'ru' else "❌ Name must be at least 2 characters:"
        await message.answer(error_text)
        return
    
    # Create category
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    category = Category(
        name=category_name,
        user_id=user.id
    )
    
    db.add(category)
    db.commit()
    
    if language == 'ru':
        success_text = f"✅ Категория '{category_name}' успешно добавлена!"
    else:
        success_text = f"✅ Category '{category_name}' successfully added!"
    
    await message.answer(
        success_text,
        reply_markup=get_main_menu_keyboard(language)
    )
    await state.clear()
