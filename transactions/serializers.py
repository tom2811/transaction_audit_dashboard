from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    approved_by = serializers.CharField(source="approved_by.username", allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "status",
            "timestamp",
            "merchant",
            "is_flagged",
            "approved_by",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["amount"] = float(data["amount"])
        return data
