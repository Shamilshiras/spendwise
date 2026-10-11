from django.db import migrations

DEFAULT_CATEGORIES = [
    "Food",
    "Fuel",
    "Travel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Gym",
    "Hospital",
]


def seed_default_categories(apps, schema_editor):
    Category = apps.get_model("expenses", "Category")
    for name in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(name=name, defaults={"is_active": True})


def reverse_seed_categories(apps, schema_editor):
    Category = apps.get_model("expenses", "Category")
    Category.objects.filter(name__in=DEFAULT_CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, reverse_code=reverse_seed_categories),
    ]
