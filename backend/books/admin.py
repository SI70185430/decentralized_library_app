from django.contrib import admin

from .models import Book, BookCopy, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        "c_code_genre",
        "name",
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "genre",
        "isbn",
        "title",
        "author",
        "publisher",
        "published_date",
        "price",
        "cover_image_url",
        "description",
        "created_at",
        "updated_at",
    )


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "status",
        "location",
        "purchase_date",
        "note",
        "created_at",
        "updated_at",
    )
