from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser

EDITABLE_FIELDS = (
    "username",
    "employee_id",
    "is_active",
)


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    fieldsets = (
        (
            "編集可能なユーザー情報",
            {
                "fields": EDITABLE_FIELDS,
            },
        ),
    )

    list_display = (
        "id",
        "username",
        "employee_id",
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
