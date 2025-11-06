from django.core.management.base import BaseCommand
from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    help = 'Add an IP address to the blocked IPs list'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to block')

    def handle(self, *args, **options):
        ip_address = options['ip_address']

        try:
            # Validate IP address format
            validate_ipv46_address(ip_address)

            # Create blocked IP entry
            blocked_ip, created = BlockedIP.objects.get_or_create(
                ip_address=ip_address
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully blocked IP: {ip_address}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'IP {ip_address} was already blocked')
                )

        except ValidationError:
            self.stdout.write(
                self.style.ERROR(f'Invalid IP address format: {ip_address}')
            )