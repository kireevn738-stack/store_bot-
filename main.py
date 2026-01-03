import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from database import create_tables
from handlers import routers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '')
WEBHOOK_PATH = f"/webhook/{os.getenv('BOT_TOKEN', '')}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 8080))

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    create_tables()
    logger.info("Database tables created")
    
    bot = Bot(
        token=os.getenv('BOT_TOKEN'), 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    for router in routers:
        dp.include_router(router)
    
    if WEBHOOK_HOST:
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()
        
        logger.info(f"Bot started in webhook mode on {WEBHOOK_URL}")
        
        await asyncio.Event().wait()
    else:
        logger.info("Bot started in polling mode")
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
