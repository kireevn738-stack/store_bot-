from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from database import Product, Category, get_db
from states import ProductStates
from keyboards import (
    get_products_menu_keyboard,
    get_categories_keyboard,
    get_edit_product_fields_keyboard,
    get_products_keyboard
)

router = Router()


@router.message(F.text.contains("📦") | F.text.contains("Products") | 
                F.text.contains("Товары") | F.text.contains("Товари"))
async def show_products_menu(message: Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Please register first using /start")
        return
    
    await message.answer(
        "📦 Products Management",
        reply_markup=get_products_menu_keyboard(user.language.value)
    )


@router.message(F.text.contains("➕ Add") | F.text.contains("➕ Добавить") | 
                F.text.contains("➕ Додати"))
async def start_add_product(message: Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Please register first using /start")
        return
    
    await message.answer(
        "📝 Enter product name:",
        reply_markup=None
    )
    await state.set_state(ProductStates.waiting_for_name)


@router.message(ProductStates.waiting_for_name)
async def process_product_name(message: Message, state: FSMContext):
    product_name = message.text.strip()
    if len(product_name) < 2:
        await message.answer("❌ Product name is too short. Please enter a valid name:")
        return
    
    await state.update_data(name=product_name)
    
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    if categories:
        await message.answer(
            "📂 Select category:",
            reply_markup=get_categories_keyboard(categories, user.language.value)
        )
    else:
        await message.answer(
            "📝 Enter category name (or 'skip' to proceed without category):",
            reply_markup=None
        )
        await state.set_state(ProductStates.waiting_for_category)


@router.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[1]
    
    if category_id == "none":
        await state.update_data(category_id=None)
    elif category_id == "cancel":
        await callback.message.edit_text("❌ Product creation cancelled.")
        await state.clear()
        return
    else:
        await state.update_data(category_id=int(category_id))
    
    await callback.message.edit_text("💰 Enter purchase price:")
    await state.set_state(ProductStates.waiting_for_purchase_price)


@router.message(ProductStates.waiting_for_category)
async def process_new_category(message: Message, state: FSMContext):
    category_name = message.text.strip()
    
    if category_name.lower() == 'skip':
        await state.update_data(category_id=None)
        await message.answer("💰 Enter purchase price:")
        await state.set_state(ProductStates.waiting_for_purchase_price)
        return
    
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    # Create new category
    category = Category(user_id=user.id, name=category_name)
    db.add(category)
    db.commit()
    
    await state.update_data(category_id=category.id)
    await message.answer("💰 Enter purchase price:")
    await state.set_state(ProductStates.waiting_for_purchase_price)@router.message(ProductStates.waiting_for_purchase_price)
async def process_purchase_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip().replace(',', '.'))
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Invalid price. Please enter a valid number:")
        return
    
    await state.update_data(purchase_price=price)
    await message.answer("🏷️ Enter sale price:")
    await state.set_state(ProductStates.waiting_for_sale_price)


@router.message(ProductStates.waiting_for_sale_price)
async def process_sale_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip().replace(',', '.'))
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Invalid price. Please enter a valid number:")
        return
    
    await state.update_data(sale_price=price)
    await message.answer("📊 Enter quantity:")
    await state.set_state(ProductStates.waiting_for_quantity)


@router.message(ProductStates.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text.strip())
        if quantity < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Invalid quantity. Please enter a valid integer:")
        return
    
    await state.update_data(quantity=quantity)
    await message.answer("🏷️ Enter SKU (Stock Keeping Unit) or 'skip':")
    await state.set_state(ProductStates.waiting_for_sku)


@router.message(ProductStates.waiting_for_sku)
async def process_sku(message: Message, state: FSMContext):
    sku = message.text.strip()
    
    if sku.lower() == 'skip':
        await state.update_data(sku=None)
    else:
        await state.update_data(sku=sku)
    
    await message.answer("📄 Enter description or 'skip':")
    await state.set_state(ProductStates.waiting_for_description)


@router.message(ProductStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    description = message.text.strip()
    
    if description.lower() == 'skip':
        await state.update_data(description=None)
    else:
        await state.update_data(description=description)
    
    # Create product
    data = await state.get_data()
    
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    product = Product(
        user_id=user.id,
        category_id=data.get('category_id'),
        name=data['name'],
        purchase_price=data['purchase_price'],
        sale_price=data['sale_price'],
        quantity=data['quantity'],
        sku=data.get('sku'),
        description=data.get('description')
    )
    
    db.add(product)
    db.commit()
    
    profit_per_unit = product.sale_price - product.purchase_price
    total_profit = profit_per_unit * product.quantity
    
    response = (
        f"✅ Product added successfully!\n\n"
        f"📦 Name: {product.name}\n"
        f"💰 Purchase: ${product.purchase_price:.2f}\n"
        f"🏷️ Sale: ${product.sale_price:.2f}\n"
        f"📊 Quantity: {product.quantity}\n"
        f"💵 Profit per unit: ${profit_per_unit:.2f}\n"
        f"💰 Total profit potential: ${total_profit:.2f}"
    )
    
    if product.sku:
        response += f"\n🏷️ SKU: {product.sku}"
    if product.description:
        response += f"\n📄 Description: {product.description}"
    
    await message.answer(response, reply_markup=get_products_menu_keyboard(user.language.value))
    await state.clear()


@router.message(F.text.contains("📋 List") | F.text.contains("Список"))
async def list_products(message: Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()if not user:
        await message.answer("Please register first using /start")
        return
    
    products = db.query(Product).filter(Product.user_id == user.id).all()
    
    if not products:
        await message.answer("📭 No products found.")
        return
    
    response = "📋 Your Products:\n\n"
    for product in products:
        profit = (product.sale_price - product.purchase_price) * product.quantity
        response += (
            f"📦 {product.name}\n"
            f"   Price: ${product.sale_price:.2f} | "
            f"Cost: ${product.purchase_price:.2f} | "
            f"Qty: {product.quantity}\n"
            f"   Profit: ${profit:.2f}\n\n"
        )
    
    await message.answer(response[:4000])  # Telegram message limit


@router.message(F.text.contains("✏️ Edit") | F.text.contains("Редактировать") | 
                F.text.contains("Редагувати"))
async def start_edit_product(message: Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Please register first using /start")
        return
    
    products = db.query(Product).filter(Product.user_id == user.id).all()
    
    if not products:
        await message.answer("📭 No products to edit.")
        return
    
    await message.answer(
        "Select product to edit:",
        reply_markup=get_products_keyboard(products, user.language.value)
    )
    await state.set_state(ProductStates.editing_product)


@router.callback_query(ProductStates.editing_product, F.data.startswith("product_"))
async def select_product_to_edit(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[1]
    
    if product_id == "cancel":
        await callback.message.edit_text("❌ Edit cancelled.")
        await state.clear()
        return
    
    await state.update_data(product_id=int(product_id))
    
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    await callback.message.edit_text(
        "Select field to edit:",
        reply_markup=get_edit_product_fields_keyboard(user.language.value)
    )
    await state.set_state(ProductStates.waiting_for_edit_field)
