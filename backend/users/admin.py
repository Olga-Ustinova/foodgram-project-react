from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from .models import Follow, User


class UserAdmin(auth_admin.UserAdmin):
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name', 'password')
    search_fields = ('username',)
    list_filter = ('email', 'first_name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user',)
    list_filter = ('following',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
