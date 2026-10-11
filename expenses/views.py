import calendar
import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ExpenseForm
from .models import Expense, Category
from .utils import format_inr


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next") or "dashboard"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm(request)

    return render(request, "expenses/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required
def dashboard_view(request):
    today = timezone.localdate()

    # Week calculation: Monday through Sunday
    weekday_idx = today.weekday()  # Monday is 0, Sunday is 6
    start_of_week = today - timedelta(days=weekday_idx)
    end_of_week = start_of_week + timedelta(days=6)

    # Month calculation: 1st of month to last day of month
    start_of_month = today.replace(day=1)
    _, num_days_in_month = calendar.monthrange(today.year, today.month)
    end_of_month = today.replace(day=num_days_in_month)

    # Base querysets
    all_expenses = Expense.objects.all()

    # 1. Summary Cards
    today_total = (
        all_expenses.filter(date=today).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    week_qs = all_expenses.filter(date__range=[start_of_week, end_of_week])
    week_total = week_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    week_count = week_qs.count()

    month_qs = all_expenses.filter(date__range=[start_of_month, end_of_month])
    month_total = month_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    month_count = month_qs.count()

    total_transactions_count = all_expenses.count()

    # 2. Weekly Daily Breakdown (Monday to Sunday)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly_chart_labels = []
    weekly_chart_data = []
    weekly_days_breakdown = []

    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        day_total = (
            all_expenses.filter(date=current_day).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        label = f"{day_names[i]} ({current_day.strftime('%d %b')})"
        weekly_chart_labels.append(label)
        weekly_chart_data.append(float(day_total))
        weekly_days_breakdown.append({
            "day_name": day_names[i],
            "date": current_day,
            "total": day_total,
            "is_today": current_day == today,
        })

    # 3. Monthly Category Breakdown (Doughnut Chart)
    # Categories with no expenses are omitted from doughnut chart as per PRD
    monthly_cat_aggregates = (
        month_qs.values("category__name")
        .annotate(total=Sum("amount"), count=Count("id"))
        .filter(total__gt=0)
        .order_by("-total")
    )
    month_category_labels = [item["category__name"] for item in monthly_cat_aggregates]
    month_category_data = [float(item["total"]) for item in monthly_cat_aggregates]

    # Highest spending category for current month
    highest_category = monthly_cat_aggregates.first() if monthly_cat_aggregates.exists() else None

    # Average daily spending for current month:
    # Calculated as monthly spending divided by number of elapsed calendar days in the month, including today.
    elapsed_days_in_month = today.day
    avg_daily_spending = (
        (month_total / Decimal(elapsed_days_in_month))
        if elapsed_days_in_month > 0
        else Decimal("0.00")
    )

    # 4. Monthly Spending Trend Line Chart (Day 1 to today / end of month)
    # PRD: daily spending throughout the current month
    month_trend_labels = []
    month_trend_data = []
    # Up to today or through end of month; showing up to today or all days of month
    for day_num in range(1, today.day + 1):
        day_date = today.replace(day=day_num)
        daily_sum = (
            all_expenses.filter(date=day_date).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        month_trend_labels.append(day_date.strftime("%d %b"))
        month_trend_data.append(float(daily_sum))

    # 5. Recent Expenses (latest 6)
    recent_expenses = all_expenses.select_related("category")[:6]

    context = {
        "today": today,
        "today_total": today_total,
        "week_total": week_total,
        "week_count": week_count,
        "month_total": month_total,
        "month_count": month_count,
        "total_transactions_count": total_transactions_count,
        "avg_daily_spending": avg_daily_spending,
        "highest_category": highest_category,
        "elapsed_days_in_month": elapsed_days_in_month,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "start_of_month": start_of_month,
        "end_of_month": end_of_month,
        "weekly_days_breakdown": weekly_days_breakdown,
        "recent_expenses": recent_expenses,
        # Chart JSON data
        "weekly_chart_labels_json": json.dumps(weekly_chart_labels),
        "weekly_chart_data_json": json.dumps(weekly_chart_data),
        "month_category_labels_json": json.dumps(month_category_labels),
        "month_category_data_json": json.dumps(month_category_data),
        "month_trend_labels_json": json.dumps(month_trend_labels),
        "month_trend_data_json": json.dumps(month_trend_data),
    }
    return render(request, "expenses/dashboard.html", context)


@login_required
def expense_list_view(request):
    queryset = Expense.objects.select_related("category").all()

    # 1. Category filter
    category_id = request.GET.get("category", "").strip()
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # 2. Date range filter
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    # 3. Search query (description)
    search_query = request.GET.get("q", "").strip()
    if search_query:
        queryset = queryset.filter(description__icontains=search_query)

    # 4. Sorting
    # Default is newest first: -date, -created_at
    sort_by = request.GET.get("sort", "-date").strip()
    valid_sorts = {
        "-date": ["-date", "-created_at"],
        "date": ["date", "created_at"],
        "-amount": ["-amount", "-date"],
        "amount": ["amount", "-date"],
    }
    ordering = valid_sorts.get(sort_by, ["-date", "-created_at"])
    queryset = queryset.order_by(*ordering)

    # Aggregates for the filtered set
    filtered_aggregates = queryset.aggregate(
        total_amount=Sum("amount"),
        total_count=Count("id"),
    )
    filtered_total = filtered_aggregates["total_amount"] or Decimal("0.00")
    filtered_count = filtered_aggregates["total_count"] or 0

    # 5. Pagination
    paginator = Paginator(queryset, 15)  # 15 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True).order_by("name")

    # Preserve GET parameters for pagination links without 'page'
    query_params = request.GET.copy()
    if "page" in query_params:
        query_params.pop("page")
    preserved_query_params = query_params.urlencode()

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_id,
        "start_date": start_date,
        "end_date": end_date,
        "search_query": search_query,
        "sort_by": sort_by,
        "filtered_total": filtered_total,
        "filtered_count": filtered_count,
        "preserved_query_params": preserved_query_params,
    }
    return render(request, "expenses/expense_list.html", context)


@login_required
def expense_create_view(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            messages.success(
                request,
                f"Expense of {format_inr(expense.amount)} under '{expense.category.name}' recorded successfully!"
            )
            return redirect("expense_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ExpenseForm()

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "action_title": "Add New Expense",
        "submit_button_label": "Save Expense",
        "is_edit": False,
    })


@login_required
def expense_update_view(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            expense = form.save()
            messages.success(
                request,
                f"Expense of {format_inr(expense.amount)} updated successfully."
            )
            return redirect("expense_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "expense": expense,
        "action_title": "Edit Expense",
        "submit_button_label": "Update Expense",
        "is_edit": True,
    })


@login_required
def expense_delete_view(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        amount_formatted = format_inr(expense.amount)
        cat_name = expense.category.name
        date_str = expense.date.strftime("%d %b %Y")
        expense.delete()
        messages.success(
            request,
            f"Expense of {amount_formatted} ({cat_name} on {date_str}) deleted successfully."
        )
        return redirect("expense_list")

    return render(request, "expenses/expense_confirm_delete.html", {
        "expense": expense,
    })
