from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserViewSet, FoodViewSet, MessageViewSet, CartViewSet

app_name = 'api'

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('food', FoodViewSet)
router.register('cart', CartViewSet)
router.register('message', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
