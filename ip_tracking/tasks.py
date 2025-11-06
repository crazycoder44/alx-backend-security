from config.celery import app
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP, BlockedIP

SENSITIVE_PATHS = ['/admin', '/login', '/auth', '/api']
REQUEST_THRESHOLD = 100  # Maximum requests per hour
BLOCK_THRESHOLD = 3  # Number of times an IP can be flagged before being blocked

@app.task
def detect_anomalies():
    """
    Celery task to detect suspicious IP activity
    Runs hourly to check for:
    - IPs exceeding 100 requests per hour
    - IPs accessing sensitive paths frequently
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Check for high request volume
    high_volume_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=Count('ip_address'))
        .filter(request_count__gt=REQUEST_THRESHOLD)
    )

    # Check for sensitive path access
    sensitive_path_ips = (
        RequestLog.objects
        .filter(
            timestamp__gte=one_hour_ago,
            path__in=SENSITIVE_PATHS
        )
        .values('ip_address')
        .annotate(sensitive_count=Count('ip_address'))
        .filter(sensitive_count__gt=10)  # More than 10 sensitive path accesses per hour
    )

    # Process high volume IPs
    for ip_data in high_volume_ips:
        _process_suspicious_ip(
            ip_data['ip_address'],
            f"Exceeded request threshold: {ip_data['request_count']} requests/hour"
        )

    # Process sensitive path access
    for ip_data in sensitive_path_ips:
        _process_suspicious_ip(
            ip_data['ip_address'],
            f"High sensitive path access: {ip_data['sensitive_count']} requests/hour"
        )

def _process_suspicious_ip(ip_address, reason):
    """Helper function to process suspicious IPs"""
    suspicious_ip, created = SuspiciousIP.objects.get_or_create(
        ip_address=ip_address,
        defaults={'reason': reason}
    )

    if not created:
        suspicious_ip.request_count += 1
        suspicious_ip.reason = f"{suspicious_ip.reason}; {reason}"
        suspicious_ip.save()

        # Check if IP should be blocked
        if suspicious_ip.request_count >= BLOCK_THRESHOLD:
            BlockedIP.objects.get_or_create(ip_address=ip_address)
            suspicious_ip.is_blocked = True
            suspicious_ip.save()