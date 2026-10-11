from decimal import Decimal
from django import forms
from django.utils import timezone
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True).order_by("name"),
        empty_label="Select a Category",
        widget=forms.Select(attrs={"class": "form-select", "required": "required"}),
    )

    class Meta:
        model = Expense
        fields = ["amount", "category", "date", "description"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 250.00",
                    "step": "0.01",
                    "min": "0.01",
                    "required": "required",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": "required",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional note (e.g. Lunch with team, Grocery shopping)",
                    "maxlength": "255",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default date to today's date if creating new expense
        if not self.instance.pk and not self.initial.get("date"):
            self.initial["date"] = timezone.localdate().isoformat()

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= Decimal("0"):
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
