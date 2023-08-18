from django.contrib import admin

from .models import Cart, Food, Order, FoodOrder

admin.site.register(Food)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(FoodOrder)
