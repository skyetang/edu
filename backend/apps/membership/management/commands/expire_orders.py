from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.membership.models import MemberOrder
from apps.membership.services import ORDER_EXPIRATION_MINUTES

class Command(BaseCommand):
    help = 'Expire pending orders older than 30 minutes'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(minutes=ORDER_EXPIRATION_MINUTES)
        count = MemberOrder.objects.filter(status="PENDING", created_at__lt=threshold).update(status="EXPIRED")
        self.stdout.write(self.style.SUCCESS(f'Successfully expired {count} orders'))
