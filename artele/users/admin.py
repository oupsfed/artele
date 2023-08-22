from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'telegram_chat_id',
        'first_name',
        'last_name',
        'phone_number',
        'role',
    )
    list_filter = ('role',)
    list_display_links = ('first_name', 'last_name')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
