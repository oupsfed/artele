class Action:
    get = 'get'
    create = 'create'
    remove = 'remove'
    get_all = 'list'
    update = 'update'

    def __init__(self,
                 callback_name):
        self.callback = f'{callback_name}-'
        self.get = self.callback + self.get
        self.create = self.callback + self.create
        self.remove = self.callback + self.remove
        self.get_all = self.callback + self.get_all
        self.update = self.callback + self.update

    def __str__(self):
        return self.callback


class FoodAction(Action):
    add_to_cart = 'add_t_c'
    remove_from_cart = 'remove_f_c'
    create_preview = 'c_preview'
    update_preview = 'u_preview'
    remove_preview = 'r_preview'
    update_column = 'col_update'


class OrderAction(Action):
    filter_by_user = 'f_b_u'
    filter_by_food = 'f_b_f'
    download = 'download'
    done = 'done'
    cancel = 'cancel'


class CartAction(Action):
    pass


food_action = FoodAction('food')
order_action = OrderAction('order')
cart_action = CartAction('cart')

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
