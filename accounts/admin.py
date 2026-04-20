from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "phone", "is_verified", "is_staff", "is_active", "created_at"]
    list_filter = ["is_verified", "is_staff", "is_active", "is_superuser"]
    search_fields = ["email", "phone"]
    readonly_fields = ["created_at", "updated_at", "last_login"]

    fieldsets = (
        ("Account", {"fields": ("email", "phone", "password")}),
        ("Verification", {"fields": ("is_verified", "otp_code", "otp_purpose", "otp_created_at")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
