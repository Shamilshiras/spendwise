from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("expenses/", views.expense_list_view, name="expense_list"),
    path("expenses/add/", views.expense_create_view, name="expense_create"),
    path("expenses/<int:pk>/edit/", views.expense_update_view, name="expense_update"),
    path("expenses/<int:pk>/delete/", views.expense_delete_view, name="expense_delete"),
]
