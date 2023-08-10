import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers.admin_panel import orders_list
from handlers.admin_panel import settings, requests_for_access, edit_menu, user_list
from bot.handlers.guest_panel import access
from bot.handlers.user_panel import menu, order, start, cart

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
                       settings.router,
                       access.router,
                       edit_menu.router,
                       user_list.router,
                       requests_for_access.router,
                       orders_list.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
