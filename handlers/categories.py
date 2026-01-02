from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import Category, get_db
from states import CategoryStates
from keyboards import get_categories_menu_keyboard

router = Router()


@router.message(F.text.contains("📂") | F.text.contains("Categories") | 
                F.text.contains("Категории") | F.text.contains("Категорії"))
async def show_categories_menu(message: Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Please register first using /start")
        return
    
    await message.answer(
        "📂 Categories Management",
        reply_markup=get_categories_menu_keyboard(user.language.value)
    )


@router.message(F.text.contains("➕ Add Category") | F.text.contains("➕ Добавить категорию") | 
                F.text.contains("➕ Додати категорію"))
async def start_add_category(message: Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Please register first using /start")
        return
    
    await message.answer(
        "📝 Enter category name:",
        reply_markup=None
    )
    await state.set_state(CategoryStates.waiting_for_name)


@router.message(CategoryStates.waiting_for_name)
async def process_category_name(message: Message, state: FSMContext):
    category_name = message.text.strip()
    if len(category_name) < 2:
        await message.answer("❌ Category name is too short. Please enter a valid name:")
        return
    
    await state.update_data(name=category_name)
    await message.answer("📄 Enter description or 'skip':")
    await state.set_state(CategoryStates.waiting_for_description)


@router.message(CategoryStates.waiting_for_description)
async def process_category_description(message: Message, state: FSMContext):
    description = message.text.strip()
    
    if description.lower() == 'skip':
        await state.update_data(description=None)
    else:
        await state.update_data(description=description)
    
    data = await state.get_data()
    
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    category = Category(
        user_id=user.id,
        name=data['name'],
        description=data.get('description')
    )
    
    db.add(category)
    db.commit()
    
    response = f"✅ Category '{category.name}' added successfully!"
    if category.description:
        response += f"\n📄 Description: {category.description}"
    
    await message.answer(response, reply_markup=get_categories_menu_keyboard(user.language.value))
    await state.clear()


@router.message(F.text.contains("📋 List Categories") | F.text.contains("Список категорий") | 
                F.text.contains("Список категорій"))
async def list_categories(message: Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Please register first using /start")
        return
    
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    if not categories:
        await message.answer("📭 No categories found.")
        return
    
    response = "📂 Your Categories:\n\n"
    for category in categories:
        response += f"📁 {category.name}"
        if category.description:
            response += f" - {category.description}"
        response += "\n"
    
    await message.answer(response)
