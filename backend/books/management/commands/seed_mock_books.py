from django.core.management.base import BaseCommand, CommandError

from books.models import Book

DEFAULT_COUNT = 70
DEFAULT_PREFIX = "PaginationTest"
MOCK_ISBN_BODY_PREFIX = "978999000"
MOCK_AUTHOR = "Mock Author"
MOCK_PUBLISHER = "Mock Publisher"
MOCK_PUBLISHED_DATE = "2026-01-01"
MOCK_PRICE = 1000
MOCK_DESCRIPTION = "ページネーション確認用のmock書籍です。"
MAX_MOCK_BOOK_COUNT = 999


class Command(BaseCommand):
    help = "ページネーション確認用のmock書籍を作成・削除します"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=DEFAULT_COUNT,
            help=f"作成するmock書籍数。デフォルトは{DEFAULT_COUNT}件です。",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default=DEFAULT_PREFIX,
            help=f"mock書籍タイトルのprefix。デフォルトは{DEFAULT_PREFIX}です。",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="指定prefixで始まるmock書籍を削除します。",
        )

    def handle(self, *args, **options):
        count = options["count"]
        prefix = options["prefix"]
        should_delete = options["delete"]

        if not prefix:
            raise CommandError("--prefix には空文字以外を指定してください。")

        if should_delete:
            deleted_count, _ = Book.objects.filter(title__startswith=prefix).delete()
            self.stdout.write(
                self.style.SUCCESS(f"mock books deleted. prefix={prefix}, deleted={deleted_count}")
            )
            return

        validate_count(count)

        created_count = 0
        updated_count = 0

        for index in range(1, count + 1):
            _, created = Book.objects.update_or_create(
                isbn=build_mock_isbn(index),
                defaults={
                    "title": f"{prefix} Book {index:03d}",
                    "author": MOCK_AUTHOR,
                    "publisher": MOCK_PUBLISHER,
                    "published_date": MOCK_PUBLISHED_DATE,
                    "price": MOCK_PRICE,
                    "description": MOCK_DESCRIPTION,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"mock books seeded. prefix={prefix}, created={created_count}, updated={updated_count}"
            )
        )


def validate_count(count: int) -> None:
    if count < 1:
        raise CommandError("--count には1以上を指定してください。")

    if count > MAX_MOCK_BOOK_COUNT:
        raise CommandError(f"--count は{MAX_MOCK_BOOK_COUNT}以下を指定してください。")


def build_mock_isbn(index: int) -> str:
    isbn_body = f"{MOCK_ISBN_BODY_PREFIX}{index:03d}"
    digits = [int(digit) for digit in isbn_body]
    total = sum(digit if position % 2 == 0 else digit * 3 for position, digit in enumerate(digits))
    check_digit = (10 - total % 10) % 10
    return f"{isbn_body}{check_digit}"
