from django.core.management.base import BaseCommand
from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    help = 'Remove an IP address from the blocked IPs list'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to unblock')

    def handle(self, *args, **options):
        ip_address = options['ip_address']

        try:
            # Validate IP address format
            validate_ipv46_address(ip_address)

            # Try to delete the blocked IP entry
            deleted_count, _ = BlockedIP.objects.filter(ip_address=ip_address).delete()

            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully unblocked IP: {ip_address}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'IP {ip_address} was not in the blocked list')
                )

        except ValidationError:
            self.stdout.write(
                self.style.ERROR(f'Invalid IP address format: {ip_address}')
            )