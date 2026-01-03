from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session, joinedload

from database import get_db, User, Product, Category
from keyboards.builders import (
    get_main_menu_keyboard, get_cancel_keyboard,
    get_product_actions_keyboard, get_categories_keyboard,
    get_yes_no_keyboard
)
from utils.validators import is_valid_price, is_valid_quantity

router = Router()

class ProductStates(StatesGroup):
    adding_name = State()
    adding_quantity = State()
    adding_purchase_price = State()
    adding_sale_price = State()
    adding_category = State()
    editing_product = State()
    editing_field = State()

@router.message(F.text.in_(["📦 Товары", "📦 Products"]))
async def products_menu(message: Message):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    products = db.query(Product).filter(Product.user_id == user.id).all()
    
    if user.language == 'ru':
        if not products:
            text = "📦 У вас пока нет товаров.\n\nЧтобы добавить товар, нажмите 'Добавить товар'"
        else:
            text = f"📦 Ваши товары ({len(products)}):\n\n"
            for idx, product in enumerate(products, 1):
                category_name = product.category.name if product.category else "Без категории"
                text += f"{idx}. {product.name}\n"
                text += f"   📊 Количество: {product.quantity}\n"
                text += f"   💰 Цена: ${product.sale_price:.2f}\n"
                text += f"   📁 Категория: {category_name}\n\n"
    else:
        if not products:
            text = "📦 You have no products yet.\n\nTo add a product, click 'Add product'"
        else:
            text = f"📦 Your products ({len(products)}):\n\n"
            for idx, product in enumerate(products, 1):
                category_name = product.category.name if product.category else "No category"
                text += f"{idx}. {product.name}\n"
                text += f"   📊 Quantity: {product.quantity}\n"
                text += f"   💰 Price: ${product.sale_price:.2f}\n"
                text += f"   📁 Category: {category_name}\n\n"
    
    await message.answer(text)

@router.message(F.text.in_(["➕ Добавить товар", "➕ Add product"]))
async def add_product_start(message: Message, state: FSMContext):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    if user.language == 'ru':
        text = "📝 Введите название товара:"
        cancel_text = "❌ Отмена"
    else:
        text = "📝 Enter product name:"
        cancel_text = "❌ Cancel"
    
    await message.answer(
        text,
        reply_markup=get_cancel_keyboard(user.language)
    )
    await state.set_state(ProductStates.adding_name)
    await state.update_data(language=user.language)

@router.message(ProductStates.adding_name)
async def process_product_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    if message.text == ("❌ Отмена" if language == 'ru' else "❌ Cancel"):
        await state.clear()
        await message.answer(
            "🚫 Добавление товара отменено" if language == 'ru' else "🚫 Product addition cancelled",
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    product_name = message.text.strip()
    
    if len(product_name) < 2:
        error_text = "❌ Название должно содержать минимум 2 символа:" if language == 'ru' else "❌ Name must be at least 2 characters:"
        await message.answer(error_text)
        return
    
    await state.update_data(name=product_name)
    
    if language == 'ru':
        text = "🔢 Введите количество товара:"
    else:
        text = "🔢 Enter product quantity:"
    
    await message.answer(text)
    await state.set_state(ProductStates.adding_quantity)

@router.message(ProductStates.adding_quantity)
async def process_product_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    quantity = message.text.strip()
    
    if not is_valid_quantity(quantity):
        error_text = "❌ Пожалуйста, введите корректное количество (целое число):" if language == 'ru' else "❌ Please enter a valid quantity (whole number):"
        await message.answer(error_text)
        return
    
    await state.update_data(quantity=int(quantity))
    
    if language == 'ru':
        text = "💰 Введите закупочную цену (стоимость за единицу):"
    else:
        text = "💰 Enter purchase price (cost per unit):"
    
    await message.answer(text)
    await state.set_state(ProductStates.adding_purchase_price)

@router.message(ProductStates.adding_purchase_price)
async def process_purchase_price(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    price = message.text.strip()
    
    if not is_valid_price(price):
        error_text = "❌ Пожалуйста, введите корректную цену:" if language == 'ru' else "❌ Please enter a valid price:"
        await message.answer(error_text)
        return
    
    await state.update_data(purchase_price=float(price))
    
    if language == 'ru':
        text = "💰 Введите цену продажи:"
    else:
        text = "💰 Enter sale price:"
    
    await message.answer(text)
    await state.set_state(ProductStates.adding_sale_price)

@router.message(ProductStates.adding_sale_price)
async def process_sale_price(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    price = message.text.strip()
    
    if not is_valid_price(price):
        error_text = "❌ Пожалуйста, введите корректную цену:" if language == 'ru' else "❌ Please enter a valid price:"
        await message.answer(error_text)
        return
    
    sale_price = float(price)
    purchase_price = data.get('purchase_price', 0)
    
    if sale_price < purchase_price:
        warning_text = "⚠️ Цена продажи ниже закупочной цены. Продолжить?" if language == 'ru' else "⚠️ Sale price is lower than purchase price. Continue?"
        await message.answer(
            warning_text,
            reply_markup=get_yes_no_keyboard(language)
        )
        await state.set_state(ProductStates.adding_category)
        await state.update_data(sale_price=sale_price)
        return
    
    profit = sale_price - purchase_price
    await state.update_data(sale_price=sale_price, profit=profit)
    
    # Ask for category
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    if categories:
        if language == 'ru':
            text = "📁 Выберите категорию для товара:"
        else:
            text = "📁 Choose a category for the product:"
        
        await message.answer(
            text,
            reply_markup=get_categories_keyboard(categories, language)
        )
        await state.set_state(ProductStates.adding_category)
    else:
        # Create product without category
        await create_product(message, state, None)

async def create_product(message: Message, state: FSMContext, category_id: int = None):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    product = Product(
        name=data['name'],
        quantity=data['quantity'],
        purchase_price=data['purchase_price'],
        sale_price=data['sale_price'],
        profit=data.get('profit', data['sale_price'] - data['purchase_price']),
        category_id=category_id,
        user_id=user.id
    )
    
    db.add(product)
    db.commit()
    
    if language == 'ru':
        success_text = f"""✅ Товар успешно добавлен!

📦 Название: {product.name}
🔢 Количество: {product.quantity}
💰 Закупочная цена: ${product.purchase_price:.2f}
💰 Цена продажи: ${product.sale_price:.2f}
📈 Прибыль: ${product.profit:.2f}"""
    else:
        success_text = f"""✅ Product successfully added!

📦 Name: {product.name}
🔢 Quantity: {product.quantity}
💰 Purchase price: ${product.purchase_price:.2f}
💰 Sale price: ${product.sale_price:.2f}
📈 Profit: ${product.profit:.2f}"""
    
    await message.answer(
        success_text,
        reply_markup=get_main_menu_keyboard(language)
    )
    await state.clear()

@router.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    
    await create_product(callback.message, state, category_id)
    await callback.answer()

@router.callback_query(F.data == "confirm_yes")
async def confirm_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    # Get categories for selection
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    if categories:
        if language == 'ru':
            text = "📁 Выберите категорию для товара:"
        else:
            text = "📁 Choose a category for the product:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_categories_keyboard(categories, language)
        )
    else:
        await create_product(callback.message, state, None)
    
    await callback.answer()

@router.callback_query(F.data == "confirm_no")
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    if language == 'ru':
        text = "💰 Введите цену продажи:"
    else:
        text = "💰 Enter sale price:"
    
    await callback.message.edit_text(text)
    await state.set_state(ProductStates.adding_sale_price)
    await callback.answer()
