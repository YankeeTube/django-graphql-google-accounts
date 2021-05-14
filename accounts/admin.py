from django.contrib import admin
from accounts.models import User


# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'email', 'created_at', 'updated_at')
    list_display_links = ('id', 'nickname', 'email')

