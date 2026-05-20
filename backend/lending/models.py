import uuid

from django.db import models
from django.db.models import F, Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        abstract = True


class Lending(TimeStampedModel):
    id = models.UUIDField("貸出ID", primary_key=True, default=uuid.uuid7, editable=False)
    book_copy = models.ForeignKey(
        "books.BookCopy",
        verbose_name="蔵書ID",
        on_delete=models.RESTRICT,
        related_name="lending",
    )
    user = models.ForeignKey(
        "accounts.AppUser",
        verbose_name="ユーザID",
        on_delete=models.RESTRICT,
        related_name="lending",
    )
    borrowed_date = models.DateField("貸出日")
    due_date = models.DateField("返却期限日")
    returned_date = models.DateField("実返却日", null=True, blank=True)
    extension_count = models.SmallIntegerField("延長回数", default=0)

    class Meta:
        db_table = "lending"
        constraints = [
            models.UniqueConstraint(
                fields=["book_copy", "user"],
                name="lending_book_copy_user_unique",
            ),
            models.CheckConstraint(
                condition=Q(due_date__gte=F("borrowed_date")),
                name="lending_due_date_gte_borrowed_date",
            ),
            models.CheckConstraint(
                condition=Q(returned_date__isnull=True) | Q(returned_date__gte=F("borrowed_date")),
                name="lending_returned_date_gte_borrowed_date",
            ),
            models.CheckConstraint(
                condition=Q(extension_count__gte=0) & Q(extension_count__lte=3),
                name="lending_extension_count_between_0_3",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.book_copy}"


class Reservation(TimeStampedModel):
    id = models.UUIDField("予約ID", primary_key=True, default=uuid.uuid7, editable=False)
    book_copy = models.ForeignKey(
        "books.BookCopy",
        verbose_name="蔵書ID",
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    user = models.ForeignKey(
        "accounts.AppUser",
        verbose_name="ユーザID",
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    scheduled_date = models.DateField("予定貸出日")
    expires_date = models.DateField("取り置き期限")

    class Meta:
        db_table = "reservation"
        constraints = [
            models.UniqueConstraint(
                fields=["book_copy", "user"],
                name="reservation_book_copy_user_unique",
            ),
            models.CheckConstraint(
                condition=Q(expires_date__gte=F("scheduled_date")),
                name="reservation_expires_date_gte_scheduled_date",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.book_copy}"
