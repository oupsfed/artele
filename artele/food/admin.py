from django.contrib import admin

from .models import Food, Cart, Order

admin.site.register(Food)
admin.site.register(Cart)
admin.site.register(Order)