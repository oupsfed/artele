import asyncio

from aiogram import Dispatcher
from handlers.admin_panel import (add_food, edit_food, orders_list,
                                  requests_for_access, settings, user_list)
from handlers.guest_panel import access
from handlers.user_panel import cart, menu, order, start
from utils import bot


async def main():
    dp = Dispatcher()
    dp.include_routers(start.router,
                       menu.router,
                       cart.router,
                       order.router,
                       settings.router,
                       access.router,
                       edit_food.router,
                       add_food.router,
                       user_list.router,
                       requests_for_access.router,
                       orders_list.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
