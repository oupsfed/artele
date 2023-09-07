from aiogram.filters.callback_data import CallbackData


def encode_callback(back: CallbackData) -> str:
    return back.pack().replace(':', '.')


def decode_callback(back: str) -> str:
    return back.replace('.', ':')


async def paginate_builder(json_response: dict,
                           builder,
                           callback_factory,
                           action):
    page_buttons = 0
    page = json_response['page']
    if json_response['previous']:
        builder.button(
            text="⬅️",
            callback_data=callback_factory(
                action=action,
                page=page - 1
            )
        )
        page_buttons += 1
    if json_response['next']:
        builder.button(
            text="➡️",
            callback_data=callback_factory(
                action=action,
                page=page + 1
            )
        )
        page_buttons += 1
    return page_buttons, builder


async def back_builder(builder,
                       callback):
    builder.button(
        text='↩️',
        callback_data=decode_callback(callback)
    )
    return builder
