from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser

EDITABLE_FIELDS = (
    "username",
    "employee_id",
    "is_active",
)

GROUP_FIELDS = ("groups",)


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    fieldsets = (
        (
            "編集可能なユーザー情報",
            {
                "fields": EDITABLE_FIELDS,
            },
        ),
        (
            "権限グループ",
            {
                "fields": GROUP_FIELDS,
            },
        ),
    )

    filter_horizontal = GROUP_FIELDS

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
