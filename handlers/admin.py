from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from config import settings
from database import User, Product, Category, Transaction, get_db

router = Router()


@router.message(Command("admin"))
async def admin_command(message: Message):
    """Admin panel access"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    admin_text = (
        "👑 Admin Panel\n\n"
        "Available commands:\n"
        "/stats - System statistics\n"
        "/users - List all users\n"
        "/products_all - All products\n"
        "/backup - Create backup\n"
        "/cleanup - Clean old data"
    )
    
    await message.answer(admin_text)


@router.message(Command("stats"))
async def admin_stats(message: Message):
    """System statistics"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    
    # Get counts
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_transactions = db.query(Transaction).count()
    
    # Get today's stats
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_users_today = db.query(User).filter(User.created_at >= today).count()
    
    # Get storage info (for SQLite)
    import os
    db_size = os.path.getsize("store_bot.db") if os.path.exists("store_bot.db") else 0
    
    stats_text = (
        f"📊 System Statistics\n\n"
        f"👥 Users:\n"
        f"• Total: {total_users}\n"
        f"• Active: {active_users}\n"
        f"• New today: {new_users_today}\n\n"
        f"📦 Products: {total_products}\n"
        f"📂 Categories: {total_categories}\n"
        f"💳 Transactions: {total_transactions}\n\n"
        f"💾 Database: {db_size / 1024:.2f} KB\n"
        f"🕐 Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    )
    
    await message.answer(stats_text)


@router.message(Command("users"))
async def list_all_users(message: Message):
    """List all registered users"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    users = db.query(User).order_by(User.created_at.desc()).limit(50).all()
    
    if not users:
        await message.answer("No users found.")
        return
    
    response = "👥 Registered Users (last 50):\n\n"
    for user in users:
        user_products = db.query(Product).filter(Product.user_id == user.id).count()
        user_categories = db.query(Category).filter(Category.user_id == user.id).count()
        
        status = "✅" if user.is_active else "❌"
        response += (
            f"{status} ID: {user.id}\n"
            f"   Telegram: {user.telegram_id}\n"
            f"   Store: {user.store_name or 'N/A'}\n"
            f"   Email: {user.email}\n"
            f"   Lang: {user.language.value}\n"
            f"   Products: {user_products}\n"
            f"   Categories: {user_categories}\n"
            f"   Registered: {user.created_at.strftime('%Y-%m-%d')}\n"
            f"{'-'*30}\n"
        )
    
    await message.answer(response[:4000])  # Telegram message limit


@router.message(Command("products_all"))
async def list_all_products(message: Message):
    """List all products in system"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    products = db.query(Product).join(User).order_by(Product.created_at.desc()).limit(50).all()vif not products:
        await message.answer("No products found.")
        return
    
    response = "📦 All Products (last 50):\n\n"
    for product in products:
        profit = (product.sale_price - product.purchase_price) * product.quantity
        response += (
            f"📦 {product.name}\n"
            f"   Store: {product.user.store_name}\n"
            f"   Price: ${product.sale_price:.2f} | "
            f"Cost: ${product.purchase_price:.2f}\n"
            f"   Qty: {product.quantity} | "
            f"Profit: ${profit:.2f}\n"
            f"   SKU: {product.sku or 'N/A'}\n"
            f"{'-'*30}\n"
        )
    
    await message.answer(response[:4000])


@router.message(Command("backup"))
async def create_backup(message: Message):
    """Create database backup"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    import shutil
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_store_bot_{timestamp}.db"
        shutil.copy2("store_bot.db", backup_file)
        
        await message.answer(f"✅ Backup created: {backup_file}")
    except Exception as e:
        await message.answer(f"❌ Backup failed: {str(e)}")


@router.message(Command("cleanup"))
async def cleanup_old_data(message: Message):
    """Clean old data"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    
    try:
        # Find users with no activity for 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        inactive_users = db.query(User).filter(
            User.is_active == True,
            User.created_at < cutoff_date,
            ~User.products.any()
        ).all()
        
        # Mark as inactive
        for user in inactive_users:
            user.is_active = False
        
        db.commit()
        
        await message.answer(
            f"✅ Cleanup completed.\n"
            f"Marked {len(inactive_users)} inactive users."
        )
    except Exception as e:
        db.rollback()
        await message.answer(f"❌ Cleanup failed: {str(e)}")


@router.message(Command("sendall"))
async def send_broadcast(message: Message):
    """Send message to all users (admin only)"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    # Extract message text (after command)
    broadcast_text = message.text.replace('/sendall', '').strip()
    
    if not broadcast_text:
        await message.answer("Please provide message text after /sendall command.")
        return
    
    db = next(get_db())
    users = db.query(User).filter(User.is_active == True).all()
    
    await message.answer(f"📢 Starting broadcast to {len(users)} users...")
    
    from aiogram import Bot
    bot = Bot.get_current()
    
    success_count = 0
    fail_count = 0
    
    for user in users:
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"📢 Announcement from Admin:\n\n{broadcast_text}"
            )
            success_count += 1
            await asyncio.sleep(0.1)  # Rate limiting
        except Exception as e:
            fail_count += 1
            print(f"Failed to send to user {user.telegram_id}: {e}")
    
    await message.answer(
        f"📊 Broadcast completed!\n"
        f"✅ Success: {success_count}\n"
        f"❌ Failed: {fail_count}"
    )
