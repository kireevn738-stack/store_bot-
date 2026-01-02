from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from database import Product, Transaction, TransactionType, get_db
from states import AnalyticsStates
from keyboards import get_analytics_period_keyboard

router = Router()


@router.message(F.text.contains("📊") | F.text.contains("Analytics") | 
                F.text.contains("Аналитика") | F.text.contains("Аналітика"))
async def show_analytics_menu(message: Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Please register first using /start")
        return
    
    await message.answer(
        "📊 Select analytics period:",
        reply_markup=get_analytics_period_keyboard(user.language.value)
    )
    await state.set_state(AnalyticsStates.waiting_for_period_type)


@router.message(AnalyticsStates.waiting_for_period_type)
async def process_analytics_period(message: Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    period_text = message.text
    now = datetime.utcnow()
    
    if "Today" in period_text or "Сегодня" in period_text or "Сьогодні" in period_text:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif "Week" in period_text or "Неделя" in period_text or "Тиждень" in period_text:
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif "Month" in period_text or "Месяц" in period_text or "Місяць" in period_text:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif "Year" in period_text or "Год" in period_text or "Рік" in period_text:
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif "All" in period_text or "Все" in period_text or "Весь" in period_text:
        start_date = datetime(2000, 1, 1)  # Very old date
        end_date = now
    elif "Back" in period_text or "Назад" in period_text:
        await message.answer(
            "Main menu",
            reply_markup=get_main_menu_keyboard(user.language.value)
        )
        await state.clear()
        return
    else:
        await message.answer("Please select a valid period:")
        return
    
    # Calculate analytics
    products = db.query(Product).filter(
        Product.user_id == user.id,
        Product.created_at >= start_date,
        Product.created_at <= end_date
    ).all()
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date
    ).all()
    
    # Calculate totals
    total_purchases = sum(t.total_amount for t in transactions if t.transaction_type == TransactionType.PURCHASE)
    total_sales = sum(t.total_amount for t in transactions if t.transaction_type == TransactionType.SALE)
    total_profit = total_sales - total_purchases
    
    total_inventory_value = sum(p.purchase_price * p.quantity for p in products)
    potential_profit = sum((p.sale_price - p.purchase_price) * p.quantity for p in products)
    
    # Generate report
    report = (
        f"📊 Analytics Report\n"
        f"Period: {period_text}\n"
        f"Store: {user.store_name}\n"
        f"Date: {now.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"💰 Financial Summary:\n"
        f"• Total Purchases: ${total_purchases:.2f}\n"
        f"• Total Sales: ${total_sales:.2f}\n"
        f"• Net Profit: ${total_profit:.2f}\n\n"f"📦 Inventory Summary:\n"
        f"• Total Products: {len(products)}\n"
        f"• Inventory Value: ${total_inventory_value:.2f}\n"
        f"• Potential Profit: ${potential_profit:.2f}\n\n"
        
        f"📈 Performance Indicators:\n"
        f"• Profit Margin: {(total_profit / total_sales * 100 if total_sales > 0 else 0):.1f}%\n"
        f"• ROI: {(total_profit / total_purchases * 100 if total_purchases > 0 else 0):.1f}%"
    )
    
    # Add top products if available
    if products:
        top_products = sorted(products, key=lambda p: (p.sale_price - p.purchase_price) * p.quantity, reverse=True)[:5]
        report += "\n\n🏆 Top 5 Products by Potential Profit:\n"
        for i, product in enumerate(top_products, 1):
            profit = (product.sale_price - product.purchase_price) * product.quantity
            report += f"{i}. {product.name}: ${profit:.2f}\n"
    
    await message.answer(report, reply_markup=get_main_menu_keyboard(user.language.value))
    await state.clear()
