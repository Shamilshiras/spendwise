from datetime import date, timedelta
from decimal import Decimal
import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from expenses.models import Category, Expense
from expenses.utils import format_inr

User = get_user_model()


class CurrencyFormattingTest(TestCase):

    def test_inr_formatting_standard_cases(self):
        self.assertEqual(format_inr(180), "₹180")
        self.assertEqual(format_inr(1200), "₹1,200")
        self.assertEqual(format_inr(25000), "₹25,000")
        self.assertEqual(format_inr(125000), "₹1,25,000")
        self.assertEqual(format_inr(1250000), "₹12,50,000")
        self.assertEqual(format_inr(10000000), "₹1,00,00,000")
        self.assertEqual(format_inr(0), "₹0")

    def test_inr_formatting_decimals(self):
        self.assertEqual(format_inr(Decimal("180.00")), "₹180")
        self.assertEqual(format_inr(Decimal("180.50")), "₹180.50")
        self.assertEqual(format_inr(Decimal("1200.75")), "₹1,200.75")
        self.assertEqual(format_inr(Decimal("180.00"), show_paise=True), "₹180.00")

    def test_inr_formatting_negatives(self):
        self.assertEqual(format_inr(-500), "-₹500")


class CategoryAndExpenseModelTest(TestCase):

    def setUp(self):
        self.food_cat = Category.objects.get(name="Food")

    def test_predefined_categories_exist(self):
        expected_categories = [
            "Food", "Fuel", "Travel", "Shopping",
            "Bills", "Entertainment", "Gym", "Hospital"
        ]
        existing_categories = list(Category.objects.values_list("name", flat=True))
        for cat in expected_categories:
            self.assertIn(cat, existing_categories)

    def test_create_expense_valid(self):
        exp = Expense.objects.create(
            amount=Decimal("250.00"),
            category=self.food_cat,
            date=timezone.localdate(),
            description="Breakfast"
        )
        self.assertEqual(exp.amount, Decimal("250.00"))
        self.assertEqual(exp.category.name, "Food")
        self.assertEqual(exp.description, "Breakfast")

    def test_amount_must_be_greater_than_zero(self):
        exp = Expense(
            amount=Decimal("0.00"),
            category=self.food_cat,
            date=timezone.localdate(),
        )
        with self.assertRaises(ValidationError):
            exp.full_clean()

        exp_neg = Expense(
            amount=Decimal("-50.00"),
            category=self.food_cat,
            date=timezone.localdate(),
        )
        with self.assertRaises(ValidationError):
            exp_neg.full_clean()


class AuthenticationAndSecurityTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="securepassword123")

    def test_unauthenticated_redirects_to_login(self):
        protected_urls = [
            reverse("dashboard"),
            reverse("expense_list"),
            reverse("expense_create"),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login/", response.url)

    def test_login_flow(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_logout_flow(self):
        self.client.login(username="testuser", password="securepassword123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))


class ExpenseCRUDAndFilterTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pw1")
        self.client.login(username="user1", password="pw1")
        self.food = Category.objects.get(name="Food")
        self.fuel = Category.objects.get(name="Fuel")
        self.today = timezone.localdate()

    def test_add_expense_valid(self):
        response = self.client.post(reverse("expense_create"), {
            "amount": "350.50",
            "category": self.food.id,
            "date": self.today.isoformat(),
            "description": "Lunch meeting",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Expense.objects.filter(description="Lunch meeting", amount=Decimal("350.50")).exists())

    def test_add_expense_invalid_amount(self):
        response = self.client.post(reverse("expense_create"), {
            "amount": "0.00",
            "category": self.food.id,
            "date": self.today.isoformat(),
            "description": "Zero amount",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "amount", "Amount must be greater than zero.")

    def test_edit_expense(self):
        exp = Expense.objects.create(
            amount=Decimal("100.00"),
            category=self.food,
            date=self.today,
            description="Initial"
        )
        response = self.client.post(reverse("expense_update", kwargs={"pk": exp.pk}), {
            "amount": "150.00",
            "category": self.fuel.id,
            "date": self.today.isoformat(),
            "description": "Updated",
        })
        self.assertEqual(response.status_code, 302)
        exp.refresh_from_db()
        self.assertEqual(exp.amount, Decimal("150.00"))
        self.assertEqual(exp.category, self.fuel)
        self.assertEqual(exp.description, "Updated")

    def test_delete_expense_with_confirmation(self):
        exp = Expense.objects.create(
            amount=Decimal("500.00"),
            category=self.food,
            date=self.today,
            description="To be deleted"
        )
        # GET request shows confirmation page
        get_res = self.client.get(reverse("expense_delete", kwargs={"pk": exp.pk}))
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "Confirm Expense Deletion")

        # POST request deletes the expense
        post_res = self.client.post(reverse("expense_delete", kwargs={"pk": exp.pk}))
        self.assertEqual(post_res.status_code, 302)
        self.assertFalse(Expense.objects.filter(pk=exp.pk).exists())

    def test_filtering_and_sorting(self):
        Expense.objects.create(amount=Decimal("100.00"), category=self.food, date=self.today - timedelta(days=2), description="Apple")
        Expense.objects.create(amount=Decimal("800.00"), category=self.fuel, date=self.today - timedelta(days=1), description="Petrol")
        Expense.objects.create(amount=Decimal("300.00"), category=self.food, date=self.today, description="Burger")

        # 1. Category filter
        res_cat = self.client.get(reverse("expense_list") + f"?category={self.food.id}")
        self.assertEqual(res_cat.context["filtered_count"], 2)

        # 2. Search query filter
        res_search = self.client.get(reverse("expense_list") + "?q=Petrol")
        self.assertEqual(res_search.context["filtered_count"], 1)

        # 3. Sort by amount descending
        res_sort = self.client.get(reverse("expense_list") + "?sort=-amount")
        items = list(res_sort.context["page_obj"])
        self.assertEqual(items[0].amount, Decimal("800.00"))


class DashboardAnalyticsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="dashuser", password="dashpassword")
        self.client.login(username="dashuser", password="dashpassword")
        self.food = Category.objects.get(name="Food")
        self.fuel = Category.objects.get(name="Fuel")
        self.today = timezone.localdate()

    def test_dashboard_aggregates(self):
        # Expense today
        Expense.objects.create(amount=Decimal("200.00"), category=self.food, date=self.today, description="Today snack")

        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

        # Verify summary cards data
        self.assertEqual(response.context["today_total"], Decimal("200.00"))
        self.assertGreaterEqual(response.context["week_total"], Decimal("200.00"))
        self.assertGreaterEqual(response.context["month_total"], Decimal("200.00"))
        self.assertGreaterEqual(response.context["total_transactions_count"], 1)

        # Verify weekly chart json contains 7 days
        weekly_labels = json.loads(response.context["weekly_chart_labels_json"])
        self.assertEqual(len(weekly_labels), 7)

        weekly_data = json.loads(response.context["weekly_chart_data_json"])
        self.assertEqual(len(weekly_data), 7)

        # Verify branding and tagline
        self.assertContains(response, "SpendWise")
        self.assertContains(response, "Because money shouldn&#x27;t just vanish")

