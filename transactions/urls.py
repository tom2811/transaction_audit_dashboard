from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<int:transaction_id>/approve/', views.ApproveTransactionView.as_view(), name='approve_transaction'),
    path('transactions/<int:transaction_id>/toggle-flag/', views.ToggleFlagTransactionView.as_view(), name='toggle_flag_transaction'),
    path('reports/', views.reports, name='reports'),

    path('api/transactions/', views.TransactionViewSet.as_view(), name='api-transactions'),
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
]
