from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (AdminUserViewSet, AuthorizedUserViewSet, CartViewSet,
                    FoodViewSet, MessageViewSet, OrderListViewSet,
                    OrderViewSet, UserViewSet)

app_name = 'api'

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('authorized', AuthorizedUserViewSet)
router.register('admin', AdminUserViewSet)
router.register('food', FoodViewSet)
router.register('cart', CartViewSet)
router.register('order', OrderViewSet)
router.register('order_list', OrderListViewSet)
router.register('message', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
