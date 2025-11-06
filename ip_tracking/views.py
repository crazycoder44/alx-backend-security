from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django_ratelimit.decorators import ratelimit  # Fixed import

def test_view(request):
    """A simple view to test IP tracking and blocking"""
    return HttpResponse("Hello! Your request has been logged. Your IP address is: " + request.META.get('REMOTE_ADDR', 'unknown'))

@csrf_protect
@require_http_methods(["POST"])
@ratelimit(key='ip',
          rate=lambda r: '10/m' if r.user.is_authenticated else '5/m',
          method=['POST'],
          group='login')
def login_view(request):
    """Login view with rate limiting:
    - Anonymous users: 5 requests per minute
    - Authenticated users: 10 requests per minute
    """
    # Check if request was rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return HttpResponseForbidden(
            'Rate limit exceeded. Please try again later.'
        )

    # Get credentials from POST data
    username = request.POST.get('username')
    password = request.POST.get('password')

    if not username or not password:
        return HttpResponseForbidden(
            'Username and password are required.'
        )

    # Authenticate user
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse('Login successful!')
    else:
        return HttpResponseForbidden('Invalid credentials.')