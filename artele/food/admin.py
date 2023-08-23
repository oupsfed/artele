from django.contrib import admin

from .models import Cart, Food, Order


class FoodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'weight',
        'price'
    )
    list_display_links = ('name',)


class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'food',
        'amount'
    )
    list_display_links = ('user',)


class FoodOrderInline(admin.TabularInline):
    model = Order.food.through
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'status',
    )
    list_display_links = ('user',)
    list_filter = ('user', 'status', 'food')
    inlines = (FoodOrderInline,)
    empty_value_display = '-пусто-'


admin.site.register(Food, FoodAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
