class Action:
    get = 'get'
    create = 'create'
    remove = 'remove'
    get_all = 'get_all'
    update = 'update'

    def __init__(self,
                 callback_name):
        self.callback = callback_name
        self.get = self.callback + self.get
        self.create = self.callback + self.create
        self.remove = self.callback + self.remove
        self.get_all = self.callback + self.get_all
        self.update = self.callback + self.update

    def __str__(self):
        return self.callback


food_action = Action('food')
food_action.create_preview = 'create_preview'
food_action.update_preview = 'update_preview'
food_action.update_column = 'update_column'
food_action.remove_preview = 'remove_preview'


order_action = Action('order')

cart_action = Action('cart')

orders_list_actions = Action('ord_list')
orders_list_actions.filter_by_user = 'by_user'
orders_list_actions.filter_by_food = 'by_food'
orders_list_actions.download = 'download'
orders_list_actions.order_done = 'ord_done'
orders_list_actions.order_cancel = 'ord_cancel'

user_list_actions = Action('user_list')
user_list_actions.send_direct = 'send_direct'
user_list_actions.send_to_all = 'send_to_all'


access_action = Action('access')
access_action.stop = 'stop'
access_action.request_remove = 'req_remove'
