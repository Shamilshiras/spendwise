from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Category name")
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this category is active for new expenses."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="Amount must be greater than zero.")],
        help_text="Expense amount in Indian Rupees (₹)"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="expenses",
        help_text="Selected expense category"
    )
    date = models.DateField(
        default=timezone.now,
        help_text="Date the expense occurred"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Optional note describing the expense"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatically recorded creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modified timestamp"
    )

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["-date"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.category.name}: ₹{self.amount} on {self.date}"
