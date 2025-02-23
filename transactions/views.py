from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Avg, Case, When
from django.db.models.functions import TruncDate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView, View
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
import json
from allauth.account.views import LoginView
from django.db import models

from .models import Transaction
from .serializers import TransactionSerializer


class CustomLoginView(LoginView):
    """
    Custom login view with template
    """

    template_name = "account/login.html"


# Report View for transaction volumes and success rates
def reports(request):
    # Daily transaction volume
    daily_volume = (
        Transaction.objects.annotate(date=TruncDate("timestamp"))
        .values("date")
        .annotate(
            total_amount=Sum("amount"),
            transaction_count=Count("id"),
        )
        .order_by("-date")[:30]  # Last 30 days
    )

    # Daily success rate
    daily_success_rate = (
        Transaction.objects.annotate(date=TruncDate("timestamp"))
        .values("date")
        .annotate(
            total_transactions=Count("id"),
            successful_transactions=Count("id", filter=models.Q(status="completed")),
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

    # Calculate total amount for the period
    total_amount = sum(day["total_amount"] for day in daily_volume)

    context = {
        "daily_volume": list(daily_volume),
        "daily_success_rate": list(daily_success_rate),
        "total_amount": total_amount,
    }

    return render(request, "transactions/reports.html", context)


# API View for listing transactions
class TransactionViewSet(ListAPIView):
    queryset = Transaction.objects.all().order_by("-timestamp")
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]


# Dashboard View
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "transactions/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Status summary - explicitly order by status to match the chart colors
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

        # Merchant summary
        merchant_summary = (
            Transaction.objects.values("merchant")
            .annotate(
                total_amount=Sum("amount"),
                count=Count("id"),
                average_amount=Avg("amount"),
            )
            .order_by("-total_amount")[:10]
        )

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


# Transaction List View
class TransactionListView(LoginRequiredMixin, ListView):
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


# Approve Transaction View
class ApproveTransactionView(LoginRequiredMixin, View):
    def post(self, request, transaction_id, *args, **kwargs):
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.status = "completed"
        transaction.approved_by = request.user
        transaction.save()
        return render(
            request,
            "transactions/partials/transaction_row.html",
            {"transaction": transaction},
        )


# Toggle Flag Transaction View
class ToggleFlagTransactionView(LoginRequiredMixin, View):
    def post(self, request, transaction_id, *args, **kwargs):
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.is_flagged = not transaction.is_flagged
        transaction.save()
        return render(
            request,
            "transactions/partials/transaction_row.html",
            {"transaction": transaction},
        )
