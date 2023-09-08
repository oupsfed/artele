from core import factories


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
                       action,
                       item_id: int = None):
    callback_data = {
        'food': factories.FoodCallbackFactory,
    }
    data = action.split('-')
    callback = callback_data[data[0]](
        action=action
    )
    if item_id:
        callback.id = item_id
    builder.button(
        text='↩️',
        callback_data=callback
    )
    return builder
