from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


User = get_user_model()

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'username', 'last_name', 'first_name',
                'subscribed_to', 'password', 'is_staff')}),
    )
    list_display = ('email', 'username', 'last_name', 'first_name')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', )
