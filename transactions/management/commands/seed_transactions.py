from django.core.management.base import BaseCommand
from transactions.models import Transaction
from django.contrib.auth.models import User
from faker import Faker
import random
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed the database with random transactions"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")
        fake = Faker()
        statuses = ["pending", "completed", "failed"]

        # Disable auto_now_add for bulk creation
        Transaction._meta.get_field("timestamp").auto_now_add = False

        transactions = []

        for _ in range(15000):
            # Generate timezone-aware datetime
            naive_datetime = fake.date_time_between(start_date="-1y", end_date="now")
            aware_datetime = timezone.make_aware(naive_datetime)

            # If status is completed, must have an approver
            status = random.choice(statuses)
            approver = None
            if status == "completed":
                approver = random.choice(User.objects.all())

            transaction = Transaction(
                amount=random.uniform(10, 10000),
                status=status,
                timestamp=aware_datetime,
                merchant=fake.company(),
                is_flagged=random.choice([True, False]),
                approved_by=approver,
            )
            transactions.append(transaction)

        Transaction.objects.bulk_create(transactions)

        # Re-enable auto_now_add
        Transaction._meta.get_field("timestamp").auto_now_add = True

        self.stdout.write(self.style.SUCCESS("Database seeded successfully"))
