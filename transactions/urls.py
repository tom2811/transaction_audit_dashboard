from django.urls import path
from . import views
from allauth.account.views import LoginView

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Transaction Management
    path("transactions/", views.TransactionListView.as_view(), name="transaction_list"),
    path(
        "transactions/<int:transaction_id>/approve/",
        views.ApproveTransactionView.as_view(),
        name="approve_transaction",
    ),
    path(
        "transactions/<int:transaction_id>/toggle-flag/",
        views.ToggleFlagTransactionView.as_view(),
        name="toggle_flag_transaction",
    ),
    path(
        "transactions/<int:transaction_id>/history/",
        views.TransactionHistoryView.as_view(),
        name="transaction_history",
    ),
    # Reports
    path("reports/", views.ReportsView.as_view(), name="reports"),
    # API
    path(
        "api/transactions/", views.TransactionViewSet.as_view(), name="api-transactions"
    ),
    # Authentication
    path("accounts/login/", LoginView.as_view(), name="account_login"),
]
