from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from django_ip_geolocation.middleware import IpGeolocationMiddleware
from .models import RequestLog, BlockedIP
import requests


class RequestLoggingMiddleware:
    """Middleware to log request details and handle IP blocking with geolocation"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_duration = timedelta(hours=24)
        self.geolocation_middleware = IpGeolocationMiddleware(get_response)

    def __call__(self, request):
        # Get the client IP address
        ip_address = self.get_client_ip(request)

        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden('Your IP address has been blocked.')

        # Get or create request log
        log_entry = RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path
        )

        # Update geolocation if needed (cached for 24 hours)
        self.update_geolocation(log_entry)

        # Process the request
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def update_geolocation(self, log_entry):
        """Update geolocation data if cache has expired"""
        now = timezone.now()
        
        # Check if we need to update geolocation data
        needs_update = (
            not log_entry.geo_cache_timestamp or
            now - log_entry.geo_cache_timestamp > self.cache_duration
        )

        if needs_update:
            # Handle localhost and private IPs
            if log_entry.ip_address in ['127.0.0.1', 'localhost', '::1']:
                log_entry.country = 'Local'
                log_entry.city = 'Localhost'
                log_entry.geo_cache_timestamp = now
                log_entry.save()
                return

            try:
                # Using ip-api.com free service
                response = requests.get(f'http://ip-api.com/json/{log_entry.ip_address}')
                if response.status_code == 200:
                    geo_data = response.json()
                    if geo_data.get('status') == 'success':
                        log_entry.country = geo_data.get('country')
                        log_entry.city = geo_data.get('city')
                        log_entry.geo_cache_timestamp = now
                        log_entry.save()
                    elif geo_data.get('message') == 'reserved range':
                        # Handle private network IPs (192.168.x.x, 10.x.x.x, etc.)
                        log_entry.country = 'Private Network'
                        log_entry.city = 'Local Network'
                        log_entry.geo_cache_timestamp = now
                        log_entry.save()
            except requests.RequestException:
                # If geolocation fails, we'll just continue without it
                pass