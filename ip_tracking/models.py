from django.db import models

class SuspiciousIP(models.Model):
    """Model to store suspicious IP addresses with reasons for flagging"""
    ip_address = models.GenericIPAddressField()
    first_detected = models.DateTimeField(auto_now_add=True)
    last_detected = models.DateTimeField(auto_now=True)
    request_count = models.IntegerField(default=0)
    reason = models.CharField(max_length=255)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Suspicious IP"
        verbose_name_plural = "Suspicious IPs"

    def __str__(self):
        return f"{self.ip_address} - {self.reason} ({self.request_count} requests)"


class RequestLog(models.Model):
    """Model to log request details with geolocation data"""
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    # Cache timestamp for geolocation data
    geo_cache_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        location = f"({self.city}, {self.country})" if self.city and self.country else ""
        return f"{self.ip_address} {location} - {self.path} at {self.timestamp}"


class BlockedIP(models.Model):
    """Model to store blocked IP addresses"""
    ip_address = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_address