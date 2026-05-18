import uuid

from django.db import models
from django.db.models import Q

class TimeStampedModel(models.Model):
    """作成日時・更新日時を持つモデルの共通基底クラス。"""

    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        abstract = True

class Genre(models.Model):
    c_code_genre = models.CharField("Cコード内容", max_length=2, primary_key=True)
    name = models.CharField("ジャンル名", max_length=255, unique=True)

    class Meta:
        db_talble = "genre"

        def __str__(self):
            return self.name

class Book(TimeStampedModel):
    id = models.UUIDField("書籍ID", primary_key=True, default=uuid.uuid7, editable=False)
    genre = models.ForeignKey(
        Genre,
        to_field="c_code_genre",
        db_column="c_code_genre",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )
    isbn = models.CharField("ISBNコード", max_length=20, unique=True)
    title = models.CharField("タイトル", max_length=255)
    author = models.CharField("著者", max_length=255, null=True, blank=True)
    publisher = models.CharField("出版社名", max_length=255, null=True, blank=True)
    published_date = models.DateField("出版日", null=True, blank=True)
    price = models.IntegerField("価格", null=True, blank=True)
    cover_image_url = models.URLField("表紙URL", max_length=500, null=True, blank=True)
    description = models.TextField("説明", null=True, blank=True)

    class Meta:
        db_table = 'book'

        constraints = [
            models.CheckConstraint(
                condition=Q(price__isnull=True) | Q(price__gte=0),
                name="book_price_gte_0_or_null"
            )
        ]

    def __str__(self):
        return self.title


class BookCopy(TimeStampedModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", "利用可能"
        RESERED = "on_loan", "貸出中"
        RESERVED = "reserved", "予約中"
        LOST = "lost", "紛失"

    id = models.UUIDField("蔵書ID", primary_key=True, default=uuid.uuid7, editable=False)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="Bookcopy",
    )
    status = models.CharField(
        "ステータス",
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    location = models.CharField("保管場所", max_length=255)
    purchase_date = models.DateField("購入日", null=True, blank= True)
    note = models.TextField("備考", null=True, blank=True)

    class Meta:
        db_table = 'book_copy'
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["available", "on_loan", "reserved", "lost"]),
                name="book_copy_status_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.book} ({self.location})"
