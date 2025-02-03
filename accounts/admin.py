from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'theme_preference')
    list_filter = ('is_staff', 'is_superuser', 'theme_preference')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('avatar', 'bio', 'theme_preference', 'notification_preferences')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'classes': ('wide',),
            'fields': ('email', 'avatar', 'bio', 'theme_preference'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
