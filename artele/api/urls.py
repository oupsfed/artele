from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CartViewSet, FoodViewSet, OrderViewSet, UserViewSet

app_name = 'api'

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('food', FoodViewSet)
router.register('cart', CartViewSet)
router.register('order', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
