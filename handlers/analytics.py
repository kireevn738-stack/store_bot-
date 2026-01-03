from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from database import get_db, User, Order, Product
from keyboards.builders import (
    get_main_menu_keyboard, get_analytics_period_keyboard,
    get_cancel_keyboard
)

router = Router()

class AnalyticsStates(StatesGroup):
    selecting_period = State()
    custom_period_start = State()
    custom_period_end = State()

@router.message(F.text.in_(["📊 Аналитика", "📊 Analytics"]))
async def analytics_menu(message: Message, state: FSMContext):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    if user.language == 'ru':
        text = "📊 Выберите период для анализа:"
    else:
        text = "📊 Select period for analytics:"
    
    await message.answer(
        text,
        reply_markup=get_analytics_period_keyboard(user.language)
    )
    await state.set_state(AnalyticsStates.selecting_period)
    await state.update_data(language=user.language)

@router.callback_query(F.data.startswith("analytics_"), AnalyticsStates.selecting_period)
async def process_period_selection(callback: CallbackQuery, state: FSMContext):
    period = callback.data.split("_")[1]
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    now = datetime.now()
    
    # Define time ranges
    if period == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'all':
        start_date = None
        end_date = now
    elif period == 'custom':
        if language == 'ru':
            text = "📅 Введите начальную дату (формат: ДД.ММ.ГГГГ):"
        else:
            text = "📅 Enter start date (format: DD.MM.YYYY):"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_cancel_keyboard(language)
        )
        await state.set_state(AnalyticsStates.custom_period_start)
        await callback.answer()
        return
    
    # Get analytics data
    await show_analytics(callback.message, user.id, start_date, end_date, language)
    await state.clear()
    await callback.answer()

@router.message(AnalyticsStates.custom_period_start)
async def process_custom_start_date(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    if message.text == ("❌ Отмена" if language == 'ru' else "❌ Cancel"):
        await state.clear()
        await message.answer(
            "🚫 Аналитика отменена" if language == 'ru' else "🚫 Analytics cancelled",
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    try:
        start_date = datetime.strptime(message.text.strip(), '%d.%m.%Y')
        await state.update_data(start_date=start_date)
        
        if language == 'ru':
            text = "📅 Введите конечную дату (формат: ДД.ММ.ГГГГ):"
        else:
            text = "📅 Enter end date (format: DD.MM.YYYY):"
        
        await message.answer(text)
        await state.set_state(AnalyticsStates.custom_period_end)
    except ValueError:
        if language == 'ru':
            error_text = "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ:"
        else:
            error_text = "❌ Invalid date format. Use DD.MM.YYYY:"
        
        await message.answer(error_text)

@router.message(AnalyticsStates.custom_period_end)
async def process_custom_end_date(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    start_date = data.get('start_date')
    
    try:
        end_date = datetime.strptime(message.text.strip(), '%d.%m.%Y')
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        db: Session = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        await show_analytics(message, user.id, start_date, end_date, language)
        await state.clear()
    except ValueError:
        if language == 'ru':
            error_text = "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ:"
        else:
            error_text = "❌ Invalid date format. Use DD.MM.YYYY:"
        
        await message.answer(error_text)

async def show_analytics(message: Message, user_id: int, start_date: datetime, end_date: datetime, language: str):
    db: Session = next(get_db())
    
    # Build query for orders
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    
    orders = query.all()
    
    # Calculate metrics
    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders)
    total_profit = sum(order.total_profit for order in orders)
    
    # Calculate total products sold
    total_items_sold = 0
    for order in orders:
        for item in order.items:
            total_items_sold += item.quantity
    
    # Get total expenses (purchase costs of sold items)
    total_expenses = 0
    for order in orders:
        for item in order.items:
            product = item.product
            total_expenses += item.quantity * product.purchase_price
    
    # Get current inventory value
    current_products = db.query(Product).filter(Product.user_id == user_id).all()
    inventory_value = sum(product.quantity * product.purchase_price for product in current_products)
    inventory_items = sum(product.quantity for product in current_products)
    
    # Format date range text
    if start_date and end_date:
        date_range = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
    elif start_date:
        date_range = f"с {start_date.strftime('%d.%m.%Y')}"
    else:
        date_range = "за все время"
    
    if language == 'ru':
        text = f"""📊 Аналитика магазина ({date_range}):

📈 Продажи:
├─ 📦 Заказов: {total_orders}
├─ 🛍️ Товаров продано: {total_items_s
