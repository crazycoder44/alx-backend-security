from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP


class RequestLoggingMiddleware:
    """Middleware to log request details and handle IP blocking"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the client IP address
        ip_address = self.get_client_ip(request)

        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden('Your IP address has been blocked.')

        # Log the request
        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path
        )

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