from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    merchant = models.CharField(max_length=255)
    is_flagged = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    history = HistoricalRecords()

    class Meta:
        indexes = [
            models.Index(fields=["merchant"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.merchant} - {self.amount} - {self.status}"
