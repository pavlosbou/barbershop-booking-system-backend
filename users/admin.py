from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User

# admin.site.register(User)
@admin.register(User)
class UserAdmin(BaseAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = ('email', 'first_name', 'last_name','phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active','is_superuser')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser','groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)