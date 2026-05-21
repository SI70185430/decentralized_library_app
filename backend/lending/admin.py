from django.contrib import admin

from .models import Lending, Reservation

@admin.register(Lending)
class LendingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book_copy",
        "user",
        "borrowed_date",
        "due_date",
        "returned_date",
        "extension_count",
        "created_at",
        "updated_at",
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book_copy",
        "user",
        "scheduled_date",
        "expires_date",
        "created_at",
        "updated_at",
    )

