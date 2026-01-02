import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database import init_db
from handlers.start import router as start_router
from handlers.products import router as products_router
from handlers.categories import router as categories_router
from handlers.analytics import router as analytics_router


async def main():
    # Initialize database
    init_db()
    
    # Initialize bot and dispatcher
    bot = Bot(token=settings.8350573268:AAG3jFDklUBVHdz9gl2R5CeKRTJ68yl_JRI)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Include routers
    dp.include_router(start_router)
    dp.include_router(products_router)
    dp.include_router(categories_router)
    dp.include_router(analytics_router)
    
    print("🤖 Bot is starting...")
    
    # Start polling
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
