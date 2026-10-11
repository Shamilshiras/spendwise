import os
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from expenses.models import Category, Expense

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


class Command(BaseCommand):
    help = "Initializes default categories and an admin user. Optionally seeds sample expense data."

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, default=os.environ.get("ADMIN_USER", "admin"))
        parser.add_argument("--password", type=str, default=os.environ.get("ADMIN_PASS", "admin123"))
        parser.add_argument("--sample-data", action="store_true", help="Seed realistic sample expenses")

    def handle(self, *args, **options):
        # 1. Ensure Categories exist
        self.stdout.write(self.style.NOTICE("Ensuring default categories exist..."))
        for name in DEFAULT_CATEGORIES:
            cat, created = Category.objects.get_or_create(name=name, defaults={"is_active": True})
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Created category: {name}"))
            else:
                self.stdout.write(f"  - Category exists: {name}")

        # 2. Ensure User exists
        User = get_user_model()
        username = options["username"]
        password = options["password"]
        user, created = User.objects.get_or_create(username=username, defaults={"is_staff": True, "is_superuser": True})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}' with provided password."))
        else:
            self.stdout.write(self.style.NOTICE(f"User '{username}' already exists."))

        # 3. Optional sample data
        if options["sample_data"]:
            self.stdout.write(self.style.NOTICE("Seeding sample expenses..."))
            today = timezone.localdate()
            cat_map = {c.name: c for c in Category.objects.all()}

            samples = [
                ("Food", Decimal("180.00"), today, "Lunch with colleague"),
                ("Fuel", Decimal("1200.00"), today - timedelta(days=1), "Petrol refill for bike"),
                ("Entertainment", Decimal("350.00"), today - timedelta(days=2), "Movie ticket"),
                ("Shopping", Decimal("2499.00"), today - timedelta(days=3), "Weekend grocery & snacks"),
                ("Bills", Decimal("850.00"), today - timedelta(days=4), "Broadband internet bill"),
                ("Gym", Decimal("1500.00"), today - timedelta(days=5), "Monthly gym subscription"),
                ("Food", Decimal("320.00"), today - timedelta(days=6), "Dinner & dessert"),
                ("Travel", Decimal("450.00"), today - timedelta(days=8), "Cab to railway station"),
                ("Hospital", Decimal("750.00"), today - timedelta(days=10), "Pharmacy medicine purchase"),
            ]

            count = 0
            for cat_name, amt, dt, desc in samples:
                if cat_name in cat_map:
                    Expense.objects.create(
                        category=cat_map[cat_name],
                        amount=amt,
                        date=dt,
                        description=desc,
                    )
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"Seeded {count} sample expense records."))

        self.stdout.write(self.style.SUCCESS("Initialization complete!"))
