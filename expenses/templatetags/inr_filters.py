from django import template
from expenses.utils import format_inr

register = template.Library()


@register.filter(name="inr")
def inr_filter(value, show_paise=False):
    """
    Template filter to format numbers as Indian Rupees.
    Usage: {{ expense.amount|inr }} or {{ expense.amount|inr:True }}
    """
    return format_inr(value, show_paise=bool(show_paise))
