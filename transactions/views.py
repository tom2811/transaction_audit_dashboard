from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Avg, Case, When
from django.db.models.functions import TruncDate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView, View, DetailView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
import json
from django.db import models
from django.core.exceptions import PermissionDenied

from .models import Transaction
from .serializers import TransactionSerializer


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view showing transaction statistics"""

    template_name = "transactions/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Status summary with specific ordering
        status_order = ["completed", "pending", "failed"]
        status_summary = list(
            Transaction.objects.values("status")
            .annotate(total_amount=Sum("amount"))
            .filter(status__in=status_order)
            .order_by(
                Case(
                    *[
                        When(status=status, then=pos)
                        for pos, status in enumerate(status_order)
                    ]
                )
            )
        )

        # Top 10 merchants by transaction volume
        merchant_summary = (
            Transaction.objects.values("merchant")
            .annotate(
                total_amount=Sum("amount"),
                count=Count("id"),
                average_amount=Avg("amount"),
            )
            .order_by("-total_amount")[:10]
        )

        # Prepare data for charts
        context.update(
            {
                "status_summary_list": status_summary,
                "merchant_summary_list": merchant_summary,
                "status_labels": json.dumps(
                    [item["status"].title() for item in status_summary]
                ),
                "status_amounts": json.dumps(
                    [float(item["total_amount"]) for item in status_summary]
                ),
                "merchant_labels": json.dumps(
                    [item["merchant"] for item in merchant_summary]
                ),
                "merchant_amounts": json.dumps(
                    [float(item["total_amount"]) for item in merchant_summary]
                ),
            }
        )
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    """View for displaying and filtering transactions"""

    model = Transaction
    template_name = "transactions/transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-timestamp")
        search_query = self.request.GET.get("merchant", "").strip()
        status_filter = self.request.GET.get("status", "")
        flag_filter = self.request.GET.get("flag", "all")

        if search_query:
            queryset = queryset.filter(merchant__icontains=search_query)
        if status_filter in dict(Transaction.STATUS_CHOICES):
            queryset = queryset.filter(status=status_filter)
        if flag_filter != "all":
            queryset = queryset.filter(is_flagged=(flag_filter == "true"))

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            self.template_name = "transactions/partials/transaction_table.html"
        return super().render_to_response(context, **response_kwargs)


class ApproveTransactionView(LoginRequiredMixin, View):
    """Handle transaction approval"""

    def post(self, request, transaction_id, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can approve transactions")

        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction._history_user = request.user
        transaction.status = "completed"
        transaction.approved_by = request.user
        transaction.save()

        return render(
            request,
            "transactions/partials/transaction_row.html",
            {"transaction": transaction},
        )


class ToggleFlagTransactionView(LoginRequiredMixin, View):
    """Handle transaction flag toggling"""

    def post(self, request, transaction_id):
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can flag transactions")

        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction._history_user = request.user
        transaction.is_flagged = not transaction.is_flagged
        transaction.save()

        return render(
            request,
            "transactions/partials/transaction_row.html",
            {"transaction": transaction},
        )


class TransactionHistoryView(LoginRequiredMixin, DetailView):
    """View the history records of a certain transaction record"""

    model = Transaction
    template_name = "transactions/transaction_history.html"
    context_object_name = "transaction"
    pk_url_kwarg = "transaction_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history"] = (
            self.object.history.all()
            .select_related("history_user")
            .order_by("-history_date")
        )
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    """Generate transaction reports for daily volumes and success rates"""

    template_name = "transactions/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Daily transaction volume
        daily_volume = (
            Transaction.objects.annotate(date=TruncDate("timestamp"))
            .values("date")
            .annotate(
                total_amount=Sum("amount"),
                transaction_count=Count("id"),
            )
            .order_by("-date")[:30]
        )

        # Daily success rate
        daily_success_rate = (
            Transaction.objects.annotate(date=TruncDate("timestamp"))
            .values("date")
            .annotate(
                total_transactions=Count("id"),
                successful_transactions=Count(
                    "id", filter=models.Q(status="completed")
                ),
            )
            .order_by("-date")[:30]
        )

        # Calculate success rates as percentages
        for day in daily_success_rate:
            day["success_rate"] = (
                (day["successful_transactions"] / day["total_transactions"] * 100)
                if day["total_transactions"] > 0
                else 0
            )

        context.update(
            {
                "daily_volume": list(daily_volume),
                "daily_success_rate": list(daily_success_rate),
                "total_amount": sum(day["total_amount"] for day in daily_volume),
            }
        )
        return context


class TransactionViewSet(ListAPIView):
    """API endpoint for listing transactions"""

    queryset = Transaction.objects.all().order_by("-timestamp")
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
