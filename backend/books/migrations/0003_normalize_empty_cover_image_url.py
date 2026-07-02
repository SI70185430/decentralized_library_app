from django.db import migrations


def normalize_empty_cover_image_url(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    Book.objects.filter(cover_image_url="").update(cover_image_url=None)


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0002_seed_genres"),
    ]

    operations = [
        migrations.RunPython(
            normalize_empty_cover_image_url,
            migrations.RunPython.noop,
        ),
    ]
