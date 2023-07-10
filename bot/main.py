import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import start, menu, cart, order, settings

load_dotenv()

token = os.getenv('TOKEN')
logging.basicConfig(level=logging.DEBUG)


async def main():
    bot = Bot(token=token, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_routers(start.router,
                       menu.router,
                       cart.router,
                       order.router,
                       settings.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
