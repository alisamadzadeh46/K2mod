from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Address, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # no username field, login is by phone number
    ordering = ["-date_joined"]
    list_display = ["phone_number", "full_name", "email", "is_staff", "is_active", "date_joined"]
    search_fields = ["phone_number", "full_name", "email"]
    list_filter = ["is_staff", "is_active", "is_superuser"]
    list_per_page = 25
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("اطلاعات شخصی", {"fields": ("full_name", "email", "avatar")}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تاریخ‌های مهم", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "full_name", "password1", "password2"),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "city", "is_default"]
    search_fields = ["user__phone_number", "user__full_name", "city"]
    list_filter = ["is_default", "province"]
    list_per_page = 25
