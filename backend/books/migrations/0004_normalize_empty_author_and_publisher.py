from django.db import migrations


def normalize_empty_author_and_publisher(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    Book.objects.filter(author="").update(author=None)
    Book.objects.filter(publisher="").update(publisher=None)


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0003_normalize_empty_cover_image_url"),
    ]

    operations = [
        migrations.RunPython(
            normalize_empty_author_and_publisher,
            migrations.RunPython.noop,
        ),
    ]
