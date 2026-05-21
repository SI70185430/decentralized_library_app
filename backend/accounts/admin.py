from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "employee_id",
        "password",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
        "updated_at",
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "employee_id",
                    "is_staff",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
