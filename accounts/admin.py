from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

class UserAdmin(BaseUserAdmin):
    list_display = ("email", "role", "branch", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "branch")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Role & Branch", {"fields": ("role", "branch")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    search_fields = ("email",)
    ordering = ("email",)

admin.site.register(User, UserAdmin)
admin.site.register(Profile)
