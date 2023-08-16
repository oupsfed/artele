from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from utils import get_api_answer


def is_admin(user_id) -> bool:
    answer = get_api_answer(f'users/{user_id}')
    return answer.json()['role'] == 'ADMIN'


def is_guest(user_id) -> bool:
    answer = get_api_answer(f'users/{user_id}')
    return answer.json()['role'] == 'GUEST'


class IsAdminMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if is_admin(event.chat.id):
            return await handler(event, data)
        await event.answer(
            "Доступ только для администратора",
            show_alert=True
        )
        return


class IsAdminCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if is_admin(event.chat.id):
            return await handler(event, data)
        await event.answer(
            "Доступ только для администратора",
            show_alert=True
        )
        return


class IsGuestMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if is_guest(event.chat.id):
            return await handler(event, data)
        await event.answer(
            "Доступ только для гостей",
            show_alert=True
        )
        return


class IsGuestCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if is_guest(event.chat.id):
            return await handler(event, data)
        await event.answer(
            "Доступ только для гостей",
            show_alert=True
        )
        return
