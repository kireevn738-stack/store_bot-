from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from database import get_db, User, Product, Order, OrderItem
from keyboards.builders import (
    get_main_menu_keyboard, get_cancel_keyboard,
    get_product_actions_keyboard, get_yes_no_keyboard
)

router = Router()

class OrderStates(StatesGroup):
    selecting_products = State()
    entering_quantities = State()
    confirming_order = State()

@router.message(F.text.in_(["💰 Заказы", "💰 Orders"]))
async def orders_menu(message: Message):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(10).all()
    
    if user.language == 'ru':
        if not orders:
            text = "💰 У вас пока нет заказов.\n\nЧтобы создать заказ, нажмите 'Создать заказ'"
        else:
            text = f"💰 Последние заказы ({len(orders)}):\n\n"
            for idx, order in enumerate(orders, 1):
                text += f"📦 Заказ #{order.order_number}\n"
                text += f"   📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                text += f"   💰 Сумма: ${order.total_amount:.2f}\n"
                text += f"   📈 Прибыль: ${order.total_profit:.2f}\n"
                text += f"   🛍️ Товаров: {len(order.items)}\n\n"
    else:
        if not orders:
            text = "💰 You have no orders yet.\n\nTo create an order, click 'Create order'"
        else:
            text = f"💰 Recent orders ({len(orders)}):\n\n"
            for idx, order in enumerate(orders, 1):
                text += f"📦 Order #{order.order_number}\n"
                text += f"   📅 Date: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                text += f"   💰 Amount: ${order.total_amount:.2f}\n"
                text += f"   📈 Profit: ${order.total_profit:.2f}\n"
                text += f"   🛍️ Items: {len(order.items)}\n\n"
    
    await message.answer(text)

@router.message(F.text.in_(["🛒 Создать заказ", "🛒 Create order"]))
async def create_order_start(message: Message, state: FSMContext):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    products = db.query(Product).filter(
        Product.user_id == user.id,
        Product.quantity > 0
    ).all()
    
    if not products:
        if user.language == 'ru':
            text = "❌ Нет товаров для продажи. Добавьте товары сначала."
        else:
            text = "❌ No products available for sale. Add products first."
        
        await message.answer(text)
        return
    
    if user.language == 'ru':
        text = "🛒 Выберите товары для заказа:\n\n"
        cancel_text = "❌ Отмена"
    else:
        text = "🛒 Select products for order:\n\n"
        cancel_text = "❌ Cancel"
    
    for idx, product in enumerate(products, 1):
        text += f"{idx}. {product.name} (доступно: {product.quantity})\n"
    
    await message.answer(
        text,
        reply_markup=get_cancel_keyboard(user.language)
    )
    await state.set_state(OrderStates.selecting_products)
    await state.update_data(language=user.language, products={})

@router.message(OrderStates.selecting_products)
async def process_product_selection(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    if message.text == ("❌ Отмена" if language == 'ru' else "❌ Cancel"):
        await state.clear()
        await message.answer(
            "🚫 Создание заказа отменено" if language == 'ru' else "🚫 Order creation cancelled",
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    # Process product selection
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    products = db.query(Product).filter(
        Product.user_id == user.id,
        Product.quantity > 0
    ).all()
    
    try:
        selected_indices = [int(idx.strip()) - 1 for idx in message.text.split(',')]
        selected_products = [products[idx] for idx in selected_indices if 0 <= idx < len(products)]
    except:
        if language == 'ru':
            error_text = "❌ Пожалуйста, введите номера товаров через запятую:"
        else:
            error_text = "❌ Please enter product numbers separated by commas:"
        
        await message.answer(error_text)
        return
    
    if not selected_products:
        if language == 'ru':
            error_text = "❌ Пожалуйста, выберите хотя бы один товар:"
        else:
            error_text = "❌ Please select at least one product:"
        
        await message.answer(error_text)
        return
    
    # Store selected products
    selected_data = {str(product.id): {"product": product, "quantity": None} for product in selected_products}
    await state.update_data(selected_products=selected_data)
    
    if language == 'ru':
        text = "🔢 Введите количество для каждого товара через запятую (в том же порядке):\n\n"
    else:
        text = "🔢 Enter quantity for each product separated by commas (in the same order):\n\n"
    
    for idx, product in enumerate(selected_products, 1):
        text += f"{idx}. {product.name} (макс: {product.quantity}):\n"
    
    await message.answer(text)
    await state.set_state(OrderStates.entering_quantities)

@router.message(OrderStates.entering_quantities)
async def process_quantities(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    selected_products = data.get('selected_products', {})
    
    quantities = message.text.split(',')
    
    if len(quantities) != len(selected_products):
        if language == 'ru':
            error_text = f"❌ Пожалуйста, введите {len(selected_products)} значений количества:"
        else:
            error_text = f"❌ Please enter {len(selected_products)} quantity values:"
        
        await message.answer(error_text)
        return
    
    # Validate quantities
    db: Session = next(get_db())
    valid_items = []
    total_amount = 0
    total_profit = 0
    
    for idx, (product_id, product_data) in enumerate(selected_products.items()):
        try:
            quantity = int(quantities[idx].strip())
            product = product_data["product"]
            
            if quantity <= 0:
                raise ValueError
            if quantity > product.quantity:
                if language == 'ru':
                    error_text = f"❌ Для товара '{product.name}' доступно только {product.quantity} единиц"
                else:
                    error_text = f"❌ For product '{product.name}' only {product.quantity} units available"
                
                await message.answer(error_text)
                return
            
            # Update product data
            selected_products[product_id]["quantity"] = quantity
            valid_items.append({
                "product": product,
                "quantity": quantity,
                "amount": quantity * product.sale_price,
                "profit": quantity * product.profit
            })
            
            total_amount += quantity * product.sale_price
            total_profit += quantity * product.profit
            
        except ValueError:
            if language == 'ru':
                error_text = "❌ Пожалуйста, введите корректные количества (целые числа):"
            else:
                error_text = "❌ Please enter valid quantities (whole numbers):"
            
            await message.answer(error_text)
            return
    
    await state.update_data(selected_products=selected_products, valid_items=valid_items)
    
    # Show order summary
    if language == 'ru':
        text = "📋 Сводка заказа:\n\n"
    else:
        text = "📋 Order Summary:\n\n"
    
    for item in valid_items:
        text += f"• {item['product'].name} x{item['quantity']} = ${item['amount']:.2f}\n"
    
    text += f"\n💰 Итого: ${total_amount:.2f}\n"
    text += f"📈 Прибыль: ${total_profit:.2f}\n\n"
    
    if language == 'ru':
        text += "Подтвердить заказ?"
    else:
        text += "Confirm order?"
    
    await message.answer(
        text,
        reply_markup=get_yes_no_keyboard(language)
    )
    await state.set_state(OrderStates.confirming_order)

@router.callback_query(F.data == "confirm_yes", OrderStates.confirming_order)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    valid_items = data.get('valid_items', [])
    
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    # Create order
    order_number = str(uuid.uuid4())[:8].upper()
    total_amount = sum(item['amount'] for item in valid_items)
    total_profit = sum(item['profit'] for item in valid_items)
    
    order = Order(
        order_number=order_number,
        total_amount=total_amount,
        total_profit=total_profit,
        user_id=user.id
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Create order items and update product quantities
    for item in valid_items:
        product = item['product']
        quantity = item['quantity']
        
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.sale_price,
            profit=product.profit * quantity
        )
        
        # Update product quantity
        product.quantity -= quantity
        
        db.add(order_item)
    
    db.commit()
    
    if language == 'ru':
        success_text = f"""✅ Заказ создан успешно!

📦 Номер заказа: #{order_number}
💰 Сумма: ${total_amount:.2f}
📈 Прибыль: ${total_profit:.2f}
📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}"""
    else:
        success_text = f"""✅ Order created successfully!

📦 Order number: #{order_number}
💰 Amount: ${total_amount:.2f}
📈 Profit: ${total_profit:.2f}
📅 Date: {order.created_at.strftime('%d.%m.%Y %H:%M')}"""
    
    await callback.message.edit_text(
        success_text,
        reply_markup=get_main_menu_keyboard(language)
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "confirm_no", OrderStates.confirming_order)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    await state.clear()
    
    if language == 'ru':
        text = "🚫 Создание заказа отменено"
    else:
        text = "🚫 Order creation cancelled"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu_keyboard(language)
    )
    await callback.answer()
