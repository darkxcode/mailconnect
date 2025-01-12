from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add rate limiting logic here if needed
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, RateLimitExceeded):
            return HttpResponseTooManyRequests("Too many requests. Please try again later.")
        return None

class RateLimitExceeded(Exception):
    pass

class HttpsRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If DEBUG is True, redirect HTTPS to HTTP
        if settings.DEBUG and request.is_secure():
            url = request.build_absolute_uri(request.get_full_path())
            url = url.replace('https://', 'http://')
            return HttpResponseRedirect(url)
        
        return self.get_response(request)