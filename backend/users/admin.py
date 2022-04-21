from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


User = get_user_model()

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('email', 'username', 'last_name', 'first_name', 'subscribed_to',
              'is_staff')
    list_display = ('email', 'username', 'last_name', 'first_name')
    search_fields = ('email', 'username')
