from django.http import HttpResponse

def test_view(request):
    """A simple view to test IP tracking and blocking"""
    return HttpResponse("Hello! Your request has been logged. Your IP address is: " + request.META.get('REMOTE_ADDR', 'unknown'))